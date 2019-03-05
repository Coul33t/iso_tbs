import pygame
from pygame.locals import *

from math import ceil, floor

from tools import dst_euc, dst_man, Point, point_in, Spritesheet
from constants import *
from ui_shapes import *
from actor import Actor, Stats
from gamemap import GameMap

DEBUG = True

class Engine:
    def __init__(self, gamemap=GameMap()):
        self.window = None
        self.map_panel = None
        self.stats_panel = None
        self.stats_enemy_panel = None
        self.message_panel = None
        self.buttons_panel = None

        self.actors = []
        self.turn_to_take = []

        self.gamemap = gamemap
        self.highlighted_cases = []

        self.event_queue = []
        self.message_queue = []

        self.unit_turn = None

        self.re_render = True

        self.under_mouse = None

        self.map_offset = Point(MAP_PANEL.x, MAP_PANEL.y)

        self.init_game()
        self.spritesheet = Spritesheet('res/spritesheet.png')

        self.game_state = 'menu'
        self.game_state = 'playing'

    def init_display(self):
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_SIZE.pv_w, WINDOW_SIZE.pv_h))
        self.map_panel = pygame.Surface((MAP_PANEL.pv_w, MAP_PANEL.pv_h))
        self.stats_panel = pygame.Surface((STATS_PANEL.pv_w, STATS_PANEL.pv_h))
        self.stats_enemy_panel = pygame.Surface((STATS_ENEMY_PANEL.pv_w, STATS_ENEMY_PANEL.pv_h))
        self.message_panel = pygame.Surface((MESSAGE_PANEL.pv_w, MESSAGE_PANEL.pv_h))
        self.buttons_panel = pygame.Surface((BUTTONS_PANEL.pv_w, BUTTONS_PANEL.pv_h))
        pygame.display.set_caption('Iso TBS')
        self.spritesheet.load_all_sprites()



    def init_game(self):
        # self.gamemap.load_map_from_json('res/map/test_map.json')
        self.gamemap.create_default_terrain()

        for i in range(3, 6):
            self.actors.append(Actor('soldier', 's', 0, sprite='soldier', color=TEAM_COLORS[0], 
                                     x=i, y=1, movement=1, stats=Stats(3,3,1)))
        for i in range(0, 10, 2):
            self.actors.append(Actor('barbarian', 'b', 1, sprite='mercenary', color=TEAM_COLORS[1], x=i, y=8, movement=2,
                                     stats=Stats(3,2,0)))


        self.actors.append(Actor('king', 'K', 0, sprite='king', color=TEAM_COLORS[0], x=4, y=0,
                                 movement=2, stats=Stats(5,3,4)))
        self.actors.append(Actor('leader', 'L', 1, sprite='leader', color=TEAM_COLORS[1], x=4, y=9,
                                 movement=2, stats=Stats(7,4,2)))

        self.actors.append(Actor('Xander', 'S', 2, sprite='xander', color=TEAM_COLORS[2], x=5, y=5,
                                 movement=10, stats=Stats(7,40,2)))

        self.turn_to_take = self.actors.copy()
        self.turn_to_take.sort(key=lambda x: x.stats.mod['agility'], reverse=True)
        self.unit_turn = self.turn_to_take.pop(0)
        self.unit_turn.new_turn()
        self.game_state = 'new_turn'

    def get_possible_movement(self, actor):
        possible_movement = []
        # This is done so tiles can be highlighted in amber for allies
        # and red for enemies
        actors_position = {(p.x, p.y): p for p in self.actors}

        if actor.movement_left == 0 and not actor.has_attacked:

            to_check =[Point(x+actor.x, y+actor.y) for x in range(-1,2) for y in range(-1,2)
                                                   if ((x != 0 or y != 0) and dst_euc(Point(x,y)) <= 1)]

            for tc in to_check:

                if ((tc.x, tc.y) in actors_position.keys()):
                    if actors_position[(tc.x, tc.y)].blocks:
                        if actors_position[(tc.x, tc.y)].team != actor.team:
                            possible_movement.append({'mov': tc, 'valid':'enemy'})

            return possible_movement



        # compute the possible movement
        possible_movement = [Point(x+actor.x, y+actor.y) for x in range(-actor.movement_left, actor.movement_left+1)
                                                         for y in range(-actor.movement_left, actor.movement_left+1)
                                                         if ((x != 0 or y != 0) and dst_euc(Point(x,y)) <= actor.movement_left)]

        # Eliminate out of bounds movements
        possible_movement = [{'mov':pm, 'valid':'true'} for pm in possible_movement
                             if (pm.x > -1 and pm.x < self.gamemap.w
                             and pm.y > -1 and pm.y < self.gamemap.h)]

        for pm in possible_movement:

            x = pm['mov'].x
            y = pm['mov'].y

            if ((x, y) in actors_position.keys()):
                if actors_position[(x, y)].blocks:
                    if actors_position[(x, y)].team != actor.team:
                        pm['valid'] = 'enemy'
                    else:
                        pm['valid'] = 'false'

        return possible_movement


    def mouse_check(self, coordinates):
        # Useful for map related stuff
        offseted_coordinates = Point(floor((coordinates[0] / TERRAIN_SCALE_X) - self.map_offset.x),
                                     floor((coordinates[1] / TERRAIN_SCALE_Y) - self.map_offset.y))

        # Moving on an empty case if there are some movement left
        if self.unit_turn.movement_left > 0 and point_in(offseted_coordinates, [x['mov'] for x in self.highlighted_cases if x['valid'] == 'true']):

            self.unit_turn.movement_left -= dst_man(Point(self.unit_turn.x, self.unit_turn.y),
                                                    Point(offseted_coordinates.x,  offseted_coordinates.y))

            message = f'Moved from {chr(self.unit_turn.x + 65)}{self.unit_turn.y} to {chr(offseted_coordinates.x + 65)}{offseted_coordinates.y}'

            self.unit_turn.x = offseted_coordinates.x
            self.unit_turn.y = offseted_coordinates.y

            self.message_queue.append(message)

        # Attacking an enemy
        elif point_in(offseted_coordinates, [x['mov'] for x in self.highlighted_cases if x['valid'] == 'enemy']):
            other_actor = [a for a in self.actors if Point(a.x, a.y) == offseted_coordinates][0]

            # If we're close enough
            if dst_man(Point(self.unit_turn.x, self.unit_turn.y), Point(other_actor.x, other_actor.y)) == 1:
                self.message_queue.append(self.unit_turn.attack(other_actor))

                # The unit lose half (floored) of its remaining movement
                self.unit_turn.movement_left = floor(self.unit_turn.movement_left / 2)

        # Ending turn
        elif coordinates in [(x, TERMINAL_SIZE_Y - 6) for x in range(TERMINAL_SIZE_X - 8, TERMINAL_SIZE_X)]:
            self.game_state = 'end_turn'

    def check_under_mouse(self):
        pass

    def render(self):
        # Clean display
        self.window.fill((0, 0, 0))
        self.map_panel.fill((0, 0, 0))
        self.stats_panel.fill((0, 0, 0))
        self.stats_enemy_panel.fill((0, 0, 0))
        self.message_panel.fill((0, 0, 0))
        self.buttons_panel.fill((0, 0, 0))

        if DEBUG:
            red = pygame.Color(255, 0, 0)
            green = pygame.Color(0, 255 ,0)
            blue = pygame.Color(0, 0, 255)
            yellow = pygame.Color(255, 255, 0)
            black = pygame.Color(0, 0, 0)
            white = pygame.Color(255, 255, 255)

            self.window.fill(white)
            self.map_panel.fill(blue)
            self.stats_panel.fill(green)
            self.stats_enemy_panel.fill(yellow)
            self.message_panel.fill(red)
            self.buttons_panel.fill(black)

        for y, row in enumerate(self.gamemap.terrain):
            for x, tile in enumerate(row):
                self.map_panel.blit(self.spritesheet.get_sprite(tile.sprite), (x * TILE_SIZE_X, y * TILE_SIZE_Y))

        for actor in [a for a in self.actors if not a.dead]:
            self.map_panel.blit(self.spritesheet.get_sprite(actor.sprite), (actor.x * TILE_SIZE_X, actor.y * TILE_SIZE_Y))

        mx, my = pygame.mouse.get_pos()
        mouse_pt = Point(mx, my)
        if mouse_pt.inside(self.map_panel):
            rel_x = mouse_pt.x - self.map_panel.pv_x
            rel_y = mouse_pt.y - self.map_panel.pv_y


        self.window.blit(self.map_panel, (MAP_PANEL.pv_x, MAP_PANEL.pv_y))
        self.window.blit(self.stats_panel, (STATS_PANEL.pv_x, STATS_PANEL.pv_y))
        self.window.blit(self.stats_enemy_panel, (STATS_ENEMY_PANEL.pv_x, STATS_ENEMY_PANEL.pv_y))
        self.window.blit(self.message_panel, (MESSAGE_PANEL.pv_x, MESSAGE_PANEL.pv_y))
        self.window.blit(self.buttons_panel, (BUTTONS_PANEL.pv_x, BUTTONS_PANEL.pv_y))
        pygame.display.update()


    def update(self):
        # If everybody took its turn, then new turn: the list containing
        # actors and order is recomputed
        if not self.turn_to_take:
            self.turn_to_take = [a for a in self.actors if not a.dead]
            self.turn_to_take.sort(key=lambda x: x.stats.mod['agility'], reverse=True)

        for event in pygame.event.get():
            if event.type == QUIT:
                self.game_state = 'exit'


        self.unit_turn.check_end()

        # If the turn is over, switch to the next unit
        if self.unit_turn.has_played or self.game_state == 'end_turn':
            self.game_state = 'new_turn'
            self.unit_turn.end_turn()

            self.unit_turn = self.turn_to_take.pop(0)
            while self.unit_turn.dead:
                self.unit_turn = self.turn_to_take.pop(0)

            self.unit_turn.new_turn()

    def exit(self):
        pygame.quit()
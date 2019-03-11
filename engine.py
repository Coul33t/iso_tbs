import pygame
from pygame.locals import *

from collections import deque
from math import ceil, floor

from tools import dst_euc, dst_man, Point, Spritesheet, BFS, get_4_connected, get_ranged_connected
from constants import *
from ui_shapes import *
from actor import Actor, Stats
from gamemap import GameMap

DEBUG = False

class Engine:
    def __init__(self, gamemap=GameMap()):
        self.window = None
        self.map_panel = None
        self.stats_panel = None
        self.stats_enemy_panel = None
        self.message_panel = None
        self.buttons_panel = None

        self.hp_bar = None

        self.spritesheet = None

        self.stats_font = None

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


        self.game_state = 'menu'
        self.game_state = 'playing'

    def init_display(self):
        pygame.init()

        # Window
        self.window = pygame.display.set_mode((WINDOW_SIZE.pv_w, WINDOW_SIZE.pv_h))
        pygame.display.set_caption('Iso TBS')

        # Panels
        self.map_panel = pygame.Surface((MAP_PANEL.pv_w, MAP_PANEL.pv_h))
        self.stats_panel = pygame.Surface((STATS_PANEL.pv_w, STATS_PANEL.pv_h))
        self.stats_enemy_panel = pygame.Surface((STATS_ENEMY_PANEL.pv_w, STATS_ENEMY_PANEL.pv_h))
        self.message_panel = pygame.Surface((MESSAGE_PANEL.pv_w, MESSAGE_PANEL.pv_h))
        self.buttons_panel = pygame.Surface((BUTTONS_PANEL.pv_w, BUTTONS_PANEL.pv_h))

        # HP Bar
        self.hp_bar = pygame.Surface((STATS_PANEL.pv_w, TILE_SIZE_Y))

        # Spritesheet loading
        self.spritesheet = Spritesheet('res/spritesheet.png')
        self.spritesheet.load_all_sprites()

        # Font loading
        self.stats_font = pygame.font.SysFont("monospace", 32)


    def init_game(self):
        # self.gamemap.load_map_from_json('res/map/test_map.json')
        self.gamemap.create_default_terrain()

        for i in range(3, 6):
            self.actors.append(Actor('soldier', 's', 0, sprite='soldier', color=TEAM_COLORS[0],
                                     x=i, y=2, movement=1, stats=Stats(3, 3, 1)))
        for i in range(0,10):
            self.actors.append(Actor('barbarian', 'b', 1, sprite='mercenary', color=TEAM_COLORS[1], x=4, y=i+6, movement=2,
                                     stats=Stats(3, 2, 0)))


        self.actors.append(Actor('king', 'K', 0, sprite='king', color=TEAM_COLORS[0], x=4, y=1,
                                 movement=2, stats=Stats(5, 3, 4)))
        self.actors.append(Actor('leader', 'L', 1, sprite='leader', color=TEAM_COLORS[1], x=5, y=9,
                                 movement=2, stats=Stats(7, 4, 2)))

        self.actors.append(Actor('Xander', 'S', 2, sprite='xander', color=TEAM_COLORS[2], x=5, y=7,
                                 movement=5, stats=Stats(7, 40, 2)))

        self.turn_to_take = self.actors.copy()
        self.turn_to_take.sort(key=lambda x: x.stats.mod['agility'], reverse=True)
        self.unit_turn = self.turn_to_take.pop(0)
        self.unit_turn.new_turn()
        self.unit_turn.stats.mod['range'] = 3
        self.game_state = 'new_turn'

        self.highlighted_cases = self.get_possible_movement(self.unit_turn)

    def get_possible_movement(self, actor):
        possible_movement = []
        # This is done so tiles can be highlighted in amber for allies
        # and red for enemies
        actors_position = {Point(p.x, p.y): p for p in self.actors if not p.dead}

        if actor.movement_left == 0 and not actor.has_attacked:

            to_check =[Point(x+actor.x, y+actor.y) for x in range(-1,2) for y in range(-1,2)
                                                   if ((x != 0 or y != 0) and dst_man(Point(x,y)) <= 1)]


            for tc in to_check:

                if tc in actors_position.keys():
                    if actors_position[tc].blocks:
                        if actors_position[tc].team != actor.team:
                            possible_movement.append({'pt': tc, 'valid':'enemy'})
                        if actors_position[tc].team == actor.team:
                            possible_movement.append({'pt': tc, 'valid':'ally'})

            attack_range = set()
            w_range = self.unit_turn.stats.mod['range']
            to_add = get_ranged_connected(Point(actor.x, actor.y), w_range)
            attack_range.update(to_add)

            enemies = list([{'pt': x, 'valid': 'attack'} for x in attack_range])
            possible_movement.extend(enemies)
            return possible_movement


        # compute the possible movement (eliminate the out of bounds movement, unwalkable tiles and enemy units tile at the same time)
        actor_pt = list(actors_position.keys())

        possible_movement = [(x+actor.x, y+actor.y)
                             for x in range(-actor.movement_left, actor.movement_left+1)
                             for y in range(-actor.movement_left, actor.movement_left+1)
                             if (x+actor.x > -1 and x+actor.x < self.gamemap.w          # Out of bounds (x)
                                 and y+actor.y > -1 and  y+actor.y < self.gamemap.h)    # Out of bounds (y)
                             and dst_man(Point(x, y)) <= actor.movement_left     # Useless?
                             and self.gamemap.terrain[y+actor.y][x+actor.x].properties['walkable'] == True # Walkable
                             and not (Point(x+actor.x, y+actor.y) in actor_pt
                                      and actors_position[Point(x+actor.x, y+actor.y)].team != actor.team)] # No enemy tiles



        origin = (actor.x,actor.y)
        movement_list = BFS(origin, possible_movement)

        # Re-add enemies for attack check
        enemies = set()
        for tile in movement_list:
            for enemy_check in get_4_connected(tile):
                if Point(enemy_check) in actor_pt and not actors_position[Point(enemy_check)].dead and actor != actors_position[Point(enemy_check)]  and actor.team != actors_position[Point(enemy_check)].team:
                    enemies.add(enemy_check)


        attack_range = set()
        w_range = self.unit_turn.stats.mod['range']
        for tile in movement_list:
            to_add = get_ranged_connected(tile, w_range)
            attack_range.update(to_add)
        attack_range = (attack_range - movement_list) - enemies

        enemies = list([{'pt': Point(x), 'valid': 'enemy'} for x in enemies])
        attack_range = list([{'pt': Point(x), 'valid': 'attack'} for x in attack_range])

        movement_list = [{'pt': Point(x)} for x in movement_list]

        for pm in movement_list:

            pm['valid'] = 'true'

            if pm['pt'] in actors_position.keys():
                if actors_position[pm['pt']].blocks:
                    if actors_position[pm['pt']].team == actor.team:
                        pm['valid'] = 'ally'
                    else:
                        pm['valid'] = 'false'

        movement_list.extend(enemies)
        movement_list.extend(attack_range)

        return movement_list

    def key_check(self, key_info):
        if key_info['key'] in QUIT_KEY:
            self.game_state = 'exit'

        if key_info['key'] in ACTION_KEY:
            if key_info['key'] == 32:
                self.game_state = 'end_turn'

    def mouse_in_panel(self):
        mx, my = pygame.mouse.get_pos()
        mouse_pt = Point(mx, my)

        if mouse_pt.inside(MAP_PANEL):
            return 'map'

        elif mouse_pt.inside(STATS_PANEL):
            return 'stats'

        elif mouse_pt.inside(STATS_ENEMY_PANEL):
            return 'stats_enemy'

        elif mouse_pt.inside(MESSAGE_PANEL):
            return 'message'

        elif mouse_pt.inside(BUTTONS_PANEL):
            return 'button'

        return None

    def mouse_click_check(self, coordinates):
        if self.mouse_in_panel() == 'map':

            new_x, new_y = self.mouse_coord_to_panel(coordinates, MAP_PANEL, to_tile=True)
            new_coord = Point(new_x, new_y)

            # Moving on an empty case if there are some movement left
            if self.unit_turn.movement_left > 0 and new_coord.point_in([x['pt'] for x in self.highlighted_cases if x['valid'] == 'true']):

                self.unit_turn.movement_left -= dst_man(Point(self.unit_turn.x, self.unit_turn.y),
                                                        Point(new_coord.x,  new_coord.y))

                message = f'Moved from {chr(self.unit_turn.x + 65)}{self.unit_turn.y} to {chr(new_coord.x + 65)}{new_coord.y}'

                self.unit_turn.x = new_coord.x
                self.unit_turn.y = new_coord.y

                self.message_queue.append(message)
                self.highlighted_cases = self.get_possible_movement(self.unit_turn)

            # Attacking an enemy
            elif new_coord.point_in([x['pt'] for x in self.highlighted_cases if x['valid'] == 'enemy']):
                other_actor = [a for a in self.actors if Point(a.x, a.y) == new_coord][0]

                # If we're close enough
                if dst_man(Point(self.unit_turn.x, self.unit_turn.y), Point(other_actor.x, other_actor.y)) <= self.unit_turn.stats.mod['range']:
                    self.message_queue.append(self.unit_turn.attack(other_actor))

                    # The unit lose 3/4 (floored) of its remaining movement
                    self.unit_turn.movement_left = floor(self.unit_turn.movement_left / 4)
                    self.highlighted_cases = self.get_possible_movement(self.unit_turn)

    def check_under_mouse(self):
        mx, my = pygame.mouse.get_pos()
        mouse_pt = Point(mx, my)

        if self.mouse_in_panel() == 'map':
            pos_x, pos_y = self.mouse_coord_to_panel(mouse_pt, MAP_PANEL, to_tile=True)
            for a in self.actors:
                if a != self.unit_turn and pos_x == a.x and pos_y == a.y:
                    return a

    def mouse_coord_to_panel(self, coords, panel, to_tile=False):
        if not isinstance(coords, Point):
            coords = Point(coords[0], coords[1])

        rel_x = coords.x - panel.pv_x
        rel_y = coords.y - panel.pv_y

        new_x = floor(rel_x / TILE_SIZE_X)
        new_y = floor(rel_y / TILE_SIZE_Y)

        if not to_tile:
            new_x *= TILE_SIZE_X
            new_y *= TILE_SIZE_Y

        return new_x, new_y

    def render_stats(self, unit, panel):

        # Name
        name = unit.name
        if len(name) > panel.get_rect()[2] / TILE_SIZE_X:
            name = name[:int(panel.get_rect()[2] / TILE_SIZE_X)-3] + '...'
        name = self.stats_font.render(f"{name}", 1, (255, 255, 255))
        panel.blit(name, (0, 0))

        # HP Bar
        self.hp_bar.fill((255, 100, 100))
        w_fill = (unit.stats.mod['hp'] / unit.stats.mod['max_hp']) * self.hp_bar.get_rect()[2]
        rect_fill = pygame.Rect(0, 0, w_fill, TILE_SIZE_Y)
        pygame.draw.rect(self.hp_bar, (100, 255, 100), rect_fill)
        panel.blit(self.hp_bar, (0, TILE_SIZE_Y))

        hp = self.stats_font.render(f"{unit.stats.mod['hp']}/{unit.stats.mod['max_hp']}", 1, (255, 255, 255))
        panel.blit(hp, (0, TILE_SIZE_Y))

        strength = self.stats_font.render(f"STR: {unit.stats.mod['strength']}", 1, (255, 150, 150))
        panel.blit(strength, (0, TILE_SIZE_Y*2))

        defence = self.stats_font.render(f"DEF: {unit.stats.mod['defence']}", 1, (150, 150, 150))
        panel.blit(defence, (panel.get_rect()[2] / 2, TILE_SIZE_Y*2))

        agility = self.stats_font.render(f"AGI: {unit.stats.mod['agility']}", 1, (150, 255, 150))
        panel.blit(agility, (0, TILE_SIZE_Y*3))

        intelligence = self.stats_font.render(f"INT: {unit.stats.mod['intel']}", 1, (150, 150, 255))
        panel.blit(intelligence, (0, TILE_SIZE_Y*4))

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

        # Terrain
        for y, row in enumerate(self.gamemap.terrain):
            for x, tile in enumerate(row):
                self.map_panel.blit(self.spritesheet.get_sprite(tile.sprite), (x * TILE_SIZE_X, y * TILE_SIZE_Y))

        # Legal moves
        for highlight in self.highlighted_cases:

            if highlight['valid'] == 'true':
                self.map_panel.blit(self.spritesheet.get_sprite('legal_move'), (highlight['pt'].x * TILE_SIZE_X, highlight['pt'].y * TILE_SIZE_Y))
            elif highlight['valid'] == 'enemy':
                self.map_panel.blit(self.spritesheet.get_sprite('enemy'), (highlight['pt'].x * TILE_SIZE_X, highlight['pt'].y * TILE_SIZE_Y))
            elif highlight['valid'] == 'attack':
                self.map_panel.blit(self.spritesheet.get_sprite('range'), (highlight['pt'].x * TILE_SIZE_X, highlight['pt'].y * TILE_SIZE_Y))
            elif highlight['valid'] == 'ally':
                self.map_panel.blit(self.spritesheet.get_sprite('ally'), (highlight['pt'].x * TILE_SIZE_X, highlight['pt'].y * TILE_SIZE_Y))

        # Actors
        for actor in [a for a in self.actors if not a.dead]:
            self.map_panel.blit(self.spritesheet.get_sprite(actor.sprite), (actor.x * TILE_SIZE_X, actor.y * TILE_SIZE_Y))

        self.map_panel.blit(self.spritesheet.get_sprite('current_unit'), (self.unit_turn.x * TILE_SIZE_X, self.unit_turn.y * TILE_SIZE_Y))

        # Cursor
        mx, my = pygame.mouse.get_pos()
        mouse_pt = Point(mx, my)
        if mouse_pt.inside(MAP_PANEL):
            new_x, new_y = self.mouse_coord_to_panel(mouse_pt, MAP_PANEL)
            self.map_panel.blit(self.spritesheet.get_sprite('cursor'), (new_x, new_y))

        self.render_stats(self.unit_turn, self.stats_panel)

        a = self.check_under_mouse()
        if a:
            self.render_stats(a, self.stats_enemy_panel)

        self.window.blit(self.map_panel, (MAP_PANEL.pv_x, MAP_PANEL.pv_y))
        self.window.blit(self.stats_panel, (STATS_PANEL.pv_x, STATS_PANEL.pv_y))
        self.window.blit(self.stats_enemy_panel, (STATS_ENEMY_PANEL.pv_x, STATS_ENEMY_PANEL.pv_y))
        #self.window.blit(self.message_panel, (MESSAGE_PANEL.pv_x, MESSAGE_PANEL.pv_y))
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

            if event.type == pygame.MOUSEBUTTONUP:
                self.event_queue.append(['mouse_left_click'])

            if event.type == KEYDOWN:
                self.event_queue.append(['key_pressed', event.dict])


        for event in self.event_queue:
            if event[0] == 'mouse_left_click':
                mx, my = pygame.mouse.get_pos()
                mouse_pt = Point(mx, my)
                self.mouse_click_check(mouse_pt)

            elif event[0] == 'key_pressed':
                self.key_check(event[1])

            self.event_queue.remove(event)

        self.unit_turn.check_end()

        # If the turn is over, switch to the next unit
        if self.unit_turn.has_played or self.game_state == 'end_turn':
            self.game_state = 'new_turn'
            self.unit_turn.end_turn()

            self.unit_turn = self.turn_to_take.pop(0)
            while self.unit_turn.dead:
                self.unit_turn = self.turn_to_take.pop(0)

            self.unit_turn.new_turn()
            self.highlighted_cases = self.get_possible_movement(self.unit_turn)

    def exit(self):
        pygame.quit()

import pygame
from pygame.locals import *

from math import ceil, floor

from tools import dst_euc, dst_man, Point, point_in
from constants import *
from actor import Actor, Stats
from gamemap import GameMap

DEBUG = False

class Engine:
    def __init__(self, gamemap=GameMap()):
        self.window = None

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
        self.window = pygame.display.set_mode((400, 300))
        pygame.display.set_caption('Iso TBS')


    def init_game(self):
        # self.gamemap.load_map_from_json('res/map/test_map.json')
        self.gamemap.create_default_terrain()

        for i in range(3, 6):
            self.actors.append(Actor('soldier', 's', 0, sprite=0xE100, color=TEAM_COLORS[0], x=i, y=1, movement=1,
                                     stats=Stats(3,3,1)))
        for i in range(0, 10, 2):
            self.actors.append(Actor('barbarian', 'b', 1, sprite=0xE101, color=TEAM_COLORS[1], x=i, y=8, movement=2,
                                     stats=Stats(3,2,0)))


        self.actors.append(Actor('king', 'K', 0, sprite=0xE102, color=TEAM_COLORS[0], x=4, y=0,
                                 movement=2, stats=Stats(5,3,4)))
        self.actors.append(Actor('leader', 'L', 1, sprite=0xE103, color=TEAM_COLORS[1], x=4, y=9,
                                 movement=2, stats=Stats(7,4,2)))

        self.actors.append(Actor('Xander', 'S', 2, sprite=0xE104, color=TEAM_COLORS[2], x=5, y=5,
                                 movement=10, stats=Stats(7,40,2)))

        self.turn_to_take = self.actors.copy()
        self.turn_to_take.sort(key=lambda x: x.stats.mod['agility'], reverse=True)
        self.unit_turn = self.turn_to_take.pop(0)
        self.unit_turn.new_turn()
        self.game_state = 'new_turn'

    def close_game(self):
        blt.close()

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

    def key_check(self, key):
        if key in QUIT_KEY:
            self.game_state = 'exit'

        if key in ACTION_KEY:
            if key == 44:
                self.game_state = 'end_turn'


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
        self.under_mouse = None

        mx = blt.state(blt.TK_MOUSE_X)
        my = blt.state(blt.TK_MOUSE_Y)
        off_mouse = Point(floor((mx / TERRAIN_SCALE_X) - self.map_offset.x),
                                     floor((my / TERRAIN_SCALE_Y) - self.map_offset.y))

        for a in self.actors:
            if a != self.unit_turn and a.x == off_mouse.x and a.y == off_mouse.y:
                self.under_mouse = a

    def render(self):


    def update(self):
        # If everybody took its turn, then new turn: the list containing
        # actors and order is recomputed
        if not self.turn_to_take:
            self.turn_to_take = [a for a in self.actors if not a.dead]
            self.turn_to_take.sort(key=lambda x: x.stats.mod['agility'], reverse=True)




        self.unit_turn.check_end()

        # If the turn is over, switch to the next unit
        if self.unit_turn.has_played or self.game_state == 'end_turn':
            self.game_state = 'new_turn'
            self.unit_turn.end_turn()

            self.unit_turn = self.turn_to_take.pop(0)
            while self.unit_turn.dead:
                self.unit_turn = self.turn_to_take.pop(0)

            self.unit_turn.new_turn()
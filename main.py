from math import sqrt, ceil

from bearlibterminal import terminal as blt
import tdl

import pdb

TERMINAL_SIZE_X = 30
TERMINAL_SIZE_Y = 19

MESSAGE_PANEL_X = 0
MESSAGE_PANEL_W = TERMINAL_SIZE_X
MESSAGE_PANEL_H = 5
MESSAGE_PANEL_Y = TERMINAL_SIZE_Y - MESSAGE_PANEL_H

QUIT_KEY = (41, 224)
ACTION_KEY = ()
MOVEMENT_KEYS = {93: [0, 0], 90: [0, 1], 89: [-1, 1], 92: [-1, 0], 95: [-1, -1], 96: [0, -1], 97: [1, -1],
                 94: [1, 0], 91: [1, 1]}

TEAM_COLORS = ['blue', 'red', 'green', 'yellow']
ACTIVE_COLOR = 'green'
KEY = {'tab': 43}

# Euclidean distance
def dst_euc(p1, p2=(0,0)):
    return sqrt(pow(p2[0] - p1[0], 2) + pow(p2[1] - p1[1], 2))

# Manhattan distance
def dst_man(p1, p2=(0,0)):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
# Classes #
class Tile:
    def __init__(self, color, charac=' ', properties=[]):
        self.color = color
        self.charac = charac
        self.properties = properties

class Actor:
    def __init__(self, name, charac, team, facing, color='blue', x=0, y=0, movement=3, stats=None, stats_growth=None, main_attribute='None'):
        self.name = name
        self.charac = charac
        self.team = team
        self.color = color
        self.perma_color = color
        self.x = x
        self.y = y

        self.level = 1

        self.has_played = False

        self.movement = movement
        self.movement_left = movement

        self.has_attacked = False

        self.stats = stats
        if not stats or not isinstance(stats, dict) or not all(k in stats for k in ('strength', 'agility', 'intel')):
            self.stats = {'strength': 1, 'agility': 1, 'intel': 1}

        self.main_attribute = main_attribute

        self.stats_growth = stats_growth
        if not stats_growth or not isinstance(stats_growth, dict) or not all(k in stats_growth for k in ('strength', 'agility', 'intel')):
            self.stats_growth = {'strength': 0.33, 'agility': 0.33, 'intel': 0.33}

        self.stats['HP'] = round(self.stats['strength'] * 2 + self.stats['agility'] * 1.5 + self.stats['intel'] * 0.5)
        self.stats['defence'] = round(self.stats['strength'] * 0.15 + self.stats['agility'] * 0.2 + self.stats['intel'] * 0.05)

        self.xp = 0
        self.next_level = 100

    def __str__(self):
        return_string = f'Name : {self.name} -> {self.charac}\n'
        return_string += f'Level: {self.level}\n'
        return_string += f'Current xp: {self.xp}\n'
        return_string += f'XP to next level: {self.next_level - self.xp}\n'
        return_string += f'Movement: up to {self.movement} tiles\n'

        return_string += '\nStats:\n'
        for stat, value in self.stats.items():
            return_string += f'{stat} : {value}\n'

        return return_string

    def check_level(self):
        if self.xp >= self.next_level:
            # xp growth: u(n) = u(n-1) + 50 * (n-1)
            self.level += 1
            self.xp = self.xp - self.next_level
            self.next_level = self.next_level + 50 * (self.level - 1)

            # If we take multiples level
            while self.xp >= self.next_level:
                self.level += 1
                self.xp = self.xp - self.next_level
                self.next_level = self.next_level + 50 * (self.level - 1)

    def end_turn(self):
        self.color = self.perma_color

    def new_turn(self):
        self.color = ACTIVE_COLOR
        self.movement_left = self.movement
        self.has_attacked = False

    def attack(self, other_actor):

        if self.has_attacked:
            return f'The {self.name} already attacked during this turn.'

        self.has_attacked = True

        damage = round(self.stats['strength'] - other_actor.stats['defence'])
        
        if self.main_attribute != 'None':
            damage += self.stats[self.main_attribute]

        if damage > 0:
            other_actor.stats['HP'] -= damage
            return f'The {self.name} did {damage} damage to the {other_actor.name}!'

        return f'The {self.name} did non damage to the {other_actor.name}.'



class GameMap:
    def __init__(self, terrain=[], display_offset={'x': 1, 'y': 2}):
        self.terrain = terrain
        self.display_offset = display_offset
        self.size = {}

    def create_default_terrain(self):
        for y in range(10):
            new_row = []
            for x in range(10):
                color = 'white'

                if (y%2 == 0 and x%2 == 1) or (y%2 == 1 and x%2 == 0):
                    color = 'grey'

                new_row.append(Tile(color))
            self.terrain.append(new_row)

        self.size = {'x': len(self.terrain[0]), 'y': len(self.terrain)}


class Engine:
    def __init__(self, gamemap=GameMap()):
        self.actors = []
        self.turn_to_take = []

        self.gamemap = gamemap
        self.highlighted_cases = []

        self.event_queue = []
        self.message_queue = []

        self.unit_turn = None

        self.re_render = True

        self.init_gamemap()

        self.game_state = 'menu'
        self.game_state = 'playing'

    def init_terminal(self):
        blt.open()
        blt.set(f"window.size={TERMINAL_SIZE_X}x{TERMINAL_SIZE_Y}, window.cellsize=48x48")
        blt.set("font: res/tilesets/Curses_square_24.png, size=24x24, resize=48x48")
        blt.set("window.title='SimplyRL'")
        blt.set("input.filter={keyboard, mouse+}")
        blt.composition(True)
        blt.refresh()

    def init_gamemap(self):
        self.gamemap.create_default_terrain()
        
        for i in range(3, 6):
            self.actors.append(Actor('soldier', 's', 0, 'south', color=TEAM_COLORS[0], x=i, y=1, movement=1,
                                     stats={'strength': 3, 'agility': 3, 'intel': 1}))
        for i in range(0, 10, 2):  
            self.actors.append(Actor('barbarian', 'b', 1, 'north', color=TEAM_COLORS[1], x=i, y=8, movement=2,
                                     stats={'strength': 3, 'agility': 2, 'intel': 0}))


        self.actors.append(Actor('king', 'K', 0, 'south', color=TEAM_COLORS[0], x=4, y=0, 
                                 movement=2, stats={'strength': 5, 'agility': 3, 'intel': 4}))
        self.actors.append(Actor('leader', 'L', 1, 'north', color=TEAM_COLORS[1], x=4, y=9, 
                                 movement=2, stats={'strength': 7, 'agility': 4, 'intel': 2}))

        self.actors.append(Actor('SOUPER', 'S', 1, 'north', color=TEAM_COLORS[2], x=5, y=5, 
                                 movement=10, stats={'strength': 7, 'agility': 40, 'intel': 2}))

        self.turn_to_take = self.actors.copy()
        self.turn_to_take.sort(key=lambda x: x.stats['agility'], reverse=True)
        self.unit_turn = self.turn_to_take[0]
        self.unit_turn.new_turn()
        self.highlighted_cases = self.get_possible_movement(self.unit_turn)
        self.game_state = 'new_turn'

    def get_possible_movement(self, actor):
        possible_movement = []

        # compute the 
        possible_movement = [(x+actor.x, y+actor.y) for x in range(-actor.movement_left, actor.movement_left+1) 
                                                    for y in range(-actor.movement_left, actor.movement_left+1) 
                                                    if ((x != 0 or y != 0) and dst_euc((x,y)) <= actor.movement_left)]

        # Eliminate out of bounds movements
        possible_movement = [{'mov':pm, 'valid':'true'} for pm in possible_movement 
                             if (pm[0] > -1 and pm[0] < self.gamemap.size['x'] 
                             and pm[1] > -1 and pm[1] < self.gamemap.size['y'])]

        # This is done so tiles can be highlighted in red for not valid movements
        actors_position = {(p.x, p.y): p for p in self.actors}

        for pm in possible_movement:
            if (pm['mov'] in actors_position.keys()):
                if actors_position[pm['mov']].team != actor.team:
                    pm['valid'] = 'enemy'
                else:
                    pm['valid'] = 'false'

        return possible_movement

    def key_check(self, key):
        if key in QUIT_KEY:
            self.game_state = 'exit'

        # elif key in ACTION_KEY or key in MOVEMENT_KEYS:
        #     print(key)
        #     self.game_state = 'turn_taken'


    def mouse_check(self, coordinates):
        # Useful for map related stuff
        offseted_coordinates = (coordinates[0] - self.gamemap.display_offset['x'], coordinates[1] - self.gamemap.display_offset['y'])

        # Moving on an empty case if there are some movement left
        if self.unit_turn.movement_left > 0 and offseted_coordinates in [x['mov'] for x in self.highlighted_cases if x['valid'] == 'true']:
            self.unit_turn.movement_left -= dst_man((self.unit_turn.x, self.unit_turn.y),
                                                    (offseted_coordinates[0],  offseted_coordinates[1]))
            
            self.unit_turn.x = offseted_coordinates[0]
            self.unit_turn.y = offseted_coordinates[1]

            self.highlighted_cases = self.get_possible_movement(self.unit_turn)
            self.message_queue.append('JFDGFDJKL')

        # Attacking an enemy
        elif offseted_coordinates in [x['mov'] for x in self.highlighted_cases if x['valid'] == 'enemy']:
            other_actor = [a for a in self.actors if (a.x, a.y) == offseted_coordinates][0]
            if dst_man((self.unit_turn.x, self.unit_turn.y), (other_actor.x, other_actor.y)) == 1:
                self.message_queue.append(self.unit_turn.attack(other_actor))

        # Ending turn
        elif coordinates in [(x, TERMINAL_SIZE_Y - 1) for x in range(TERMINAL_SIZE_X - 8, TERMINAL_SIZE_X)]:
            self.game_state = 'end_turn'

    def render(self):

        if not self.re_render:
            return 

        print('Renderuuuu')
        blt.clear()

        offset = self.gamemap.display_offset

        # Gameboard related stuff
        blt.layer(0)
        
        # Board drawing
        for y, row in enumerate(self.gamemap.terrain):
            for x, _ in enumerate(row):
                color = 'white'

                if (y%2 == 0 and x%2 == 1) or (y%2 == 1 and x%2 == 0):
                    color = 'grey'

                blt.bkcolor(color)
                blt.puts(x + offset['x'], y + offset['y'], '[font=terrain] [/font]')

        # Legal moves for current actors
        for highlight in self.highlighted_cases:
            color = 'pink'
            if highlight['valid'] == 'enemy': 
                color = 'red'
            if highlight['valid'] == 'false':
                color = 'amber'
            blt.bkcolor(color)
            blt.puts(highlight['mov'][0] + offset['x'], highlight['mov'][1] + offset['y'], '[font=terrain] [/font]')

        # Coordinates
        blt.bkcolor('black')

        for y in range(10):
            blt.puts(0, y + offset['y'], f'{str(y)}')
            blt.puts(self.gamemap.size['y'] + 1, y + offset['y'], f'{str(y)}')
            blt.puts(y + 1, offset['y'] - 1, f'{chr(65 + y)}')
            blt.puts(y + 1, offset['y'] + self.gamemap.size['y'], f'{chr(65 + y)}')

        # actors
        blt.layer(1)

        for actor in self.actors:
            blt.color(actor.color)
            blt.puts(actor.x + offset['x'], actor.y + offset['y'], actor.charac)

        # Text
        blt.layer(2)
        off_x = self.gamemap.size['x'] + self.gamemap.display_offset['x']
        off_y = self.gamemap.size['y'] + self.gamemap.display_offset['y']
        blt.color('white')
        blt.bkcolor('black')
        blt.puts(off_x + 1, 1, f'[font=text]{self.unit_turn.perma_color} {self.unit_turn.name}[/font]')

        blt.puts(TERMINAL_SIZE_X - 8, TERMINAL_SIZE_Y - 6, 'End turn')

        if self.message_queue:
            # TODO: get total ength of 5 last messages
            # If > 5 lines, then take one less, etc.
            i = 5
            last_five_messages = self.message_queue[-5:]
            
            for mess in reversed(last_five_messages):
                
                mess_len = len(mess) / MESSAGE_PANEL_W
                if len(mess) > 1:
                    i -= ceil(mess_len - 1)

            messages_to_display = []
            while i > 0:
                messages_to_display.append(last_five_messages[i])
                i -= 1

            print(messages_to_display)


            # while i > 0:
            #     if i > len(self.message_queue):
            #         i = len(self.message_queue)

            #     i -= 1
            #     message = self.message_queue[:-i]
            #     mess_len = len(message) / MESSAGE_PANEL_W

            #     if mess_len > 1:
            #         i -= ceil(mess_len - 1)

            #     blt.puts(MESSAGE_PANEL_X, MESSAGE_PANEL_Y + 4 - i, 
            #              message, MESSAGE_PANEL_W, MESSAGE_PANEL_H, blt.TK_ALIGN_LEFT)

        self.re_render = False

    def update(self):

        # If everybody took its turn, then new turn: the list containing
        # actors and order is recomputed
        if not self.turn_to_take:
            self.turn_to_take = self.actors.copy()
            self.turn_to_take.sort(key=lambda x: x.stats['agility'], reverse=True) 

        # Non-blocking input
        while blt.has_input():   
            key = blt.read()

            if key == blt.TK_MOUSE_LEFT:
                self.event_queue.append(['mouse_left_click', (blt.state(blt.TK_MOUSE_X), blt.state(blt.TK_MOUSE_Y))])

            elif key in MOVEMENT_KEYS or key in QUIT_KEY:
                self.event_queue.append(['keypressed', key])

        # Event processing
        for event in self.event_queue:
            # Check the key pressed if it was a key press (duh)
            if event[0] == 'keypressed':
                self.key_check(event[1])
                self.re_render = True

            elif 'mouse' in event[0]:
                self.mouse_check(event[1])
                self.re_render = True

            # Once the event was processed, remove it so we don't process it twice
            self.event_queue.remove(event)

            # If the turn is over, switch to the next unit
            if self.game_state == 'end_turn':             
                self.unit_turn.end_turn()
                
                self.unit_turn = self.turn_to_take.pop(0)
                
                self.unit_turn.new_turn()
                self.highlighted_cases = self.get_possible_movement(self.unit_turn)
                self.game_state = 'new_turn'


if __name__ == '__main__':

    engine = Engine()
    engine.init_terminal()

    while engine.game_state is not 'exit':
        engine.update()
        engine.render()
        blt.refresh()

    blt.close()
    
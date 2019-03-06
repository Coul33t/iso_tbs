from math import ceil

TILE_SIZE_X = 32
TILE_SIZE_Y = 32

WINDOW_SIZE_X = 40
WINDOW_SIZE_Y = 20


MAP_PANEL_X = WINDOW_SIZE_X / 4
MAP_PANEL_Y = 0
MAP_PANEL_W = 20
MAP_PANEL_H = 20

MESSAGE_PANEL_X = MAP_PANEL_X
MESSAGE_PANEL_W = MAP_PANEL_W
MESSAGE_PANEL_H = 4
MESSAGE_PANEL_Y = MAP_PANEL_H - MESSAGE_PANEL_H

STATS_PANEL_X = 0
STATS_PANEL_Y = 0
STATS_PANEL_W = WINDOW_SIZE_X - MAP_PANEL_W - MAP_PANEL_X
STATS_PANEL_H = WINDOW_SIZE_Y

STATS_ENEMY_PANEL_X = MAP_PANEL_X + MAP_PANEL_W
STATS_ENEMY_PANEL_Y = 0
STATS_ENEMY_PANEL_W = STATS_PANEL_W
STATS_ENEMY_PANEL_H = WINDOW_SIZE_Y

BUTTONS_PANEL_H = 2
BUTTONS_PANEL_Y = WINDOW_SIZE_Y - BUTTONS_PANEL_H
BUTTONS_PANEL_X = STATS_ENEMY_PANEL_X
BUTTONS_PANEL_W = STATS_ENEMY_PANEL_W


SPRITES = {'grass': (0,0),
           'water': (0,1),
           'forest': (0,2),
           'king': (1,0),
           'leader': (1,1),
           'soldier': (1,2),
           'mercenary': (1,3),
           'xander': (1,4),
           'cursor':(2,0),
           'legal_move': (2,1),
           'attack_move': (2,2),
           'current_unit': (2,3)}


QUIT_KEY = (27, 224)
ACTION_KEY = (32,)
MOVEMENT_KEYS = {93: [0, 0], 90: [0, 1], 89: [-1, 1], 92: [-1, 0], 95: [-1, -1], 96: [0, -1], 97: [1, -1],
                 94: [1, 0], 91: [1, 1]}

TEAM_COLORS = ['blue', 'red', 'green', 'yellow']
ACTIVE_COLOR = 'green'

KEY = {'tab': 43}

ABBR = {'strength': 'str', 'agility': 'agi', 'intel': 'int', 'defence': 'def', 'hp': 'HP'}

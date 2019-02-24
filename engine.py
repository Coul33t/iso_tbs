from math import ceil, floor

from bearlibterminal import terminal as blt

from tools import dst_euc, dst_man, Point, point_in
from constants import *
from actor import Actor, Stats
from gamemap import GameMap

DEBUG = False

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

        self.under_mouse = None

        self.map_offset = Point(MAP_PANEL.x, MAP_PANEL.y)

        self.init_game()

        self.game_state = 'menu'
        self.game_state = 'playing'

    def init_terminal(self):
        blt.open()
        blt.set(f"""window.size={TERMINAL_SIZE_X}x{TERMINAL_SIZE_Y},
                    window.cellsize={TERMINAL_CELL_SIZE_X}x{TERMINAL_CELL_SIZE_Y},
                    resizeable=true, minimum-size={TERMINAL_SIZE_X}x{TERMINAL_SIZE_Y}""")
        blt.set("font: res/fonts/VeraMono.ttf, size=12x24, spacing=1x1")
        blt.set("terrain font: res/tilesets/Curses_square_24.png, size=24x24, codepage=437, spacing=2x1")
        blt.set("U+E100: res/tilesets/test_tiles.png, size=32x32")
        blt.set("window.title='SimplyRL'")
        blt.set("input.filter={keyboard, mouse+}")
        blt.composition(True)
        blt.refresh()

    def init_game(self):
        # self.gamemap.load_map_from_json('res/map/test_map.json')
        self.gamemap.create_default_terrain()

        for i in range(3, 6):
            self.actors.append(Actor('soldier', 's', 0, color=TEAM_COLORS[0], x=i, y=1, movement=1,
                                     stats=Stats(3,3,1)))
        for i in range(0, 10, 2):
            self.actors.append(Actor('barbarian', 'b', 1, color=TEAM_COLORS[1], x=i, y=8, movement=2,
                                     stats=Stats(3,2,0)))


        self.actors.append(Actor('king', 'K', 0, sprite=0xE100+10, color=TEAM_COLORS[0], x=4, y=0,
                                 movement=2, stats=Stats(5,3,4)))
        self.actors.append(Actor('leader', 'L', 1, color=TEAM_COLORS[1], x=4, y=9,
                                 movement=2, stats=Stats(7,4,2)))

        self.actors.append(Actor('Xander', 'S', 2, color=TEAM_COLORS[2], x=5, y=5,
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

    def render_frames(self):
        for x in range(1, TERMINAL_SIZE_X - 1):
            blt.put(x, 0, '═')
            blt.put(x, TERMINAL_SIZE_Y - 1, '═')
            blt.put(x, BUTTONS_PANEL.bottom, '═')

        for y in range(1, TERMINAL_SIZE_Y - 1):
            blt.put(0, y, '║')
            blt.put(TERMINAL_SIZE_X - 1, y, '║')

        for x in range(STATS_PANEL.left, STATS_PANEL.right + 1):
            blt.put(x, STATS_PANEL.bottom, '═')
            blt.put(x, STATS_ENEMY_PANEL.bottom, '═')

        for y in range(MAP_PANEL.top, MAP_PANEL.bottom):
            blt.put(STATS_PANEL.left - 1, y, '║')

        blt.put(STATS_PANEL.left - 1, STATS_PANEL.bottom, '╠')
        blt.put(STATS_PANEL.left - 1, STATS_ENEMY_PANEL.bottom, '╠')
        blt.put(0, MESSAGE_PANEL.top - 1, '╠')

        blt.put(STATS_PANEL.right + 1, STATS_PANEL.bottom , '╣')
        blt.put(STATS_ENEMY_PANEL.right + 1, STATS_ENEMY_PANEL.bottom, '╣')
        blt.put(MESSAGE_PANEL.right + 1, MESSAGE_PANEL.top - 1, '╣')

        blt.put(STATS_PANEL.left - 1, 0, '╦')
        blt.put(STATS_PANEL.left - 1, BUTTONS_PANEL.bottom, '╩')
        blt.put(0, 0, '╔')
        blt.put(TERMINAL_SIZE_X - 1, 0, '╗')
        blt.put(TERMINAL_SIZE_X - 1, TERMINAL_SIZE_Y - 1, '╝')
        blt.put(0, TERMINAL_SIZE_Y - 1, '╚')


    def render_stats(self, x_base, y_base, unit):
        blt.puts(x_base, y_base, f'[font=text]{unit.perma_color} {unit.name}[/font]')

        blt.puts(x_base, y_base + 2, f"[font=text]HP: {unit.stats.mod['hp']}/{unit.stats.base['max_hp']}[/font]")

        blt.puts(x_base, y_base + 4, f"[font=text]Str: {unit.stats.mod['strength']}[/font]")
        blt.puts(x_base, y_base + 5, f"[font=text]Agi: {unit.stats.mod['agility']}[/font]")
        blt.puts(x_base, y_base + 6, f"[font=text]Int: {unit.stats.mod['intel']}[/font]")
        blt.puts(x_base, y_base + 7, f"[font=text]Def: {unit.stats.mod['defence']}[/font]")

    def render(self):
        # No need to render endlessly
        # EDIT: Actually now I need it
        # if not self.re_render:
        #     return

        blt.clear()

        self.render_frames()
        # Gameboard related stuff
        blt.layer(0)

        # Coloring the different panels
        if DEBUG:
            for y in range(MESSAGE_PANEL.y, MESSAGE_PANEL.y + MESSAGE_PANEL.h):
                for x in range(MESSAGE_PANEL.x, MESSAGE_PANEL.x + MESSAGE_PANEL.w):
                    blt.bkcolor('green')
                    blt.put(x, y, ' ')

            for y in range(STATS_PANEL.y, STATS_PANEL.y + STATS_PANEL.h):
                for x in range(STATS_PANEL.x, STATS_PANEL.x + STATS_PANEL.w):
                    blt.bkcolor('blue')
                    blt.put(x, y, ' ')

            for y in range(STATS_ENEMY_PANEL.y, STATS_ENEMY_PANEL.y + STATS_ENEMY_PANEL.h):
                for x in range(STATS_ENEMY_PANEL.x, STATS_ENEMY_PANEL.x + STATS_ENEMY_PANEL.w):
                    blt.bkcolor('red')
                    blt.put(x, y, ' ')

            for y in range(BUTTONS_PANEL.y, BUTTONS_PANEL.y + BUTTONS_PANEL.h):
                for x in range(BUTTONS_PANEL.x, BUTTONS_PANEL.x + BUTTONS_PANEL.w):
                    blt.bkcolor('violet')
                    blt.put(x, y, ' ')


        # Board drawing
        for y, row in enumerate(self.gamemap.terrain):
            for x, tile in enumerate(row):
                blt.bkcolor(tile.color)
                blt.puts((x + self.map_offset.x) * TERRAIN_SCALE_X, (y + self.map_offset.y) * TERRAIN_SCALE_Y, '[font=terrain] [/font]')

        blt.layer(0)
        # Legal moves for current actors
        self.highlighted_cases = self.get_possible_movement(self.unit_turn)
        for highlight in self.highlighted_cases:
            color = 'turquoise'
            if highlight['valid'] == 'enemy':
                color = 'red'
            if highlight['valid'] == 'false':
                color = 'amber'
            blt.bkcolor(color)
            blt.puts((highlight['mov'].x + self.map_offset.x) * TERRAIN_SCALE_X,
                     (highlight['mov'].y + self.map_offset.y) * TERRAIN_SCALE_Y, '[font=terrain] [/font]')

        # Coordinates
        blt.bkcolor('black')

        # for y in range(10):
        #     blt.puts(0, (y + offset.y) * TERRAIN_SCALE_Y, f'[font=terrain]{str(y)}[/font]')
        #     blt.puts((self.gamemap.h + 1) * TERRAIN_SCALE_X, (y + offset.y) * TERRAIN_SCALE_Y, f'[font=terrain]{str(y)}[/font]')
        #     blt.puts((y + 1) * TERRAIN_SCALE_X, (offset.y - 1) * TERRAIN_SCALE_Y, f'[font=terrain]{chr(65 + y)}[/font]')
        #     blt.puts((y + 1) * TERRAIN_SCALE_X, (offset.y + self.gamemap.h) * TERRAIN_SCALE_Y, f'[font=terrain]{chr(65 + y)}[/font]')

        # actors
        blt.layer(2)
        # First, the daed actors, so that they are below the living ones
        for actor in [a for a in self.actors if a.dead]:
            blt.color(actor.color)
            blt.puts((actor.x + self.map_offset.x) * TERRAIN_SCALE_X,
                     (actor.y + self.map_offset.y) * TERRAIN_SCALE_Y, actor.charac)
        # Then the living ones
        for actor in [a for a in self.actors if not a.dead]:
            blt.color(actor.color)
            blt.puts(((actor.x + self.map_offset.x) * TERRAIN_SCALE_X),
                      (actor.y + self.map_offset.y) * TERRAIN_SCALE_Y, f'[offset={TERMINAL_CELL_SIZE_X/2},0]{actor.charac}[/offset]')

        # Text
        blt.layer(3)
        off_x = (self.gamemap.w + self.map_offset.x) * TERRAIN_SCALE_X
        off_y = (self.gamemap.h + self.map_offset.y) * TERRAIN_SCALE_Y
        blt.color('white')
        blt.bkcolor('black')
        self.render_stats(STATS_PANEL.x, STATS_PANEL.y, self.unit_turn)

        if self.under_mouse:
            self.render_stats(STATS_ENEMY_PANEL.x, STATS_ENEMY_PANEL.y, self.under_mouse)


        blt.puts(BUTTONS_PANEL.top_right.x - 8, BUTTONS_PANEL.top_right.y, 'End turn')

        if self.message_queue:
            blt.puts(MESSAGE_PANEL.x, MESSAGE_PANEL.y,
                     self.message_queue[-1], MESSAGE_PANEL.w, MESSAGE_PANEL.h, blt.TK_ALIGN_LEFT)

        self.re_render = False

    def update(self):
        self.check_under_mouse()
        # If everybody took its turn, then new turn: the list containing
        # actors and order is recomputed
        if not self.turn_to_take:
            self.turn_to_take = [a for a in self.actors if not a.dead]
            self.turn_to_take.sort(key=lambda x: x.stats.mod['agility'], reverse=True)

        # Non-blocking input
        while blt.has_input():
            key = blt.read()

            if key == blt.TK_MOUSE_LEFT:
                self.event_queue.append(['mouse_left_click', (blt.state(blt.TK_MOUSE_X), blt.state(blt.TK_MOUSE_Y))])

            elif key in ACTION_KEY or key in QUIT_KEY:
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

        self.unit_turn.check_end()

        # If the turn is over, switch to the next unit
        if self.unit_turn.has_played or self.game_state == 'end_turn':
            self.game_state = 'new_turn'
            self.unit_turn.end_turn()

            self.unit_turn = self.turn_to_take.pop(0)
            while self.unit_turn.dead:
                self.unit_turn = self.turn_to_take.pop(0)

            self.unit_turn.new_turn()

        blt.refresh()
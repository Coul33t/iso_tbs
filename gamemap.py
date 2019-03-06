import json

from tools import Point

# tmp
COLORS = {'~': 'blue', 'T': 'green', '.': 'yellow'}
class Tile:
    def __init__(self, color='pink', charac=' ', sprite=None, properties={}):
        self.color = color
        self.charac = charac
        self.sprite = sprite
        self.properties = properties

    def add_property(self, prop, val):
        self.properties[prop] = val


class GameMap:
    def __init__(self, terrain=[]):
        self.terrain = terrain
        self.w = 0
        self.h = 0

    def create_default_terrain(self):
        for y in range(20):
            new_row = []
            for x in range(20):
                sprite = 'grass'
                prop = {'walkable': True}

                if y == 0 or x == 0 or x == 19 or y == 19 or y == 5:
                    sprite = 'water'
                    prop = {'walkable': False}

                new_row.append(Tile(sprite=sprite, properties=prop))
            self.terrain.append(new_row)

        self.w = len(self.terrain[0])
        self.h = len(self.terrain)

    def load_map_from_json(self, path):
        with open(path, 'r') as jso:
            gmap = json.load(jso)[3]

            for row in gmap:
                new_row = []
                for x, char in enumerate(row):
                    new_row.append(Tile(COLORS[char]))
                self.terrain.append(new_row)

            self.w = len(self.terrain[0])
            self.h = len(self.terrain)

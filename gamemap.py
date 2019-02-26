import json

from tools import Point

# tmp
COLORS = {'~': 'blue', 'T': 'green', '.': 'yellow'}
class Tile:
    def __init__(self, color, charac=' ', properties=[]):
        self.color = color
        self.charac = charac
        self.properties = properties


class GameMap:
    def __init__(self, terrain=[]):
        self.terrain = terrain
        self.w = 0
        self.h = 0

    def create_default_terrain(self):
        for y in range(10):
            new_row = []
            for x in range(10):
                color = 'white'

                if (y%2 == 0 and x%2 == 1) or (y%2 == 1 and x%2 == 0):
                    color = 'grey'

                new_row.append(Tile(color))
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

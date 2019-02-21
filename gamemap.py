from tools import Point

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
        for y in range(20):
            new_row = []
            for x in range(20):
                color = 'white'

                if (y%2 == 0 and x%2 == 1) or (y%2 == 1 and x%2 == 0):
                    color = 'grey'

                new_row.append(Tile(color))
            self.terrain.append(new_row)

        self.w = len(self.terrain[0])
        self.h = len(self.terrain)
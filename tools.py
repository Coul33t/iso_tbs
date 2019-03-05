from math import sqrt
import pygame
from constants import *

# Do I really need to put some docstring for this?
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

# Do I really need to put some docstring for this?
class Rect:
    def __init__(self, x, y, w, h, size_x, size_y):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        # Because this will be easier to use
        self.top = y
        self.left = x
        self.bottom = y+h
        self.right = x+w

        self.top_left = Point(self.left, self.top)
        self.top_right = Point(self.right, self.top)
        self.bottom_right = Point(self.right, self.bottom)
        self.bottom_left = Point(self.left, self.bottom)



        # Pixels values (true value for the window)
        self.pv_x = x * size_x
        self.pv_y = y * size_y
        self.pv_w = w * size_x
        self.pv_h = h * size_y

        self.pv_top = self.pv_y
        self.pv_left = self.pv_x
        self.pv_bottom = self.pv_y + self.pv_h
        self.pv_right = self.pv_x + self.pv_w

        self.pv_top_left = Point(self.pv_left, self.pv_top)
        self.top_right = Point(self.pv_right, self.pv_top)
        self.bottom_right = Point(self.pv_right, self.pv_bottom)
        self.pv_top_left = Point(self.pv_left, self.pv_top)


    def inside(self, pt):
        return pt.x > self.x and pt.x < self.x + self.w and pt.y > self.y and pt.y < self.y + self.h


class Spritesheet():
    def __init__(self, path):
        self.sheet = None
        self.set_spritesheet(path)
        self.size = self.sheet.get_rect().size
        self.rows = int(self.size[1] / TILE_SIZE_X)
        self.cols = int(self.size[0] / TILE_SIZE_Y)
        self.sprites = []

    def set_spritesheet(self, path):
        try:
            self.sheet = pygame.image.load(path)
        except:
            print('ERROR: error while loading the spritesheet.')

    def load_sprite(self, row, col, sprite_size=(TILE_SIZE_X, TILE_SIZE_Y)):
        if row > self.rows:
            print('ERROR: row number is too high.')
            return

        if col > self.cols:
            print('ERROR: column number is to high.')
            return

        row = row * TILE_SIZE_Y
        col = col * TILE_SIZE_X

        sprite = pygame.Surface((sprite_size[0], sprite_size[1])).convert()
        sprite.blit(self.sheet, (row, col))
        return sprite

    def load_all_sprites(self):
        sprite_size=(TILE_SIZE_X, TILE_SIZE_Y)

        for i in range(self.rows):
            new_row = []
            for j in range(self.cols):
                sprite = self.load_sprite(i, j)
                new_row.append(sprite)
            self.sprites.append(new_row)

    def get_sprite(self, pos):

        if isinstance(pos, str):
            pos = SPRITES[pos]

        if pos[0] > self.rows - 1:
            print('ERROR: row number is too high.')
            return

        if pos[1] > self.cols - 1:
            print('ERROR: column number is to high.')
            return

        return self.sprites[pos[0]][pos[1]]


# Euclidean distance
def dst_euc(p1, p2=Point(0,0)):
    return sqrt(pow(p2.x - p1.x, 2) + pow(p2.y - p1.y, 2))

# Manhattan distance
def dst_man(p1, p2=Point(0,0)):
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)

def point_in(ptn, lst):
    for other_ptn in lst:
        if ptn.x == other_ptn.x and ptn.y == other_ptn.y:
            return True

    return False


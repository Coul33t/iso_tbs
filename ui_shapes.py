from constants import *
from tools import Rect


WINDOW_SIZE = Rect(0, 0, WINDOW_SIZE_X, WINDOW_SIZE_Y, TILE_SIZE_X, TILE_SIZE_Y)
MAP_PANEL = Rect(MAP_PANEL_X, MAP_PANEL_Y, MAP_PANEL_W, MAP_PANEL_H, TILE_SIZE_X, TILE_SIZE_Y)
MESSAGE_PANEL = Rect(MESSAGE_PANEL_X, MESSAGE_PANEL_Y, MESSAGE_PANEL_W, MESSAGE_PANEL_H, TILE_SIZE_X, TILE_SIZE_Y)
STATS_PANEL = Rect(STATS_PANEL_X, STATS_PANEL_Y, STATS_PANEL_W, STATS_PANEL_H, TILE_SIZE_X, TILE_SIZE_Y)
STATS_ENEMY_PANEL = Rect(STATS_ENEMY_PANEL_X, STATS_ENEMY_PANEL_Y, STATS_ENEMY_PANEL_W, STATS_ENEMY_PANEL_H, TILE_SIZE_X, TILE_SIZE_Y)
BUTTONS_PANEL = Rect(BUTTONS_PANEL_X, BUTTONS_PANEL_Y, BUTTONS_PANEL_W, BUTTONS_PANEL_H, TILE_SIZE_X, TILE_SIZE_Y)
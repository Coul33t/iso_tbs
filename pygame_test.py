import pygame
from pygame.locals import QUIT
from tools import Spritesheet

pygame.init()
window = pygame.display.set_mode((100, 100))

spritesheet = Spritesheet('res/spritesheet.png')
spritesheet.load_all_sprites()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

    for i, sprite in enumerate(spritesheet.sprites[0]):
        window.blit(sprite, (i*32, 0))
    pygame.display.update()
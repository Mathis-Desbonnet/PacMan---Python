import pygame
from pygame.sprite import AbstractGroup

class Life(pygame.sprite.Sprite):
    def __init__(self, *groups: AbstractGroup, x, y) -> None:
        super().__init__(*groups)
        
        self.imageLife = (pygame.image.load("./data/PacManSprites.png").convert_alpha().subsurface((19, 15, 16, 16)))
        self.rect = self.imageLife.get_rect()
        self.rect.x = x
        self.rect.y = y
import pygame
from pygame.sprite import AbstractGroup

class Gomme(pygame.sprite.Sprite):
    def __init__(self, *groups: AbstractGroup, x, y) -> None:
        super().__init__(*groups)
        self.image = pygame.image.load("./data/PacManSprites.png").subsurface((17, 240, 8, 8))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.score = 10

class GommePlus(pygame.sprite.Sprite):
    def __init__(self, *groups: AbstractGroup, x, y) -> None:
        super().__init__(*groups)
        self.image = pygame.image.load("./data/PacManSprites.png").subsurface((7, 240, 8, 8))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.score = 10
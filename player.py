import pygame
from pygame.sprite import AbstractGroup

class Pacman(pygame.sprite.Sprite):
    def __init__(self, *groups: AbstractGroup) -> None:
        super().__init__(*groups)
        self.image = pygame.image.load("./data/PacManSprites.png").convert_alpha().subsurface((18, 0, 16, 16))
        self.rect = self.image.get_rect()
        self.rect.x = 108
        self.rect.y = 132
    
    def getRect(self):
        return self.rect
    
    def setPos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def getPos(self):
        return (self.rect.x, self.rect.y)
    
    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y

    

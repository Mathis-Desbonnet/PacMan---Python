import pygame
from pygame.sprite import AbstractGroup

class Pinky(pygame.sprite.Sprite):
    def __init__(self, *groups: AbstractGroup, x, y) -> None:
        super().__init__(*groups)
        self.image = pygame.image.load("./data/PacManSprites.png").convert_alpha().subsurface((3, 80, 16, 16))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.collisionBox = pygame.Rect(self.rect.x, self.rect.y, 16, 16)
        self.allMovement = ["Right", "Down", "Left", "Up"]
        self.okMovement = ["Right", "Left", "Up"]

    def setPos(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.collisionBox.x = x
        self.collisionBox.y = y

    def getPos(self):
        return (self.rect.x, self.rect.y)
    
    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y
        self.collisionBox.x += x
        self.collisionBox.y += y

    def moveCollisionBox(self, x, y):
        self.collisionBox.x += x
        self.collisionBox.y += y
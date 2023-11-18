import pygame
from pygame.sprite import AbstractGroup


class Pacman(pygame.sprite.Sprite):
    def __init__(self, *groups: AbstractGroup) -> None:
        super().__init__(*groups)
        self.image = (
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((18, 0, 16, 16))
        )
        self.rect = self.image.get_rect()
        self.rect.x = 108
        self.rect.y = 132

        self.frameUp = [
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((2, 32, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((18, 32, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((34, 32, 16, 16)),
        ]

        self.frameLeft = [
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((2, 16, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((18, 16, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((34, 16, 16, 16)),
        ]

        self.frameDown = [
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((2, 48, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((18, 48, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((34, 48, 16, 16)),
        ]

        self.frameRight = [
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((2, 0, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((18, 0, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((34, 0, 16, 16)),
        ]

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

    def animation(self, way):
        if way == "Right":
            return self.frameRight
        elif way == "Left":
            return self.frameLeft
        elif way == "Up":
            return self.frameUp
        elif way == "Down":
            return self.frameDown

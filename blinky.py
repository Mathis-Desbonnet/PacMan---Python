import pygame
from pygame.sprite import AbstractGroup


class Blinky(pygame.sprite.Sprite):
    def __init__(self, *groups: AbstractGroup, x, y) -> None:
        super().__init__(*groups)
        self.image = (
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((3, 64, 16, 16))
        )
        self.imageBackup = self.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.basePoint = (224, 0)
        self.isScatter = True
        self.firstFright = True
        self.collisionBox = pygame.Rect(self.rect.x, self.rect.y, 16, 16)
        self.allMovement = ["Right", "Down", "Left", "Up"]
        self.okMovement = ["Right", "Left", "Up"]
        
        self.bug = False
        self.bugCounter = 0
        
        self.frameRight = [pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((3, 64, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((19, 64, 16, 16))]
        
        self.frameLeft = [pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((35, 64, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((51, 64, 16, 16))]
        
        self.frameUp = [pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((67, 64, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((83, 64, 16, 16))]
        
        self.frameDown = [pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((99, 64, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((115, 64, 16, 16))]
        
        self.frameFright = [pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((131, 64, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((147, 64, 16, 16))]
        
        self.frameFrightBug = [pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((163, 64, 16, 16)),
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((179, 64, 16, 16))]

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
        
    def animationNotFright(self, way):
        if way=="Up":
            return self.frameUp
        elif way=="Down":
            return self.frameDown
        elif way=="Left":
            return self.frameLeft
        elif way=="Right":
            return self.frameRight

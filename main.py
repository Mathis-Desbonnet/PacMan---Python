from math import sqrt, cos, sin, radians
from time import sleep
import pygame
import pytmx
import pyscroll
from player import Pacman
from item import Gomme
from blinky import Blinky
from pinky import Pinky
from inky import Inky
from clyde import Clyde

pygame.init()


class Debug:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((224, 248))
        self.clock = pygame.time.Clock()

        self.map = pytmx.load_pygame("./data/Map.tmx")
        self.tmx_data = pytmx.util_pygame.load_pygame("./data/Map.tmx")
        self.background = self.map.layers[0]

        self.pacman = Pacman()
        self.pacmanLife = 0
        self.pacmanWay = "Right"
        self.pinkyDirectionAddition = (32, 0)
        self.inkyDirectionAddition = (16, 0)

        self.blinky = Blinky(x=108, y=108)
        self.blinkyLife = 0
        self.blinkyPossibleDirection = "Up"

        self.pinky = Pinky(x=92, y=108)
        self.pinkyLife = 0
        self.pinkyPossibleDirection = "Up"

        self.inky = Inky(x=108, y=84)
        self.inkyLife = 0
        self.inkyPossibleDirection = "Right"

        self.clyde = Clyde(x=92, y=84)
        self.clydeLife = 0
        self.clydePossibleDirection = "Right"

        self.CollisionBox = pygame.Rect(self.pacman.rect.x, self.pacman.rect.y, 16, 16)
        self.scoreBox = pygame.Rect(
            self.pacman.rect.x + 4, self.pacman.rect.y + 4, 8, 8
        )
        self.running = True
        self.score = 0

        self.collisions = []
        self.collisionHub = None
        self.collisionTp = []
        self.gommeSpawn = []
        self.ghostCollisionRight = None
        self.ghostCollisionLeft = None

        for obj in self.tmx_data.objects:
            if obj.type == "collision":
                self.collisions.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "collisionHub":
                self.collisionHub = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            elif obj.type == "collisionTPRight":
                self.collisionTp.append(
                    pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                )
            elif obj.type == "collisionTPLeft":
                self.collisionTp.append(
                    pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                )
            elif obj.type == "gomme":
                self.gommeSpawn.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "collisionGhostRight":
                self.ghostCollisionRight = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            elif obj.type == "collisionGhostLeft":
                self.ghostCollisionLeft = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

        self.gommes = []

        for gomme in self.gommeSpawn:
            self.gommes.append(Gomme(x=gomme.x, y=gomme.y))

    def checkCollision(self):
        ifCollision = False
        for collision in self.collisions:
            if self.CollisionBox.colliderect(
                collision
            ) or self.CollisionBox.colliderect(self.collisionHub):
                ifCollision = True

        return ifCollision

    def checkTp(self, x, y, xCollision):
        for collision in self.collisionTp:
            if self.CollisionBox.colliderect(collision):
                self.pacman.setPos(x, y)
                self.CollisionBox.x = xCollision
                self.CollisionBox.y = y
                self.scoreBox.x = x + 4
                self.scoreBox.y = y + 4

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_z]:
            self.CollisionBox.y -= 8
            self.pacmanWay = "Up"
            self.pinkyDirectionAddition = (-32, -32)
            self.inkyDirectionAddition = (-16, -16)
            if not self.checkCollision():
                self.pacman.move(0, -8)
                self.scoreBox.y -= 8
            else:
                self.CollisionBox.y += 8

        if keys[pygame.K_q]:
            self.CollisionBox.x -= 8
            self.pacmanWay = "Left"
            self.pinkyDirectionAddition = (-32, 0)
            self.inkyDirectionAddition = (-16, 0)
            self.checkTp(228, 108, 220)
            if not self.checkCollision():
                self.pacman.move(-8, 0)
                self.scoreBox.x -= 8
            else:
                self.CollisionBox.x += 8

        if keys[pygame.K_s]:
            self.CollisionBox.y += 8
            self.pacmanWay = "Down"
            self.pinkyDirectionAddition = (0, 32)
            self.inkyDirectionAddition = (0, 16)
            if not self.checkCollision():
                self.pacman.move(0, 8)
                self.scoreBox.y += 8
            else:
                self.CollisionBox.y -= 8

        if keys[pygame.K_d]:
            self.CollisionBox.x += 8
            self.pacmanWay = "Right"
            self.pinkyDirectionAddition = (32, 0)
            self.inkyDirectionAddition = (16, 0)
            self.checkTp(-20, 108, -12)
            if not self.checkCollision():
                self.pacman.move(8, 0)
                self.scoreBox.x += 8
            else:
                self.CollisionBox.x -= 8

    def addScore(self):
        for gomme in self.gommeSpawn:
            if self.scoreBox.colliderect(gomme):
                for gommeOnScreen in self.gommes:
                    if (
                        gommeOnScreen.rect.x == gomme.x
                        and gommeOnScreen.rect.y == gomme.y
                    ):
                        self.gommes.remove(gommeOnScreen)
                        self.score += gommeOnScreen.score

    def blinkyMovement(self):
        if self.blinkyLife <= 2:
            self.blinky.move(0, -8)
        else:
            min = 1000000000000000000000
            for i in self.blinky.okMovement:
                plusPetit = True
                if i == "Right":
                    self.blinky.moveCollisionBox(8, 0)
                    self.blinkyDistance = sqrt(
                        (self.blinky.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.blinky.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.blinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.blinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.blinkyDistance <= min and plusPetit:
                        min = self.blinkyDistance
                        self.blinkyPossibleDirection = "Right"
                    self.blinky.moveCollisionBox(-8, 0)
                elif i == "Down":
                    self.blinky.moveCollisionBox(0, 8)
                    self.blinkyDistance = sqrt(
                        (self.blinky.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.blinky.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.blinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.blinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.blinkyDistance <= min and plusPetit:
                        min = self.blinkyDistance
                        self.blinkyPossibleDirection = "Down"
                    self.blinky.moveCollisionBox(0, -8)
                elif i == "Left":
                    self.blinky.moveCollisionBox(-8, 0)
                    self.blinkyDistance = sqrt(
                        (self.blinky.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.blinky.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.blinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.blinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.blinkyDistance <= min and plusPetit:
                        min = self.blinkyDistance
                        self.blinkyPossibleDirection = "Left"
                    self.blinky.moveCollisionBox(8, 0)
                elif i == "Up":
                    self.blinky.moveCollisionBox(0, -8)
                    self.blinkyDistance = sqrt(
                        (self.blinky.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.blinky.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.blinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.blinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.blinkyDistance <= min and plusPetit:
                        min = self.blinkyDistance
                        self.blinkyPossibleDirection = "Up"
                    self.blinky.moveCollisionBox(0, 8)

            if self.blinkyLife <= 7:
                if self.blinkyPossibleDirection == "Right":
                    if self.blinky.collisionBox.colliderect(self.ghostCollisionRight):
                        self.blinky.setPos(-20, 108)
                    self.blinky.move(8, 0)
                    self.blinky.okMovement = (
                        self.blinky.allMovement.copy()[0:2]
                        + self.blinky.allMovement.copy()[3:4]
                    )
                elif self.blinkyPossibleDirection == "Down":
                    self.blinky.move(0, 8)
                    self.blinky.okMovement = self.blinky.allMovement.copy()[:3]
                elif self.blinkyPossibleDirection == "Left":
                    if self.blinky.collisionBox.colliderect(self.ghostCollisionLeft):
                        self.blinky.setPos(228, 108)
                    self.blinky.move(-8, 0)
                    self.blinky.okMovement = self.blinky.allMovement.copy()[1:]
                elif self.blinkyPossibleDirection == "Up":
                    self.blinky.move(0, -8)
                    self.blinky.okMovement = (
                        self.blinky.allMovement.copy()[0:1]
                        + self.blinky.allMovement.copy()[2:4]
                    )
            else:
                self.blinkyLife = 3

    def pinkyMovement(self):
        if self.pinkyLife == 0:
            self.pinky.move(8, 0)
        elif self.pinkyLife <= 3:
            self.pinky.move(0, -8)
        else:
            min = 1000000000000000000000
            for i in self.pinky.okMovement:
                plusPetit = True
                if i == "Right":
                    self.pinky.moveCollisionBox(8, 0)
                    self.pinkyDistance = sqrt(
                        (self.pinky.collisionBox.x - (self.pacman.rect.x+self.pinkyDirectionAddition[0])) ** 2
                        + (self.pinky.collisionBox.y - (self.pacman.rect.y+self.pinkyDirectionAddition[1])) ** 2
                    )
                    pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.pinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.pinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.pinkyDistance <= min and plusPetit:
                        min = self.pinkyDistance
                        self.pinkyPossibleDirection = "Right"
                    self.pinky.moveCollisionBox(-8, 0)
                elif i == "Down":
                    self.pinky.moveCollisionBox(0, 8)
                    self.pinkyDistance = sqrt(
                        (self.pinky.collisionBox.x - (self.pacman.rect.x+self.pinkyDirectionAddition[0])) ** 2
                        + (self.pinky.collisionBox.y - (self.pacman.rect.y+self.pinkyDirectionAddition[1])) ** 2
                    )
                    pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.pinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.pinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.pinkyDistance <= min and plusPetit:
                        min = self.pinkyDistance
                        self.pinkyPossibleDirection = "Down"
                    self.pinky.moveCollisionBox(0, -8)
                elif i == "Left":
                    self.pinky.moveCollisionBox(-8, 0)
                    self.pinkyDistance = sqrt(
                        (self.pinky.collisionBox.x - (self.pacman.rect.x+self.pinkyDirectionAddition[0])) ** 2
                        + (self.pinky.collisionBox.y - (self.pacman.rect.y+self.pinkyDirectionAddition[1])) ** 2
                    )
                    pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.pinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.pinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.pinkyDistance <= min and plusPetit:
                        min = self.pinkyDistance
                        self.pinkyPossibleDirection = "Left"
                    self.pinky.moveCollisionBox(8, 0)
                elif i == "Up":
                    self.pinky.moveCollisionBox(0, -8)
                    self.pinkyDistance = sqrt(
                        (self.pinky.collisionBox.x - (self.pacman.rect.x+self.pinkyDirectionAddition[0])) ** 2
                        + (self.pinky.collisionBox.y - (self.pacman.rect.y+self.pinkyDirectionAddition[1])) ** 2
                    )
                    pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.pinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.pinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.pinkyDistance <= min and plusPetit:
                        min = self.pinkyDistance
                        self.pinkyPossibleDirection = "Up"
                    self.pinky.moveCollisionBox(0, 8)

            if self.pinkyLife <= 8:
                if self.pinkyPossibleDirection == "Right":
                    if self.pinky.collisionBox.colliderect(self.ghostCollisionRight):
                        self.pinky.setPos(-20, 108)
                    self.pinky.move(8, 0)
                    self.pinky.okMovement = (
                        self.pinky.allMovement.copy()[0:2]
                        + self.pinky.allMovement.copy()[3:4]
                    )
                elif self.pinkyPossibleDirection == "Down":
                    self.pinky.move(0, 8)
                    self.pinky.okMovement = self.pinky.allMovement.copy()[:3]
                elif self.pinkyPossibleDirection == "Left":
                    if self.pinky.collisionBox.colliderect(self.ghostCollisionLeft):
                        self.pinky.setPos(228, 108)
                    self.pinky.move(-8, 0)
                    self.pinky.okMovement = self.pinky.allMovement.copy()[1:]
                elif self.pinkyPossibleDirection == "Up":
                    self.pinky.move(0, -8)
                    self.pinky.okMovement = (
                        self.pinky.allMovement.copy()[0:1]
                        + self.pinky.allMovement.copy()[2:4]
                    )
            else:
                self.pinkyLife = 4

    def inkyMovement(self):
        if self.inkyLife >= 0:
            min = 1000000000000000000000
            xDistance = self.blinky.getPos()[0] - (self.pacman.rect.x+self.inkyDirectionAddition[0])
            yDistance = self.blinky.getPos()[1] - (self.pacman.rect.y+self.inkyDirectionAddition[1])
            xInkyGraph = self.pacman.rect.x+self.inkyDirectionAddition[0] - xDistance
            yInkyGraph = self.pacman.rect.y+self.inkyDirectionAddition[1] - yDistance
            for i in self.inky.okMovement:
                plusPetit = True
                if i == "Right":
                    self.inky.moveCollisionBox(8, 0)
                    self.inkyDistance = sqrt(
                        (self.inky.collisionBox.x - xInkyGraph) ** 2
                        + (self.inky.collisionBox.y - yInkyGraph) ** 2
                    )
                    pygame.draw.rect(self.screen, (0, 255, 255), self.inky.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.inky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.inky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.inkyDistance <= min and plusPetit:
                        min = self.inkyDistance
                        self.inkyPossibleDirection = "Right"
                    self.inky.moveCollisionBox(-8, 0)
                elif i == "Down":
                    self.inky.moveCollisionBox(0, 8)
                    pygame.draw.rect(self.screen, (0, 255, 255), self.inky.collisionBox, 1)
                    pygame.display.flip()
                    self.inkyDistance = sqrt(
                        (self.inky.collisionBox.x - xInkyGraph) ** 2
                        + (self.inky.collisionBox.y - yInkyGraph) ** 2
                    )
                    for collision in self.collisions:
                        if self.inky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.inky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.inkyDistance <= min and plusPetit:
                        min = self.inkyDistance
                        self.inkyPossibleDirection = "Down"
                    self.inky.moveCollisionBox(0, -8)
                elif i == "Left":
                    self.inky.moveCollisionBox(-8, 0)
                    pygame.draw.rect(self.screen, (0, 255, 255), self.inky.collisionBox, 1)
                    pygame.display.flip()
                    self.inkyDistance = sqrt(
                        (self.inky.collisionBox.x - xInkyGraph) ** 2
                        + (self.inky.collisionBox.y - yInkyGraph) ** 2
                    )
                    for collision in self.collisions:
                        if self.inky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.inky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.inkyDistance <= min and plusPetit:
                        min = self.inkyDistance
                        self.inkyPossibleDirection = "Left"
                    self.inky.moveCollisionBox(8, 0)
                elif i == "Up":
                    self.inky.moveCollisionBox(0, -8)
                    pygame.draw.rect(self.screen, (0, 255, 255), self.inky.collisionBox, 1)
                    pygame.display.flip()
                    self.inkyDistance = sqrt(
                        (self.inky.collisionBox.x - xInkyGraph) ** 2
                        + (self.inky.collisionBox.y - yInkyGraph) ** 2
                    )
                    for collision in self.collisions:
                        if self.inky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.inky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.inkyDistance <= min and plusPetit:
                        min = self.inkyDistance
                        self.inkyPossibleDirection = "Up"
                    self.inky.moveCollisionBox(0, 8)
                # print(self.inky.okMovement)
                # print(min)
                # print(self.inkyDistance)
                # print(self.inkyPossibleDirection)
                # print()

            if self.inkyLife <= 4:
                if self.inkyPossibleDirection == "Right":
                    if self.inky.collisionBox.colliderect(self.ghostCollisionRight):
                        self.inky.setPos(-20, 108)
                    self.inky.move(8, 0)
                    self.inky.okMovement = (
                        self.inky.allMovement.copy()[0:2]
                        + self.inky.allMovement.copy()[3:4]
                    )
                elif self.inkyPossibleDirection == "Down":
                    self.inky.move(0, 8)
                    self.inky.okMovement = self.inky.allMovement.copy()[:3]
                elif self.inkyPossibleDirection == "Left":
                    if self.inky.collisionBox.colliderect(self.ghostCollisionLeft):
                        self.inky.setPos(228, 108)
                    self.inky.move(-8, 0)
                    self.inky.okMovement = self.inky.allMovement.copy()[1:]
                elif self.inkyPossibleDirection == "Up":
                    self.inky.move(0, -8)
                    self.inky.okMovement = (
                        self.inky.allMovement.copy()[0:1]
                        + self.inky.allMovement.copy()[2:4]
                    )
            else:
                self.inkyLife = 0

    def clydeMovement(self):
        if self.clydeLife >= 0:
            min = 1000000000000000000000
            for i in self.clyde.okMovement:
                plusPetit = True
                if i == "Right":
                    self.clyde.moveCollisionBox(8, 0)
                    self.clydeDistance = sqrt(
                        (self.clyde.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.clyde.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    pygame.draw.rect(self.screen, (255, 0, 0), self.clyde.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.clyde.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.clyde.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.clydeDistance > 64:
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Right"
                    else:
                        self.clydeDistance = sqrt(
                            (self.clyde.collisionBox.x - self.clyde.basePoint[0]) ** 2
                            + (self.clyde.collisionBox.y - self.clyde.basePoint[1]) ** 2
                        )
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Right"
                    self.clyde.moveCollisionBox(-8, 0)
                elif i == "Down":
                    self.clyde.moveCollisionBox(0, 8)
                    self.clydeDistance = sqrt(
                        (self.clyde.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.clyde.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    pygame.draw.rect(self.screen, (255, 0, 0), self.clyde.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.clyde.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.clyde.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.clydeDistance > 64:
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Down"
                    else:
                        self.clydeDistance = sqrt(
                            (self.clyde.collisionBox.x - self.clyde.basePoint[0]) ** 2
                            + (self.clyde.collisionBox.y - self.clyde.basePoint[1]) ** 2
                        )
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Down"
                    self.clyde.moveCollisionBox(0, -8)
                elif i == "Left":
                    self.clyde.moveCollisionBox(-8, 0)
                    self.clydeDistance = sqrt(
                        (self.clyde.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.clyde.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    pygame.draw.rect(self.screen, (255, 0, 0), self.clyde.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.clyde.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.clyde.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.clydeDistance > 64:
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Left"
                    else:
                        self.clydeDistance = sqrt(
                            (self.clyde.collisionBox.x - self.clyde.basePoint[0]) ** 2
                            + (self.clyde.collisionBox.y - self.clyde.basePoint[1]) ** 2
                        )
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Left"
                    self.clyde.moveCollisionBox(8, 0)
                elif i == "Up":
                    self.clyde.moveCollisionBox(0, -8)
                    self.clydeDistance = sqrt(
                        (self.clyde.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.clyde.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    pygame.draw.rect(self.screen, (255, 0, 0), self.clyde.collisionBox, 1)
                    pygame.display.flip()
                    for collision in self.collisions:
                        if self.clyde.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.clyde.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.clydeDistance > 64:
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Up"
                    else:
                        self.clydeDistance = sqrt(
                            (self.clyde.collisionBox.x - self.clyde.basePoint[0]) ** 2
                            + (self.clyde.collisionBox.y - self.clyde.basePoint[1]) ** 2
                        )
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Up"
                    # print(self.clyde.okMovement)
                    # print(min)
                    # print(self.clydeDistance)
                    # print(self.clydePossibleDirection)
                    # print()
                    self.clyde.moveCollisionBox(0, 8)

            if self.clydeLife <= 4:
                if self.clydePossibleDirection == "Right":
                    if self.clyde.collisionBox.colliderect(self.ghostCollisionRight):
                        self.clyde.setPos(-20, 108)
                    self.clyde.move(8, 0)
                    self.clyde.okMovement = (
                        self.clyde.allMovement.copy()[0:2]
                        + self.clyde.allMovement.copy()[3:4]
                    )
                elif self.clydePossibleDirection == "Down":
                    self.clyde.move(0, 8)
                    self.clyde.okMovement = self.clyde.allMovement.copy()[:3]
                elif self.clydePossibleDirection == "Left":
                    if self.clyde.collisionBox.colliderect(self.ghostCollisionLeft):
                        self.clyde.setPos(228, 108)
                    self.clyde.move(-8, 0)
                    self.clyde.okMovement = self.clyde.allMovement.copy()[1:]
                elif self.clydePossibleDirection == "Up":
                    self.clyde.move(0, -8)
                    self.clyde.okMovement = (
                        self.clyde.allMovement.copy()[0:1]
                        + self.clyde.allMovement.copy()[2:4]
                    )
            else:
                self.clydeLife = 0

    def updateScreen(self):
        for layer in self.map.visible_layers:
            if layer.name == "Background":
                for x, y, gid in layer:
                    tile = self.map.get_tile_image_by_gid(gid)
                    self.screen.blit(
                        tile, (x * self.map.tilewidth, y * self.map.tileheight)
                    )

        # pygame.draw.rect(self.screen, (255, 0, 0), self.CollisionBox, 1)
        self.screen.blit(self.pacman.animation(self.pacmanWay)[self.pacmanLife % 3], self.pacman.getPos())

        pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.rect, 1)
        self.screen.blit(self.blinky.image, self.blinky.getPos())

        pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.rect, 1)
        self.screen.blit(self.pinky.image, self.pinky.getPos())

        pygame.draw.rect(self.screen, (0, 255, 255), self.inky.rect, 1)
        self.screen.blit(self.inky.image, self.inky.getPos())

        pygame.draw.rect(self.screen, (255, 200, 255), self.clyde.rect, 1)
        self.screen.blit(self.clyde.image, self.clyde.getPos())


        pygame.draw.rect(self.screen, (255, 0, 0), self.pacman.getRect(), 1)
        pygame.draw.rect(self.screen, (188, 0, 255), pygame.Rect(self.pacman.rect.x+self.pinkyDirectionAddition[0], self.pacman.rect.y+self.pinkyDirectionAddition[1], 16, 16), 1)
        pygame.draw.rect(self.screen, (0, 255, 255), pygame.Rect(self.pacman.rect.x+self.inkyDirectionAddition[0], self.pacman.rect.y+self.inkyDirectionAddition[1], 16, 16), 1)

        xDistance = self.blinky.getPos()[0] - (self.pacman.rect.x+self.inkyDirectionAddition[0])
        yDistance = self.blinky.getPos()[1] - (self.pacman.rect.y+self.inkyDirectionAddition[1])
        xInkyGraph = self.pacman.rect.x+self.inkyDirectionAddition[0] - xDistance
        yInkyGraph = self.pacman.rect.y+self.inkyDirectionAddition[1] - yDistance
        pygame.draw.line(self.screen, (255, 0, 0), (self.pacman.rect.x+self.inkyDirectionAddition[0], self.pacman.rect.y+self.inkyDirectionAddition[1]), (self.blinky.getPos()))
        pygame.draw.line(self.screen, (0, 255, 255), (self.pacman.rect.x+self.inkyDirectionAddition[0], self.pacman.rect.y+self.inkyDirectionAddition[1]), (xInkyGraph, yInkyGraph))

        pygame.draw.circle(self.screen, (255, 200, 0), self.pacman.rect.center, 64, 1)

        for gomme in self.gommes:
            self.screen.blit(gomme.image, (gomme.rect.x, gomme.rect.y))

        pygame.display.update()

    def run(self, running) -> None:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.input()
            self.addScore()
            self.updateScreen()

            self.blinkyMovement()
            self.pinkyMovement()
            self.inkyMovement()
            self.clydeMovement()

            self.pacmanLife += 1
            self.blinkyLife += 1
            self.pinkyLife += 1
            self.inkyLife += 1
            self.clydeLife += 1

            self.clock.tick(10)


class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((448, 496))
        self.clock = pygame.time.Clock()

        self.map = pytmx.load_pygame("./data/Map.tmx")
        test = pyscroll.data.TiledMapData(self.map)
        layer = pyscroll.orthographic.BufferedRenderer(test, self.screen.get_size())
        layer.zoom = 2
        self.tmx_data = pytmx.util_pygame.load_pygame("./data/Map.tmx")
        self.background = self.map.layers[0]

        self.group = pyscroll.PyscrollGroup(map_layer=layer)

        self.pacman = Pacman()
        self.pacmanLife = 0
        self.pacmanWay = "Right"
        self.pinkyDirectionAddition = (32, 0)
        self.inkyDirectionAddition = (16, 0)

        self.blinky = Blinky(x=108, y=108)
        self.blinkyLife = 0
        self.blinkyPossibleDirection = "Up"

        self.pinky = Pinky(x=92, y=108)
        self.pinkyLife = 0
        self.pinkyPossibleDirection = "Up"

        self.inky = Inky(x=108, y=84)
        self.inkyLife = 0
        self.inkyPossibleDirection = "Right"

        self.clyde = Clyde(x=92, y=84)
        self.clydeLife = 0
        self.clydePossibleDirection = "Right"

        self.group.add(self.blinky)
        self.group.add(self.pinky)
        self.group.add(self.inky)
        self.group.add(self.clyde)
        self.group.add(self.pacman)

        self.CollisionBox = pygame.Rect(self.pacman.rect.x, self.pacman.rect.y, 16, 16)
        self.scoreBox = pygame.Rect(
            self.pacman.rect.x + 4, self.pacman.rect.y + 4, 8, 8
        )
        self.running = True
        self.score = 0

        self.collisions = []
        self.collisionHub = None
        self.collisionTp = []
        self.gommeSpawn = []
        self.ghostCollisionRight = None
        self.ghostCollisionLeft = None

        for obj in self.tmx_data.objects:
            if obj.type == "collision":
                self.collisions.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "collisionHub":
                self.collisionHub = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            elif obj.type == "collisionTPRight":
                self.collisionTp.append(
                    pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                )
            elif obj.type == "collisionTPLeft":
                self.collisionTp.append(
                    pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                )
            elif obj.type == "gomme":
                self.gommeSpawn.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "collisionGhostRight":
                self.ghostCollisionRight = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            elif obj.type == "collisionGhostLeft":
                self.ghostCollisionLeft = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

        self.gommes = []

        for gomme in self.gommeSpawn:
            self.gommes.append(Gomme(x=gomme.x, y=gomme.y))
            self.group.add(Gomme(x=gomme.x, y=gomme.y))


    def checkCollision(self):
        ifCollision = False
        for collision in self.collisions:
            if self.CollisionBox.colliderect(
                collision
            ) or self.CollisionBox.colliderect(self.collisionHub):
                ifCollision = True

        return ifCollision

    def checkTp(self, x, y, xCollision):
        for collision in self.collisionTp:
            if self.CollisionBox.colliderect(collision):
                self.pacman.setPos(x, y)
                self.CollisionBox.x = xCollision
                self.CollisionBox.y = y
                self.scoreBox.x = x + 4
                self.scoreBox.y = y + 4

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_z]:
            self.CollisionBox.y -= 8
            self.pacmanWay = "Up"
            self.pinkyDirectionAddition = (-32, -32)
            self.inkyDirectionAddition = (-16, -16)
            if not self.checkCollision():
                self.pacman.move(0, -8)
                self.scoreBox.y -= 8
            else:
                self.CollisionBox.y += 8

        if keys[pygame.K_q]:
            self.CollisionBox.x -= 8
            self.pacmanWay = "Left"
            self.pinkyDirectionAddition = (-32, 0)
            self.inkyDirectionAddition = (-16, 0)
            self.checkTp(228, 108, 220)
            if not self.checkCollision():
                self.pacman.move(-8, 0)
                self.scoreBox.x -= 8
            else:
                self.CollisionBox.x += 8

        if keys[pygame.K_s]:
            self.CollisionBox.y += 8
            self.pacmanWay = "Down"
            self.pinkyDirectionAddition = (0, 32)
            self.inkyDirectionAddition = (0, 16)
            if not self.checkCollision():
                self.pacman.move(0, 8)
                self.scoreBox.y += 8
            else:
                self.CollisionBox.y -= 8

        if keys[pygame.K_d]:
            self.CollisionBox.x += 8
            self.pacmanWay = "Right"
            self.pinkyDirectionAddition = (32, 0)
            self.inkyDirectionAddition = (16, 0)
            self.checkTp(-20, 108, -12)
            if not self.checkCollision():
                self.pacman.move(8, 0)
                self.scoreBox.x += 8
            else:
                self.CollisionBox.x -= 8

    def addScore(self):
        for gomme in self.gommeSpawn:
            if self.scoreBox.colliderect(gomme):
                for gommeOnScreen in self.group.sprites():
                    if (
                        gommeOnScreen.rect.x == gomme.x
                        and gommeOnScreen.rect.y == gomme.y
                    ):
                        self.group.remove(gommeOnScreen)
                        self.group.update()
                        self.score += gommeOnScreen.score
        self.group.update()
        self.group.draw(self.screen)

    def blinkyMovement(self):
        if self.blinkyLife <= 2:
            self.blinky.move(0, -8)
        else:
            min = 1000000000000000000000
            for i in self.blinky.okMovement:
                plusPetit = True
                if i == "Right":
                    self.blinky.moveCollisionBox(8, 0)
                    self.blinkyDistance = sqrt(
                        (self.blinky.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.blinky.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    # pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.blinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.blinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.blinkyDistance <= min and plusPetit:
                        min = self.blinkyDistance
                        self.blinkyPossibleDirection = "Right"
                    self.blinky.moveCollisionBox(-8, 0)
                elif i == "Down":
                    self.blinky.moveCollisionBox(0, 8)
                    self.blinkyDistance = sqrt(
                        (self.blinky.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.blinky.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    # pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.blinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.blinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.blinkyDistance <= min and plusPetit:
                        min = self.blinkyDistance
                        self.blinkyPossibleDirection = "Down"
                    self.blinky.moveCollisionBox(0, -8)
                elif i == "Left":
                    self.blinky.moveCollisionBox(-8, 0)
                    self.blinkyDistance = sqrt(
                        (self.blinky.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.blinky.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    # pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.blinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.blinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.blinkyDistance <= min and plusPetit:
                        min = self.blinkyDistance
                        self.blinkyPossibleDirection = "Left"
                    self.blinky.moveCollisionBox(8, 0)
                elif i == "Up":
                    self.blinky.moveCollisionBox(0, -8)
                    self.blinkyDistance = sqrt(
                        (self.blinky.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.blinky.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    # pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.blinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.blinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.blinkyDistance <= min and plusPetit:
                        min = self.blinkyDistance
                        self.blinkyPossibleDirection = "Up"
                    self.blinky.moveCollisionBox(0, 8)

            if self.blinkyLife <= 7:
                if self.blinkyPossibleDirection == "Right":
                    if self.blinky.collisionBox.colliderect(self.ghostCollisionRight):
                        self.blinky.setPos(-20, 108)
                    self.blinky.move(8, 0)
                    self.blinky.okMovement = (
                        self.blinky.allMovement.copy()[0:2]
                        + self.blinky.allMovement.copy()[3:4]
                    )
                elif self.blinkyPossibleDirection == "Down":
                    self.blinky.move(0, 8)
                    self.blinky.okMovement = self.blinky.allMovement.copy()[:3]
                elif self.blinkyPossibleDirection == "Left":
                    if self.blinky.collisionBox.colliderect(self.ghostCollisionLeft):
                        self.blinky.setPos(228, 108)
                    self.blinky.move(-8, 0)
                    self.blinky.okMovement = self.blinky.allMovement.copy()[1:]
                elif self.blinkyPossibleDirection == "Up":
                    self.blinky.move(0, -8)
                    self.blinky.okMovement = (
                        self.blinky.allMovement.copy()[0:1]
                        + self.blinky.allMovement.copy()[2:4]
                    )
            else:
                self.blinkyLife = 3

    def pinkyMovement(self):
        if self.pinkyLife == 0:
            self.pinky.move(8, 0)
        elif self.pinkyLife <= 3:
            self.pinky.move(0, -8)
        else:
            min = 1000000000000000000000
            for i in self.pinky.okMovement:
                plusPetit = True
                if i == "Right":
                    self.pinky.moveCollisionBox(8, 0)
                    self.pinkyDistance = sqrt(
                        (self.pinky.collisionBox.x - (self.pacman.rect.x+self.pinkyDirectionAddition[0])) ** 2
                        + (self.pinky.collisionBox.y - (self.pacman.rect.y+self.pinkyDirectionAddition[1])) ** 2
                    )
                    # pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.pinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.pinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.pinkyDistance <= min and plusPetit:
                        min = self.pinkyDistance
                        self.pinkyPossibleDirection = "Right"
                    self.pinky.moveCollisionBox(-8, 0)
                elif i == "Down":
                    self.pinky.moveCollisionBox(0, 8)
                    self.pinkyDistance = sqrt(
                        (self.pinky.collisionBox.x - (self.pacman.rect.x+self.pinkyDirectionAddition[0])) ** 2
                        + (self.pinky.collisionBox.y - (self.pacman.rect.y+self.pinkyDirectionAddition[1])) ** 2
                    )
                    # pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.pinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.pinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.pinkyDistance <= min and plusPetit:
                        min = self.pinkyDistance
                        self.pinkyPossibleDirection = "Down"
                    self.pinky.moveCollisionBox(0, -8)
                elif i == "Left":
                    self.pinky.moveCollisionBox(-8, 0)
                    self.pinkyDistance = sqrt(
                        (self.pinky.collisionBox.x - (self.pacman.rect.x+self.pinkyDirectionAddition[0])) ** 2
                        + (self.pinky.collisionBox.y - (self.pacman.rect.y+self.pinkyDirectionAddition[1])) ** 2
                    )
                    # pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.pinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.pinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.pinkyDistance <= min and plusPetit:
                        min = self.pinkyDistance
                        self.pinkyPossibleDirection = "Left"
                    self.pinky.moveCollisionBox(8, 0)
                elif i == "Up":
                    self.pinky.moveCollisionBox(0, -8)
                    self.pinkyDistance = sqrt(
                        (self.pinky.collisionBox.x - (self.pacman.rect.x+self.pinkyDirectionAddition[0])) ** 2
                        + (self.pinky.collisionBox.y - (self.pacman.rect.y+self.pinkyDirectionAddition[1])) ** 2
                    )
                    # pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.pinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.pinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.pinkyDistance <= min and plusPetit:
                        min = self.pinkyDistance
                        self.pinkyPossibleDirection = "Up"
                    self.pinky.moveCollisionBox(0, 8)

            if self.pinkyLife <= 8:
                if self.pinkyPossibleDirection == "Right":
                    if self.pinky.collisionBox.colliderect(self.ghostCollisionRight):
                        self.pinky.setPos(-20, 108)
                    self.pinky.move(8, 0)
                    self.pinky.okMovement = (
                        self.pinky.allMovement.copy()[0:2]
                        + self.pinky.allMovement.copy()[3:4]
                    )
                elif self.pinkyPossibleDirection == "Down":
                    self.pinky.move(0, 8)
                    self.pinky.okMovement = self.pinky.allMovement.copy()[:3]
                elif self.pinkyPossibleDirection == "Left":
                    if self.pinky.collisionBox.colliderect(self.ghostCollisionLeft):
                        self.pinky.setPos(228, 108)
                    self.pinky.move(-8, 0)
                    self.pinky.okMovement = self.pinky.allMovement.copy()[1:]
                elif self.pinkyPossibleDirection == "Up":
                    self.pinky.move(0, -8)
                    self.pinky.okMovement = (
                        self.pinky.allMovement.copy()[0:1]
                        + self.pinky.allMovement.copy()[2:4]
                    )
            else:
                self.pinkyLife = 4

    def inkyMovement(self):
        if self.inkyLife >= 0:
            min = 1000000000000000000000
            xDistance = self.blinky.getPos()[0] - (self.pacman.rect.x+self.inkyDirectionAddition[0])
            yDistance = self.blinky.getPos()[1] - (self.pacman.rect.y+self.inkyDirectionAddition[1])
            xInkyGraph = self.pacman.rect.x+self.inkyDirectionAddition[0] - xDistance
            yInkyGraph = self.pacman.rect.y+self.inkyDirectionAddition[1] - yDistance
            for i in self.inky.okMovement:
                plusPetit = True
                if i == "Right":
                    self.inky.moveCollisionBox(8, 0)
                    self.inkyDistance = sqrt(
                        (self.inky.collisionBox.x - xInkyGraph) ** 2
                        + (self.inky.collisionBox.y - yInkyGraph) ** 2
                    )
                    # pygame.draw.rect(self.screen, (0, 255, 255), self.inky.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.inky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.inky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.inkyDistance <= min and plusPetit:
                        min = self.inkyDistance
                        self.inkyPossibleDirection = "Right"
                    self.inky.moveCollisionBox(-8, 0)
                elif i == "Down":
                    self.inky.moveCollisionBox(0, 8)
                    # pygame.draw.rect(self.screen, (0, 255, 255), self.inky.collisionBox, 1)
                    # pygame.display.flip()
                    self.inkyDistance = sqrt(
                        (self.inky.collisionBox.x - xInkyGraph) ** 2
                        + (self.inky.collisionBox.y - yInkyGraph) ** 2
                    )
                    for collision in self.collisions:
                        if self.inky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.inky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.inkyDistance <= min and plusPetit:
                        min = self.inkyDistance
                        self.inkyPossibleDirection = "Down"
                    self.inky.moveCollisionBox(0, -8)
                elif i == "Left":
                    self.inky.moveCollisionBox(-8, 0)
                    # pygame.draw.rect(self.screen, (0, 255, 255), self.inky.collisionBox, 1)
                    # pygame.display.flip()
                    self.inkyDistance = sqrt(
                        (self.inky.collisionBox.x - xInkyGraph) ** 2
                        + (self.inky.collisionBox.y - yInkyGraph) ** 2
                    )
                    for collision in self.collisions:
                        if self.inky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.inky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.inkyDistance <= min and plusPetit:
                        min = self.inkyDistance
                        self.inkyPossibleDirection = "Left"
                    self.inky.moveCollisionBox(8, 0)
                elif i == "Up":
                    self.inky.moveCollisionBox(0, -8)
                    # pygame.draw.rect(self.screen, (0, 255, 255), self.inky.collisionBox, 1)
                    # pygame.display.flip()
                    self.inkyDistance = sqrt(
                        (self.inky.collisionBox.x - xInkyGraph) ** 2
                        + (self.inky.collisionBox.y - yInkyGraph) ** 2
                    )
                    for collision in self.collisions:
                        if self.inky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.inky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.inkyDistance <= min and plusPetit:
                        min = self.inkyDistance
                        self.inkyPossibleDirection = "Up"
                    self.inky.moveCollisionBox(0, 8)
                # print(self.inky.okMovement)
                # print(min)
                # print(self.inkyDistance)
                # print(self.inkyPossibleDirection)
                # print()

            if self.inkyLife <= 4:
                if self.inkyPossibleDirection == "Right":
                    if self.inky.collisionBox.colliderect(self.ghostCollisionRight):
                        self.inky.setPos(-20, 108)
                    self.inky.move(8, 0)
                    self.inky.okMovement = (
                        self.inky.allMovement.copy()[0:2]
                        + self.inky.allMovement.copy()[3:4]
                    )
                elif self.inkyPossibleDirection == "Down":
                    self.inky.move(0, 8)
                    self.inky.okMovement = self.inky.allMovement.copy()[:3]
                elif self.inkyPossibleDirection == "Left":
                    if self.inky.collisionBox.colliderect(self.ghostCollisionLeft):
                        self.inky.setPos(228, 108)
                    self.inky.move(-8, 0)
                    self.inky.okMovement = self.inky.allMovement.copy()[1:]
                elif self.inkyPossibleDirection == "Up":
                    self.inky.move(0, -8)
                    self.inky.okMovement = (
                        self.inky.allMovement.copy()[0:1]
                        + self.inky.allMovement.copy()[2:4]
                    )
            else:
                self.inkyLife = 0

    def clydeMovement(self):
        if self.clydeLife >= 0:
            min = 1000000000000000000000
            for i in self.clyde.okMovement:
                plusPetit = True
                if i == "Right":
                    self.clyde.moveCollisionBox(8, 0)
                    self.clydeDistance = sqrt(
                        (self.clyde.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.clyde.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    # pygame.draw.rect(self.screen, (255, 0, 0), self.clyde.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.clyde.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.clyde.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.clydeDistance > 64:
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Right"
                    else:
                        self.clydeDistance = sqrt(
                            (self.clyde.collisionBox.x - self.clyde.basePoint[0]) ** 2
                            + (self.clyde.collisionBox.y - self.clyde.basePoint[1]) ** 2
                        )
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Right"
                    self.clyde.moveCollisionBox(-8, 0)
                elif i == "Down":
                    self.clyde.moveCollisionBox(0, 8)
                    self.clydeDistance = sqrt(
                        (self.clyde.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.clyde.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    # pygame.draw.rect(self.screen, (255, 0, 0), self.clyde.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.clyde.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.clyde.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.clydeDistance > 64:
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Down"
                    else:
                        self.clydeDistance = sqrt(
                            (self.clyde.collisionBox.x - self.clyde.basePoint[0]) ** 2
                            + (self.clyde.collisionBox.y - self.clyde.basePoint[1]) ** 2
                        )
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Down"
                    self.clyde.moveCollisionBox(0, -8)
                elif i == "Left":
                    self.clyde.moveCollisionBox(-8, 0)
                    self.clydeDistance = sqrt(
                        (self.clyde.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.clyde.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    # pygame.draw.rect(self.screen, (255, 0, 0), self.clyde.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.clyde.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.clyde.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.clydeDistance > 64:
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Left"
                    else:
                        self.clydeDistance = sqrt(
                            (self.clyde.collisionBox.x - self.clyde.basePoint[0]) ** 2
                            + (self.clyde.collisionBox.y - self.clyde.basePoint[1]) ** 2
                        )
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Left"
                    self.clyde.moveCollisionBox(8, 0)
                elif i == "Up":
                    self.clyde.moveCollisionBox(0, -8)
                    self.clydeDistance = sqrt(
                        (self.clyde.collisionBox.x - self.pacman.rect.x) ** 2
                        + (self.clyde.collisionBox.y - self.pacman.rect.y) ** 2
                    )
                    # pygame.draw.rect(self.screen, (255, 0, 0), self.clyde.collisionBox, 1)
                    # pygame.display.flip()
                    for collision in self.collisions:
                        if self.clyde.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.clyde.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.clydeDistance > 64:
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Up"
                    else:
                        self.clydeDistance = sqrt(
                            (self.clyde.collisionBox.x - self.clyde.basePoint[0]) ** 2
                            + (self.clyde.collisionBox.y - self.clyde.basePoint[1]) ** 2
                        )
                        if self.clydeDistance <= min and plusPetit:
                            min = self.clydeDistance
                            self.clydePossibleDirection = "Up"
                    # print(self.clyde.okMovement)
                    # print(min)
                    # print(self.clydeDistance)
                    # print(self.clydePossibleDirection)
                    # print()
                    self.clyde.moveCollisionBox(0, 8)

            if self.clydeLife <= 4:
                if self.clydePossibleDirection == "Right":
                    if self.clyde.collisionBox.colliderect(self.ghostCollisionRight):
                        self.clyde.setPos(-20, 108)
                    self.clyde.move(8, 0)
                    self.clyde.okMovement = (
                        self.clyde.allMovement.copy()[0:2]
                        + self.clyde.allMovement.copy()[3:4]
                    )
                elif self.clydePossibleDirection == "Down":
                    self.clyde.move(0, 8)
                    self.clyde.okMovement = self.clyde.allMovement.copy()[:3]
                elif self.clydePossibleDirection == "Left":
                    if self.clyde.collisionBox.colliderect(self.ghostCollisionLeft):
                        self.clyde.setPos(228, 108)
                    self.clyde.move(-8, 0)
                    self.clyde.okMovement = self.clyde.allMovement.copy()[1:]
                elif self.clydePossibleDirection == "Up":
                    self.clyde.move(0, -8)
                    self.clyde.okMovement = (
                        self.clyde.allMovement.copy()[0:1]
                        + self.clyde.allMovement.copy()[2:4]
                    )
            else:
                self.clydeLife = 0

    def updateScreen(self):
        # for layer in self.map.visible_layers:
        #     if layer.name == "Background":
        #         for x, y, gid in layer:
        #             tile = self.map.get_tile_image_by_gid(gid)
        #             self.screen.blit(
        #                 tile, (x * self.map.tilewidth, y * self.map.tileheight)
        #             )

        # pygame.draw.rect(self.screen, (255, 0, 0), self.CollisionBox, 1)
        self.pacman.image = self.pacman.animation(self.pacmanWay)[self.pacmanLife % 3]
        self.screen.blit(self.pacman.animation(self.pacmanWay)[self.pacmanLife % 3], self.pacman.getPos())

        #pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.rect, 1)
        self.screen.blit(self.blinky.image, self.blinky.getPos())

        #pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.rect, 1)
        self.screen.blit(self.pinky.image, self.pinky.getPos())

        #pygame.draw.rect(self.screen, (0, 255, 255), self.inky.rect, 1)
        self.screen.blit(self.inky.image, self.inky.getPos())

        #pygame.draw.rect(self.screen, (255, 200, 255), self.clyde.rect, 1)
        self.screen.blit(self.clyde.image, self.clyde.getPos())


        # pygame.draw.rect(self.screen, (255, 0, 0), self.pacman.getRect(), 1)
        # pygame.draw.rect(self.screen, (188, 0, 255), pygame.Rect(self.pacman.rect.x+self.pinkyDirectionAddition[0], self.pacman.rect.y+self.pinkyDirectionAddition[1], 16, 16), 1)
        # pygame.draw.rect(self.screen, (0, 255, 255), pygame.Rect(self.pacman.rect.x+self.inkyDirectionAddition[0], self.pacman.rect.y+self.inkyDirectionAddition[1], 16, 16), 1)

        # xDistance = self.blinky.getPos()[0] - (self.pacman.rect.x+self.inkyDirectionAddition[0])
        # yDistance = self.blinky.getPos()[1] - (self.pacman.rect.y+self.inkyDirectionAddition[1])
        # xInkyGraph = self.pacman.rect.x+self.inkyDirectionAddition[0] - xDistance
        # yInkyGraph = self.pacman.rect.y+self.inkyDirectionAddition[1] - yDistance
        # pygame.draw.line(self.screen, (255, 0, 0), (self.pacman.rect.x+self.inkyDirectionAddition[0], self.pacman.rect.y+self.inkyDirectionAddition[1]), (self.blinky.getPos()))
        # pygame.draw.line(self.screen, (0, 255, 255), (self.pacman.rect.x+self.inkyDirectionAddition[0], self.pacman.rect.y+self.inkyDirectionAddition[1]), (xInkyGraph, yInkyGraph))

        # pygame.draw.circle(self.screen, (255, 200, 0), self.pacman.rect.center, 64, 1)

        for gomme in self.gommes:
            self.screen.blit(gomme.image, (gomme.rect.x, gomme.rect.y))

        self.group.update()
        self.group.draw(self.screen)

        pygame.display.update()

    def run(self, running) -> None:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.input()
            self.addScore()
            self.updateScreen()

            self.blinkyMovement()
            self.pinkyMovement()
            self.inkyMovement()
            self.clydeMovement()

            self.pacmanLife += 1
            self.blinkyLife += 1
            self.pinkyLife += 1
            self.inkyLife += 1
            self.clydeLife += 1

            self.clock.tick(10)


if __name__ == "__main__":
    game = Game()
    game.run(True)

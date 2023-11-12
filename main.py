from math import sqrt
from time import sleep
import pygame
import pytmx
from player import Pacman
from item import Gomme
from blinky import Blinky
from pinky import Pinky

pygame.init()


class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((224, 248))
        self.clock = pygame.time.Clock()

        self.map = pytmx.load_pygame("./data/Map.tmx")
        self.tmx_data = pytmx.util_pygame.load_pygame("./data/Map.tmx")
        self.background = self.map.layers[0]

        self.pacman = Pacman()
        self.pacmanLife = 0
        self.pacmanWay = "Right"
        self.pinkyDirectionAddition = (0, 32)

        self.blinky = Blinky(x=108, y=108)
        self.blinkyLife = 0
        self.blinkyPossibleDirection = "Up"

        self.pinky = Pinky(x=92, y=108)
        self.pinkyLife = 0
        self.pinkyPossibleDirection = "Up"

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
            if not self.checkCollision():
                self.pacman.move(0, -8)
                self.scoreBox.y -= 8
            else:
                self.CollisionBox.y += 8

        if keys[pygame.K_q]:
            self.CollisionBox.x -= 8
            self.pacmanWay = "Left"
            self.pinkyDirectionAddition = (-32, 0)
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
            if not self.checkCollision():
                self.pacman.move(0, 8)
                self.scoreBox.y += 8
            else:
                self.CollisionBox.y -= 8

        if keys[pygame.K_d]:
            self.CollisionBox.x += 8
            self.pacmanWay = "Right"
            self.pinkyDirectionAddition = (32, 0)
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
                    pygame.draw.rect(self.screen, (255, 0, 0), self.pinky.collisionBox, 1)
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
                    pygame.draw.rect(self.screen, (255, 0, 0), self.pinky.collisionBox, 1)
                    pygame.display.flip()
                    self.pinkyDistance = sqrt(
                        (self.pinky.collisionBox.x - (self.pacman.rect.x+self.pinkyDirectionAddition[0])) ** 2
                        + (self.pinky.collisionBox.y - (self.pacman.rect.y+self.pinkyDirectionAddition[1])) ** 2
                    )
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
                    pygame.draw.rect(self.screen, (255, 0, 0), self.pinky.collisionBox, 1)
                    pygame.display.flip()
                    self.pinkyDistance = sqrt(
                        (self.pinky.collisionBox.x - (self.pacman.rect.x+self.pinkyDirectionAddition[0])) ** 2
                        + (self.pinky.collisionBox.y - (self.pacman.rect.y+self.pinkyDirectionAddition[1])) ** 2
                    )
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
                    pygame.draw.rect(self.screen, (255, 0, 0), self.pinky.collisionBox, 1)
                    pygame.display.flip()
                    self.pinkyDistance = sqrt(
                        (self.pinky.collisionBox.x - (self.pacman.rect.x+self.pinkyDirectionAddition[0])) ** 2
                        + (self.pinky.collisionBox.y - (self.pacman.rect.y+self.pinkyDirectionAddition[1])) ** 2
                    )
                    for collision in self.collisions:
                        if self.pinky.collisionBox.colliderect(
                            self.collisionHub
                        ) or self.pinky.collisionBox.colliderect(collision):
                            plusPetit = False
                    if self.pinkyDistance <= min and plusPetit:
                        min = self.pinkyDistance
                        self.pinkyPossibleDirection = "Up"
                    self.pinky.moveCollisionBox(0, 8)
                print(self.pinky.okMovement)
                print(min)
                print(self.pinkyDistance)
                print(self.pinkyPossibleDirection)
                print()
                pygame.draw.rect(self.screen, (255, 0, 0), self.pinky.collisionBox, 1)
                pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(self.pacman.rect.x+self.pinkyDirectionAddition[0], self.pacman.rect.y+self.pinkyDirectionAddition[1], 16, 16), 1)
                pygame.display.flip()

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

    def updateScreen(self):
        for layer in self.map.visible_layers:
            if layer.name == "Background":
                for x, y, gid in layer:
                    tile = self.map.get_tile_image_by_gid(gid)
                    self.screen.blit(
                        tile, (x * self.map.tilewidth, y * self.map.tileheight)
                    )

        # pygame.draw.rect(self.screen, (255, 0, 0), self.CollisionBox, 1)
        # pygame.draw.rect(self.screen, (0, 255, 0), self.scoreBox, 1)
        self.screen.blit(self.pacman.animation(self.pacmanWay)[self.pacmanLife % 3], self.pacman.getPos())

        # pygame.draw.rect(self.screen, (0, 0, 255), self.blinky.rect, 1)
        self.screen.blit(self.blinky.image, self.blinky.getPos())

        pygame.draw.rect(self.screen, (0, 0, 255), self.pinky.rect, 1)
        self.screen.blit(self.pinky.image, self.pinky.getPos())

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

            self.pacmanLife += 1
            self.blinkyLife += 1

            self.pinkyLife += 1

            self.clock.tick(10)


if __name__ == "__main__":
    game = Game()
    game.run(True)

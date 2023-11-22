from math import sqrt, cos, sin, radians
import random
from time import sleep
import pygame
import pytmx
import pyscroll
from player import Pacman
from item import Gomme, GommePlus
from blinky import Blinky
from pinky import Pinky
from inky import Inky
from clyde import Clyde
from life import Life

pygame.init()


class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((672, 825))
        self.clock = pygame.time.Clock()

        self.map = pytmx.load_pygame("./data/Map.tmx")
        test = pyscroll.data.TiledMapData(self.map)
        layer = pyscroll.orthographic.BufferedRenderer(test, self.screen.get_size())
        layer.zoom = 3
        self.tmx_data = pytmx.util_pygame.load_pygame("./data/Map.tmx")
        self.background = self.map.layers[0]

        self.group = pyscroll.PyscrollGroup(map_layer=layer)

        self.deathSound = pygame.mixer.Sound("./data/pacman_death.wav")
        self.eatGhostSound = pygame.mixer.Sound("./data/eat_ghost.wav")
        self.ghostGoToHubSound = pygame.mixer.Sound("./data/retreating.wav")
        self.munchSound = [
            pygame.mixer.Sound("./data/munch_1.wav"),
            pygame.mixer.Sound("./data/munch_2.wav"),
        ]
        self.powerPelletSound = pygame.mixer.Sound("./data/power_pellet.wav")
        self.sirenGhost1 = pygame.mixer.Sound("./data/siren_1.wav")
        self.introSound = pygame.mixer.Sound("./data/game_start.wav")
        self.endLevelSound = pygame.mixer.Sound("./data/intermission.wav")

        self.ghostGoToHubSoundPlaying = False
        self.ghostFrightSoundPlaying = False
        self.sirenPlaying = False

        pygame.font.init()
        self.font = pygame.font.Font("./data/emulogic.ttf", 32)

        self.gameState = "Chase"
        self.timeFright = 0
        self.imageFright = (
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((131, 64, 16, 16))
        )
        self.imageGoToHub = (
            pygame.image.load("./data/PacManSprites.png")
            .convert_alpha()
            .subsurface((131, 80, 16, 16))
        )

        self.imageLife = pygame.transform.scale(
            (
                pygame.image.load("./data/PacManSprites.png")
                .convert_alpha()
                .subsurface((19, 15, 16, 16))
            ),
            (64, 64),
        )

        self.running = True
        self.runDeath = False
        self.deathTime = 0
        self.deathAnim = 0
        self.numberLife = 3

        self.pacman = Pacman()
        self.pacmanSpeed = 2
        self.pacmanLife = 0
        self.pacmanWay = "Right"
        self.pacmanLastWay = "Right"
        self.pacmanCheck = 0

        self.pinkyDirectionAddition = (32, 0)
        self.inkyDirectionAddition = (16, 0)

        self.blinky = Blinky(x=104, y=84)
        self.blinkyLife = 0
        self.blinkyCheck = 0
        self.blinkyGoToHub = False
        self.blinkyFright = False
        self.blinkyPossibleDirection = "Right"

        self.pinky = Pinky(x=104, y=108)
        self.pinkyLife = 0
        self.pinkyCheck = 0
        self.pinkyGoToHub = False
        self.pinkyFright = False
        self.pinkyPossibleDirection = "Up"

        self.inky = Inky(x=88, y=108)
        self.inkyLife = 0
        self.inkyCheck = 0
        self.inkyGoToHub = False
        self.inkyFright = False
        self.inkyPossibleDirection = "Right"

        self.clyde = Clyde(x=120, y=108)
        self.clydeLife = 0
        self.clydeCheck = 0
        self.clydeGoToHub = False
        self.clydeFright = False
        self.clydePossibleDirection = "Right"

        self.CollisionBox = pygame.Rect(self.pacman.rect.x, self.pacman.rect.y, 16, 16)
        self.scoreBox = pygame.Rect(
            self.pacman.rect.x + 4, self.pacman.rect.y + 4, 8, 8
        )

        self.running = True
        self.score = 0
        self.numberGom = 0

        self.collisions = []
        self.collisionHub = None
        self.collisionTp = []
        self.gommeSpawn = []
        self.gommePlusSpawn = []
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
            elif obj.type == "gommePlus":
                self.gommePlusSpawn.append(
                    pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                )
            elif obj.type == "collisionGhostRight":
                self.ghostCollisionRight = pygame.Rect(
                    obj.x, obj.y, obj.width, obj.height
                )
            elif obj.type == "collisionGhostLeft":
                self.ghostCollisionLeft = pygame.Rect(
                    obj.x, obj.y, obj.width, obj.height
                )

        self.gommes = []
        self.gommesPlus = []

        for gomme in self.gommeSpawn:
            self.gommes.append(Gomme(x=gomme.x, y=gomme.y))
            self.group.add(Gomme(x=gomme.x, y=gomme.y))

        for gomme in self.gommePlusSpawn:
            self.gommesPlus.append(GommePlus(x=gomme.x, y=gomme.y))
            self.group.add(GommePlus(x=gomme.x, y=gomme.y))

        self.group.add(self.blinky)
        self.group.add(self.pinky)
        self.group.add(self.inky)
        self.group.add(self.clyde)
        self.group.add(self.pacman)

        self.group.change_layer(self.blinky, 1000)
        self.group.change_layer(self.pinky, 1000)
        self.group.change_layer(self.inky, 1000)
        self.group.change_layer(self.clyde, 1000)
        self.group.change_layer(self.pacman, 1000)

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

    def checkSpriteCollision(self):
        if (
            self.blinky.isScatter or self.gameState == "Chase"
        ) and self.scoreBox.colliderect(self.blinky.rect):
            self.numberLife -= 1
            self.runDeath = True
            self.running = False
            self.runAfterDeath()
        if (
            self.scoreBox.colliderect(self.blinky.rect)
            and self.blinkyFright
            and not self.blinkyGoToHub
        ):
            pygame.mixer.Sound.play(self.eatGhostSound)
            self.blinkyGoToHub = True
            self.score += 700

        if (
            self.pinky.isScatter or self.gameState == "Chase"
        ) and self.scoreBox.colliderect(self.pinky.rect):
            self.numberLife -= 1
            self.runDeath = True
            self.running = False
            self.runAfterDeath()
        if (
            self.scoreBox.colliderect(self.pinky.rect) and self.pinkyFright
        ) and not self.pinkyGoToHub:
            pygame.mixer.Sound.play(self.eatGhostSound)
            self.pinkyGoToHub = True
            self.score += 700

        if (
            self.inky.isScatter or self.gameState == "Chase"
        ) and self.scoreBox.colliderect(self.inky.rect):
            self.numberLife -= 1
            self.runDeath = True
            self.running = False
            self.runAfterDeath()
        if (
            self.scoreBox.colliderect(self.inky.rect)
            and self.inkyFright
            and not self.inkyGoToHub
        ):
            pygame.mixer.Sound.play(self.eatGhostSound)
            self.inkyGoToHub = True
            self.score += 700

        if (
            self.clyde.isScatter or self.gameState == "Chase"
        ) and self.scoreBox.colliderect(self.clyde.rect):
            self.numberLife -= 1
            self.runDeath = True
            self.running = False
            self.runAfterDeath()
        if (
            self.scoreBox.colliderect(self.clyde.rect)
            and self.clydeFright
            and not self.clydeGoToHub
        ):
            pygame.mixer.Sound.play(self.eatGhostSound)
            self.clydeGoToHub = True
            self.score += 700

        if self.gameState == "Fright":
            pass
        # else:
        #     if self.scoreBox.colliderect(self.blinky.rect):
        #         self.running = False
        #     if self.scoreBox.colliderect(self.pinky.rect):
        #         self.running = False
        #     if self.scoreBox.colliderect(self.inky.rect):
        #         self.running = False
        #     if self.scoreBox.colliderect(self.clyde.rect):
        #         self.running = False

    def input(self):
        # print("pacman x, y =", self.pacman.rect.x, self.pacman.rect.y)
        # print("collision pacman x, y =", self.CollisionBox.x, self.CollisionBox.y)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_z] or keys[pygame.K_UP]:
            self.CollisionBox.y -= self.pacmanSpeed
            self.pinkyDirectionAddition = (-32, -32)
            self.inkyDirectionAddition = (-16, -16)
            if not self.checkCollision():
                self.pacmanLastWay = "Up"
                self.pacmanWay = "Up"
            self.CollisionBox.y = self.pacman.rect.y
            self.pacmanCheck = 0

        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            self.CollisionBox.x -= self.pacmanSpeed
            self.pinkyDirectionAddition = (-32, 0)
            self.inkyDirectionAddition = (-16, 0)
            if not self.checkCollision():
                self.pacmanLastWay = "Left"
                self.pacmanWay = "Left"
            self.CollisionBox.x = self.pacman.rect.x
            self.pacmanCheck = 0

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.CollisionBox.y += self.pacmanSpeed
            self.pinkyDirectionAddition = (0, 32)
            self.inkyDirectionAddition = (0, 16)
            if not self.checkCollision():
                self.pacmanLastWay = "Down"
                self.pacmanWay = "Down"
            self.CollisionBox.y = self.pacman.rect.y
            self.pacmanCheck = 0

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.CollisionBox.x += self.pacmanSpeed
            self.pinkyDirectionAddition = (32, 0)
            self.inkyDirectionAddition = (16, 0)
            if not self.checkCollision():
                self.pacmanLastWay = "Right"
                self.pacmanWay = "Right"
            self.CollisionBox.x = self.pacman.rect.x
            self.pacmanCheck = 0

        if self.pacmanLastWay == "Right":
            self.CollisionBox.x += self.pacmanSpeed
            self.checkTp(-12, 108, -4)
            if not self.checkCollision():
                self.pacman.move(self.pacmanSpeed, 0)
                self.scoreBox.x += self.pacmanSpeed
            self.CollisionBox.x = self.pacman.rect.x
            self.CollisionBox.y = self.pacman.rect.y

        if self.pacmanLastWay == "Down":
            self.CollisionBox.y += self.pacmanSpeed
            if not self.checkCollision():
                self.pacman.move(0, self.pacmanSpeed)
                self.scoreBox.y += self.pacmanSpeed
            self.CollisionBox.x = self.pacman.rect.x
            self.CollisionBox.y = self.pacman.rect.y

        if self.pacmanLastWay == "Left":
            self.CollisionBox.x -= self.pacmanSpeed
            self.checkTp(220, 108, 228)
            if not self.checkCollision():
                self.pacman.move(-self.pacmanSpeed, 0)
                self.scoreBox.x -= self.pacmanSpeed
            self.CollisionBox.x = self.pacman.rect.x
            self.CollisionBox.y = self.pacman.rect.y

        if self.pacmanLastWay == "Up":
            self.CollisionBox.y -= self.pacmanSpeed
            if not self.checkCollision():
                self.scoreBox.y -= self.pacmanSpeed
                self.pacman.move(0, -self.pacmanSpeed)
            self.CollisionBox.x = self.pacman.rect.x
            self.CollisionBox.y = self.pacman.rect.y

        # print(self.pacmanLastWay)

    def setState(self):
        for gomme in self.gommePlusSpawn:
            if self.scoreBox.colliderect(gomme):
                for gommeOnScreen in self.group.sprites():
                    if (
                        gommeOnScreen.rect.x == gomme.x
                        and gommeOnScreen.rect.y == gomme.y
                    ):
                        self.group.remove(gommeOnScreen)
                        self.group.update()
                        self.gameState = "Fright"
                        self.blinkyFright = True
                        self.blinky.isScatter = False
                        self.pinkyFright = True
                        self.pinky.isScatter = False
                        self.inkyFright = True
                        self.inky.isScatter = False
                        self.clydeFright = True
                        self.clyde.isScatter = False
                        self.timeFright = 420
                        self.score += 50
                        if not self.ghostFrightSoundPlaying:
                            self.ghostFrightSoundPlaying = True
                            self.ghostGoToHubSoundPlaying = False
                            pygame.mixer.Sound.stop(self.sirenGhost1)
                            pygame.mixer.Sound.stop(self.ghostGoToHubSound)
                            pygame.mixer.Sound.play(self.powerPelletSound, -1)
        self.group.draw(self.screen)

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
                        pygame.mixer.Sound.play(self.munchSound[self.numberGom % 2])
                        pygame.mixer.Sound.play(self.munchSound[self.numberGom % 2])
                        self.numberGom += 1
                        self.score += gommeOnScreen.score

                for gommeOnScreen in self.gommes:
                    if (
                        gommeOnScreen.rect.x == gomme.x
                        and gommeOnScreen.rect.y == gomme.y
                    ):
                        if gommeOnScreen in self.gommes:
                            self.gommes.remove(gommeOnScreen)
        self.group.update()
        self.group.draw(self.screen)

    def blinkyMovement(self):
        if self.blinkyLife <= 3:
            self.blinky.move(1, 0)
            self.blinkyCheck = 8
        else:
            if (self.blinkyFright and self.blinkyCheck >= 8) and not self.blinkyGoToHub:
                self.blinkyCheck = 0
                # print("MODDDIIIIIIFFFFYY")
                if self.blinky.firstFright:
                    for i in self.blinky.allMovement:
                        if i not in self.blinky.okMovement:
                            if i == "Right":
                                self.blinky.okMovement = (
                                    self.blinky.allMovement.copy()[:2]
                                    + self.blinky.allMovement.copy()[3:4]
                                )
                            elif i == "Down":
                                self.blinky.okMovement = self.blinky.allMovement.copy()[
                                    :3
                                ]
                            elif i == "Left":
                                self.blinky.okMovement = self.blinky.allMovement.copy()[
                                    1:4
                                ]
                            elif i == "Up":
                                self.blinky.okMovement = (
                                    self.blinky.allMovement.copy()[:1]
                                    + self.blinky.allMovement.copy()[2:4]
                                )
                self.blinky.firstFright = False
                listValidMove = self.blinky.okMovement.copy()
                # print(listValidMove)
                # print(self.blinky.okMovement)
                # print()
                for i in self.blinky.okMovement:
                    kill = False
                    # print(i)
                    if i == "Right":
                        self.blinky.moveCollisionBox(1, 0)
                        for collision in self.collisions:
                            if self.blinky.collisionBox.colliderect(
                                collision
                            ) or self.blinky.collisionBox.colliderect(
                                self.collisionHub
                            ):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)

                        self.blinky.moveCollisionBox(-1, 0)
                    elif i == "Down":
                        self.blinky.moveCollisionBox(0, 1)
                        for collision in self.collisions:
                            if self.blinky.collisionBox.colliderect(
                                collision
                            ) or self.blinky.collisionBox.colliderect(
                                self.collisionHub
                            ):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.blinky.moveCollisionBox(0, -1)
                    elif i == "Left":
                        self.blinky.moveCollisionBox(-1, 0)
                        for collision in self.collisions:
                            if self.blinky.collisionBox.colliderect(
                                collision
                            ) or self.blinky.collisionBox.colliderect(
                                self.collisionHub
                            ):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.blinky.moveCollisionBox(1, 0)
                    elif i == "Up":
                        self.blinky.moveCollisionBox(0, -1)
                        for collision in self.collisions:
                            if self.blinky.collisionBox.colliderect(
                                collision
                            ) or self.blinky.collisionBox.colliderect(
                                self.collisionHub
                            ):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.blinky.moveCollisionBox(0, 1)
                # print()
                # print(listValidMove)
                # print(self.blinky.okMovement)
                self.blinkyPossibleDirection = random.choice(listValidMove)
                # print(self.blinky.rect.x, self.blinky.rect.y)
                # print(self.blinkyPossibleDirection)
                pygame.draw.rect(
                    self.screen, (0, 255, 255), self.blinky.collisionBox, 1
                )
            elif (
                self.gameState == "Chase" or self.blinky.isScatter or self.blinkyGoToHub
            ) and self.blinkyCheck >= 8:
                # print("MODDDIIIIIIFFFFYY")
                # print(self.blinky.rect.x, self.blinky.rect.y)
                # print()
                min = 1000000000000000000000
                self.blinkyCheck = 0
                for i in self.blinky.okMovement:
                    plusPetit = True
                    if i == "Right":
                        self.blinky.moveCollisionBox(8, 0)
                        if self.blinkyGoToHub:
                            self.blinkyDistance = sqrt(
                                (self.blinky.collisionBox.x - 108) ** 2
                                + (self.blinky.collisionBox.y - 108) ** 2
                            )
                        elif self.blinky.isScatter:
                            self.blinkyDistance = sqrt(
                                (self.blinky.collisionBox.x - self.blinky.basePoint[0])
                                ** 2
                                + (
                                    self.blinky.collisionBox.y
                                    - self.blinky.basePoint[1]
                                )
                                ** 2
                            )
                        else:
                            self.blinkyDistance = sqrt(
                                (self.blinky.collisionBox.x - self.pacman.rect.x) ** 2
                                + (self.blinky.collisionBox.y - self.pacman.rect.y) ** 2
                            )
                        # pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.collisionBox, 1)
                        # pygame.display.flip()
                        if self.blinkyGoToHub:
                            for collision in self.collisions:
                                if self.blinky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
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
                        if self.blinkyGoToHub:
                            self.blinkyDistance = sqrt(
                                (self.blinky.collisionBox.x - 108) ** 2
                                + (self.blinky.collisionBox.y - 108) ** 2
                            )
                        elif self.blinky.isScatter:
                            self.blinkyDistance = sqrt(
                                (self.blinky.collisionBox.x - self.blinky.basePoint[0])
                                ** 2
                                + (
                                    self.blinky.collisionBox.y
                                    - self.blinky.basePoint[1]
                                )
                                ** 2
                            )
                        else:
                            self.blinkyDistance = sqrt(
                                (self.blinky.collisionBox.x - self.pacman.rect.x) ** 2
                                + (self.blinky.collisionBox.y - self.pacman.rect.y) ** 2
                            )
                        # pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.collisionBox, 1)
                        # pygame.display.flip()
                        if self.blinkyGoToHub:
                            for collision in self.collisions:
                                if self.blinky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
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
                        if self.blinkyGoToHub:
                            self.blinkyDistance = sqrt(
                                (self.blinky.collisionBox.x - 108) ** 2
                                + (self.blinky.collisionBox.y - 108) ** 2
                            )
                        elif self.blinky.isScatter:
                            self.blinkyDistance = sqrt(
                                (self.blinky.collisionBox.x - self.blinky.basePoint[0])
                                ** 2
                                + (
                                    self.blinky.collisionBox.y
                                    - self.blinky.basePoint[1]
                                )
                                ** 2
                            )
                        else:
                            self.blinkyDistance = sqrt(
                                (self.blinky.collisionBox.x - self.pacman.rect.x) ** 2
                                + (self.blinky.collisionBox.y - self.pacman.rect.y) ** 2
                            )
                        # pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.collisionBox, 1)
                        # pygame.display.flip()
                        if self.blinkyGoToHub:
                            for collision in self.collisions:
                                if self.blinky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
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
                        if self.blinkyGoToHub:
                            self.blinkyDistance = sqrt(
                                (self.blinky.collisionBox.x - 108) ** 2
                                + (self.blinky.collisionBox.y - 108) ** 2
                            )
                        elif self.blinky.isScatter:
                            self.blinkyDistance = sqrt(
                                (self.blinky.collisionBox.x - self.blinky.basePoint[0])
                                ** 2
                                + (
                                    self.blinky.collisionBox.y
                                    - self.blinky.basePoint[1]
                                )
                                ** 2
                            )
                        else:
                            self.blinkyDistance = sqrt(
                                (self.blinky.collisionBox.x - self.pacman.rect.x) ** 2
                                + (self.blinky.collisionBox.y - self.pacman.rect.y) ** 2
                            )
                        # pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.collisionBox, 1)
                        # pygame.display.flip()
                        if self.blinkyGoToHub:
                            for collision in self.collisions:
                                if self.blinky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
                            for collision in self.collisions:
                                if self.blinky.collisionBox.colliderect(
                                    self.collisionHub
                                ) or self.blinky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        if self.blinkyDistance <= min and plusPetit:
                            min = self.blinkyDistance
                            self.blinkyPossibleDirection = "Up"
                        self.blinky.moveCollisionBox(0, 8)

            if self.blinkyLife >= 0:
                if self.blinkyPossibleDirection == "Right":
                    self.blinky.move(1, 0)
                    if self.blinky.rect.colliderect(self.ghostCollisionRight):
                        self.blinky.setPos(-19, 108)
                    self.blinky.okMovement = (
                        self.blinky.allMovement.copy()[0:2]
                        + self.blinky.allMovement.copy()[3:4]
                    )
                elif self.blinkyPossibleDirection == "Down":
                    self.blinky.move(0, 1)
                    self.blinky.okMovement = self.blinky.allMovement.copy()[:3]
                elif self.blinkyPossibleDirection == "Left":
                    self.blinky.move(-1, 0)
                    if self.blinky.collisionBox.colliderect(self.ghostCollisionLeft):
                        self.blinky.setPos(227, 108)
                    self.blinky.okMovement = self.blinky.allMovement.copy()[1:]
                elif self.blinkyPossibleDirection == "Up":
                    self.blinky.move(0, -1)
                    self.blinky.okMovement = (
                        self.blinky.allMovement.copy()[0:1]
                        + self.blinky.allMovement.copy()[2:4]
                    )

            if (
                self.blinky.rect.x == 108
                and self.blinky.rect.y == 108
                and self.blinkyGoToHub
            ):
                self.blinkyGoToHub = False
                self.blinky.setPos(108, 107)
                self.blinkyLife = 0
                self.blinkyCheck = 0
                self.blinkyPossibleDirection = "Up"
                self.blinkyFright = False
                self.blinky.isScatter = True

    def pinkyMovement(self):
        if self.pinkyLife <= 4:
            self.pinky.move(0, 1)
            self.pinkyLoop = 0
            self.pinkyLoopDown = False
        elif self.pinkyLife <= 183:
            if self.pinkyLoopDown:
                self.pinky.move(0, 1)
            else:
                self.pinky.move(0, -1)

            self.pinkyLoop += 1

            if self.pinkyLoop >= 9:
                self.pinkyLoopDown = not self.pinkyLoopDown
                self.pinkyLoop = 0

        elif self.pinkyLife <= 211:
            self.pinky.move(0, -1)
        elif self.pinkyLife <= 215:
            self.pinky.move(-1, 0)
        else:
            if (self.pinkyFright and self.pinkyCheck >= 8) and not self.pinkyGoToHub:
                self.pinkyCheck = 0
                if self.pinky.firstFright:
                    for i in self.pinky.allMovement:
                        if i not in self.pinky.okMovement:
                            if i == "Right":
                                self.pinky.okMovement = (
                                    self.pinky.allMovement.copy()[:2]
                                    + self.pinky.allMovement.copy()[3:4]
                                )
                            elif i == "Down":
                                self.pinky.okMovement = self.pinky.allMovement.copy()[
                                    :3
                                ]
                            elif i == "Left":
                                self.pinky.okMovement = self.pinky.allMovement.copy()[
                                    1:4
                                ]
                            elif i == "Up":
                                self.pinky.okMovement = (
                                    self.pinky.allMovement.copy()[:1]
                                    + self.pinky.allMovement.copy()[2:4]
                                )
                self.pinky.firstFright = False
                listValidMove = self.pinky.okMovement.copy()
                # print(listValidMove)
                # print(self.pinky.okMovement)
                # print()
                for i in self.pinky.okMovement:
                    kill = False
                    # print(i)
                    if i == "Right":
                        self.pinky.moveCollisionBox(1, 0)
                        for collision in self.collisions:
                            if self.pinky.collisionBox.colliderect(
                                collision
                            ) or self.pinky.collisionBox.colliderect(self.collisionHub):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.pinky.moveCollisionBox(-1, 0)
                    elif i == "Down":
                        self.pinky.moveCollisionBox(0, 1)
                        for collision in self.collisions:
                            if self.pinky.collisionBox.colliderect(
                                collision
                            ) or self.pinky.collisionBox.colliderect(self.collisionHub):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.pinky.moveCollisionBox(0, -1)
                    elif i == "Left":
                        self.pinky.moveCollisionBox(-1, 0)
                        for collision in self.collisions:
                            if self.pinky.collisionBox.colliderect(
                                collision
                            ) or self.pinky.collisionBox.colliderect(self.collisionHub):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.pinky.moveCollisionBox(1, 0)
                    elif i == "Up":
                        self.pinky.moveCollisionBox(0, -1)
                        for collision in self.collisions:
                            if self.pinky.collisionBox.colliderect(
                                collision
                            ) or self.pinky.collisionBox.colliderect(self.collisionHub):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.pinky.moveCollisionBox(0, 1)
                self.pinkyPossibleDirection = random.choice(listValidMove)

            elif (
                self.gameState == "Chase" or self.pinky.isScatter or self.pinkyGoToHub
            ) and self.pinkyCheck >= 8:
                min = 1000000000000000000000
                self.pinkyCheck = 0
                for i in self.pinky.okMovement:
                    plusPetit = True
                    if i == "Right":
                        self.pinky.moveCollisionBox(8, 0)
                        if self.pinkyGoToHub:
                            self.pinkyDistance = sqrt(
                                (self.pinky.collisionBox.x - 92) ** 2
                                + (self.pinky.collisionBox.y - 108) ** 2
                            )
                        elif self.pinky.isScatter:
                            self.pinkyDistance = sqrt(
                                (self.pinky.collisionBox.x - self.pinky.basePoint[0])
                                ** 2
                                + (self.pinky.collisionBox.y - self.pinky.basePoint[1])
                                ** 2
                            )
                        else:
                            self.pinkyDistance = sqrt(
                                (
                                    self.pinky.collisionBox.x
                                    - (
                                        self.pacman.rect.x
                                        + self.pinkyDirectionAddition[0]
                                    )
                                )
                                ** 2
                                + (
                                    self.pinky.collisionBox.y
                                    - (
                                        self.pacman.rect.y
                                        + self.pinkyDirectionAddition[1]
                                    )
                                )
                                ** 2
                            )
                        # pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.collisionBox, 1)
                        # pygame.display.flip()
                        if self.pinkyGoToHub:
                            for collision in self.collisions:
                                if self.pinky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
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
                        if self.pinkyGoToHub:
                            self.pinkyDistance = sqrt(
                                (self.pinky.collisionBox.x - 92) ** 2
                                + (self.pinky.collisionBox.y - 108) ** 2
                            )
                        elif self.pinky.isScatter:
                            self.pinkyDistance = sqrt(
                                (self.pinky.collisionBox.x - self.pinky.basePoint[0])
                                ** 2
                                + (self.pinky.collisionBox.y - self.pinky.basePoint[1])
                                ** 2
                            )
                        else:
                            self.pinkyDistance = sqrt(
                                (
                                    self.pinky.collisionBox.x
                                    - (
                                        self.pacman.rect.x
                                        + self.pinkyDirectionAddition[0]
                                    )
                                )
                                ** 2
                                + (
                                    self.pinky.collisionBox.y
                                    - (
                                        self.pacman.rect.y
                                        + self.pinkyDirectionAddition[1]
                                    )
                                )
                                ** 2
                            )
                        # pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.collisionBox, 1)
                        # pygame.display.flip()
                        if self.pinkyGoToHub:
                            for collision in self.collisions:
                                if self.pinky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
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
                        if self.pinkyGoToHub:
                            self.pinkyDistance = sqrt(
                                (self.pinky.collisionBox.x - 92) ** 2
                                + (self.pinky.collisionBox.y - 108) ** 2
                            )
                        elif self.pinky.isScatter:
                            self.pinkyDistance = sqrt(
                                (self.pinky.collisionBox.x - self.pinky.basePoint[0])
                                ** 2
                                + (self.pinky.collisionBox.y - self.pinky.basePoint[1])
                                ** 2
                            )
                        else:
                            self.pinkyDistance = sqrt(
                                (
                                    self.pinky.collisionBox.x
                                    - (
                                        self.pacman.rect.x
                                        + self.pinkyDirectionAddition[0]
                                    )
                                )
                                ** 2
                                + (
                                    self.pinky.collisionBox.y
                                    - (
                                        self.pacman.rect.y
                                        + self.pinkyDirectionAddition[1]
                                    )
                                )
                                ** 2
                            )
                        # pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.collisionBox, 1)
                        # pygame.display.flip()
                        if self.pinkyGoToHub:
                            for collision in self.collisions:
                                if self.pinky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
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
                        if self.pinkyGoToHub:
                            self.pinkyDistance = sqrt(
                                (self.pinky.collisionBox.x - 92) ** 2
                                + (self.pinky.collisionBox.y - 108) ** 2
                            )
                        elif self.pinky.isScatter:
                            self.pinkyDistance = sqrt(
                                (self.pinky.collisionBox.x - self.pinky.basePoint[0])
                                ** 2
                                + (self.pinky.collisionBox.y - self.pinky.basePoint[1])
                                ** 2
                            )
                        else:
                            self.pinkyDistance = sqrt(
                                (
                                    self.pinky.collisionBox.x
                                    - (
                                        self.pacman.rect.x
                                        + self.pinkyDirectionAddition[0]
                                    )
                                )
                                ** 2
                                + (
                                    self.pinky.collisionBox.y
                                    - (
                                        self.pacman.rect.y
                                        + self.pinkyDirectionAddition[1]
                                    )
                                )
                                ** 2
                            )
                        # pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.collisionBox, 1)
                        # pygame.display.flip()
                        if self.pinkyGoToHub:
                            for collision in self.collisions:
                                if self.pinky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
                            for collision in self.collisions:
                                if self.pinky.collisionBox.colliderect(
                                    self.collisionHub
                                ) or self.pinky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        if self.pinkyDistance <= min and plusPetit:
                            min = self.pinkyDistance
                            self.pinkyPossibleDirection = "Up"
                        self.pinky.moveCollisionBox(0, 8)

            if self.pinkyLife >= 27:
                if self.pinkyPossibleDirection == "Right":
                    if self.pinky.collisionBox.colliderect(self.ghostCollisionRight):
                        self.pinky.setPos(-19, 108)
                    self.pinky.move(1, 0)
                    self.pinky.okMovement = (
                        self.pinky.allMovement.copy()[0:2]
                        + self.pinky.allMovement.copy()[3:4]
                    )
                elif self.pinkyPossibleDirection == "Down":
                    self.pinky.move(0, 1)
                    self.pinky.okMovement = self.pinky.allMovement.copy()[:3]
                elif self.pinkyPossibleDirection == "Left":
                    if self.pinky.collisionBox.colliderect(self.ghostCollisionLeft):
                        self.pinky.setPos(227, 108)
                    self.pinky.move(-1, 0)
                    self.pinky.okMovement = self.pinky.allMovement.copy()[1:]
                elif self.pinkyPossibleDirection == "Up":
                    self.pinky.move(0, -1)
                    self.pinky.okMovement = (
                        self.pinky.allMovement.copy()[0:1]
                        + self.pinky.allMovement.copy()[2:4]
                    )

            if (
                self.pinky.rect.x == 92
                and self.pinky.rect.y == 108
                and self.pinkyGoToHub
            ):
                self.pinkyGoToHub = False
                self.pinky.setPos(93, 108)
                self.pinkyLife = 0
                self.pinkyCheck = 0
                self.pinkyPossibleDirection = "Up"
                self.pinkyFright = False
                self.pinky.isScatter = True

    def inkyMovement(self):
        if self.inkyLife <= 4:
            self.inky.move(0, -1)
            self.inkyLoop = 0
            self.inkyLoopDown = True
        elif self.inkyLife <= 219:
            if self.inkyLoopDown:
                self.inky.move(0, 1)
            else:
                self.inky.move(0, -1)

            self.inkyLoop += 1

            if self.inkyLoop >= 9:
                self.inkyLoopDown = not self.inkyLoopDown
                self.inkyLoop = 0

        elif self.inkyLife <= 223:
            print(self.inky.rect.x, self.inky.rect.y)
            print()
            self.inky.move(0, 1)
        elif self.inkyLife <= 239:
            print(self.inky.rect.x, self.inky.rect.y)
            print()
            self.inky.move(1, 0)
        elif self.inkyLife <= 263:
            print(self.inky.rect.x, self.inky.rect.y)
            print()
            self.inky.move(0, -1)
        elif self.inkyLife <= 267:
            print(self.inky.rect.x, self.inky.rect.y)
            print()
            self.inky.move(1, 0)
        else:
            if (self.inkyFright and self.inkyCheck >= 8) and not self.inkyGoToHub:
                self.inkyCheck = 0
                if self.inky.firstFright:
                    for i in self.inky.allMovement:
                        if i not in self.inky.okMovement:
                            if i == "Right":
                                self.inky.okMovement = (
                                    self.inky.allMovement.copy()[:2]
                                    + self.inky.allMovement.copy()[3:4]
                                )
                            elif i == "Down":
                                self.inky.okMovement = self.inky.allMovement.copy()[:3]
                            elif i == "Left":
                                self.inky.okMovement = self.inky.allMovement.copy()[1:4]
                            elif i == "Up":
                                self.inky.okMovement = (
                                    self.inky.allMovement.copy()[:1]
                                    + self.inky.allMovement.copy()[2:4]
                                )
                self.inky.firstFright = False
                listValidMove = self.inky.okMovement.copy()
                # print(listValidMove)
                # print(self.inky.okMovement)
                # print()
                for i in self.inky.okMovement:
                    kill = False
                    # print(i)
                    if i == "Right":
                        self.inky.moveCollisionBox(1, 0)
                        for collision in self.collisions:
                            if self.inky.collisionBox.colliderect(
                                collision
                            ) or self.inky.collisionBox.colliderect(self.collisionHub):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)

                        self.inky.moveCollisionBox(-1, 0)
                    elif i == "Down":
                        self.inky.moveCollisionBox(0, 1)
                        for collision in self.collisions:
                            if self.inky.collisionBox.colliderect(
                                collision
                            ) or self.inky.collisionBox.colliderect(self.collisionHub):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.inky.moveCollisionBox(0, -1)
                    elif i == "Left":
                        self.inky.moveCollisionBox(-1, 0)
                        for collision in self.collisions:
                            if self.inky.collisionBox.colliderect(
                                collision
                            ) or self.inky.collisionBox.colliderect(self.collisionHub):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.inky.moveCollisionBox(1, 0)
                    elif i == "Up":
                        self.inky.moveCollisionBox(0, -1)
                        for collision in self.collisions:
                            if self.inky.collisionBox.colliderect(
                                collision
                            ) or self.inky.collisionBox.colliderect(self.collisionHub):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.inky.moveCollisionBox(0, 1)
                # print()
                # print(listValidMove)
                # print(self.inky.okMovement)
                self.inkyPossibleDirection = random.choice(listValidMove)
                # print(self.inkyPossibleDirection)
                # pygame.draw.rect(self.screen, (0, 255, 255), self.inky.collisionBox, 1)

            elif (
                self.gameState == "Chase" or self.inky.isScatter or self.inkyGoToHub
            ) and self.inkyCheck >= 8:
                print("modifyy")
                print(self.inky.rect.x, self.inky.rect.y)
                print()
                min = 1000000000000000000000
                self.inkyCheck = 0
                xDistance = self.blinky.getPos()[0] - (
                    self.pacman.rect.x + self.inkyDirectionAddition[0]
                )
                yDistance = self.blinky.getPos()[1] - (
                    self.pacman.rect.y + self.inkyDirectionAddition[1]
                )
                xInkyGraph = (
                    self.pacman.rect.x + self.inkyDirectionAddition[0] - xDistance
                )
                yInkyGraph = (
                    self.pacman.rect.y + self.inkyDirectionAddition[1] - yDistance
                )
                for i in self.inky.okMovement:
                    plusPetit = True
                    if i == "Right":
                        self.inky.moveCollisionBox(8, 0)
                        if self.inkyGoToHub:
                            self.inkyDistance = sqrt(
                                (self.inky.collisionBox.x - 108) ** 2
                                + (self.inky.collisionBox.y - 84) ** 2
                            )
                        elif self.inky.isScatter:
                            self.inkyDistance = sqrt(
                                (self.inky.collisionBox.x - self.inky.basePoint[0]) ** 2
                                + (self.inky.collisionBox.y - self.inky.basePoint[1])
                                ** 2
                            )
                        else:
                            self.inkyDistance = sqrt(
                                (self.inky.collisionBox.x - xInkyGraph) ** 2
                                + (self.inky.collisionBox.y - yInkyGraph) ** 2
                            )
                        # pygame.draw.rect(self.screen, (0, 255, 255), self.inky.collisionBox, 1)
                        # pygame.display.flip()
                        if self.inkyGoToHub:
                            for collision in self.collisions:
                                if self.inky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
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
                        if self.inkyGoToHub:
                            self.inkyDistance = sqrt(
                                (self.inky.collisionBox.x - 108) ** 2
                                + (self.inky.collisionBox.y - 84) ** 2
                            )
                        elif self.inky.isScatter:
                            self.inkyDistance = sqrt(
                                (self.inky.collisionBox.x - self.inky.basePoint[0]) ** 2
                                + (self.inky.collisionBox.y - self.inky.basePoint[1])
                                ** 2
                            )
                        else:
                            self.inkyDistance = sqrt(
                                (self.inky.collisionBox.x - xInkyGraph) ** 2
                                + (self.inky.collisionBox.y - yInkyGraph) ** 2
                            )
                        if self.inkyGoToHub:
                            for collision in self.collisions:
                                if self.inky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
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
                        if self.inkyGoToHub:
                            self.inkyDistance = sqrt(
                                (self.inky.collisionBox.x - 108) ** 2
                                + (self.inky.collisionBox.y - 84) ** 2
                            )
                        elif self.inky.isScatter:
                            self.inkyDistance = sqrt(
                                (self.inky.collisionBox.x - self.inky.basePoint[0]) ** 2
                                + (self.inky.collisionBox.y - self.inky.basePoint[1])
                                ** 2
                            )
                        else:
                            self.inkyDistance = sqrt(
                                (self.inky.collisionBox.x - xInkyGraph) ** 2
                                + (self.inky.collisionBox.y - yInkyGraph) ** 2
                            )
                        if self.inkyGoToHub:
                            for collision in self.collisions:
                                if self.inky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
                            for collision in self.collisions:
                                if self.inky.collisionBox.colliderect(
                                    self.collisionHub
                                ) or self.inky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        if self.inkyDistance <= min and plusPetit:
                            # print("oui", self.inkyLife)
                            min = self.inkyDistance
                            self.inkyPossibleDirection = "Left"
                        self.inky.moveCollisionBox(8, 0)
                    elif i == "Up":
                        self.inky.moveCollisionBox(0, -8)
                        # pygame.draw.rect(self.screen, (0, 255, 255), self.inky.collisionBox, 1)
                        # pygame.display.flip()
                        if self.inkyGoToHub:
                            self.inkyDistance = sqrt(
                                (self.inky.collisionBox.x - 108) ** 2
                                + (self.inky.collisionBox.y - 84) ** 2
                            )
                        elif self.inky.isScatter:
                            self.inkyDistance = sqrt(
                                (self.inky.collisionBox.x - self.inky.basePoint[0]) ** 2
                                + (self.inky.collisionBox.y - self.inky.basePoint[1])
                                ** 2
                            )
                        else:
                            self.inkyDistance = sqrt(
                                (self.inky.collisionBox.x - xInkyGraph) ** 2
                                + (self.inky.collisionBox.y - yInkyGraph) ** 2
                            )
                        if self.inkyGoToHub:
                            for collision in self.collisions:
                                if self.inky.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
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

            if self.inkyLife >= 0:
                if self.inkyPossibleDirection == "Right":
                    if self.inky.collisionBox.colliderect(self.ghostCollisionRight):
                        self.inky.setPos(-19, 108)
                    self.inky.move(1, 0)
                    self.inky.okMovement = (
                        self.inky.allMovement.copy()[0:2]
                        + self.inky.allMovement.copy()[3:4]
                    )
                elif self.inkyPossibleDirection == "Down":
                    self.inky.move(0, 1)
                    self.inky.okMovement = self.inky.allMovement.copy()[:3]
                elif self.inkyPossibleDirection == "Left":
                    if self.inky.collisionBox.colliderect(self.ghostCollisionLeft):
                        self.inky.setPos(227, 108)
                    self.inky.move(-1, 0)
                    self.inky.okMovement = self.inky.allMovement.copy()[1:]
                elif self.inkyPossibleDirection == "Up":
                    self.inky.move(0, -1)
                    self.inky.okMovement = (
                        self.inky.allMovement.copy()[0:1]
                        + self.inky.allMovement.copy()[2:4]
                    )

            if self.inky.rect.x == 108 and self.inky.rect.y == 84 and self.inkyGoToHub:
                self.inkyGoToHub = False
                self.inky.setPos(108, 83)
                self.inkyLife = 0
                self.inkyCheck = 0
                self.inkyPossibleDirection = "Up"
                self.inkyFright = False
                self.inky.isScatter = True

    def clydeMovement(self):
        if self.clydeLife <= 4:
            self.clyde.move(0, -1)
            self.clydeLoop = 0
            self.clydeLoopDown = True
        elif self.clydeLife <= 255:
            if self.clydeLoopDown:
                self.clyde.move(0, 1)
            else:
                self.clyde.move(0, -1)

            self.clydeLoop += 1

            if self.clydeLoop >= 9:
                self.clydeLoopDown = not self.clydeLoopDown
                self.clydeLoop = 0

        elif self.clydeLife <= 259:
            print(self.clyde.rect.x, self.clyde.rect.y)
            print()
            self.clyde.move(0, 1)
        elif self.clydeLife <= 275:
            print(self.clyde.rect.x, self.clyde.rect.y)
            print()
            self.clyde.move(-1, 0)
        elif self.clydeLife <= 299:
            print(self.clyde.rect.x, self.clyde.rect.y)
            print()
            self.clyde.move(0, -1)
        elif self.clydeLife <= 303:
            print(self.clyde.rect.x, self.clyde.rect.y)
            print()
            self.clyde.move(-1, 0)
        else:
            min = 1000000000000000000000
            if (self.clydeFright and self.clydeCheck >= 8) and not self.clydeGoToHub:
                self.clydeCheck = 0
                if self.clyde.firstFright:
                    for i in self.clyde.allMovement:
                        if i not in self.clyde.okMovement:
                            if i == "Right":
                                self.clyde.okMovement = (
                                    self.clyde.allMovement.copy()[:2]
                                    + self.clyde.allMovement.copy()[3:4]
                                )
                            elif i == "Down":
                                self.clyde.okMovement = self.clyde.allMovement.copy()[
                                    :3
                                ]
                            elif i == "Left":
                                self.clyde.okMovement = self.clyde.allMovement.copy()[
                                    1:4
                                ]
                            elif i == "Up":
                                self.clyde.okMovement = (
                                    self.clyde.allMovement.copy()[:1]
                                    + self.clyde.allMovement.copy()[2:4]
                                )
                self.clyde.firstFright = False
                listValidMove = self.clyde.okMovement.copy()
                # print(listValidMove)
                # print(self.clyde.okMovement)
                # print()
                for i in self.clyde.okMovement:
                    kill = False
                    # print(i)
                    if i == "Right":
                        self.clyde.moveCollisionBox(8, 0)
                        for collision in self.collisions:
                            if self.clyde.collisionBox.colliderect(
                                collision
                            ) or self.clyde.collisionBox.colliderect(self.collisionHub):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.clyde.moveCollisionBox(-8, 0)
                    elif i == "Down":
                        self.clyde.moveCollisionBox(0, 8)
                        for collision in self.collisions:
                            if self.clyde.collisionBox.colliderect(
                                collision
                            ) or self.clyde.collisionBox.colliderect(self.collisionHub):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.clyde.moveCollisionBox(0, -8)
                    elif i == "Left":
                        self.clyde.moveCollisionBox(-8, 0)
                        for collision in self.collisions:
                            if self.clyde.collisionBox.colliderect(
                                collision
                            ) or self.clyde.collisionBox.colliderect(self.collisionHub):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.clyde.moveCollisionBox(8, 0)
                    elif i == "Up":
                        self.clyde.moveCollisionBox(0, -8)
                        for collision in self.collisions:
                            if self.clyde.collisionBox.colliderect(
                                collision
                            ) or self.clyde.collisionBox.colliderect(self.collisionHub):
                                # print("remove = ", i)
                                kill = True
                        if kill:
                            listValidMove.remove(i)
                        self.clyde.moveCollisionBox(0, 8)
                self.clydePossibleDirection = random.choice(listValidMove)

            elif (
                self.gameState == "Chase" or self.clyde.isScatter or self.clydeGoToHub
            ) and self.clydeCheck >= 8:
                self.clydeCheck = 0
                for i in self.clyde.okMovement:
                    plusPetit = True
                    if i == "Right":
                        self.clyde.moveCollisionBox(8, 0)
                        if self.clydeGoToHub:
                            self.clydeDistance = sqrt(
                                (self.clyde.collisionBox.x - 92) ** 2
                                + (self.clyde.collisionBox.y - 84) ** 2
                            )
                        elif self.clyde.isScatter:
                            self.clydeDistance = sqrt(
                                (self.clyde.collisionBox.x - self.clyde.basePoint[0])
                                ** 2
                                + (self.clyde.collisionBox.y - self.clyde.basePoint[1])
                                ** 2
                            )
                        else:
                            self.clydeDistance = sqrt(
                                (self.clyde.collisionBox.x - self.pacman.rect.x) ** 2
                                + (self.clyde.collisionBox.y - self.pacman.rect.y) ** 2
                            )
                        # pygame.draw.rect(self.screen, (255, 0, 0), self.clyde.collisionBox, 1)
                        # pygame.display.flip()
                        if self.clydeGoToHub:
                            for collision in self.collisions:
                                if self.clyde.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
                            for collision in self.collisions:
                                if self.clyde.collisionBox.colliderect(
                                    self.collisionHub
                                ) or self.clyde.collisionBox.colliderect(collision):
                                    plusPetit = False
                        if self.clydeGoToHub:
                            if self.clydeDistance <= min and plusPetit:
                                min = self.clydeDistance
                                self.clydePossibleDirection = "Right"
                        else:
                            if self.clydeDistance > 64:
                                if self.clydeDistance <= min and plusPetit:
                                    min = self.clydeDistance
                                    self.clydePossibleDirection = "Right"
                            else:
                                self.clydeDistance = sqrt(
                                    (
                                        self.clyde.collisionBox.x
                                        - self.clyde.basePoint[0]
                                    )
                                    ** 2
                                    + (
                                        self.clyde.collisionBox.y
                                        - self.clyde.basePoint[1]
                                    )
                                    ** 2
                                )
                                if self.clydeDistance <= min and plusPetit:
                                    min = self.clydeDistance
                                    self.clydePossibleDirection = "Right"
                        self.clyde.moveCollisionBox(-8, 0)
                    elif i == "Down":
                        self.clyde.moveCollisionBox(0, 8)
                        if self.clydeGoToHub:
                            self.clydeDistance = sqrt(
                                (self.clyde.collisionBox.x - 92) ** 2
                                + (self.clyde.collisionBox.y - 84) ** 2
                            )
                        elif self.clyde.isScatter:
                            self.clydeDistance = sqrt(
                                (self.clyde.collisionBox.x - self.clyde.basePoint[0])
                                ** 2
                                + (self.clyde.collisionBox.y - self.clyde.basePoint[1])
                                ** 2
                            )
                        else:
                            self.clydeDistance = sqrt(
                                (self.clyde.collisionBox.x - self.pacman.rect.x) ** 2
                                + (self.clyde.collisionBox.y - self.pacman.rect.y) ** 2
                            )
                        # pygame.draw.rect(self.screen, (255, 0, 0), self.clyde.collisionBox, 1)
                        # pygame.display.flip()
                        if self.clydeGoToHub:
                            for collision in self.collisions:
                                if self.clyde.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
                            for collision in self.collisions:
                                if self.clyde.collisionBox.colliderect(
                                    self.collisionHub
                                ) or self.clyde.collisionBox.colliderect(collision):
                                    plusPetit = False
                        if self.clydeGoToHub:
                            if self.clydeDistance <= min and plusPetit:
                                min = self.clydeDistance
                                self.clydePossibleDirection = "Down"
                        else:
                            if self.clydeDistance > 64:
                                if self.clydeDistance <= min and plusPetit:
                                    min = self.clydeDistance
                                    self.clydePossibleDirection = "Down"
                            else:
                                self.clydeDistance = sqrt(
                                    (
                                        self.clyde.collisionBox.x
                                        - self.clyde.basePoint[0]
                                    )
                                    ** 2
                                    + (
                                        self.clyde.collisionBox.y
                                        - self.clyde.basePoint[1]
                                    )
                                    ** 2
                                )
                                if self.clydeDistance <= min and plusPetit:
                                    min = self.clydeDistance
                                    self.clydePossibleDirection = "Down"
                        self.clyde.moveCollisionBox(0, -8)
                    elif i == "Left":
                        self.clyde.moveCollisionBox(-8, 0)
                        if self.clydeGoToHub:
                            self.clydeDistance = sqrt(
                                (self.clyde.collisionBox.x - 92) ** 2
                                + (self.clyde.collisionBox.y - 84) ** 2
                            )
                        elif self.clyde.isScatter:
                            self.clydeDistance = sqrt(
                                (self.clyde.collisionBox.x - self.clyde.basePoint[0])
                                ** 2
                                + (self.clyde.collisionBox.y - self.clyde.basePoint[1])
                                ** 2
                            )
                        else:
                            self.clydeDistance = sqrt(
                                (self.clyde.collisionBox.x - self.pacman.rect.x) ** 2
                                + (self.clyde.collisionBox.y - self.pacman.rect.y) ** 2
                            )
                        # pygame.draw.rect(self.screen, (255, 0, 0), self.clyde.collisionBox, 1)
                        # pygame.display.flip()
                        if self.clydeGoToHub:
                            for collision in self.collisions:
                                if self.clyde.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
                            for collision in self.collisions:
                                if self.clyde.collisionBox.colliderect(
                                    self.collisionHub
                                ) or self.clyde.collisionBox.colliderect(collision):
                                    plusPetit = False
                        if self.clydeGoToHub:
                            if self.clydeDistance <= min and plusPetit:
                                min = self.clydeDistance
                                self.clydePossibleDirection = "Left"
                        else:
                            if self.clydeDistance > 64:
                                if self.clydeDistance <= min and plusPetit:
                                    min = self.clydeDistance
                                    self.clydePossibleDirection = "Left"
                            else:
                                self.clydeDistance = sqrt(
                                    (
                                        self.clyde.collisionBox.x
                                        - self.clyde.basePoint[0]
                                    )
                                    ** 2
                                    + (
                                        self.clyde.collisionBox.y
                                        - self.clyde.basePoint[1]
                                    )
                                    ** 2
                                )
                                if self.clydeDistance <= min and plusPetit:
                                    min = self.clydeDistance
                                    self.clydePossibleDirection = "Left"
                        self.clyde.moveCollisionBox(8, 0)
                    elif i == "Up":
                        self.clyde.moveCollisionBox(0, -8)
                        if self.clydeGoToHub:
                            self.clydeDistance = sqrt(
                                (self.clyde.collisionBox.x - 92) ** 2
                                + (self.clyde.collisionBox.y - 84) ** 2
                            )
                        elif self.clyde.isScatter:
                            self.clydeDistance = sqrt(
                                (self.clyde.collisionBox.x - self.clyde.basePoint[0])
                                ** 2
                                + (self.clyde.collisionBox.y - self.clyde.basePoint[1])
                                ** 2
                            )
                        else:
                            self.clydeDistance = sqrt(
                                (self.clyde.collisionBox.x - self.pacman.rect.x) ** 2
                                + (self.clyde.collisionBox.y - self.pacman.rect.y) ** 2
                            )
                        # pygame.draw.rect(self.screen, (255, 0, 0), self.clyde.collisionBox, 1)
                        # pygame.display.flip()
                        if self.clydeGoToHub:
                            for collision in self.collisions:
                                if self.clyde.collisionBox.colliderect(collision):
                                    plusPetit = False
                        else:
                            for collision in self.collisions:
                                if self.clyde.collisionBox.colliderect(
                                    self.collisionHub
                                ) or self.clyde.collisionBox.colliderect(collision):
                                    plusPetit = False
                        if self.clydeGoToHub:
                            if self.clydeDistance <= min and plusPetit:
                                min = self.clydeDistance
                                self.clydePossibleDirection = "Up"
                        else:
                            if self.clydeDistance > 64:
                                if self.clydeDistance <= min and plusPetit:
                                    min = self.clydeDistance
                                    self.clydePossibleDirection = "Up"
                            else:
                                self.clydeDistance = sqrt(
                                    (
                                        self.clyde.collisionBox.x
                                        - self.clyde.basePoint[0]
                                    )
                                    ** 2
                                    + (
                                        self.clyde.collisionBox.y
                                        - self.clyde.basePoint[1]
                                    )
                                    ** 2
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

            if self.clydeLife >= 0:
                if self.clydePossibleDirection == "Right":
                    if self.clyde.collisionBox.colliderect(self.ghostCollisionRight):
                        self.clyde.setPos(-19, 108)
                    self.clyde.move(1, 0)
                    self.clyde.okMovement = (
                        self.clyde.allMovement.copy()[0:2]
                        + self.clyde.allMovement.copy()[3:4]
                    )
                elif self.clydePossibleDirection == "Down":
                    self.clyde.move(0, 1)
                    self.clyde.okMovement = self.clyde.allMovement.copy()[:3]
                elif self.clydePossibleDirection == "Left":
                    if self.clyde.collisionBox.colliderect(self.ghostCollisionLeft):
                        self.clyde.setPos(227, 108)
                    self.clyde.move(-1, 0)
                    self.clyde.okMovement = self.clyde.allMovement.copy()[1:]
                elif self.clydePossibleDirection == "Up":
                    self.clyde.move(0, -1)
                    self.clyde.okMovement = (
                        self.clyde.allMovement.copy()[0:1]
                        + self.clyde.allMovement.copy()[2:4]
                    )

            if (
                self.clyde.rect.x == 92
                and self.clyde.rect.y == 84
                and self.clydeGoToHub
            ):
                self.clydeGoToHub = False
                self.clyde.setPos(92, 83)
                self.clydeLife = 0
                self.clydeCheck = 0
                self.clydePossibleDirection = "Up"
                self.clydeFright = False
                self.clyde.isScatter = True

    def updateScreen(self):
        # for layer in self.map.visible_layers:
        #     if layer.name == "Background":
        #         for x, y, gid in layer:
        #             tile = self.map.get_tile_image_by_gid(gid)
        #             self.screen.blit(
        #                 tile, (x * self.map.tilewidth, y * self.map.tileheight)
        #             )

        # pygame.draw.rect(self.screen, (255, 0, 0), self.CollisionBox, 1)
        # print(self.blinky.rect.x, self.blinky.rect.y)
        # print(self.blinky.collisionBox.x, self.blinky.collisionBox.y)
        if self.pacmanLife % 5 == 0:
            self.pacman.image = self.pacman.animation(self.pacmanWay)[
                self.pacmanLife % 3
            ]
            self.screen.blit(
                self.pacman.animation(self.pacmanWay)[self.pacmanLife % 3],
                self.pacman.getPos(),
            )

        if self.gameState == "Chase":
            self.blinky.image = self.blinky.animationNotFright(
                self.blinkyPossibleDirection
            )[self.blinkyLife % 2]
            self.pinky.image = self.pinky.imageBackup
            self.inky.image = self.inky.imageBackup
            self.clyde.image = self.clyde.imageBackup

            # pygame.draw.rect(self.screen, (255, 0, 0), self.blinky.rect, 1)
            self.screen.blit(self.blinky.image, self.blinky.getPos())

            # pygame.draw.rect(self.screen, (188, 0, 255), self.pinky.rect, 1)
            self.screen.blit(self.pinky.image, self.pinky.getPos())

            # pygame.draw.rect(self.screen, (0, 255, 255), self.inky.rect, 1)
            self.screen.blit(self.inky.image, self.inky.getPos())

            # pygame.draw.rect(self.screen, (255, 200, 255), self.clyde.rect, 1)
            self.screen.blit(self.clyde.image, self.clyde.getPos())
        elif self.gameState == "Fright":
            if self.timeFright <= 180:
                if self.blinky.bugCounter >= 30:
                    self.blinky.bug = not self.blinky.bug
                    self.blinky.bugCounter = 0
                if self.blinky.bug:
                    self.blinky.image = self.blinky.frameFrightBug[self.blinkyLife % 2]
                else:
                    self.blinky.image = self.blinky.frameFright[self.blinkyLife % 2]

                if self.pinky.bugCounter >= 30:
                    self.pinky.bug = not self.pinky.bug
                    self.pinky.bugCounter = 0
                if self.pinky.bug:
                    self.pinky.image = self.pinky.frameFrightBug[self.pinkyLife % 2]
                else:
                    self.pinky.image = self.pinky.frameFright[self.pinkyLife % 2]

                if self.inky.bugCounter >= 30:
                    self.inky.bug = not self.inky.bug
                    self.inky.bugCounter = 0
                if self.inky.bug:
                    self.inky.image = self.inky.frameFrightBug[self.inkyLife % 2]
                else:
                    self.inky.image = self.inky.frameFright[self.inkyLife % 2]

                if self.clyde.bugCounter >= 30:
                    self.clyde.bug = not self.clyde.bug
                    self.clyde.bugCounter = 0
                if self.clyde.bug:
                    self.clyde.image = self.clyde.frameFrightBug[self.clydeLife % 2]
                else:
                    self.clyde.image = self.clyde.frameFright[self.clydeLife % 2]
            else:
                self.blinky.image = self.blinky.frameFright[self.blinkyLife % 2]
                self.pinky.image = self.imageFright
                self.inky.image = self.imageFright
                self.clyde.image = self.imageFright

            # pygame.draw.rect(self.screen, (0, 255, 255), self.blinky.rect, 1)
            self.screen.blit(self.imageFright, self.blinky.getPos())

            # pygame.draw.rect(self.screen, (0, 255, 255), self.pinky.rect, 1)
            self.screen.blit(self.imageFright, self.pinky.getPos())

            # pygame.draw.rect(self.screen, (0, 255, 255), self.inky.rect, 1)
            self.screen.blit(self.imageFright, self.inky.getPos())

            # pygame.draw.rect(self.screen, (0, 255, 255), self.clyde.rect, 1)
            self.screen.blit(self.imageFright, self.clyde.getPos())

        if self.blinky.isScatter:
            self.blinky.image = self.blinky.animationNotFright(
                self.blinkyPossibleDirection
            )[self.blinkyLife % 2]
        if self.blinkyGoToHub:
            self.blinky.image = self.imageGoToHub

        if self.pinky.isScatter:
            self.pinky.image = self.pinky.imageBackup
        if self.pinkyGoToHub:
            self.pinky.image = self.imageGoToHub

        if self.inky.isScatter:
            self.inky.image = self.inky.imageBackup
        if self.inkyGoToHub:
            self.inky.image = self.imageGoToHub

        if self.clyde.isScatter:
            self.clyde.image = self.clyde.imageBackup
        if self.clydeGoToHub:
            self.clyde.image = self.imageGoToHub

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

        self.group.update()
        self.group.draw(self.screen)

        textScore = self.font.render(str(self.score), True, (255, 255, 255))
        self.screen.blit(textScore, (500, 750))
        if self.numberLife == 3:
            self.screen.blit(self.imageLife, (64, 750))
            self.screen.blit(self.imageLife, (148, 750))
        elif self.numberLife == 2:
            self.screen.blit(self.imageLife, (148, 750))

        pygame.display.flip()
        pygame.display.update()

    def intro(self):
        pygame.mixer.Sound.play(self.introSound)
        self.updateScreen()
        sleep(3.5)
        self.run()

    def run(self) -> None:
        pygame.mixer.Sound.play(self.sirenGhost1, -1)
        self.sirenPlaying = True
        while self.running:
            print(self.numberLife)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.input()
            self.addScore()
            self.setState()

            self.checkSpriteCollision()

            self.blinkyMovement()
            self.pinkyMovement()
            self.inkyMovement()
            self.clydeMovement()

            self.pacmanCheck += 1

            self.pacmanLife += 1
            self.blinkyLife += 1
            self.pinkyLife += 1
            self.inkyLife += 1
            self.clydeLife += 1

            self.blinkyCheck += 1
            self.pinkyCheck += 1
            self.inkyCheck += 1
            self.clydeCheck += 1

            self.blinky.bugCounter += 1
            self.pinky.bugCounter += 1
            self.inky.bugCounter += 1
            self.clyde.bugCounter += 1

            if (
                not self.ghostFrightSoundPlaying
                and self.gameState == "Fright"
                and not self.ghostGoToHubSoundPlaying
            ):
                self.ghostFrightSoundPlaying = True
                self.ghostGoToHubSoundPlaying = False
                self.sirenPlaying = False
                pygame.mixer.Sound.stop(self.sirenGhost1)
                pygame.mixer.Sound.stop(self.ghostGoToHubSound)
                pygame.mixer.Sound.play(self.powerPelletSound, -1)

            if (
                self.blinkyGoToHub
                or self.pinkyGoToHub
                or self.inkyGoToHub
                or self.clydeGoToHub
            ) and not self.ghostGoToHubSoundPlaying:
                self.ghostFrightSoundPlaying = False
                self.ghostGoToHubSoundPlaying = True
                self.sirenPlaying = False
                pygame.mixer.Sound.stop(self.sirenGhost1)
                pygame.mixer.Sound.stop(self.powerPelletSound)
                pygame.mixer.Sound.play(self.ghostGoToHubSound, -1)

            if not (
                self.blinkyGoToHub
                or self.pinkyGoToHub
                or self.inkyGoToHub
                or self.clydeGoToHub
            ):
                self.ghostGoToHubSoundPlaying = False

            if self.timeFright == 0 and not self.sirenPlaying:
                self.ghostFrightSoundPlaying = False
                self.ghostGoToHubSoundPlaying = False
                self.sirenPlaying = True
                pygame.mixer.Sound.stop(self.ghostGoToHubSound)
                pygame.mixer.Sound.stop(self.powerPelletSound)
                pygame.mixer.Sound.play(self.sirenGhost1, -1)

            if self.numberLife <= 0:
                self.running = False

            if self.blinkyLife >= 420:
                self.blinky.isScatter = False
            if self.pinkyLife >= 420:
                self.pinky.isScatter = False
            if self.inkyLife >= 420:
                self.inky.isScatter = False
            if self.clydeLife >= 420:
                self.clyde.isScatter = False

            if self.timeFright == 0:
                self.gameState = "Chase"
                self.blinkyFright = False
                self.pinkyFright = False
                self.inkyFright = False
                self.clydeFright = False
                self.blinky.firstFright = True
                self.pinky.firstFright = True
                self.inky.firstFright = True
                self.clyde.firstFright = True
            else:
                self.timeFright -= 1

            if self.gommes == []:
                self.endLevel()
                self.running = False

            self.updateScreen()
            self.clock.tick(30)

    def runAfterDeath(self):
        pygame.mixer.Sound.stop(self.sirenGhost1)
        pygame.mixer.Sound.stop(self.powerPelletSound)
        pygame.mixer.Sound.stop(self.ghostGoToHubSound)
        self.ghostFrightSoundPlaying = False
        self.ghostGoToHubSoundPlaying = False
        pygame.mixer.Sound.stop(self.sirenGhost1)
        pygame.mixer.Sound.play(self.deathSound)
        while self.runDeath:
            print(self.numberLife)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.runDeath = False

            self.group.remove(self.blinky)
            self.group.remove(self.pinky)
            self.group.remove(self.inky)
            self.group.remove(self.clyde)
            self.group.update()
            self.group.draw(self.screen)

            textScore = self.font.render(str(self.score), True, (255, 255, 255))
            self.screen.blit(textScore, (500, 750))
            if self.numberLife == 3:
                self.screen.blit(self.imageLife, (64, 750))
                self.screen.blit(self.imageLife, (148, 750))
            elif self.numberLife == 2:
                self.screen.blit(self.imageLife, (148, 750))

            pygame.display.flip()
            pygame.display.update()

            if self.deathAnim <= 11:
                self.pacman.image = self.pacman.frameDeath[self.deathAnim]

            if self.deathTime % 10 == 0:
                self.deathAnim += 1

            if self.deathTime == 120 and self.numberLife > 0:
                self.deathAnim = 0
                self.deathTime = 0
                self.runDeath = False
                self.running = True
                self.deathTime = 0
                self.pacman.setPos(104, 180)
                self.CollisionBox.x, self.CollisionBox.y = (
                    self.pacman.rect.x,
                    self.pacman.rect.y,
                )
                self.scoreBox.x, self.scoreBox.y = (
                    self.pacman.rect.x + 4,
                    self.pacman.rect.y + 4,
                )
                self.pacmanSpeed = 2
                self.pacmanLife = 0
                self.pacmanWay = "Right"
                self.pacmanLastWay = "Right"
                self.pacmanCheck = 0

                self.pinkyDirectionAddition = (32, 0)
                self.inkyDirectionAddition = (16, 0)

                self.blinky.setPos(104, 84)
                self.blinkyLife = 0
                self.blinkyCheck = 0
                self.blinkyGoToHub = False
                self.blinkyFright = False
                self.blinkyPossibleDirection = "Up"
                self.blinky.isScatter = True
                self.blinky.firstFright = True
                self.blinky.bug = False
                self.blinky.bugCounter = 0
                self.blinky.okMovement = ["Right", "Left", "Up"]

                self.pinky.setPos(104, 108)
                self.pinkyLife = 0
                self.pinkyCheck = 0
                self.pinkyGoToHub = False
                self.pinkyFright = False
                self.pinkyPossibleDirection = "Up"
                self.pinky.isScatter = True
                self.pinky.firstFright = True
                self.pinky.bug = False
                self.pinky.bugCounter = 0
                self.pinky.okMovement = ["Right", "Left", "Up"]

                self.inky.setPos(88, 108)
                self.inkyLife = 0
                self.inkyCheck = 0
                self.inkyGoToHub = False
                self.inkyFright = False
                self.inkyPossibleDirection = "Right"
                self.inky.isScatter = True
                self.inky.firstFright = True
                self.inky.bug = False
                self.inky.bugCounter = 0
                self.inky.okMovement = ["Right", "Left", "Up"]

                self.clyde.setPos(120, 108)
                self.clydeLife = 0
                self.clydeCheck = 0
                self.clydeGoToHub = False
                self.clydeFright = False
                self.clydePossibleDirection = "Right"
                self.clyde.isScatter = True
                self.clyde.firstFright = True
                self.clyde.bug = False
                self.clyde.bugCounter = 0
                self.clyde.okMovement = ["Right", "Left", "Up"]

                self.group.add(self.blinky)
                self.group.add(self.pinky)
                self.group.add(self.inky)
                self.group.add(self.clyde)
                self.group.add(self.pacman)
                self.group.update()
                self.group.draw(self.screen)
                pygame.display.flip()
                self.intro()
            elif self.deathTime == 120 and self.numberLife <= 0:
                self.runDeath = False
                self.run = False

            self.deathTime += 1

            self.clock.tick(60)

    def endLevel(self):
        pygame.mixer.Sound.stop(self.sirenGhost1)
        pygame.mixer.Sound.stop(self.powerPelletSound)
        pygame.mixer.Sound.stop(self.ghostGoToHubSound)
        pygame.mixer.Sound.play(self.endLevelSound)
        self.group.remove(self.blinky)
        self.group.update()
        self.group.remove(self.pinky)
        self.group.update()
        self.group.remove(self.inky)
        self.group.update()
        self.group.remove(self.clyde)
        self.group.update()
        self.group.draw(self.screen)
        pygame.display.update()
        sleep(5)


if __name__ == "__main__":
    game = Game()
    game.intro()

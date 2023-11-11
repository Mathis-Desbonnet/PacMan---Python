import pygame
import pytmx
from player import Pacman
from item import Gomme
from blinky import Blinky

pygame.init()

class Game():
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((224, 248))
        self.clock = pygame.time.Clock()

        self.map = pytmx.load_pygame("./data/Map.tmx")
        self.tmx_data = pytmx.util_pygame.load_pygame("./data/Map.tmx")
        self.background = self.map.layers[0]

        self.pacman = Pacman()
        self.blinky = Blinky(x=104, y=108)

        self.blinkyLife = 0
        self.blinkyPossibleDirection = "Up"

        self.CollisionBox = pygame.Rect(self.pacman.rect.x, self.pacman.rect.y, 16, 16)
        self.scoreBox = pygame.Rect(self.pacman.rect.x+4, self.pacman.rect.y+4, 8, 8)
        self.running = True
        self.score = 0

        self.collisions = []
        self.collisionHub = None
        self.collisionTp = []
        self.gommeSpawn = []

        for obj in self.tmx_data.objects:
            if obj.type == "collision":
                self.collisions.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "collisionHub":
                self.collisionHub = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            elif obj.type == "collisionTPRight":
                self.collisionTp.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "collisionTPLeft":
                self.collisionTp.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "gomme":
                self.gommeSpawn.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        self.gommes = []

        for gomme in self.gommeSpawn:
            self.gommes.append(Gomme(x=gomme.x, y=gomme.y))

    def checkCollision(self):
        ifCollision = False
        for collision in self.collisions:
                if self.CollisionBox.colliderect(collision) or self.CollisionBox.colliderect(self.collisionHub):
                    ifCollision = True
        
        return ifCollision
    
    def checkTp(self, x, y, xCollision):
        for collision in self.collisionTp:
            if self.CollisionBox.colliderect(collision):
                self.pacman.setPos(x, y)
                self.CollisionBox.x = xCollision
                self.CollisionBox.y = y
                self.scoreBox.x = x+4
                self.scoreBox.y = y+4

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_z]:
            self.CollisionBox.y -= 8
            if not self.checkCollision():
                self.pacman.move(0, -8)
                self.scoreBox.y -= 8
            else:
                self.CollisionBox.y += 8

        if keys[pygame.K_q]:
            self.CollisionBox.x -= 8
            self.checkTp(228, 108, 220)
            if not self.checkCollision():
                self.pacman.move(-8, 0)
                self.scoreBox.x -= 8
            else:
                self.CollisionBox.x += 8

        if keys[pygame.K_s]:
            self.CollisionBox.y += 8
            if not self.checkCollision():
                self.pacman.move(0, 8)
                self.scoreBox.y += 8
            else:
                self.CollisionBox.y -= 8

        if keys[pygame.K_d]:
            self.CollisionBox.x += 8
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
                    if gommeOnScreen.rect.x == gomme.x and gommeOnScreen.rect.y == gomme.y:
                        self.gommes.remove(gommeOnScreen)
                        self.score += gommeOnScreen.score

    def updateScreen(self):
        for layer in self.map.visible_layers:
                if layer.name == "Background":
                    for x, y, gid in layer:
                        tile = self.map.get_tile_image_by_gid(gid)
                        self.screen.blit(tile, (x * self.map.tilewidth, y * self.map.tileheight))
        
        
        pygame.draw.rect(self.screen, (255, 0, 0), self.CollisionBox, 1)
        pygame.draw.rect(self.screen, (0, 255, 0), self.scoreBox, 1)
        self.screen.blit(self.pacman.image, self.pacman.getPos())

        pygame.draw.rect(self.screen, (0, 0, 255), self.blinky.rect, 1)
        self.screen.blit(self.blinky.image, self.blinky.getPos())


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

            if self.blinkyLife <= 2:
                self.blinky.move(0, 8)
                self.blinkyLife += 1
            else:
                for i in self.blinky.okMovement:
                    if i == "Left":
                        self.blinky.moveCollisionBox(0, -8)
                        self.blinkyRelativePos = (self.blinky.collisionBox.x - self.pacman.rect.x, self.blinky.collisionBox.y - self.pacman.rect.y)


            print(self.score)
                    
            self.clock.tick(10)

if __name__ == "__main__":
    game = Game()
    game.run(True)
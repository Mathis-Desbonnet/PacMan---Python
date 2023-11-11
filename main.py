import pygame
import pytmx
from player import Pacman
from item import Gomme

pygame.init()

class Game():
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((224, 248))
        self.clock = pygame.time.Clock()

        self.map = pytmx.load_pygame("./data/Map.tmx")
        self.tmx_data = pytmx.util_pygame.load_pygame("./data/Map.tmx")
        self.background = self.map.layers[0]

        self.pacman = Pacman()
        self.CollisionBox = pygame.Rect(108, 132, 16, 16)
        self.running = True

        self.collisions = []
        self.collisionTp = []
        self.gommeSpawn = []

        for obj in self.tmx_data.objects:
            if obj.type == "collision":
                self.collisions.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
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
                if self.CollisionBox.colliderect(collision):
                    ifCollision = True
        
        return ifCollision
    
    def checkTp(self, x, y, xCollision):
        for collision in self.collisionTp:
            if self.CollisionBox.colliderect(collision):
                self.pacman.setPos(x, y)
                self.CollisionBox.x = xCollision
                self.CollisionBox.y = y

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_z]:
            self.CollisionBox.y -= 8
            if not self.checkCollision():
                self.pacman.move(0, -8)
            else:
                self.CollisionBox.y += 8

        if keys[pygame.K_q]:
            self.CollisionBox.x -= 8
            self.checkTp(228, 108, 220)
            if not self.checkCollision():
                self.pacman.move(-8, 0)
            else:
                self.CollisionBox.x += 8

        if keys[pygame.K_s]:
            self.CollisionBox.y += 8
            if not self.checkCollision():
                self.pacman.move(0, 8)
            else:
                self.CollisionBox.y -= 8

        if keys[pygame.K_d]:
            self.CollisionBox.x += 8
            self.checkTp(-20, 108, -12)
            if not self.checkCollision():
                self.pacman.move(8, 0)
            else:
                self.CollisionBox.x -= 8

    def updateScreen(self):
        for layer in self.map.visible_layers:
                if layer.name == "Background":
                    for x, y, gid in layer:
                        tile = self.map.get_tile_image_by_gid(gid)
                        self.screen.blit(tile, (x * self.map.tilewidth, y * self.map.tileheight))
        
        
        pygame.draw.rect(self.screen, (255, 0, 0), self.CollisionBox, 1)
        self.screen.blit(self.pacman.image, self.pacman.getPos())

        for gomme in self.gommes:
            self.screen.blit(gomme.image, (gomme.rect.x, gomme.rect.y))

        pygame.display.update()

    def run(self, running) -> None:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.input()
            self.updateScreen()
                    
            self.clock.tick(10)

if __name__ == "__main__":
    game = Game()
    game.run(True)
from time import sleep
import pygame
import pytmx, pyscroll

pygame.init()
screen = pygame.display.set_mode((224, 248))
clock = pygame.time.Clock()

map = pytmx.load_pygame("Map.tmx")
background = map.layers[0]

tmx_data = pytmx.util_pygame.load_pygame("Map.tmx")

pacman = pygame.sprite.Sprite()
pacman.image = pygame.image.load("PacManSprites.png").convert_alpha().subsurface((18, 0, 16, 16))
pacman.rect = pacman.image.get_rect()
pacmanDeplacement = pacman.rect.copy()
pacmanDeplacement.x = 108
pacmanDeplacement.y = 132
CollisionBox = pygame.Rect(108, 132, 16, 16)
pacmanCollision = pygame.sprite.Sprite().rect = CollisionBox
running = True

collisions = []
collisionTp = []

for obj in tmx_data.objects:
    if obj.type == "collision":
        collisions.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
    elif obj.type == "collisionTPRight":
        collisionTp.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
    elif obj.type == "collisionTPLeft":
        collisionTp.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for layer in map.visible_layers:
        if layer.name == "Background":
            for x, y, gid in layer:
                tile = map.get_tile_image_by_gid(gid)
                screen.blit(tile, (x * map.tilewidth, y * map.tileheight))
    

    keys = pygame.key.get_pressed()

    ifCollision = False

    if keys[pygame.K_z]:
        CollisionBox.y -= 8
        for collision in collisions:
            if CollisionBox.colliderect(collision):
                ifCollision = True
        if not ifCollision:
            pacmanDeplacement.y -= 8
        else:
            CollisionBox.y += 8
    if keys[pygame.K_q]:
        CollisionBox.x -= 8
        for collision in collisions:
            if CollisionBox.colliderect(collision):
                ifCollision = True
        for collision in collisionTp:
            if CollisionBox.colliderect(collision):
                pacmanDeplacement.x = 228
                pacmanDeplacement.y = 108
                CollisionBox.x = 220
                CollisionBox.y = 108
        if not ifCollision:
            pacmanDeplacement.x -= 8
        else:
            CollisionBox.x += 8
    if keys[pygame.K_s]:
        CollisionBox.y += 8
        for collision in collisions:
            if CollisionBox.colliderect(collision):
                ifCollision = True
        if not ifCollision:
            pacmanDeplacement.y += 8
        else:
            CollisionBox.y -= 8
    if keys[pygame.K_d]:
        CollisionBox.x += 8
        for collision in collisions:
            if CollisionBox.colliderect(collision):
                ifCollision = True
        for collision in collisionTp:
            if CollisionBox.colliderect(collision):
                pacmanDeplacement.x = -20
                pacmanDeplacement.y = 108
                CollisionBox.x = -12
                CollisionBox.y = 108
        if not ifCollision:
            pacmanDeplacement.x += 8
        else:
            CollisionBox.x -= 8
            
    pygame.draw.rect(screen, (255, 0, 0), CollisionBox, 1)
    screen.blit(pacman.image, (pacmanDeplacement.x, pacmanDeplacement.y))

    pygame.display.update()
    clock.tick(10)

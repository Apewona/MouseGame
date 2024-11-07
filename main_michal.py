import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

original_image = pygame.image.load('./img_mouse/mouse.png')
player_image = original_image
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
angle = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("purple")

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
        angle = 0
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
        angle = 180
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
        angle = 90
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt
        angle = -90
    
    #Limit do krawędzi
    player_pos.x = max(20, min(player_pos.x, screen.get_width()-20))
    player_pos.y = max(20, min(player_pos.y, screen.get_height()-20))

    #Obracanie gracza
    player_image = pygame.transform.rotate(original_image, angle)
    player_rect = player_image.get_rect(center=player_pos)

    screen.blit(player_image, player_rect.topleft)

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
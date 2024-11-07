import pygame
import math

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

# Player setup
speed = 300
player_body = pygame.image.load('./img_mouse/mouse.png')
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
player_angle = 0  # to store the rotation angle of the player

# Rotate player based on movement direction
def rotate_player(direction):
    global player_angle
    if direction.length() > 0:
        player_angle = -math.degrees(math.atan2(-direction.y, direction.x))
    rotated_player = pygame.transform.rotate(player_body, player_angle)
    return rotated_player, rotated_player.get_rect(center=player_pos)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with a background color
    screen.fill("purple")

    # Get key inputs and set direction
    keys = pygame.key.get_pressed()
    direction = pygame.Vector2(0, 0)
    if keys[pygame.K_w]: direction.y = -1
    if keys[pygame.K_s]: direction.y = 1
    if keys[pygame.K_a]: direction.x = -1
    if keys[pygame.K_d]: direction.x = 1
    
    if direction.length() > 0:
        direction = direction.normalize()  # Ensures consistent speed in all directions
        player_pos += direction * speed * dt

    # Rotate player and draw on screen
    rotated_player, rotated_rect = rotate_player(direction)
    screen.blit(rotated_player, rotated_rect.topleft)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()

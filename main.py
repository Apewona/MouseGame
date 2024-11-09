import pygame
import math
import random

from classes import Mouseai, Cheese
from functions import draw_grid, display_text


# pygame setup
pygame.init()


# Screen display width and height and method
screen = pygame.display.set_mode((1280, 720))


# Initialize game global clock
clock = pygame.time.Clock()
running = True
dt = 0


# Specify fonts in game
font = pygame.font.SysFont("Arial", 12)



# Initialize player (mouse) instance
player = Mouseai('./img_mouse/mouse.png', (screen.get_width() / 2, screen.get_height() / 2), 300)

# Initialize random cheese initial position
pos = pygame.Vector2()
pos.x = random.randrange(screen.get_width()-0)
pos.y = random.randrange(screen.get_height()-0)

ch = Cheese('./img_mouse/cheese.png',pos)
tile_size = 20
# MAIN PROGRAM LOOP
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with a background color
    screen.fill("purple")

    #
    least_neighbour = draw_grid(screen, tile_size, player.position, ch.position)

    print(f"{least_neighbour}")

    if least_neighbour:
        # Jeśli znaleziono najmniejszego sąsiada, ustawiamy cel na ten węzeł
        target = pygame.Vector2(least_neighbour.x * tile_size, least_neighbour.y * tile_size)
    else:
        target = pygame.mouse.get_pos()


    # Update and draw player
    keys = pygame.key.get_pressed()

    # player update
    player.update_and_draw(dt, target, screen) 

    # Cheese update
    ch.draw(screen)

    if player.get_rect().colliderect(ch.get_rect()):
        ch.relocate(screen) 
        player.hunger_upgrade()
        player.cheeseclock_reset()
    

    # Display stats
    display_text(player.get_position(), (10, 15), font, screen)
    display_text(player.get_hunger(), (10,30), font, screen)
    display_text(player.get_lifetime(), (10,45), font, screen)
    display_text(player.get_cheesedist(), (10,60), font, screen)
    display_text(player.get_cheeseclock(), (10,75), font, screen)

    # End looopp
    pygame.display.flip()
    dt = clock.tick(60) / 1000.0


pygame.quit()

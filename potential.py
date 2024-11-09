import pygame
import math
import random
import heapq

from Mouse_AI import Mouseai
from cheese import Cheese

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

font = pygame.font.SysFont("Arial", 12)


def display_text(text, position):
    text_surface = font.render(text, True, (0, 0, 0))  # White color
    screen.blit(text_surface, position)

# Ogólnie tu jest problem, że w siatce chodzi o węzły, a nie środek tila. 
def draw_grid(screen, tile_size, position, cheese_position):
    current_tile_pos = pygame.Vector2()
    current_tile = pygame.Vector2()
    max_distance = math.hypot(screen.get_width(), screen.get_height())
    num_columns = screen.get_width() // tile_size
    num_rows = screen.get_height() // tile_size
    tile_heuristic = [[0 for _ in range(num_rows)] for _ in range(num_columns)]

    # Rysowanie siatki
    for x in range(0, screen.get_width(), tile_size):
        for y in range(0, screen.get_height(), tile_size):
            rect = pygame.Rect(x, y, tile_size, tile_size)
            
            if rect.collidepoint(position):
                pygame.draw.rect(screen, (255, 0, 0), rect)  # Czerwony dla gracza
                current_tile_pos.x = x 
                current_tile_pos.y = y  
                current_tile.x = int(x // tile_size)
                current_tile.y = int(y // tile_size)
            else:
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)  # Szary dla innych

    # Ustawienie heurystyki
    for x in range(0, screen.get_width(), tile_size):
        for y in range(0, screen.get_height(), tile_size):
            rect = pygame.Rect(x, y, tile_size, tile_size)
            tile_pos = pygame.Vector2(x, y)
            
            player_distance = current_tile_pos.distance_to(tile_pos)
            cheese_distance = pygame.Vector2(cheese_position).distance_to(tile_pos)
            tile_heuristic_x = int(x // tile_size)
            tile_heuristic_y = int(y // tile_size)
            tile_heuristic[tile_heuristic_x][tile_heuristic_y] = abs(player_distance) + abs(cheese_distance)
            
            heuristic_intensity = max(0, min(255, int((1 - tile_heuristic[tile_heuristic_x][tile_heuristic_y] / max_distance) * 255)))

            pygame.draw.rect(screen, (0, heuristic_intensity, 255-heuristic_intensity), rect)  # Green for low intensity


    least_neighbour = find_least_neighbour(current_tile, tile_heuristic)
    return least_neighbour
    

def find_least_neighbour(current, tile_heuristic):
    least = pygame.Vector2()
    neighbours = []

    # Convert current to tuple to make it hashable
    current_tuple = (current.x, current.y)

    if current.y > 0:
        neighbours.append((int(current.x), int(current.y - 1), tile_heuristic[int(current.x)][int(current.y - 1)]))
    if current.y < len(tile_heuristic[0]) - 1:
        neighbours.append((int(current.x), int(current.y + 1), tile_heuristic[int(current.x)][int(current.y + 1)]))
    if current.x > 0:
        neighbours.append((int(current.x - 1), int(current.y), tile_heuristic[int(current.x - 1)][int(current.y)]))
    if current.x < len(tile_heuristic) - 1:
        neighbours.append((int(current.x + 1), int(current.y), tile_heuristic[int(current.x + 1)][int(current.y)]))

    if current.x > 0 and current.y > 0:
        neighbours.append((int(current.x - 1), int(current.y - 1), tile_heuristic[int(current.x - 1)][int(current.y - 1)]))
    if current.x > 0 and current.y < len(tile_heuristic[0]) - 1:
        neighbours.append((int(current.x - 1), int(current.y + 1), tile_heuristic[int(current.x - 1)][int(current.y + 1)]))
    if current.x < len(tile_heuristic) - 1 and current.y > 0:
        neighbours.append((int(current.x + 1), int(current.y - 1), tile_heuristic[int(current.x + 1)][int(current.y - 1)]))
    if current.x < len(tile_heuristic) - 1 and current.y < len(tile_heuristic[0]) - 1:
        neighbours.append((int(current.x + 1), int(current.y + 1), tile_heuristic[int(current.x + 1)][int(current.y + 1)]))

    if neighbours:
        least_neighbour = min(neighbours, key=lambda x: x[2]) 
        least.x = least_neighbour[0]
        least.y = least_neighbour[1]
        return least
    
    return None





# Initialize player (mouse) instance
player = Mouseai('./img_mouse/mouse.png', (screen.get_width() / 2, screen.get_height() / 2), 300)

pos = pygame.Vector2()
pos.x = random.randrange(screen.get_width()-0)
pos.y = random.randrange(screen.get_height()-0)

ch = Cheese('./img_mouse/cheese.png',pos)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with a background color
    screen.fill("purple")
    #least_neighbour = draw_grid(screen, 40, player.position,ch.position)
    least_neighbour = draw_grid(screen, 10, player.position, ch.position)
    print(f"{least_neighbour}")
    if least_neighbour:
        # Jeśli znaleziono najmniejszego sąsiada, ustawiamy cel na ten węzeł
        target = pygame.Vector2(least_neighbour.x * 10, least_neighbour.y * 10)
    else:
        target = pygame.mouse.get_pos()
    # Update and draw player
    keys = pygame.key.get_pressed()

    player.update_and_draw(dt, target, screen)





    ch.draw(screen)

    player.player_cheese_dist(ch.position)

    if player.get_rect().colliderect(ch.get_rect()):
        ch.relocate() 
        player.hunger_upgrade()
        player.cheeseclock_reset()
    

    # Display player position in the top-left corner
    display_text(player.get_position(), (10, 15))
    display_text(player.get_hunger(), (10,30))
    display_text(player.get_lifetime(), (10,45))
    display_text(player.get_cheesedist(), (10,60))
    display_text(player.get_cheeseclock(), (10,75))
    pygame.display.flip()
    dt = clock.tick(60) / 1000.0

pygame.quit()

import pygame
import math
import random

## co dodałem? można rysować przeszkody w postaci kresek, które mysz może troche nie udolnie omija ale omija


# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

font = pygame.font.SysFont("Arial", 12)

class Obstacle:
    def __init__(self):
        self.lines = []  # Stores each obstacle as a start and end point

    def add_line(self, start_pos, end_pos):
        self.lines.append((start_pos, end_pos))

    def draw(self, screen):
        # Draw each line in the obstacle list
        for line in self.lines:
            pygame.draw.line(screen, (0, 0, 0), line[0], line[1], 20)  # Black color, thickness 5

    def check_collision(self, mouse_rect, extension=0):
        # Expand the rectangle to account for the extension
        mouse_rect.inflate_ip(extension, extension)
        
        for line in self.lines:
            if self.line_intersects(mouse_rect.topleft, mouse_rect.topright, line[0], line[1]) or \
               self.line_intersects(mouse_rect.topleft, mouse_rect.bottomleft, line[0], line[1]) or \
               self.line_intersects(mouse_rect.topright, mouse_rect.bottomright, line[0], line[1]) or \
               self.line_intersects(mouse_rect.bottomleft, mouse_rect.bottomright, line[0], line[1]):
                return True
        return False

    @staticmethod
    def line_intersects(p1, p2, q1, q2):
        """ Helper function to check if two line segments (p1-p2 and q1-q2) intersect """
        def ccw(a, b, c):
            return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

        return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)
        
class Mouse:
    def __init__(self, image_path, pos, speed):
        self.image = pygame.image.load(image_path)
        self.position = pygame.Vector2(pos)
        self.speed = speed
        self.angle = 0
        self.hunger = 100
        self.lifetime = 0 
        self.cheesedist = 0
        self.cheeseclock = 0
        self.is_turning_around = False

    def update(self, dt, cheese_pos, obstacles):
        if not self.is_turning_around:
            direction = pygame.Vector2(cheese_pos - self.position)

            if direction.length() > 0:
                direction = direction.normalize()
                next_position = self.position + direction * self.speed * dt
                
                # Sprawdzamy kolizję z przeszkodami
                mouse_rect = self.get_rect()
                if obstacles.check_collision(mouse_rect, extension=20):  # Dodajemy rozszerzenie
                    print("Obiekt wykryty! Zawracam...")
                    self.is_turning_around = True  # Włączamy tryb omijania przeszkody
                    self.angle += 90  # Obracamy o 90 stopni

                else:
                    self.position = next_position
                    self.angle = math.degrees(math.atan2(-direction.y, direction.x))
        else:
            # Mysz jest w trybie omijania przeszkody
            movement_direction = pygame.Vector2(math.cos(math.radians(self.angle)), -math.sin(math.radians(self.angle)))
            next_position = self.position + movement_direction * self.speed * dt
            
            # Sprawdzamy kolizję z przeszkodami
            mouse_rect = self.get_rect()
            if obstacles.check_collision(mouse_rect, extension=30):
                self.angle += 1  # Obrót w kierunku omijania przeszkody
            else:
                self.is_turning_around = False

            self.position = next_position

        # Aktualizacja głodu, czasu życia i zegara sera
        self.hunger -= 5 * dt
        self.lifetime += dt
        self.cheeseclock += dt

        # Zapobiegamy wychodzeniu myszki poza ekran
        self.position.x = max(20, min(self.position.x, screen.get_width() - 20))
        self.position.y = max(20, min(self.position.y, screen.get_height() - 20))

    def get_rect(self):
        # Returns a rectangle for the mouse with some expanded area for collision detection
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        rect = rotated_image.get_rect(center=self.position)
        # Increase the rectangle size for better collision detection
        return rect.inflate(10, 10)  # Zwiększamy o 20 pikseli w obu kierunkach
    
    def avoid_obstacle(self, direction, obstacles):
        """ Try to find the best path to avoid the obstacle by steering around it """
        best_position = self.position
        best_clearance = 0
        radius = 50  # Radius for circular movement around the obstacle

        # Try a circular path around the obstacle
        for angle in range(-90, 91, 10):  # Try angles from -90 to 90 degrees with steps
            new_direction = direction.rotate(angle)
            # Calculate the new position in the direction of the angle
            new_position = self.position + new_direction * self.speed * dt
            
            # Check for collision in the new position
            if not obstacles.check_collision(self.position, new_position):
                # Measure how far this direction clears the obstacle (just a simple distance measure)
                clearance = self.position.distance_to(new_position)
                if clearance > best_clearance:
                    best_clearance = clearance
                    best_position = new_position

        # Return the best new position (or the current position if no good path found)
        return best_position

    def player_cheese_dist(self, cheese_pos):
        self.cheesedist = self.position.distance_to(cheese_pos)

    def cheeseclock_reset(self):
        self.cheeseclock = 0

    def draw(self, screen):
        # Rotate the player image and draw it at the correct position
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        rotated_rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rotated_rect.topleft)

    def hunger_upgrade(self):
        self.hunger += 20

    def get_position(self):
        return f"Position: ({int(self.position.x)}, {int(self.position.y)})"
    
    def get_hunger(self):
        return f"Hunger: ({int(self.hunger)})"
    
    def get_cheesedist(self):
        return f"Cheese dist: ({self.cheesedist:.2f})"
    
    def get_lifetime(self):
        return f"Lifetime: ({int(self.lifetime)})"
    
    def get_cheeseclock(self):
        return f"Cheese clock: ({self.cheeseclock:.2f})"
    
    def get_rect(self):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        return rotated_image.get_rect(center=self.position)

class Cheese:
    def __init__(self, image_path, pos):
        self.image = pygame.image.load(image_path)
        self.position = pygame.Vector2(pos)

    def draw(self, screen):
        screen.blit(self.image, self.position)

    def get_rect(self):
        return self.image.get_rect(topleft=self.position)
    
    def relocate(self):
        self.position.x = random.randrange(20, screen.get_width() - 20)
        self.position.y = random.randrange(20, screen.get_height() - 20)

def display_text(text, position):
    text_surface = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, position)

# Initialize player (mouse), cheese, and obstacle instances
player = Mouse('./img_mouse/mouse.png', (screen.get_width() / 2, screen.get_height() / 2), 300)
ch = Cheese('./img_mouse/cheese.png', (random.randrange(20, screen.get_width() - 20), random.randrange(20, screen.get_height() - 20)))
obstacles = Obstacle()

drawing = False
start_pos = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
            start_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                end_pos = pygame.mouse.get_pos()
                obstacles.add_line(start_pos, end_pos)
                drawing = False

    screen.fill("purple")
    player.update(dt, ch.position, obstacles)
    player.draw(screen)
    ch.draw(screen)
    obstacles.draw(screen)
    
    player.player_cheese_dist(ch.position)

    if player.get_rect().colliderect(ch.get_rect()):
        ch.relocate()
        player.hunger_upgrade()
        player.cheeseclock_reset()
    
    display_text(player.get_position(), (10, 15))
    display_text(player.get_hunger(), (10, 30))
    display_text(player.get_lifetime(), (10, 45))
    display_text(player.get_cheesedist(), (10, 60))
    display_text(player.get_cheeseclock(), (10, 75))

    pygame.display.flip()
    dt = clock.tick(60) / 1000.0

pygame.quit()

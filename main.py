import pygame
import math
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

font = pygame.font.SysFont("Arial", 12)

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

    def update(self, dt, keys):
        # Determine direction based on input keys
        direction = pygame.Vector2(0, 0)
        self.hunger -= 5 * dt
        self.lifetime += dt
        self.cheeseclock += dt
        if keys[pygame.K_w]: direction.y = -1
        if keys[pygame.K_s]: direction.y = 1
        if keys[pygame.K_a]: direction.x = -1
        if keys[pygame.K_d]: direction.x = 1
        
        # Update position and angle if there is movement
        if direction.length() > 0:
            direction = direction.normalize()
            self.position += direction * self.speed * dt
            self.angle = math.degrees(math.atan2(-direction.y, direction.x))

        self.position.x = max(20, min(self.position.x, screen.get_width()-20))
        self.position.y = max(20, min(self.position.y, screen.get_height()-20))

    def player_cheese_dist(self,cheese_pos):
        self.cheesedist = math.sqrt((self.position.x - cheese_pos.x)**2 + (self.position.y - cheese_pos.y)**2)

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
        # Returns the current position as a string
        return f"Position: ({int(self.position.x)}, {int(self.position.y)})"
    
    def get_hunger(self):
        # Returns the current position as a string
        return f"Hunger: ({int(self.hunger)})"
    
    def get_cheesedist(self):
        # Returns the current position as a string
        return f"Cheese dist: ({(self.cheesedist)})"
    
    def get_lifetime(self):
        # Returns the current position as a string
        return f"Lifetime: ({int(self.lifetime)})"
    
    def get_cheeseclock(self):
        # Returns the current position as a string
        return f"Cheese clock: ({(self.cheeseclock)})"
    
    def get_rect(self):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        return rotated_image.get_rect(center=self.position)
    
    
    # Update the player update method to prevent going through walls

class Cheese:
    def __init__(self,image_path,pos):
        self.image = pygame.image.load(image_path)
        self.position = pygame.Vector2(pos)

    def draw(self,screen):
        screen.blit(self.image,self.position)

    def get_rect(self):
        return self.image.get_rect(topleft=self.position)
    
    def relocate(self):
        self.position.x = random.randrange(20, screen.get_width() - 20)
        self.position.y = random.randrange(20, screen.get_height() - 20)




# Function to display text on screen
def display_text(text, position):
    text_surface = font.render(text, True, (255, 255, 255))  # White color
    screen.blit(text_surface, position)



# Initialize player (mouse) instance
player = Mouse('./img_mouse/mouse.png', (screen.get_width() / 2, screen.get_height() / 2), 300)

pos = pygame.Vector2()
pos.x = random.randrange(screen.get_width()-20)
pos.y = random.randrange(screen.get_height()-20)

ch = Cheese('./img_mouse/cheese.png',pos)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with a background color
    screen.fill("purple")

    # Update and draw player
    keys = pygame.key.get_pressed()

    player.update(dt, keys)



    player.draw(screen)
    


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

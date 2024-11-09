import pygame
import random
screen = pygame.display.set_mode((1280, 720))
class Cheese:
    def __init__(self,image_path,pos):
        self.image = pygame.image.load(image_path)
        self.position = pygame.Vector2(pos)

    def draw(self,screen):
        screen.blit(self.image,self.position)

    def get_rect(self):
        return self.image.get_rect(topleft=self.position)
    
    def relocate(self):
        self.position.x = random.randrange(40, screen.get_width() - 40)
        self.position.y = random.randrange(40, screen.get_height() - 40)
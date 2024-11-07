import pygame
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
import math

# Inicjalizacja Pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Hyperparametry
GAMMA = 0.99
ALPHA = 0.0001
BATCH_SIZE = 64
MEMORY_SIZE = 10000
EPSILON = 1.0
EPSILON_DECAY = 0.995
MIN_EPSILON = 0.01
UPDATE_TARGET_EVERY = 100 
MAX_STEPS_PER_EPISODE = 50

# Model sieci neuronowej
class DQNModel(tf.keras.Model):
    def __init__(self, action_space):
        super(DQNModel, self).__init__()
        self.dense1 = layers.Dense(128, activation='relu')
        self.dense2 = layers.Dense(128, activation='relu')
        self.q_values = layers.Dense(action_space)

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        return self.q_values(x)

# Replay Buffer
class ReplayBuffer:
    def __init__(self, max_size):
        self.buffer = []
        self.max_size = max_size

    def add(self, experience):
        if len(self.buffer) >= self.max_size:
            self.buffer.pop(0)
        self.buffer.append(experience)

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

# Klasa reprezentująca gracza (mysz)
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
        self.last_cheese_time = 0

    def update(self, dt, direction):
        self.hunger -= 5 * dt
        self.lifetime += dt
        self.cheeseclock += dt

        # Aktualizacja pozycji gracza
        if direction.length() > 0:
            direction = direction.normalize()
            self.position += direction * self.speed * dt
            self.angle = math.degrees(math.atan2(-direction.y, direction.x))

        self.position.x = max(20, min(self.position.x, screen.get_width()-20))
        self.position.y = max(20, min(self.position.y, screen.get_height()-20))

    def player_cheese_dist(self, cheese_pos):
        self.cheesedist = math.sqrt((self.position.x - cheese_pos.x)**2 + (self.position.y - cheese_pos.y)**2)

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        rotated_rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rotated_rect.topleft)

    def cheeseclock_reset(self):
        self.cheeseclock = 0
        self.last_cheese_time = pygame.time.get_ticks()

    def hunger_upgrade(self):
        self.hunger = min(100, self.hunger + 20)

# Klasa reprezentująca ser
class Cheese:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.image = pygame.image.load('./img_mouse/cheese.png')
        self.rect = self.image.get_rect(center=self.position)

    def relocate(self):
        self.position = pygame.Vector2(random.randrange(20, screen.get_width()-20), random.randrange(20, screen.get_height()-20))
        self.rect = self.image.get_rect(center=self.position)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

# Inicjalizacja gry
player = Mouse('./img_mouse/mouse.png', (screen.get_width() / 2, screen.get_height() / 2), 300)
cheeses = [Cheese(random.randrange(screen.get_width()-20), random.randrange(screen.get_height()-20)) for _ in range(50)]
buffer = ReplayBuffer(MEMORY_SIZE)

# Modele DQN
action_space = 4  # cztery kierunki ruchu
model = DQNModel(action_space)
target_model = DQNModel(action_space)
target_model.set_weights(model.get_weights())
optimizer = tf.keras.optimizers.Adam(learning_rate=ALPHA)

def train_dqn():
    global EPSILON
    for episode in range(1000):
        state = np.array([player.position.x, player.position.y, player.hunger, player.cheesedist])
        total_reward = 0
        steps = 0
        done = False

        while not done and steps < MAX_STEPS_PER_EPISODE:
            # Decyzja: eksploracja/eksploatacja
            if np.random.rand() < EPSILON:
                action = random.randrange(action_space)
            else:
                q_values = model(tf.convert_to_tensor(np.expand_dims(state, axis=0), dtype=tf.float32))
                action = np.argmax(q_values)

            direction = pygame.Vector2(0, 0)
            if action == 0:  # Up
                direction.y = -1
            elif action == 1:  # Down
                direction.y = 1
            elif action == 2:  # Left
                direction.x = -1
            elif action == 3:  # Right
                direction.x = 1

            player.update(0.1, direction)

            # Nagroda i kara
            reward = -1  # Kara za ruch
            for cheese in cheeses:
                player.player_cheese_dist(cheese.position)
                if player.cheesedist < 20:
                    cheese.relocate()
                    player.hunger_upgrade()
                    reward = 100
                    done = True  # Zakończenie epizodu

            reward -= player.cheesedist * 0.01
            reward += max(0, 50 - player.cheeseclock)

            next_state = np.array([player.position.x, player.position.y, player.hunger, player.cheesedist])
            buffer.add((state, action, reward, next_state, done))
            state = next_state
            total_reward += reward
            steps += 1

            if len(buffer.buffer) > BATCH_SIZE:
                experiences = buffer.sample(BATCH_SIZE)
                states, actions, rewards, next_states, dones = zip(*experiences)
                states, next_states = np.array(states), np.array(next_states)

                with tf.GradientTape() as tape:
                    q_values = model(tf.convert_to_tensor(states, dtype=tf.float32))
                    next_q_values = target_model(tf.convert_to_tensor(next_states, dtype=tf.float32))
                    max_next_q_values = tf.reduce_max(next_q_values, axis=1)
                    target_q_values = rewards + (GAMMA * max_next_q_values * (1 - np.array(dones)))

                    indices = np.array([actions]).T
                    predicted_q_values = tf.gather_nd(q_values, indices, batch_dims=1)
                    loss = tf.reduce_mean(tf.square(target_q_values - predicted_q_values))

                grads = tape.gradient(loss, model.trainable_variables)
                optimizer.apply_gradients(zip(grads, model.trainable_variables))

            if steps % UPDATE_TARGET_EVERY == 0:
                target_model.set_weights(model.get_weights())

            screen.fill("purple")
            player.draw(screen)
            for cheese in cheeses:
                cheese.draw(screen)
            pygame.display.update()
            clock.tick(60)

        EPSILON = max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
        print(f"Episode {episode}: Total Reward: {total_reward} Epsilon: {EPSILON}")

train_dqn()
pygame.quit()

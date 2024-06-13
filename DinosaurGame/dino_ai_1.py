
# import pygame
# import random

# # Initialize Pygame
# pygame.init()

# # Set up the game window
# width = 800
# height = 400
# screen = pygame.display.set_mode((width, height))
# pygame.display.set_caption("Dinosaur Game")

# # Define colors
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)

# # Define game objects
# dino_width = 40
# dino_height = 60
# dino_x = 50
# dino_y = height - dino_height - 10
# dino_jump_speed = -20
# dino_gravity = 0.8
# dino_y_velocity = 0

# cactus_width = 60
# cactus_height = 80
# cactus_x = width
# cactus_y = height - cactus_height - 10
# cactus_speed = 5

# # Initialize score and high score
# score = 0
# high_score = 0

# # Game loop
# running = True
# clock = pygame.time.Clock()

# def reset_game():
#     global dino_y, dino_y_velocity, cactus_x, score
#     dino_y = height - dino_height - 10
#     dino_y_velocity = 0
#     cactus_x = width
#     score = 0

# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         elif event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_SPACE and dino_y == height - dino_height - 10:
#                 dino_y_velocity = dino_jump_speed

#     # Update dinosaur position
#     dino_y_velocity += dino_gravity
#     dino_y += dino_y_velocity

#     # Keep the dinosaur on the ground
#     if dino_y > height - dino_height - 10:
#         dino_y = height - dino_height - 10
#         dino_y_velocity = 0

#     # Move the cactus
#     cactus_x -= cactus_speed

#     # Reset cactus position when it goes off-screen
#     if cactus_x < -cactus_width:
#         cactus_x = width
#         cactus_y = height - cactus_height - 10
#         score += 1

#     # Check for collision
#     if dino_x + dino_width > cactus_x and dino_x < cactus_x + cactus_width and dino_y + dino_height > cactus_y:
#         reset_game()

#     # Clear the screen
#     screen.fill(WHITE)

#     # Draw the dinosaur
#     pygame.draw.rect(screen, BLACK, (dino_x, dino_y, dino_width, dino_height))

#     # Draw the cactus
#     pygame.draw.rect(screen, BLACK, (cactus_x, cactus_y, cactus_width, cactus_height))

#     # Display the score
#     font = pygame.font.Font(None, 36)
#     score_text = font.render("Score: " + str(score), True, BLACK)
#     screen.blit(score_text, (10, 10))

#     # Update the high score
#     if score > high_score:
#         high_score = score

#     # Display the high score
#     high_score_text = font.render("High Score: " + str(high_score), True, BLACK)
#     screen.blit(high_score_text, (10, 50))

#     # Update the display
#     pygame.display.flip()

#     # Set the frame rate
#     clock.tick(60)

# # Quit the game
# pygame.quit()

import pygame
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the game window
width = 800
height = 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dinosaur Game")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Define game objects
dino_width = 40
dino_height = 60
dino_x = 50
dino_y = height - dino_height - 10
dino_jump_speed = -20
dino_gravity = 0.8
dino_y_velocity = 0

cactus_width = 60
cactus_height = 80
cactus_x = width
cactus_y = height - cactus_height - 10
cactus_speed = 5

# Initialize score and high score
score = 0
high_score = 0

# Q-learning parameters
actions = ['jump', 'stay']
state_size = (10, 10)
q_table = np.zeros(state_size + (len(actions),))
learning_rate = 0.8
discount_rate = 0.95
epsilon = 0.1

def get_state(dino_y, cactus_x):
    dino_y_bin = int(dino_y / (height / state_size[0]))
    cactus_x_bin = int(cactus_x / (width / state_size[1]))
    # Ensure the indices are within the valid range for the q_table
    dino_y_bin = min(dino_y_bin, state_size[0] - 1)
    cactus_x_bin = min(cactus_x_bin, state_size[1] - 1)
    return (dino_y_bin, cactus_x_bin)


def get_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.choice(actions)
    else:
        return actions[np.argmax(q_table[state[0], state[1]])]

def update_q_table(state, action, reward, next_state):
    q_value = q_table[state[0], state[1], actions.index(action)]
    max_q_next_state = np.max(q_table[next_state[0], next_state[1]])
    q_table[state[0], state[1], actions.index(action)] = q_value + learning_rate * (reward + discount_rate * max_q_next_state - q_value)

def reset_game():
    global dino_y, dino_y_velocity, cactus_x, score
    dino_y = height - dino_height - 10
    dino_y_velocity = 0
    cactus_x = width
    score = 0

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    state = get_state(dino_y, cactus_x)
    action = get_action(state)

    if action == 'jump' and dino_y == height - dino_height - 10:
        dino_y_velocity = dino_jump_speed

    # Update dinosaur position
    dino_y_velocity += dino_gravity
    dino_y += dino_y_velocity

    # Keep the dinosaur on the ground
    if dino_y > height - dino_height - 10:
        dino_y = height - dino_height - 10
        dino_y_velocity = 0

    # Move the cactus
    cactus_x -= cactus_speed

    # Reset cactus position when it goes off-screen
    if cactus_x < -cactus_width:
        cactus_x = width
        cactus_y = height - cactus_height - 10
        score += 1

    next_state = get_state(dino_y, cactus_x)

    # Check for collision
    if dino_x + dino_width > cactus_x and dino_x < cactus_x + cactus_width and dino_y + dino_height > cactus_y:
        reward = -10
        update_q_table(state, action, reward, next_state)
        reset_game()
    else:
        reward = 1
        update_q_table(state, action, reward, next_state)

    # Clear the screen
    screen.fill(WHITE)

    # Draw the dinosaur
    pygame.draw.rect(screen, BLACK, (dino_x, dino_y, dino_width, dino_height))

    # Draw the cactus
    pygame.draw.rect(screen, BLACK, (cactus_x, cactus_y, cactus_width, cactus_height))

    # Display the score
    font = pygame.font.Font(None, 36)
    score_text = font.render("Score: " + str(score), True, BLACK)
    screen.blit(score_text, (10, 10))

    # Update the high score
    if score > high_score:
        high_score = score

    # Display the high score
    high_score_text = font.render("High Score: " + str(high_score), True, BLACK)
    screen.blit(high_score_text, (10, 50))

    # Update the display
    pygame.display.flip()

    # Set the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()
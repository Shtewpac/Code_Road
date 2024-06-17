
import pygame
import random
import numpy as np
import multiprocessing

# Constants
WIDTH = 600
HEIGHT = 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DINO_WIDTH = 40
DINO_HEIGHT = 60
DINO_X = 50
DINO_JUMP_SPEED = -20
DINO_GRAVITY = 0.8
CACTUS_WIDTH = 60
CACTUS_HEIGHT = 80
CACTUS_SPEED = 5
ACTIONS = ['jump', 'stay']
STATE_SIZE = (10, 10)
LEARNING_RATE = 0.8
DISCOUNT_RATE = 0.95
EPSILON = 0.1

# Global variables
score = 0
high_score = 0
q_table = np.zeros(STATE_SIZE + (len(ACTIONS),))

def get_state(dino_y, cactus_x):
    dino_y_bin = int(dino_y / (HEIGHT / STATE_SIZE[0]))
    cactus_x_bin = int(cactus_x / (WIDTH / STATE_SIZE[1]))
    dino_y_bin = min(dino_y_bin, STATE_SIZE[0] - 1)
    cactus_x_bin = min(cactus_x_bin, STATE_SIZE[1] - 1)
    return (dino_y_bin, cactus_x_bin)

def get_action(state):
    if random.uniform(0, 1) < EPSILON:
        return random.choice(ACTIONS)
    else:
        return ACTIONS[np.argmax(q_table[state[0], state[1]])]

def update_q_table(state, action, reward, next_state):
    q_value = q_table[state[0], state[1], ACTIONS.index(action)]
    max_q_next_state = np.max(q_table[next_state[0], next_state[1]])
    q_table[state[0], state[1], ACTIONS.index(action)] = q_value + LEARNING_RATE * (reward + DISCOUNT_RATE * max_q_next_state - q_value)

def reset_game():
    global score
    dino_y = HEIGHT - DINO_HEIGHT - 10
    dino_y_velocity = 0
    cactus_x = WIDTH
    cactus_y = HEIGHT - CACTUS_HEIGHT - 10
    score = 0
    return dino_y, dino_y_velocity, cactus_x, cactus_y

def draw_game_objects(screen, dino_x, dino_y, cactus_x, cactus_y):
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, (dino_x, dino_y, DINO_WIDTH, DINO_HEIGHT))
    pygame.draw.rect(screen, BLACK, (cactus_x, cactus_y, CACTUS_WIDTH, CACTUS_HEIGHT))

def display_scores(screen, score, high_score):
    font = pygame.font.Font(None, 36)
    score_text = font.render("Score: " + str(score), True, BLACK)
    high_score_text = font.render("High Score: " + str(high_score), True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 50))

def run_game(process_id):
    global high_score, score

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Dinosaur Game - Instance {process_id}")

    dino_x = DINO_X
    dino_y, dino_y_velocity, cactus_x, cactus_y = reset_game()

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        state = get_state(dino_y, cactus_x)
        action = get_action(state)

        if action == 'jump' and dino_y == HEIGHT - DINO_HEIGHT - 10:
            dino_y_velocity = DINO_JUMP_SPEED

        dino_y_velocity += DINO_GRAVITY
        dino_y += dino_y_velocity

        if dino_y > HEIGHT - DINO_HEIGHT - 10:
            dino_y = HEIGHT - DINO_HEIGHT - 10
            dino_y_velocity = 0

        cactus_x -= CACTUS_SPEED

        if cactus_x < -CACTUS_WIDTH:
            cactus_x = WIDTH
            cactus_y = HEIGHT - CACTUS_HEIGHT - 10
            score += 1

        next_state = get_state(dino_y, cactus_x)

        if dino_x + DINO_WIDTH > cactus_x and dino_x < cactus_x + CACTUS_WIDTH and dino_y + DINO_HEIGHT > cactus_y:
            reward = -10
            update_q_table(state, action, reward, next_state)
            dino_y, dino_y_velocity, cactus_x, cactus_y = reset_game()
        else:
            reward = 1
            update_q_table(state, action, reward, next_state)

        draw_game_objects(screen, dino_x, dino_y, cactus_x, cactus_y)
        display_scores(screen, score, high_score)

        high_score = max(score, high_score)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    num_processes = 12

    processes = []
    for i in range(num_processes):
        process = multiprocessing.Process(target=run_game, args=(i,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
unknown
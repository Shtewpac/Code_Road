
# import pygame
# import random
# import numpy as np

# # Initialize Pygame
# pygame.init()

# # Set up the game window
# width, height = 400, 400
# screen = pygame.display.set_mode((width, height))
# pygame.display.set_caption("Dinosaur Game - Multi Instance with Q-learning")

# # Define colors and game parameters
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
# dino_width, dino_height = 40, 60
# cactus_width, cactus_height = 60, 80
# dino_jump_speed = -20
# dino_gravity = 0.8
# cactus_speed = 5
# # Define multiple colors for different instances
# colors = [
#     (255, 0, 0),  # Red
#     (0, 255, 0),  # Green
#     (0, 0, 255),  # Blue
#     (255, 255, 0),  # Yellow
#     (255, 165, 0),  # Orange
#     (255, 0, 255),  # Magenta
#     # Add more colors as needed
# ]


# # Q-learning parameters
# epsilon = 0.1  # Exploration rate
# learning_rate = 0.1 # Step size
# discount_rate = 0.95 # Future reward discount factor
# actions = [0, 1]  # 0: do nothing, 1: jump
# state_size = (2,)  # Simplified state: Distance to next obstacle (discrete), Y velocity of dinosaur (binary)

# # Add logging variables
# total_games = 0
# total_score = 0
# average_scores = []
# games_since_last_log = 0
# log_interval = 10  # Log average score every 10 games

# # Initialize game instances with Q-learning components
# num_instances = 7  # Adjust as needed
# instances = []

# for i in range(num_instances):
#     color = colors[i % len(colors)]  # Cycle through colors if necessary
#     instances.append({
#         'dino_x': 50, 'dino_y': height - dino_height - 10, 'dino_y_velocity': 0,
#         'cactus_x': width, 'cactus_y': height - cactus_height - 10,
#         'score': 0, 'color': color,  # Assign the color here
#         'q_table': np.zeros(state_size + (len(actions),))
#     })

# high_score = 0

# def get_state(instance):
#     # Simplified state: Distance to next obstacle (0: far, 1: close), is jumping (0: no, 1: yes)
#     distance_to_obstacle = 1 if instance['cactus_x'] - instance['dino_x'] < width / 2 else 0
#     is_jumping = 1 if instance['dino_y'] < (height - dino_height - 10) else 0
#     return distance_to_obstacle, is_jumping

# def choose_action(state, q_table):
#     if random.uniform(0, 1) < epsilon:
#         return random.choice(actions)  # Explore
#     else:
#         return np.argmax(q_table[state])  # Exploit

# def update_q_table(instance, action, reward, next_state):
#     current_state_index = get_state_index(current_state)
#     next_state_index = get_state_index(next_state)
#     q_value = instance['q_table'][current_state_index, action]
#     future_reward = np.max(instance['q_table'][next_state_index])
#     instance['q_table'][current_state_index, action] = q_value + learning_rate * (reward + discount_rate * future_reward - q_value)
    
#     # Print statement for debugging
#     print(f"Updating Q-table for Instance {i+1}, Action: {'Jump' if action == 1 else 'Stay'}, Reward: {reward}, New Q-value: {instance['q_table'][current_state_index, action]}")

# def get_state_index(state):
#     # Convert state tuple to a single index, if necessary
#     # This depends on how you've structured your states and Q-table
#     # For a simple approach, you could directly use the state tuple if it's already compatible with your Q-table's indexing
#     return state  # Placeholder, adjust based on your state-to-index mapping logic

# # Game loop
# running = True
# clock = pygame.time.Clock()
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     screen.fill(WHITE)
    
#     any_collision = False  # Track if any collision happened in this loop iteration

#     for instance in instances:
#         current_state = get_state(instance)
#         action = choose_action(current_state, instance['q_table'])
#         print(f"Instance {i+1}, State: {current_state}, Chosen Action: {'Jump' if action == 1 else 'Stay'}, Score: {instance['score']}")
#         if action == 1 and instance['dino_y'] == height - dino_height - 10:
#             instance['dino_y_velocity'] = dino_jump_speed  # Jump

#         # Update dinosaur position
#         instance['dino_y_velocity'] += dino_gravity
#         instance['dino_y'] += instance['dino_y_velocity']
#         if instance['dino_y'] > height - dino_height - 10:
#             instance['dino_y'] = height - dino_height - 10
#             instance['dino_y_velocity'] = 0

#         # Move the cactus
#         instance['cactus_x'] -= cactus_speed
#         if instance['cactus_x'] < -cactus_width:
#             instance['cactus_x'] = width
#             instance['score'] += 1
#             high_score = max(high_score, instance['score'])

#         # Draw the dinosaur and cactus
#         # Draw the dinosaur and cactus using the instance's assigned color
#         pygame.draw.rect(screen, instance['color'], (instance['dino_x'], instance['dino_y'], dino_width, dino_height))
#         pygame.draw.rect(screen, instance['color'], (instance['cactus_x'], instance['cactus_y'], cactus_width, cactus_height))

#         # Update Q-table based on the outcome
#         reward = 0  # Default reward
#         if instance['cactus_x'] < instance['dino_x']:  # Passed the cactus
#             reward = 1
#             print(f"Instance {i+1} successfully jumped over the obstacle. Reward: {reward}")
#         elif instance['dino_x'] + dino_width > instance['cactus_x'] and instance['dino_y'] + dino_height > instance['cactus_y']:
#             # print("Collision!")
#             reward = -100  # Collision
#             any_collision = True
#             # Reset the game state for this instance
#             instance['dino_y'] = height - dino_height - 10
#             instance['cactus_x'] = width
#             instance['score'] = 0
#         next_state = get_state(instance)
#         update_q_table(instance, action, reward, next_state)
        
#     if any_collision:
#         total_games += 1
#         games_since_last_log += 1
        
#     # Update total score and check for logging interval
#     if games_since_last_log >= log_interval:
#         average_score = total_score / total_games
#         average_scores.append(average_score)
#         print(f"Average score after {total_games} games: {average_score}")
#         games_since_last_log = 0  # Reset counter after logging
        
#     # Display the scores and high score
#     font = pygame.font.Font(None, 36)
#     y_offset = 10
#     for i, instance in enumerate(instances):
#         score_text = font.render(f"Instance {i+1} Score: {instance['score']}", True, BLACK)
#         screen.blit(score_text, (10, y_offset))
#         y_offset += 30
#     high_score_text = font.render("High Score: " + str(high_score), True, BLACK)
#     screen.blit(high_score_text, (10, y_offset))

#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()


import pygame
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the game window
width, height = 400, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dinosaur Game - Multi Instance with Q-learning Adjusted")

# Colors, game parameters
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
dino_width, dino_height = 40, 60
cactus_width, cactus_height = 60, 80
dino_jump_speed, dino_gravity = -20, 0.8
cactus_speed = 5
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (255, 0, 255)]

# Q-learning parameters
epsilon = 0.2  # Increased for more exploration
learning_rate = 0.5
discount_rate = 0.95
actions = [0, 1]  # 0: do nothing, 1: jump
state_size = (2,)

num_states = 4  # For two binary features, producing four combinations
num_actions = 2  # Stay and Jump
q_table = np.zeros((num_states, num_actions))


# Initialize game instances
num_instances = 7
instances = []
for i in range(num_instances):
    color = colors[i % len(colors)]
    instances.append({
        'dino_x': 50, 'dino_y': height - dino_height - 10, 'dino_y_velocity': 0,
        'cactus_x': width, 'cactus_y': height - cactus_height - 10,
        'score': 0, 'color': color,
        'q_table': np.zeros(state_size + (len(actions),))
    })

high_score = 0

def get_state(instance):
    distance_to_obstacle = 1 if instance['cactus_x'] - instance['dino_x'] < width / 2 else 0
    is_jumping = 1 if instance['dino_y'] < (height - dino_height - 10) else 0
    return (distance_to_obstacle, is_jumping)

def choose_action(state, q_table):
    if random.uniform(0, 1) < epsilon:
        return random.choice(actions)
    else:
        return np.argmax(q_table[state])

def state_to_index(state):
    # Example mapping, specific implementation depends on the state space
    return state[0] * len(state_size) + state[1]

# Corrected indexing in the update_q_table function
def update_q_table(instance, action, reward, next_state):
    current_state_idx = state_to_index(current_state)
    next_state_idx = state_to_index(next_state)
    q_value = instance['q_table'][current_state_idx, action]
    future_reward = np.max(instance['q_table'][next_state_idx])
    instance['q_table'][current_state_idx, action] = q_value + learning_rate * (reward + discount_rate * future_reward - q_value)

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    for i, instance in enumerate(instances):
        current_state = get_state(instance)
        action = choose_action(current_state, instance['q_table'])
        
        # Apply action
        if action == 1 and instance['dino_y'] == height - dino_height - 10:
            instance['dino_y_velocity'] = dino_jump_speed
        
        # Dinosaur physics
        instance['dino_y_velocity'] += dino_gravity
        instance['dino_y'] += instance['dino_y_velocity']
        if instance['dino_y'] > height - dino_height - 10:
            instance['dino_y'] = height - dino_height - 10
            instance['dino_y_velocity'] = 0

        instance['cactus_x'] -= cactus_speed
        if instance['cactus_x'] < -cactus_width:
            instance['cactus_x'] = width
            instance['score'] += 1
            high_score = max(high_score, instance['score'])

        pygame.draw.rect(screen, instance['color'], (instance['dino_x'], instance['dino_y'], dino_width, dino_height))
        pygame.draw.rect(screen, instance['color'], (instance['cactus_x'], instance['cactus_y'], cactus_width, cactus_height))

        reward = 0  # Default reward
        if instance['cactus_x'] < instance['dino_x']:
            reward = 1  # Reward for successfully jumping over
        elif instance['dino_x'] + dino_width > instance['cactus_x'] and instance['dino_y'] + dino_height > instance['cactus_y']:
            reward = -100  # Penalty for collision
            instance['dino_y'] = height - dino_height - 10
            instance['cactus_x'] = width
            instance['score'] = 0

        next_state = get_state(instance)
        update_q_table(instance, action, reward, next_state)

    # Display scores and high score
    font = pygame.font.Font(None, 36)
    y_offset = 10
    for i, instance in enumerate(instances):
        score_text = font.render(f"Instance {i+1} Score: {instance['score']}", True, BLACK)
        screen.blit(score_text, (10, y_offset))
        y_offset += 30
    high_score_text = font.render("High Score: " + str(high_score), True, BLACK)
    screen.blit(high_score_text, (10, y_offset))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

unknown
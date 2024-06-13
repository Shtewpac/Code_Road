import numpy as np
import logging
from game.game import Game

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QLearningAgent:
    def __init__(self, board_size, num_pieces, learning_rate, discount_factor, exploration_rate):
        self.board_size = board_size
        self.num_pieces = num_pieces
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.q_table = {}

    def get_action(self, state):
        """
        Choose an action based on the current state using the Q-table.
        Incorporate the epsilon-greedy strategy to balance exploration and exploitation.
        """
        try:
            if np.random.uniform(0, 1) < self.exploration_rate:
                # Exploration: choose a random action
                action = self.random_action()
                logging.info(f"Exploration: Chose random action {action}")
            else:
                # Exploitation: choose the best action based on Q-values
                if state not in self.q_table:
                    self.q_table[state] = self._initialize_q_values()
                action = max(self.q_table[state], key=self.q_table[state].get)
                logging.info(f"Exploitation: Chose best action {action} for state {state}")
            return action
        except Exception as e:
            logging.error(f"Error in get_action: {e}", exc_info=True)
            raise

    def random_action(self):
        """
        Generate a random action. This method should be implemented based on the game's action space.
        """
        try:
            piece = np.random.choice(self.num_pieces)
            position = (np.random.randint(self.board_size), np.random.randint(self.board_size))
            action = (piece, position)
            logging.info(f"Generated random action {action}")
            return action
        except Exception as e:
            logging.error(f"Error in random_action: {e}", exc_info=True)
            raise

    def _initialize_q_values(self):
        """
        Initialize Q-values for a new state. This method should return a dictionary with actions as keys and
        initial Q-values as values.
        """
        try:
            q_values = {}
            for piece in range(self.num_pieces):
                for row in range(self.board_size):
                    for col in range(self.board_size):
                        action = (piece, (row, col))
                        q_values[action] = 0.0
            logging.info("Initialized Q-values for a new state")
            return q_values
        except Exception as e:
            logging.error(f"Error in initialize_q_values: {e}", exc_info=True)
            raise

    def update_q_table(self, state, action, reward, next_state):
        """
        Update the Q-table based on the observed transition.
        Q-learning update rule: Q(s, a) = Q(s, a) + learning_rate * (reward + discount_factor * max(Q(s', a')) - Q(s, a))
        """
        try:
            if state not in self.q_table:
                self.q_table[state] = self._initialize_q_values()
            if next_state not in self.q_table:
                self.q_table[next_state] = self._initialize_q_values()
                
            current_q_value = self.q_table[state][action]
            max_next_q_value = max(self.q_table[next_state].values())
            
            # Q-learning update rule
            updated_q_value = current_q_value + self.learning_rate * (reward + self.discount_factor * max_next_q_value - current_q_value)
            
            self.q_table[state][action] = updated_q_value
            logging.info(f"Updated Q-value for state {state} and action {action}: {updated_q_value}")
        except Exception as e:
            logging.error(f"Error in update_q_table: {e}", exc_info=True)
            raise

    def train(self, num_episodes):
        """
        Train the agent for a specified number of episodes.
        """
        try:
            for episode in range(num_episodes):
                logging.info(f"Starting episode {episode + 1}/{num_episodes}")
                game = Game(self.board_size, self.num_pieces)
                state = game.get_state()

                while not game.is_game_over():
                    action = self.get_action(state)
                    piece_index, (row, col) = action
                    piece = game.pieces[piece_index]

                    if game.place_piece(piece, (row, col)):
                        reward = game.calculate_reward()
                        next_state = game.get_state()
                        self.update_q_table(state, action, reward, next_state)
                        state = next_state

                logging.info(f"Episode {episode + 1} finished with score: {game.calculate_score()}")
                self.exploration_rate *= 0.99  # Decrease exploration rate over time
        except Exception as e:
            logging.error(f"Error in train method: {e}", exc_info=True)
            raise
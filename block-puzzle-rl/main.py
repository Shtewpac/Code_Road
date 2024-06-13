from game.game import Game
from agents.q_learning_agent import QLearningAgent
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        board_size = 9  # Updated to the correct board size for consistency
        num_pieces = 3
        learning_rate = 0.1
        discount_factor = 0.9
        exploration_rate = 0.1

        # Initialize the agent
        logging.info("Initializing Q-learning agent.")
        agent = QLearningAgent(board_size, num_pieces, learning_rate, discount_factor, exploration_rate)
        
        # Train the agent
        logging.info("Training the agent.")
        agent.train(num_episodes=1000)

        # Initialize the game
        logging.info("Initializing the game.")
        game = Game(board_size, num_pieces)

        # Play the game using the trained agent
        logging.info("Starting the game with the trained agent.")
        game.play(agent)

        # Print the final board state and score
        logging.info("Game Over!")
        logging.info("Final Board:")
        logging.info(f"\n{game.board.grid}")
        logging.info(f"Final Score: {game.calculate_score()}")

        sys.exit()

    except Exception as e:
        logging.error(f"An error occurred in main: {e}", exc_info=True)
        sys.exit()

if __name__ == '__main__':
    main()
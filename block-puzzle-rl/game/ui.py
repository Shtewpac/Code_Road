import pygame
import sys
import logging
from game.game import Game
from agents.q_learning_agent import QLearningAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 9
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

class BlockPuzzleUI:
    def __init__(self, game):
        self.game = game
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Block Puzzle Game")
        self.clock = pygame.time.Clock()

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))

    def draw_board(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.game.board.grid[row][col] == 1:
                    pygame.draw.rect(self.screen, BLUE, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def run(self):
        try:
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        col = x // CELL_SIZE
                        row = y // CELL_SIZE
                        # Placeholder for piece selection and placement logic
                        # self.game.place_piece(selected_piece, (row, col))

                self.screen.fill(WHITE)
                self.draw_grid()
                self.draw_board()
                pygame.display.flip()
                self.clock.tick(FPS)

            pygame.quit()
            sys.exit()
        except Exception as e:
            logging.error(f"An error occurred in the UI run loop: {e}", exc_info=True)
            raise

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

        # Initialize the UI
        logging.info("Initializing the UI.")
        ui = BlockPuzzleUI(game)

        # Run the UI
        logging.info("Starting the UI.")
        ui.run()

        # Print the final board state and score
        logging.info("Game Over!")
        logging.info("Final Board:")
        logging.info(f"\n{game.board.grid}")
        logging.info(f"Final Score: {game.calculate_score()}")

    except Exception as e:
        logging.error(f"An error occurred in main: {e}", exc_info=True)

if __name__ == '__main__':
    main()
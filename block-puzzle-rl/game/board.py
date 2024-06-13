import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Board:
    def __init__(self, size):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)

    def place_piece(self, piece, position):
        """
        Place the piece on the board at the given position.
        """
        try:
            if self.is_valid_move(piece, position):
                for (i, j) in piece.get_positions(position):
                    self.grid[i][j] = 1
                return True
            return False
        except Exception as e:
            logging.error(f"Error in place_piece: {e}", exc_info=True)
            raise

    def clear_lines(self):
        """
        Clear completed lines from the board.
        """
        try:
            lines_cleared = 0
            for i in range(self.size):
                if all(self.grid[i, :]):
                    self.grid[i, :] = 0
                    lines_cleared += 1
            for j in range(self.size):
                if all(self.grid[:, j]):
                    self.grid[:, j] = 0
                    lines_cleared += 1
            return lines_cleared
        except Exception as e:
            logging.error(f"Error in clear_lines: {e}", exc_info=True)
            raise

    def is_valid_move(self, piece, position):
        """
        Check if placing the piece at the given position is a valid move.
        """
        try:
            for (i, j) in piece.get_positions(position):
                if i < 0 or i >= self.size or j < 0 or j >= self.size or self.grid[i][j] != 0:
                    return False
            return True
        except Exception as e:
            logging.error(f"Error in is_valid_move: {e}", exc_info=True)
            raise

    def calculate_score(self):
        """
        Calculate and return the current score based on the board state.
        """
        try:
            score = np.sum(self.grid)
            return score
        except Exception as e:
            logging.error(f"Error in calculate_score: {e}", exc_info=True)
            raise
import numpy as np
from game.piece import Piece
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def display_all_piece_shapes():
    try:
        # Define all possible shapes for the pieces
        shapes = [
            np.array([[1, 1, 1, 1]]),  # Line piece
            np.array([[1, 1], [1, 1]]),  # Square piece
            np.array([[1, 1, 1], [0, 1, 0]]),  # T piece
            np.array([[1, 1, 0], [0, 1, 1]]),  # Z piece
            np.array([[0, 1, 1], [1, 1, 0]]),  # S piece
            np.array([[1, 0, 0], [1, 1, 1]]),  # L piece
            np.array([[0, 0, 1], [1, 1, 1]])   # J piece
        ]

        # Instantiate and display each piece
        for shape in shapes:
            piece = Piece(shape)
            logging.info(f"Piece shape:\n{piece.shape}")

    except Exception as e:
        logging.error(f"An error occurred while displaying all piece shapes: {e}", exc_info=True)

if __name__ == '__main__':
    display_all_piece_shapes()
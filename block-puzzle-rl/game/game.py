import numpy as np
from game.board import Board
from game.piece import Piece
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Game:
    def __init__(self, board_size, num_pieces):
        self.board = Board(board_size)
        self.num_pieces = num_pieces
        self.pieces = self.generate_pieces()

    def generate_pieces(self):
        pieces = []
        for _ in range(self.num_pieces):
            shape = np.random.randint(0, 2, size=(3, 3))
            piece = Piece(shape)
            pieces.append(piece)
        return pieces

    def place_piece(self, piece, position):
        try:
            row, col = position
            if self.is_valid_move(piece, row, col):
                self.board.grid[row:row+piece.shape.shape[0], col:col+piece.shape.shape[1]] += piece.shape
                return True
            return False
        except Exception as e:
            logging.error(f"Error in place_piece: {e}", exc_info=True)
            raise

    def is_valid_move(self, piece, row, col):
        try:
            if row < 0 or row > self.board.size - piece.shape.shape[0] or col < 0 or col > self.board.size - piece.shape.shape[1]:
                return False
            if np.any(self.board.grid[row:row+piece.shape.shape[0], col:col+piece.shape.shape[1]] + piece.shape > 1):
                return False
            return True
        except Exception as e:
            logging.error(f"Error in is_valid_move: {e}", exc_info=True)
            raise

    def clear_lines(self):
        try:
            lines_cleared = self.board.clear_lines()
            return lines_cleared
        except Exception as e:
            logging.error(f"Error in clear_lines: {e}", exc_info=True)
            raise

    def get_valid_moves(self):
        try:
            valid_moves = []
            for piece in self.pieces:
                for row in range(self.board.size - piece.shape.shape[0] + 1):
                    for col in range(self.board.size - piece.shape.shape[1] + 1):
                        if self.is_valid_move(piece, row, col):
                            valid_moves.append((piece, row, col))
            return valid_moves
        except Exception as e:
            logging.error(f"Error in get_valid_moves: {e}", exc_info=True)
            raise

    def is_game_over(self):
        try:
            return len(self.get_valid_moves()) == 0
        except Exception as e:
            logging.error(f"Error in is_game_over: {e}", exc_info=True)
            raise

    def get_state(self):
        """
        Extract the current state of the game. This method should return a representation of the current state.
        """
        try:
            # Assuming the state is represented by the board's grid
            state = tuple(map(tuple, self.board.grid))
            logging.info(f"Extracted state from game: {state}")
            return state
        except Exception as e:
            logging.error(f"Error in get_state: {e}", exc_info=True)
            raise

    def play(self, agent):
        try:
            state = self.get_state()

            while not self.is_game_over():
                action = agent.get_action(state)
                piece_index, (row, col) = action
                piece = self.pieces[piece_index]
                if self.place_piece(piece, (row, col)):
                    self.clear_lines()  # Clear lines after placing the piece
                    reward = self.calculate_reward()
                    next_state = self.get_state()
                    agent.update_q_table(state, action, reward, next_state)
                    state = next_state

            logging.info("Game Over!")
            logging.info("Final Board:")
            logging.info(f"\n{self.board.grid}")
            logging.info(f"Final Score: {self.calculate_score()}")
        except Exception as e:
            logging.error(f"Error in play method: {e}", exc_info=True)
            raise

    def play_with_ui(self, ui):
        try:
            state = self.get_state()

            while not self.is_game_over():
                ui.update_display()
                action = ui.get_user_action()
                piece_index, (row, col) = action
                piece = self.pieces[piece_index]
                if self.place_piece(piece, (row, col)):
                    self.clear_lines()
                    state = self.get_state()

            logging.info("Game Over!")
            logging.info("Final Board:")
            logging.info(f"\n{self.board.grid}")
        except Exception as e:
            logging.error(f"Error in play_with_ui method: {e}", exc_info=True)
            raise

    def calculate_reward(self):
        try:
            # Calculate reward based on lines cleared during the piece placement
            reward = self.calculate_score()  # Example reward calculation
            return reward
        except Exception as e:
            logging.error(f"Error in calculate_reward: {e}", exc_info=True)
            raise

    def calculate_score(self):
        try:
            score = np.sum(self.board.grid)
            return score
        except Exception as e:
            logging.error(f"Error in calculate_score: {e}", exc_info=True)
            raise
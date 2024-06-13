import numpy as np
from game.piece import Piece

def test_get_positions():
    shape = np.array([
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
    ])
    piece = Piece(shape)
    position = (1, 2)
    expected_positions = [(1, 2), (2, 2), (2, 3), (2, 4)]
    actual_positions = piece.get_positions(position)
    
    assert actual_positions == expected_positions, f"Expected {expected_positions}, but got {actual_positions}"
    print("test_get_positions passed!")

if __name__ == "__main__":
    test_get_positions()
class Piece:
    def __init__(self, shape):
        self.shape = shape

    def rotate(self):
        # Rotation is disabled in this game.
        pass

    def get_positions(self, position):
        """
        Return the positions occupied by the piece when placed at the given position.
        
        Args:
            position (tuple): The top-left position (row, col) where the piece is to be placed.
        
        Returns:
            list of tuples: List of coordinate tuples occupied by the piece.
        """
        positions = []
        top_left_row, top_left_col = position
        
        try:
            for row in range(self.shape.shape[0]):
                for col in range(self.shape.shape[1]):
                    if self.shape[row, col] == 1:
                        positions.append((top_left_row + row, top_left_col + col))
        except Exception as e:
            print(f"Error in get_positions: {e}")
            raise
        
        return positions
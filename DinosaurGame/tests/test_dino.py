import unittest
from src.dino import *

class TestDinosaurGame(unittest.TestCase):
    def test_game_initialization(self):
        game = DinosaurGame()
        self.assertIsNotNone(game)

    def test_jump_action(self):
        dino = Dinosaur()
        initial_y = dino.y
        dino.jump()
        self.assertNotEqual(dino.y, initial_y)

if __name__ == '__main__':
    unittest.main()

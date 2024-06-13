from game.game import Game
from agents.q_learning_agent import QLearningAgent

def train_agent():
    board_size = 8
    num_pieces = 3
    learning_rate = 0.1
    discount_factor = 0.9
    exploration_rate = 0.1
    num_episodes = 1000

    agent = QLearningAgent(board_size, num_pieces, learning_rate, discount_factor, exploration_rate)
    agent.train(num_episodes)

if __name__ == '__main__':
    train_agent()
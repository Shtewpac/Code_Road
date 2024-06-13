from agents.q_learning_agent import QLearningAgent

def test_update_q_table():
    # Initialize QLearningAgent with test parameters
    agent = QLearningAgent(board_size=9, num_pieces=3, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.1)
    
    # Define test states and actions
    state = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    next_state = ((1, 0, 0), (0, 1, 0), (1, 0, 0))
    action = (1, (0, 0))
    reward = 10
    
    # Initialize Q-values for the given state and next_state
    agent.q_table[state] = {action: 0.0}
    agent.q_table[next_state] = {action: 1.0}
    
    # Update Q-table
    agent.update_q_table(state, action, reward, next_state)
    
    # Check if the Q-value was updated correctly
    expected_q_value = 0.0 + 0.1 * (10 + 0.9 * 1.0 - 0.0)
    updated_q_value = agent.q_table[state][action]
    
    assert updated_q_value == expected_q_value, f"Expected {expected_q_value}, but got {updated_q_value}"
    print("Test passed!")

if __name__ == "__main__":
    test_update_q_table()
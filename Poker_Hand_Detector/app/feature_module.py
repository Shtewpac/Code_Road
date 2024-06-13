import logging
import os

# Configure logging to log messages to a file named `feature_test.log` in the project's root directory.
logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'feature_test.log'),
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def test_feature():
    """
    Simulates testing the new feature's functionality.
    Logs messages before and after a mock computation.
    """
    try:
        logging.info("Testing new feature...")

        # Perform a mock computation (e.g., adding two numbers)
        result = 1 + 1  # Example of a mock computation

        logging.info(f"Test completed successfully. Result of mock computation: {result}")
    except Exception as e:
        logging.error(f"Error testing new feature: {e}", exc_info=True)
# Dinosaur Game with AI

This project includes several implementations of a Dinosaur game using Pygame, showcasing different AI techniques like Q-learning and evolutionary learning.

## Setup
1. Install the required packages:
```
pip install -r requirements.txt
```

2. Run the desired game script:
```
python src/dino.py
```

## Implementations
- **dino.py:** Basic game with Q-learning.
- **dino_ai_1.py:** Improved Q-learning.
- **dino_ai_2-multiprocessing.py:** Multiprocessing for concurrent training.
- **dino_ai_3-multiprocessing.py:** Multiple instances in one window.
- **dino_ai_4-evolutionary_learning.py:** Evolutionary learning.

## Testing
To run the tests:
```
python -m unittest discover -s tests
```

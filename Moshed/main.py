from src.game import MoshedGame

if __name__ == "__main__":
    try:
        game = MoshedGame()
        game.run()
    except Exception as e:
        import traceback
        print("An error occurred while running the game:")
        print(str(e))
        traceback.print_exc()
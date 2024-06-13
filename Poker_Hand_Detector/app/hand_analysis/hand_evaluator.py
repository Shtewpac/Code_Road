from collections import Counter
import logging

class HandRank:
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

class HandEvaluator:
    @staticmethod
    def evaluate_hand(cards):
        """Evaluates the poker hand and returns its rank and the high card(s) for comparison."""
        try:
            ranks = sorted([card.rank for card in cards], reverse=True)
            suits = [card.suit for card in cards]
            rank_counts = Counter(ranks).most_common()

            is_flush = len(set(suits)) == 1
            is_straight = len(set(ranks)) == 5 and (max(ranks) - min(ranks) == 4)

            if is_flush and is_straight:
                logging.info("Detected Straight Flush or Royal Flush")
                return (HandRank.ROYAL_FLUSH if max(ranks) == 14 else HandRank.STRAIGHT_FLUSH), ranks
            if rank_counts[0][1] == 4:
                logging.info("Detected Four of a Kind")
                return HandRank.FOUR_OF_A_KIND, ranks
            if rank_counts[0][1] == 3 and rank_counts[1][1] == 2:
                logging.info("Detected Full House")
                return HandRank.FULL_HOUSE, ranks
            if is_flush:
                logging.info("Detected Flush")
                return HandRank.FLUSH, ranks
            if is_straight:
                logging.info("Detected Straight")
                return HandRank.STRAIGHT, ranks
            if rank_counts[0][1] == 3:
                logging.info("Detected Three of a Kind")
                return HandRank.THREE_OF_A_KIND, ranks
            if rank_counts[0][1] == 2 and rank_counts[1][1] == 2:
                logging.info("Detected Two Pair")
                return HandRank.TWO_PAIR, ranks
            if rank_counts[0][1] == 2:
                logging.info("Detected Pair")
                return HandRank.PAIR, ranks
            logging.info("Detected High Card")
            return HandRank.HIGH_CARD, ranks
        except Exception as e:
            logging.error("Error evaluating hand: %s", e, exc_info=True)
            raise

    @staticmethod
    def compare_hands(hand1, hand2):
        """Compares two hands and returns the winning hand or indicates a tie."""
        try:
            rank1, high_cards1 = HandEvaluator.evaluate_hand(hand1)
            rank2, high_cards2 = HandEvaluator.evaluate_hand(hand2)

            if rank1 > rank2:
                logging.info("Hand 1 wins by rank")
                return 'hand1'
            elif rank2 > rank1:
                logging.info("Hand 2 wins by rank")
                return 'hand2'
            else:
                # Compare the high cards
                for card1, card2 in zip(high_cards1, high_cards2):
                    if card1 > card2:
                        logging.info("Hand 1 wins by high card")
                        return 'hand1'
                    elif card2 > card1:
                        logging.info("Hand 2 wins by high card")
                        return 'hand2'
                logging.info("Hands are a tie")
                return 'tie'
        except Exception as e:
            logging.error("Error comparing hands: %s", e, exc_info=True)
            raise
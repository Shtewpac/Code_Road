class Card:
    def __init__(self, rank, suit):
        self.rank = rank  # Numeric value: 2-14 (where 11=Jack, 12=Queen, 13=King, 14=Ace)
        self.suit = suit  # String value: 'Hearts', 'Diamonds', 'Clubs', 'Spades'
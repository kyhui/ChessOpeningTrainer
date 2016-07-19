class OpeningBook:
    opening_book = {}

    def __init__(self):
        self.load_all_openings()

    def load_all_openings(self):
        return

    def get_opening_games(self, first_move):
        return self.opening_book.get(first_move)

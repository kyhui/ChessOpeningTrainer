class ChessNotation:

    class Move:
        white_move = None
        black_move = None

        def __init__(self):
            None

        def add_white_move(self, white):
            self.white_move = white

        def add_black_move(self, black):
            self.black_move = black

        def __str__(self):
            return self.white_move, self.black_move

    def __init__(self):
        self.history = {}
        self.movenumber = 1

    def add_move(self, square):
        if self.history.__contains__(self.movenumber):
            currentmove = self.history[self.movenumber]
            currentmove.add_black_move(square)
            self.history[self.movenumber] = currentmove
            self.movenumber += 1
        else:
            newmove = self.Move()
            newmove.add_white_move(square)
            self.history[self.movenumber] =newmove

    def get_move_number(self):
        return self.movenumber

    def get_notation_sheet(self):
        return self.history


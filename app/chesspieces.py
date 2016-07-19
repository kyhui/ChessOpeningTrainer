def get_piece_from_notation(abbreviation):
    pieces = {
        'p': Pawn(abbreviation),
        'n': Knight(abbreviation),
        'b': Bishop(abbreviation),
        'r': Rook(abbreviation),
        'q': Queen(abbreviation),
        'k': King(abbreviation),
        'P': Pawn(abbreviation),
        'N': Knight(abbreviation),
        'B': Bishop(abbreviation),
        'R': Rook(abbreviation),
        'Q': Queen(abbreviation),
        'K': King(abbreviation)
    }
    return pieces.get(abbreviation)


class Piece(object):
    __slots__ = ('fen', 'color', 'value')

    def __init__(self, fen):
        self.fen = fen
        if fen.islower():
            self.color = 'black'
        elif fen.isupper():
            self.color = 'white'

    def get_piece_type(self):
        return {
            'p': Pawn(self.fen),
            'n': Knight(self.fen),
            'b': Bishop(self.fen),
            'r': Rook(self.fen),
            'q': Queen(self.fen),
            'k': King(self.fen)
        }[self.fen.lower()]

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.color + ' ' + self.__class__.__name__


class Pawn(Piece):
    value = 1


class Knight(Piece):
    value = 3


class Rook(Piece):
    value = 5


class Bishop(Piece):
    value = 3.5


class Queen(Piece):
    value = 9


class King(Piece):
    value = 0


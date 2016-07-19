import re
import chesspieces

RANK_REGEX = re.compile(r"^[A-Z][1-8]$")
STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


class ChessBoard(dict):

    def __init__(self):
        self.piece_locations = []
        self.build_from_fen(STARTING_FEN)
        self.fen_position = STARTING_FEN

    def __getitem__(self, square):
        if square is not None:
            square = square.upper()
            if super(ChessBoard, self).__contains__(square):
                item = super(ChessBoard, self).__getitem__(square)
                if isinstance(item, chesspieces.Piece):
                    return item.get_piece_type()
                else:
                    return item

    def build_from_fen(self, fen):
        """
            Import state from FEN notation
            'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
            :param fen:
        """
        self.clear()
        self.piece_locations[:] = []
        # Split data
        self.fen_position = fen
        fen = fen.split(' ')
        nextmovecolor = 'white' if fen[1] == 'w' else 'black'

        def addspaces(match):
            return ' ' * int(match.group(0))

        fen_board = reversed((re.compile(r'\d').sub(addspaces, fen[0])).split('/'))

        for fen_row, row in enumerate(fen_board):
            for fen_column, item in enumerate(row):
                square = self.letter_notation((fen_row + 1, fen_column + 1))
                if item != ' ':
                    piece = chesspieces.Piece(item).get_piece_type()
                    self[square] = piece
                    if nextmovecolor == piece.color:
                        self.piece_locations.append(square)
                else:
                    self[square] = None

        return self

    @staticmethod
    def get_coordinates_on_board(english_notation):
        x_axis = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8}
        english_notation = english_notation.upper()
        column = x_axis[english_notation[0]]
        row = int(english_notation[1])
        return row, column

    def get_position(self):
        return self.fen_position

    def letter_notation(self, coordinates):
        """
        Converts coordinates to english notation i.e. 'e4'
        :param coordinates:
        :return:
        """
        row, column = coordinates[0], coordinates[1]
        x_axis = tuple('ABCDEFGH')
        y_axis = tuple(range(1, 9))
        if not self.is_in_bounds((row, column)):
            return
        return x_axis[column - 1] + str(y_axis[row - 1])

    def get_piece_locations(self):
        return self.piece_locations

    @staticmethod
    def is_in_bounds(coordinates):
        x, y = coordinates[0], coordinates[1]
        return 1 <= x <= 8 and 1 <= y <= 8



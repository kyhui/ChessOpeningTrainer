import chesspieces as chesspiece
import chessboard as board
import chessrules as rules
import chessnotation as notation
import traceback

FEN_STARTING = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


class Completed(Exception):
    def __init__(self, value):
        self.value = value


class ChessGame(dict):
    """
       Board

       A simple chessboard class

       TODO:

        * PGN export
        * En passant
        * Castling
        * Promoting pawns
        * Fifty-choice rule
    """

    player_turn = 'w'
    castling = 'KQkq'
    en_passant = '-'
    half_move = 0
    fullmove_number = 1

    def __init__(self):
        self.chessboard = board.ChessBoard()
        self.rulebook = rules.ChessRules()
        self.notebook = notation.ChessNotation()

    def try_move(self, move):
        try:
            # Deal with castling
            if move in ['0-0', '0-0-0', 'O-O', 'O-O-O']:
                self.__try_castling(move)
                return
            # Pawn choice
            elif len(move) == 2:
                piece_type = chesspiece.get_piece_from_notation(
                    'p' if self.player_turn == 'b' else 'P')
                ending_square = move.upper()
            # Piece choice or pawn capture. pieces must be upper case
            elif len(move) == 3:
                if move[0].isupper():
                    piece_type = chesspiece.get_piece_from_notation(
                        move[0].lower() if self.player_turn == 'b' else move[0].upper())
                else:
                    piece_type = chesspiece.get_piece_from_notation(
                        'p' if self.player_turn == 'b' else 'P')
                ending_square = move[1::].upper()
            elif len(move) == 4:
                piece_type = chesspiece.get_piece_from_notation(
                    move[0].lower() if self.player_turn == 'b' else move[0].upper())
                ending_square = move[2::]
            else:
                raise rules.InvalidMove(move)

            # Validate all pieces movements given a piece_type
            all_my_pieces = self.chessboard.get_piece_locations()
            for square in all_my_pieces:
                piece = self.chessboard[square]
                if (isinstance(piece_type, type(piece)) and
                        self.rulebook.valid_move(square + ending_square, self.chessboard)):
                    self.__move(square, ending_square)

        except rules.InvalidMove as ex:
            print "Failed to make choice: ", ex.move, "because: \n", traceback.format_exc()
            raise rules.InvalidMove(ex.move)
        except TypeError as ex:
            print "Error for choice:", move, "Error:", traceback.format_exc()

    # Move a piece from start to end without choice validation
    def __move(self, starting_square, ending_square):
        starting_square, ending_square = starting_square.upper(), ending_square.upper()
        piece = self.chessboard[starting_square]
        end = self.chessboard[ending_square]
        if self.player_turn == 'b':
            self.player_turn = 'w'
            self.fullmove_number += 1
        else:
            self.player_turn = 'b'
        self.half_move += 1
        # reset half_move clock on capture or pawn choice
        if isinstance(end, chesspiece.Piece) or isinstance(piece, chesspiece.Pawn):
            self.half_move = 0
        # add notation
        self.notebook.add_move(piece.fen.upper() if not isinstance(piece, chesspiece.Pawn) else '' + ending_square)
        # choice the piece
        del self.chessboard[starting_square]
        self.chessboard[ending_square] = piece
        self.build_fen()

    def __try_castling(self, move):
        color = 'white' if self.player_turn == 'w' else 'black'
        if move == '0-0' or move == 'O-O':
            self.__king_side_castle()
        elif move =='0-0-0' or move == 'O-O-O':
            self.__queen_side_castle()

        if self.player_turn == 'w':
            self.player_turn = 'w'
            self.fullmove_number += 1
        else:
            self.player_turn = 'b'
        self.half_move += 1
        # add notation
        self.notebook.add_move(move)
        self.build_fen()

    # make moves for king side castle without choice validation
    def __king_side_castle(self):
        if self.player_turn == 'w':
            king = self.chessboard['E1']
            rook = self.chessboard['H1']
            del self.chessboard['E1']
            del self.chessboard['H1']
            self.chessboard['G1'] = king
            self.chessboard['F1'] = rook
        elif self.player_turn == 'b':
            king = self.chessboard['E8']
            rook = self.chessboard['H8']
            del self.chessboard['E8']
            del self.chessboard['H8']
            self.chessboard['G8'] = king
            self.chessboard['F8'] = rook

    # make moves for queen side castle without choice validation
    def __queen_side_castle(self):
        if self.player_turn == 'w':
            king = self.chessboard['E1']
            rook = self.chessboard['A1']
            del self.chessboard['E1']
            del self.chessboard['A1']
            self.chessboard['C1'] = king
            self.chessboard['D1'] = rook
        elif self.player_turn == 'b':
            king = self.chessboard['E8']
            rook = self.chessboard['A8']
            del self.chessboard['E8']
            del self.chessboard['A8']
            self.chessboard['C8'] = king
            self.chessboard['D8'] = rook

    # build fen notation string
    def build_fen(self):
        x_axis = tuple('ABCDEFGH')
        y_axis = tuple(range(1, 9))

        result = ''
        for number in y_axis[::-1]:
            blanks = 0
            for letter in x_axis:
                piece = self.chessboard[letter + str(number)]
                if isinstance(piece, chesspiece.Piece):
                    if blanks != 0:
                        result += str(blanks) + piece.fen
                        blanks = 0
                    else:
                        result += piece.fen
                else:
                    blanks += 1
            result += ('' if blanks == 0 else str(blanks)) + ('/' if number > 1 else '')

        castling_privelages = self.rulebook.get_castling_rights()
        if not castling_privelages[0]: self.castling = self.castling.replace('K', '')
        if not castling_privelages[1]: self.castling = self.castling.replace('Q', '')
        if not castling_privelages[2]: self.castling = self.castling.replace('k', '')
        if not castling_privelages[3]: self.castling = self.castling.replace('q', '')

        result += " " + (" ".join([self.player_turn[0],
                                   self.castling,
                                   self.en_passant,
                                   str(self.half_move),
                                   str(self.fullmove_number)]))

        self.chessboard.build_from_fen(result)
        return result

    def get_position(self):
        return self.chessboard.get_position()
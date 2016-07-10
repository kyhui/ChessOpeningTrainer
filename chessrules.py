import chesspieces as chesspiece
from copy import deepcopy


class ChessError(Exception): pass


class InvalidColor(ChessError): pass


class InvalidMove(ChessError):
    def __init__(self, move):
        self.move = move


class Check(ChessError): pass


class CheckMate(ChessError): pass


class Draw(ChessError): pass


class NotYourTurn(ChessError): pass


class ChessRules:
    def __init__(self):
        self.chessboard = None
        self.has_king_moved = [False, False] # [white king, black king]
        # [white king side rook, white queen side rook, black king side rook, black queen side rook]
        self.has_rook_moved = [False, False, False, False]

    def valid_move(self, move, chessboard):
        self.chessboard = chessboard
        starting_square = move[:2]
        ending_square = move[2:]
        selected_piece = self.chessboard[starting_square]
        current_valid_moves = self.__valid_moves_for_piece_in_position(selected_piece, starting_square)

        def is_my_king(item):
            return isinstance(self.chessboard[item], chesspiece.King) \
                   and self.chessboard[item].color == selected_piece.color

        my_king = filter(is_my_king, self.chessboard.keys())[0]

        is_valid_move = ending_square in current_valid_moves and not (self.__am_in_check(my_king)
            and not self.__will_be_in_check(move, my_king))
        if is_valid_move and (isinstance(selected_piece, chesspiece.King)
                              or isinstance(selected_piece, chesspiece.Rook)):
            self.__update_castling_flags(starting_square)
        return is_valid_move

    def __update_castling_flags(self, startingsquare):
        piece = self.chessboard[startingsquare]
        if isinstance(piece, chesspiece.King):
            if not self.has_king_moved[1] and piece.color == 'black':
                self.has_king_moved[1] = True
            elif not self.has_king_moved[0] and piece.color == 'white':
                self.has_king_moved[0] = True
        elif isinstance(piece, chesspiece.Rook):
            rook_homes = {'H1': 0, 'A1': 1, 'H8': 2, 'A8': 3}
            index = rook_homes.get(startingsquare)
            if index is not None:
                self.has_rook_moved[index] = True

    def __valid_moves_for_piece_in_position(self, piece, startsquare):
        if isinstance(piece, chesspiece.Pawn):
            return self.__possible_moves_for_pawn(piece.color, startsquare)
        elif isinstance(piece, chesspiece.Knight):
            return self.__possible_moves_for_knight(startsquare)
        elif isinstance(piece, chesspiece.Bishop):
            return self.__possible_moves_on_board(startsquare, False, True, 8)
        elif isinstance(piece, chesspiece.Rook):
            return self.__possible_moves_on_board(startsquare, True, False, 8)
        elif isinstance(piece, chesspiece.Queen):
            return self.__possible_moves_on_board(startsquare, True, True, 8)
        elif isinstance(piece, chesspiece.King):
            return self.__possible_moves_on_board(startsquare, True, True, 1)

    def __possible_moves_on_board(self, startsquare, orthogonal, diagonal, distance):
        possible_moves_in_coordinates = []
        orth = ((-1, 0), (0, -1), (0, 1), (1, 0))
        diag = ((-1, -1), (-1, 1), (1, -1), (1, 1))

        start = self.chessboard.get_coordinates_on_board(startsquare)
        if orthogonal and diagonal:
            directions = diag + orth
        elif diagonal:
            directions = diag
        elif orthogonal:
            directions = orth

        for horizontal, vertical in directions:
            for move in range(1, distance + 1):
                x = start[0] + move * horizontal
                y = start[1] + move * vertical
                end = x, y
                endsquare = self.chessboard.letter_notation(end)
                if endsquare not in self.chessboard.get_piece_locations():
                    possible_moves_in_coordinates.append((x, y))
                elif endsquare in self.chessboard.get_piece_locations():
                    break

        return set(self.convert_list_to_english_notation(possible_moves_in_coordinates))

    def __possible_moves_for_pawn(self, color, square):

        if color == 'white':
            homerow, direction, enemy = 2, 1, 'black'
        else:
            homerow, direction, enemy = 7, -1, 'white'

        possible_moves_in_coordinates = []

        # Moving
        start = self.chessboard.get_coordinates_on_board(square)
        x, y = start[0], start[1]
        forward = x + direction, y
        key = self.chessboard.letter_notation(forward)

        # Can we choice forward?
        if isinstance(self.chessboard[key], type(None)):
            possible_moves_in_coordinates.append(forward)
            if x == homerow:
                # If pawn in starting square we can do a double choice
                double_forward = x + direction * 2, y
                key = self.chessboard.letter_notation(double_forward)
                if not isinstance(self.chessboard[key], chesspiece.Piece):
                    possible_moves_in_coordinates.append(double_forward)

        # Attacking
        for diagonal in [-1, 1]:
            attack = x + direction, y + diagonal
            key = self.chessboard.letter_notation(attack)
            if isinstance(self.chessboard[key], chesspiece.Piece) and self.chessboard[key].color != color:
                possible_moves_in_coordinates.append(attack)

        # TODO: En passant

        return set(self.convert_list_to_english_notation(possible_moves_in_coordinates))

    def __possible_moves_for_knight(self, square):
        """
        Find all possible moves a Knight can make in a given position
        :param square: square that the knight is on in english notation i.e. 'e4'
        :return:
        """
        possible_moves_in_coordinates = []
        start = self.chessboard.get_coordinates_on_board(square)
        x, y = start[0], start[1]
        deltas = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))

        for horizontal, vertical in deltas:
            end = x + horizontal, y + vertical
            if self.chessboard.letter_notation(end) not in self.chessboard.get_piece_locations():
                possible_moves_in_coordinates.append(end)

        return set(self.convert_list_to_english_notation(possible_moves_in_coordinates))

    def __am_in_check(self, my_king_square):
        def is_piece(item):
            return isinstance(self.chessboard[item], chesspiece.Piece) \
                   and self.chessboard[item].color != self.chessboard[my_king_square].color
        all_enemy_squares = filter(is_piece, self.chessboard.keys())

        danger_squares = set()
        for enemy_square in all_enemy_squares:
            enemy = self.chessboard[enemy_square]
            danger_squares.update(self.__valid_moves_for_piece_in_position(enemy, enemy_square))
        return my_king_square in danger_squares

    def __will_be_in_check(self, move, my_king_square):

        starting_square = move[:2]
        ending_square = move[2:]
        backup = deepcopy(self.chessboard)
        self.chessboard = backup
        piece = self.chessboard[starting_square]
        del self.chessboard[starting_square]
        self.chessboard[ending_square] = piece
        tmp = self.__am_in_check(my_king_square)
        return tmp

    def get_castling_rights(self):
        castling_privelages = [False, False, False, False]
        if not self.has_king_moved[0]:
            castling_privelages[0] = False if self.has_rook_moved[0] else True
            castling_privelages[1] = False if self.has_rook_moved[1] else True
        else:
            castling_privelages[0] = False
            castling_privelages[1] = False
        if not self.has_king_moved[1]:
            castling_privelages[2] = False if self.has_rook_moved[2] else True
            castling_privelages[3] = False if self.has_rook_moved[3] else True
        else:
            castling_privelages[2] = False
            castling_privelages[3] = False

        return castling_privelages

    def is_castle_possible(self, color, side):
        index = (0 if color == 'white' else 2) + (0 if side == 'king' else 1)
        castling_rights = self.get_castling_rights()
        king_moves = ['E1F1G1','E1D1C1', 'E8F8G8', 'E8D8C8']
        rook_moves = ['H1F1', 'A1D1', 'H8F8', 'E8C8']
        king = self.chessboard[king_moves[index][0:2]]
        rook = self.chessboard[rook_moves[index][0:2]]

        def can_rook_move():
            return isinstance(rook, chesspiece.Rook) \
                and self.valid_move(rook_moves[index], self.chessboard)

        def can_king_move():
            my_king_square = king_moves[index][0:2]
            first_move = king_moves[index][0:4]
            second_move = king_moves[index][2::]
            return isinstance(king, chesspiece.King) \
                and not self.__will_be_in_check(first_move, my_king_square) \
                and not self.__will_be_in_check(second_move, my_king_square)

        if castling_rights[index] and can_rook_move() and can_king_move():
            if color == 'white':
                self.has_king_moved[0] = True
            else:
                self.has_king_moved[1] = True
            return True
        return False

    def convert_list_to_english_notation(self, list):
        for i, item in enumerate(list):
            if self.chessboard.is_in_bounds(item):
                list[i] = self.chessboard.letter_notation(item)
        return list

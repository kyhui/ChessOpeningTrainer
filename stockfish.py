import pexpect
import os
import re
import random


class StockFish:
    moves_to_choose_from = 3
    position = None
    opening = None

    def __init__(self, opening = "QueensGambit"):
        base_path = os.path.dirname(os.path.dirname(__file__))
        self.opening = opening
        self.child = pexpect.spawn(base_path + '/engine/stockfish/stockfish')
        self.child.sendline('setoption name MultiPV value ' + str(self.moves_to_choose_from))
        self.child.maxsize = 1
        self.child.timeout = 60 * 20

    def get_engine_move(self, position):
        self.position = position
        return self.get_best_move()

    def get_best_move(self):
        # variations = book.get_opening_variations(self.opening)
        all_moves = self.get_all_moves()
        best_move = random.choice(all_moves)
        return [best_move[:2], best_move[2:4]]
        # for choice in all_moves:
        #     for variation in variations:
        #         if choice in variation:
        #             return choice

    def get_all_moves(self):
        self.child.sendline('position fen ' + self.position)
        self.child.sendline('go depth 1')
        self.child.expect('\.*')
        all_moves = []
        for line in self.child:
            if re.match('^info', line):
                all_moves.append(line[-6:-2])
                if len(all_moves) == 3:
                    return all_moves


import re
import os
import csv
from chessgame import ChessGame, Completed
from chessrules import InvalidMove, InvalidColor

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def crunch_data(relative_data_file_name, relative_training_data_file):
    opening_book = {}
    data = PGNParser(BASE_DIR + relative_data_file_name)
    game_list = data.get_games()
    for game in game_list:
        if game is not None:
            first_moves = game[0], game[1], game[2]
            if opening_book.get(first_moves) is None:
                tmp = [game]
                opening_book[first_moves] = tmp
            else:
                opening_book[first_moves].append(game)

    response_map = {}
    correct_move_map = {}
    data_file = open(BASE_DIR + relative_training_data_file, 'wb')
    field_names = ['position', 'response', 'correct_move']
    writer = csv.DictWriter(data_file, fieldnames=field_names)
    writer.writeheader()
    for move_list in game_list:
        new_game = ChessGame()
        for move_number in range(0, len(move_list), 2):
            try:
                move = move_list[move_number]
                new_game.try_move(move)

                position = new_game.get_position()
                response = move_list[move_number + 1]
                correct_move = move_list[move_number + 2]

                if response_map.get(position) is None:
                    tmp = [response]
                    response_map[position] = tmp
                    tmp2 = [correct_move]
                    correct_move_map[position] = tmp2
                else:
                    response_map.get(position).append(response)
                    correct_move_map.get(position).append(correct_move)

                response = move_list[move_number + 1]
                new_game.try_move(response)
            except IndexError:
                print "Finished list with last choice", move_list[move_number - 1]
            except:
                return

    for position in response_map.keys():
        writer.writerow({'position': position, 'response': ", ".join(response_map.get(position)),
                         'correct_move': ", ".join(correct_move_map.get(position))})


def read_data_into_memory():
    memory_db = {}
    try:
        reader = csv.DictReader(open(BASE_DIR + '/app/reports/trainerdb.csv', 'rb'))
    except IOError:
        crunch_data('/app/openings/test.pgn', '/app/reports/trainerdb.csv')
        reader = csv.DictReader(open(BASE_DIR + '/app/reports/trainerdb.csv', 'rb'))

    for row in reader:
        memory_db[row['position']] = (row['response'], row['correct_move'])
    return memory_db


class PGNParser:

    def __init__(self, file_name):
        self.games = []
        self.pgn_reader = open(file_name, 'rb')
        self.__parse_file()

    def __parse_file(self):
        game_info = []
        game_moves = ''

        def extract_moves(line_with_moves):
            move_list = []
            half_moves_to_return = 22
            tmp = re.split('\s?\d+\.', line_with_moves)
            for item in tmp:
                if len(item) > 0:
                    move_list += re.split(' ', item.replace('x', '').replace('+', ''))
            return None if len(move_list) < half_moves_to_return else move_list[:half_moves_to_return]

        for line in self.pgn_reader:
            if line != '\n':
                # at the start of a new game dump moves into games list
                if 'Event' in line and len(game_moves) > 0:
                    self.games.append(extract_moves(game_moves))
                    game_moves = ''
                    game_info_item = re.findall(r'"(.*?)"', line)
                    if len(game_info_item) > 0:
                        game_info.append(game_info_item[0])
                # a line with moves on it
                elif re.search(r'(\s?\d+\.)', line) is not None and '[' not in line:
                    game_moves += line.replace('\r', '')
                else:
                    game_info_item = re.findall(r'"(.*?)"', line)
                    if len(game_info_item) > 0:
                        game_info.append(game_info_item[0])
        # append the last game in the pgn file to games
        self.games.append(extract_moves(game_moves))

    def get_games(self):
        return self.games

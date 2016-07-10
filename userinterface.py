from chessgame import ChessGame, Completed
import chessdatahandler
import random
import logging
from Tkinter import *


class UserInterface:

    output_text = None
    input_text = None
    correct_move = None

    def __init__(self):
        self.master = Tk()
        self.new_game = ChessGame()
        self.move_base = chessdatahandler.read_data_into_memory()
        self.choice = StringVar()
        self.startgame()

    def startgame(self):
        response = self.logic('e4')
        result = "Game starts with e4 " + response + " input correct response"
        self.display(result)

    def playgame(self):
        if self.correct_move == self.choice.get():
            try:
                response = self.logic(self.choice.get())
                result = ("Correct, Computer responded with " + response)
                self.output_text.configure(text=result)
                self.input_text.delete(0, 'end')
            except Completed as complete:
                return complete.value
        else:
            logging.error("Incorrect Move")
            result = "Incorrect Move.  Select hint for correct answer"
            self.output_text.configure(text=result)

    def getanswer(self):
        self.output_text.configure(text="Correct move is " + self.correct_move)

    def display(self, starttext):
        f1 = Frame(self.master, width=200, height=100)
        f2 = Frame(self.master, width=200, height=100)
        self.output_text = Label(f1, text=starttext)
        self.input_text = Entry(f1, textvariable=self.choice)
        Button(f2, text='send', command=lambda:self.playgame()).pack(side=LEFT)
        Button(f2, text='quit', command=lambda:self.master.destroy()).pack(side=LEFT)
        Button(f2, text='hint', command=lambda:self.getanswer()).pack(side=LEFT)
        self.output_text.pack(side=TOP)
        self.input_text.pack(side=TOP)
        f1.pack()
        f2.pack()
        self.master.mainloop()

    def logic(self, move):
        self.new_game.try_move(move)
        move_pair = self.move_base.get(self.new_game.get_position())
        responses = move_pair[0].split(',')
        correct_moves = move_pair[1].split(',')
        index = random.randrange(0, len(responses))
        self.new_game.try_move(responses[index].strip())
        self.correct_move = correct_moves[index].strip()
        return responses[index].strip()

ui = UserInterface()
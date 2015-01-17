#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# TODO: calc # of mines based on board size?
#   generate map after first click?
import sys
from random import randint
from time import sleep

from board import Dir
from mines_lib import MinesBoard, Mines, Tile
from avkutil import Term

size        = 12
num_mines   = randint(8, 16)
padding     = 2, 1
blink_speed = 0.1

commands    = {
                r'\x1b[D' : "left",
                r'\x1b[C' : "right",
                r'\x1b[A' : "up",
                r'\x1b[B' : "down",

                't' : "toggle",
                'm' : "mark",
                '\n': "move",
                ' ' : "move",
                'q' : "quit",
                }

class Commands:
    player = None
    commands = commands

    def __getitem__(self, cmd):
        return getattr(self, self.commands[cmd])

    def move_dir(self, dir):
        loc = board.nextloc(board.current, dir)
        self.highlight(loc)

    def down(self):
        self.move_dir(Dir(0,1))
    def up(self):
        self.move_dir(Dir(0,-1))
    def right(self):
        self.move_dir(Dir(1,0))
    def left(self):
        self.move_dir(Dir(-1,0))

    def toggle(self):
        if board.hl_visible:
            board.hl_visible = False
            board.draw()
        else:
            i = board[board.current]
            board[board.current] = '*'
            board.draw()
            board[board.current] = i
            board.hl_visible = True

    def move(self):
        loc = board.current
        board.hl_visible = False
        board.reveal(board[loc])
        for _ in range(2):
            self.blink_tile(board[loc])
        return board[loc]

    def blink_tile(self, tile):
        tile.hidden = not tile.hidden
        sleep(blink_speed)
        board.draw()

    def mark(self):
        loc = board.current
        board.hl_visible = False
        board[loc].toggle_mark()
        return board[loc]

    def highlight(self, loc):
        if not loc: return
        i = board[loc]
        board[loc] = '*'
        board.draw()
        board[loc] = i
        board.current = loc
        board.hl_visible = True

    def quit(self):
        sys.exit()


class BasicInterface:
    def run(self):
        self.term = Term()
        while True:
            board.draw()
            tile = self.get_move()
            mines.check_end(tile)

    def get_move(self):
        """Get user command and return the tile to reveal."""
        while True:
            cmd = self.term.getch()
            try:
                val = commands[cmd]()
                if val:
                    return val
            except KeyError:
                print("unknown command:", cmd)


if __name__ == "__main__":
    board = MinesBoard(size, Tile, num_mines=num_mines, num_grid=False, padding=padding)
    mines = Mines(board)
    commands = Commands()
    try:
        BasicInterface().run()
    except KeyboardInterrupt:
        pass

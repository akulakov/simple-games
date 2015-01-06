#!/usr/bin/env python3

# Imports {{{
import sys
from random import choice as rndchoice

from utils import enumerate1, sjoin, TextInput, space, nl
from board import Board, Loc, BaseTile, Dir
from avkutil import Term

size    = 9
blank   = '.'
tiletpl = '%2s'
rng3    = range(3)
rng9    = range(9)
offsets = (0, 3, 6)

# in the format produced by QQwing program; just one puzzle for testing
puzzles    = [".13.....22.....48....7...19...9..8..7......2....3.......263.9..4.9.7.6....149...8"]

commands    = {
                b'a' : "left",
                b'd' : "right",
                b'w' : "up",
                b's' : "down",
                b't' : "toggle",
                b'\n': "move",
                b' ' : "move",
                b'q' : "quit",
                }

# }}}


class Tile(BaseTile):
    initial = blank = False
    num     = None

    def __repr__(self):
        return str(self.num) if self.num else blank

    def __eq__(self, other):
        return bool(self.num == other)


class Number(Tile):
    def __init__(self, num):
        super(Number, self).__init__()
        self.num = int(num)

class Blank(Tile):
    pass
class Initial(Number):
    pass


class SudokuBoard(Board):
    def __init__(self, size, def_tile, puzzle):
        super(SudokuBoard, self).__init__(size, def_tile)
        self.hl_visible = False
        self.current = Loc(0,0)

        for tile, val in zip(self, puzzle):
            if val != blank:
                self[tile] = Initial(val)

        self.regions = [self.make_region(xo, yo) for xo in offsets for yo in offsets]

        lines = []
        for n in rng9:
            lines.extend(( [Loc(x, n) for x in rng9], [Loc(n, y) for y in rng9] ))
        self.lines = lines

    def make_region(self, xo, yo):
        """Make one region at x offset `xo` and y offset `yo`."""
        return [ Loc(xo + x, yo + y) for x in rng3 for y in rng3 ]

    def draw(self):
        print(nl*5)
        def ljoin(L):
            return sjoin(L, space, tiletpl)

        for n, row in enumerate1(self.board):
            print(space,
                  ljoin(row[:3]),
                  space,
                  ljoin(row[3:6]),
                  space,
                  ljoin(row[6:9]),
                  nl)
            if n in (3,6):
                print()


class Sudoku(object):
    winmsg = "Solved!"

    def valid_move(self, loc, val):
        if board[loc].initial:
            return False

        for reg_line in board.lines + board.regions:
            if loc in reg_line and val in (board[loc] for loc in reg_line):
                return False
        return True

    def check_end(self):
        if not any(t.blank for t in board):
            print(nl, self.winmsg)
            sys.exit()

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

    def move(self, val):
        loc = board.current
        if sudoku.valid_move(loc, val):
            board[loc] = val
            board.hl_visible = False
            return loc, val
        else:
            print("Invalid move")

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


class BasicInterface(object):
    def run(self):
        self.term = Term()

        while True:
            board.draw()
            loc, val   = self.get_move()
            board[loc] = Number(val)
            sudoku.check_end()

    def get_move(self):
        "UNUSED."
        while True:
            cmd = self.textinput.getinput()
            if sudoku.valid_move(*cmd):
                return cmd
            else:
                print(self.textinput.invalid_move)

    def get_move(self):
        while True:
            cmd = self.term.getch()
            try:
                if cmd.isdigit():
                    val = commands.move(int(cmd))
                else:
                    val = commands[cmd]()
                if val:
                    return val
            except KeyError:
                print("invalid command:", cmd)


if __name__ == "__main__":
    board    = SudokuBoard(size, Blank, rndchoice(puzzles))
    sudoku   = Sudoku()
    commands = Commands()

    try:
        BasicInterface().run()
    except KeyboardInterrupt:
        sys.exit()

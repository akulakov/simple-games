#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
from random import choice as rndchoice
from itertools import cycle
from time import sleep

from utils import Loop, TextInput, range1, first, nl
from board import Board, BaseTile, Loc, Dir
from avkutil import Term

size        = 5
pause_time  = 0.2
players     = {1: "➀➁➂➃", 2: "➊➋➌➍"}
ai_players  = [1, ]
check_moves = 15
padding     = 2, 1

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


class Tile(BaseTile):
    num = maxnum = player = None

    def __repr__(self):
        if self.player:
            n = players[self.player][self.num-1]
            # need separate representations of 'maxnum' for both players
            # if self.num == self.maxnum:
            #     return '='
            return n
        else:
            return str(self.num)

    def increment(self, player):
        """ Increment tile number; if number wraps, increment neighbour tiles.
            `bblocks.counter` is used to avoid infinite recursion loops.
        """
        if not bblocks.counter.next():
            bblocks.check_end(player)

        if self._increment(player):
            for tile in board.cross_neighbours(self):
                tile.increment(player)
            board.draw()

    def _increment(self, player):
        self.player = player
        self.num.next()
        return bool(self.num == 1)


class BlocksBoard(Board):
    def __init__(self, *args, **kwargs):
        super(BlocksBoard, self).__init__(*args, **kwargs)
        neighbours = self.neighbour_cross_locs
        self.current = Loc(0,0)
        self.hl_visible = False

        for tile in self:
            tile.maxnum = len( [self.valid(nbloc) for nbloc in neighbours(tile)] )
            tile.num    = Loop(range1(tile.maxnum))

    def ai_move(self, player):
        """Randomly choose between returning the move closest to completing a tile or a random move."""
        tiles = [t for t in self if self.valid_move(player, t)]

        to_max = lambda t: t.maxnum - t.num
        tiles.sort(key=to_max)
        loc = rndchoice( [first(tiles), rndchoice(tiles)] )
        if loc == self.current:
            self.hl_visible = False
        return loc

    def valid_move(self, player, tile):
        return bool(tile.player==player or not tile.player)


class BlockyBlocks(object):
    winmsg  = "player %s wins!"
    counter = Loop(range(check_moves))

    def __init__(self):
        self.term = Term()

    def check_end(self, player):
        """Check if game is finished."""
        if all(tile.player==player for tile in board):
            board.draw()
            print(nl, self.winmsg % player)
            sys.exit()

    def run(self):
        self.textinput = TextInput(board=board)

        for p in cycle(players.keys()):
            board.draw()
            tile = board.ai_move(p) if p in ai_players else self.get_move(p)
            tile.increment(p)
            self.check_end(p)

    def down(self):
        loc = board.nextloc(board.current, Dir(0,1))
        self.highlight(loc)

    def highlight(self, loc):
        if not loc: return
        i = board[loc]
        board[loc] = '*'
        board.draw()
        board[loc] = i
        board.current = loc
        board.hl_visible = True

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

    def up(self):
        loc = board.nextloc(board.current, Dir(0,-1))
        self.highlight(loc)

    def right(self):
        loc = board.nextloc(board.current, Dir(1,0))
        self.highlight(loc)

    def left(self):
        loc = board.nextloc(board.current, Dir(-1,0))
        self.highlight(loc)

    def move(self):
        loc = board.current
        if board.valid_move(self.cur_player, board[loc]):
            board.hl_visible = False
            return board[loc]
        else:
            print("Invalid move")

    def get_move(self, player):
        self.cur_player = player
        while True:
            cmd = self.term.getch()
            if cmd in commands:
                val = getattr(self, commands[cmd])()
                if commands[cmd] == "move" and val:
                    return val
            else:
                print("unknown command:", cmd)

    def quit(self):
        sys.exit()


if __name__ == "__main__":
    board   = BlocksBoard(size, Tile, num_grid=False, padding=padding, pause_time=pause_time)
    bblocks = BlockyBlocks()

    try:
        bblocks.run()
    except KeyboardInterrupt:
        sys.exit()

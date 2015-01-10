#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
from random import choice as rndchoice
from random import randrange
from itertools import cycle
from time import sleep

from utils import Loop, TextInput, range1, first, nl
from board import Board, BaseTile, Loc, Dir
from avkutil import Term

size             = 6
pause_time       = 0.2
players          = {1: "➀➁➂➃", 2: "➊➋➌➍"}
ai_players       = [1, ]
check_moves      = 15
padding          = 2, 1
blink_speed      = 0.1
randomize_option = False

commands         = {
                'a' : "left",
                'd' : "right",
                'w' : "up",
                's' : "down",
                't' : "toggle",
                '\n': "move",
                ' ' : "move",
                'q' : "quit",
                }

p=print

class Tile(BaseTile):
    num = maxnum = player = blank = None

    def __repr__(self):
        if self.blank:
            return ' '
        if self.player:
            n = players[self.player][self.num-1]
            # need separate representations of 'maxnum' for both players
            # if self.num == self.maxnum:
            #     return '='
            return n
        else:
            return str(self.num)

    def increment(self, player, initial=True):
        """ Increment tile number; if number wraps, increment neighbour tiles.

            `bblocks.counter` is used to avoid infinite recursion loops.
            IF initial, get list of tiles, and blink all of them + original tile; otherwise, return list of tiles
        """
        end = False
        if not bblocks.counter.next():
            end = bblocks.check_end(player)

        tiles = []
        do_wrap = self._increment(player)
        if do_wrap and not end:
            for tile in board.cross_neighbours(self):
                tiles.append(tile)
                tiles.extend(tile.increment(player, initial=False))

        if initial or end:
            self.blink_tiles(set(tiles + [self]))
            if end:
                bblocks.end(player)
        else:
            return tiles

    def blink_tiles(self, tiles):
        for _ in range(2):
            for tile in tiles:
                tile.blank = not tile.blank
            sleep(blink_speed)
            board.draw()

    def _increment(self, player):
        self.player = player
        self.num.next()
        return bool(self.num == 1)  # return True if wrapping around


class BlocksBoard(Board):
    def __init__(self, *args, **kwargs):
        super(BlocksBoard, self).__init__(*args, **kwargs)
        neighbours = self.neighbour_cross_locs
        self.current = Loc(0,0)
        self.hl_visible = False

        for tile in self:
            tile.maxnum = len( [self.valid(nbloc) for nbloc in neighbours(tile)] )
            tile.num    = Loop(range1(tile.maxnum))
            if randomize_option:
                for _ in range(randrange(0, tile.maxnum)):
                    tile.num.next()

    def ai_move(self, player):
        """Randomly choose between returning the move closest to completing a tile or a random move."""
        tiles = [t for t in self if self.valid_move(player, t)]

        # tiles.sort(key=to_max)
        to_max = lambda t: t.maxnum - t.num
        loc = rndchoice( [min(tiles, key=to_max), rndchoice(tiles)] )
        if loc == self.current:
            self.hl_visible = False
        return loc

    def valid_move(self, player, tile):
        return bool(tile.player==player or not tile.player)


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
        if board.valid_move(self.player, board[loc]):
            board.hl_visible = False
            return board[loc]
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


class BlockyBlocks(object):
    winmsg  = "player %s wins!"
    counter = Loop(range(check_moves))

    def __init__(self):
        self.term = Term()

    def check_end(self, player):
        """Check if game is finished."""
        return all(tile.player==player for tile in board)

    def end(self, player):
        board.draw()
        print(nl, self.winmsg % player)
        sleep(2)
        sys.exit()

    def run(self):
        for p in cycle(players.keys()):
            board.draw()
            tile = board.ai_move(p) if p in ai_players else self.get_move(p)
            tile.increment(p)
            if self.check_end(p):
                self.end(p)

    def get_move(self, player):
        commands.player = player
        while True:
            cmd = self.term.getch()
            try:
                val = commands[cmd]()
                if val:
                    return val
            except KeyError:
                print("unknown command:", cmd)


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg and arg[0] == '-r':
        randomize_option = True

    commands = Commands()
    board   = BlocksBoard(size, Tile, num_grid=False, padding=padding, pause_time=pause_time)
    bblocks = BlockyBlocks()

    try:
        bblocks.run()
    except KeyboardInterrupt:
        sys.exit()

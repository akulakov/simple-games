#!/usr/bin/env python3
# coding: utf-8

import sys
import random
from avkutil import color, Term

"""
Game1
colors:
black red green brown blue purple cyan lgray gray lred lgreen yellow lblue pink lcyan white
"""

term = Term()

max_size = 75
board = [' ']*max_size
loc = 40
player = color(u'☺', "green")

def getkey(n=1):
    s = ''
    for _ in range(n):
        s += term.getch()
    return s

def flush():
    sys.stdout.flush()

def display():
    term.clear()
    # print("loc", loc)
    print(''.join(board))
    print("> ", end='')
    flush()

def up(): ...
def down(): ...

# -----------------------------------------------------------------------------------------------

"""
Suggested features to add:

    - handle end of game board
    - second dimension
    - additional levels
    - coins / gems to gather
    - teleport
    - doors
    - monsters
    - robots
    - show inventory
"""


def right():
    """Move to the right."""
    global loc          # allow to change loc
    board[loc] = ' '    # put empty space
    loc += 1            # change location by +1
    board[loc] = player # place player at new location

def left():
    """Move to the left."""
    global loc
    board[loc] = ' '
    loc -= 1
    board[loc] = player

def teleport():
    global loc
    board[loc] = ' '
    loc = random.randint(0, max_size)
    board[loc] = player

def game1():
    """Play game."""
    board[loc] = player     # place player at original location

    while True:             # loop continuously
        display()           # show playing board
        c = term.getch()    # get user input

        if c == 'q':       # Quit game
            break

        if c == 'a': left()    # if key is 'a', move left
        if c == 'd': right()
        if c == 't': teleport()

game1()

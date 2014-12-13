#!/usr/bin/env python3

import sys
from avkutil import color, Term

"""
Game1
colors:
black red green brown blue purple cyan lgray gray lred lgreen yellow lblue pink lcyan white
"""

term = Term()

board = [' ']*75
loc = 40
player = color('@', "green")

def getkey(n=1):
    s = b''
    for _ in range(n):
        s += term.getch()
    return s

def flush():
    sys.stdout.flush()

def display():
    term.clear()
    print(''.join(board))
    print("> ", end='')
    flush()

def up(): ...
def down(): ...
# if c == b'w': up()
# if c == b's': down()

# -----------------------------------------------------------------------------------------------


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

def game1():
    """Play game."""
    board[loc] = player     # place player at original location

    while True:             # loop continuously
        display()           # show playing board
        c = term.getch()    # get user input

        if c == b'q':       # Quit game
            break

        if c == b'a': left()
        if c == b'd': right()

game1()

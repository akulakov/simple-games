import sys
from board import Dir

class BaseCommands:
    def __init__(self, board, commands):
        self.commands = commands
        self.board = board

    def __getitem__(self, cmd):
        return getattr(self, self.commands[cmd])

    def move_dir(self, dir):
        loc = self.board.nextloc(self.board.current, dir)
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
        board = self.board
        if board.hl_visible:
            board.hl_visible = False
            board.draw()
        else:
            i = board[board.current]
            board[board.current] = '*'
            board.draw()
            board[board.current] = i
            board.hl_visible = True

    def highlight(self, loc):
        board = self.board
        if not loc: return
        i = board[loc]
        board[loc] = '*'
        board.draw()
        board[loc] = i
        board.current = loc
        board.hl_visible = True

    def quit(self):
        sys.exit()

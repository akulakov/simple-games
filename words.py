#!/usr/bin/env python3

# Imports {{{
import sys
from random import choice as rndchoice

from utils import TextInput, sjoin, enumerate1, range1, first, space, nl
from avkutil import Term
from commands import BaseCommands


num_words      = 5
hidden_char    = '_'
lettertpl      = "%2s"
initial_hide   = 0.7                # how much of the word to hide, 0.7 = 70%
randcmd        = 'r'                # reveal random letter; must be one char
limit9         = True               # only use 9-or-less letter words
random_reveals = num_words // 2     # allow player to reveal x random letters

wordsfn        = "words"

guesses_divby  = 3      # calc allowed wrong guesses by dividing total # of letters by this number
blink_speed = 0.1

move_cmds = (' ', '\n')
commands    = {
                r'\x1b[D' : "left",
                r'\x1b[C' : "right",
                r'\x1b[A' : "up",
                r'\x1b[B' : "down",

                'r' : "random",
                '\n': "move",
                ' ' : "move",
                'q' : "quit",
                }

# }}}

class Commands(BaseCommands):
    def __init__(self, term, commands):
        self.commands = commands
        self.term = term

    def move_dir(self, dir):
        x, y = words.current
        x   += dir.x
        y   += dir.y
        x = max(0,x)
        y = max(0,y)
        if y >= len(words):
            y = len(words)-1
        if x >= len(words[y]):
            x = len(words[y])-1
        words.current = x, y
        words.hl_visible = True
        words.display()

    def move(self):
        c = self.term.getch("> ")
        words.guess(c)
        words.hl_visible = False
        words.display()

    def random(self):
        words.randreveal()
        words.display()


class Word(object):
    def __init__(self, word):
        self.hidden = []
        self.word   = word.rstrip()
        self.gen_hidden(initial_hide)

    def display(self, cursor=False, i=0):
        word = list( (hidden_char if n in self.hidden else l) for n, l in enumerate(self.word) )
        if cursor and words.hl_visible:
            word[i] = '*'
        return sjoin(word, space * self.spacing(), lettertpl)

    def __len__(self):
        return len(self.word)

    def spacing(self):
        return 2 if len(self) > 9 else 1

    def randreveal(self):
        self.reveal( self.word[rndchoice(self.hidden)] )

    def guess(self, i, letter):
        """Reveal all instances of `l` if word[i] == `l` & reveal random letter in one other word."""
        if i in self.hidden and self.word[i] == letter:
            self.reveal(letter)

            L = [w for w in words if w.hidden and w != self]
            if L:
                rndchoice(L).randreveal()
            return True

    def reveal(self, letter):
        """Reveal all letters equal to `letter`."""
        for n, nletter in enumerate(self.word):
            if nletter == letter:
                self.hidden.remove(n)

    def hide(self, index):
        """Hide all letters matching letter at `index`."""
        if index not in self.hidden:
            for n, nletter in enumerate(self.word):
                if nletter == self.word[index]:
                    self.hidden.append(n)

    def gen_hidden(self, hidden):
        """Hide letters according to `hidden`, e.g. if 0.7, hide 70%."""
        length       = len(self.word)
        num_to_hide  = round(length * hidden)
        letter_range = range(length)

        while len(self.hidden) < num_to_hide:
            self.hide(rndchoice(letter_range))


class Words(object):
    winmsg  = "Congratulations! You've revealed all words! (score: %d)"
    losemsg = "You've run out of guesses.."
    stattpl = "random reveals: %d | attempts: %d"

    def __init__(self, wordlist):
        self.random_reveals = random_reveals
        self.words          = set()

        while len(self.words) < num_words:
            word = Word( rndchoice(wordlist).rstrip() )
            if (limit9 and len(word)>9) or len(word) < 3:
                continue
            self.words.add(word)

        self.words   = list(self.words)
        self.guesses = sum(len(w) for w in self.words) // guesses_divby
        self.current = 0,0
        self.hl_visible = False

    def __len__(self):
        return len(self.words)

    def __getitem__(self, i):
        return self.words[i]

    def __iter__(self):
        return iter(self.words)

    def display(self):
        print(nl*25)

        for n, word in enumerate(self.words):
            cursor = n==self.current[1]
            print(space, word.display(cursor, self.current[0]), nl)

        print(self.stattpl % (self.random_reveals, self.guesses), nl)

    def randreveal(self):
        if self.random_reveals:
            rndchoice( [w for w in self if w.hidden] ).randreveal()
            self.random_reveals -= 1

    def guess(self, letter):
        x, y = self.current
        if self.guesses and not self[y].guess(x, letter):
            self.guesses -= 1

    def check_end(self):
        if not any(word.hidden for word in self):
            self.game_end(True)
        elif not (self.guesses or self.random_reveals):
            self.game_end(False)

    def game_end(self, won):
        self.display()
        msg = self.winmsg % (self.random_reveals*3 + self.guesses) if won else self.losemsg
        print(msg)
        sys.exit()


class BasicInterface(object):
    def run(self):
        while True:
            words.display()
            self.get_move()
            words.check_end()

    def get_move(self):
        while True:
            cmd = term.getch()
            try:
                val = commands[cmd]()
                if val:
                    return val
            except KeyError:
                print("unknown command:", cmd)
            words.check_end()


if __name__ == "__main__":
    term = Term()
    words = Words(open(wordsfn).readlines())
    commands = Commands(term, commands)
    BasicInterface().run()

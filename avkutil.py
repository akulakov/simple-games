#!/usr/bin/env python
"""Miscellaneous small utility functions.

    vol(vol=None) - Get or set volume using aumix.

    progress(ratio, length=40, col=1, cols=("yellow", None, "cyan"),
            nocol="=.")
        Text mode progress bar.

    yes(question, [default answer])
        i.e. if yes("erase file?", 'n'): erase_file()

    color(text, fg, [bg])
        Colorize text using terminal color codes.

    beep(times) - Beep terminal bell number of times.

    ftime(seconds) - returns h:m:s or m:s if there's no hours.

    Term() - terminal stuff
        term.size() => height, width
        term.clear() => clear terminal
        term.getch() => get one char at a time

Andrei Kulakov <ak@silmarill.org>
"""

import os
try:
    import commands
except:
    pass
import time
try:
    from termios import *
except ImportError:
    from TERMIOS import *
from types import *
from sys import stdin, stdout

dbg = 1
enable_color = 1
hotkeycol = "red"

colors = dict([c.split() for c in (     # make dict {"red": "31", ...}
  "black 30, red 31, green 32, brown 33, blue 34, purple 35, cyan 36, lgray 37, gray 1;30, "
  "lred 1;31, lgreen 1;32, yellow 1;33, lblue 1;34, pink 1;35, lcyan 1;36, white 1;37"
).split(', ')])

"\033]Pg4040ff\033\\"


class AvkError(Exception):
    def __init__(self, value): self.value = value
    def __str__(self): return repr(self.value)

def debug(*msgs):
    if dbg:
        for m in msgs: print( '###  ', m)

def replace(val, lst):
    """ Replace patterns within `val`."""
    for pat, repl in lst:
        val = val.replace(pat, repl)
    return val

def split(fname):
    """ Split filename into (name, extension) tuple."""
    lst = fname.split('.')
    if len(lst) == 1: return fname, None
    else: return str.join(lst[:-1], '.'), lst[-1]

def vol(vol=None):
    """ Set or show audio volume.

        Uses external mixer called aumix. One optional argument, vol, may
        be an int or a string. If a string, it can be of the form "+10".
    """
    if vol: os.system("aumix -v%s" % vol)
    else: return commands.getoutput("aumix -vq").split()[1][:-1]

def progress(ratio, length=40, col=1, cols=("yellow", None, "cyan"), nocol="=."):
    """ Text mode progress bar.

        ratio   - current position / total (e.g. 0.6 is 60%)
        length  - bar size
        col     - color bar
        cols    - tuple: (elapsed, left, percentage num)
        nocol   - string, if default="=.", bar is [=======.....]
    """
    if ratio > 1: ratio = 1
    elchar, leftchar = nocol
    elapsed = int(round(ratio*length))
    left = length - elapsed
    bar = (elchar*elapsed + leftchar*left)[:length]

    if col: return color(' '*elapsed, "gray", cols[0]) + color(' '*left, "gray", cols[1])
    else: return elchar*elapsed + leftchar*left

def yes(question, default=None):
    """ Get an answer for the question.

        Return 1 on 'yes' and 0 on 'no'; default may be set to 'y' or 'n';
        asks "Question? [Y/n]" (default is capitalized). Yy and Nn are
        acceptable. Question is asked until a valid answer is given.
    """
    y, n = "yn"
    if default:
        if default in "Yy": y = 'Y'
        elif default in "Nn": n = 'N'
        else:
            raise AvkError("Error: default must be 'y' or 'n'.")

    while 1:
        answer = raw_input("%s [%s/%s] " % (question, y, n))
        if default and not answer:
            return (1 if default in "Yy" else 0)
        else:
            if not answer: continue
            elif answer in "Yy": return 1
            elif answer in "Nn": return 0

def no(question, default=None):
    return not yes(question, default)

def color(text, fg, bg=None, raw=0):
    """ Return colored text.

        Uses terminal color codes; set avk_util.enable_color to 0 to return plain un-colored text.
        If fg is a tuple, it's assumed to be (fg, bg). Both colors may be 'None'.

        Raw means return string in raw form - for writing to a file instead of printing to screen.
        Leave default if not sure.
    """
    # init vars
    xterm, bgcode = 0, ''
    if not enable_color or not fg:
        return text
    if not isinstance(fg, str):
        fg, bg = fg
    opencol, closecol = "\033[", "m"
    tpl = "\033[%sm"
    if raw:
        opencol, closecol = r"\033[", r"\033[0m"
    # clear = opencol + '0' + closecol
    clear = tpl % 0
    if os.environ["TERM"] == "xterm":
        xterm = 1

    # create color codes
    if xterm and fg == "yellow":    # In xterm, brown comes out as yellow..
        fg = "brown"
    # fgcode = opencol + colors[fg] + closecol
    fgcode = tpl % colors[fg]
    if bg:
        if bg == "yellow" and xterm: bg = "brown"

        try: bgcode = opencol + colors[bg].replace('3', '4', 1) + closecol
        except KeyError: pass

    return "%s%s%s%s" % (bgcode, fgcode, text, clear)

def beep(times, interval=1):
    """Beep terminal bell specified times with `interval` seconds (float or int)."""
    for t in range(times):
        print( '\a')
        time.sleep(interval)

def ftime(seconds, suffixes=['y','w','d','','',''], separator=':', nosec=False):
    """ Takes an amount of seconds and turns it into a human-readable amount of time.
        ftime(953995) => 1w:04d:00:59:55
        if `nosec` is True, seconds will be omitted from output.
        adapted from code by: http://snipplr.com/users/wbowers/
    """
    t = []
    parts = [ (suffixes[0], 60 * 60 * 24 * 7 * 52),
              (suffixes[1], 60 * 60 * 24 * 7),
              (suffixes[2], 60 * 60 * 24),
              (suffixes[3], 60 * 60),
              (suffixes[4], 60),
              (suffixes[5], 1)]

    # for each time piece, grab the value and remaining seconds, and add it to the time string
    if nosec:
        del parts[-1]
    for n, (suffix, length) in enumerate(parts):
        value = int(seconds) / length
        if value > 0 or t:                      # skip parts until we get first non-zero
            seconds = seconds % length
            fmt = "%02d%s"
            if not t and n+1 < len(parts):
                fmt = "%d%s"              # don't pad the first part with zeroes
            t.append(fmt % (value, suffix))
    if not t: t = ['0s']
    elif len(t) == 1 and not nosec: t[0] += 's'
    return str.join(t, separator)

# print ftime(105, nosec=True)

class Term:
    """ Linux terminal management.

        clear   - calls os.system("clear")
        getch   - get one char at a time
        size    - return height, width of the terminal
    """
    def __init__(self):
        self.fd = stdin.fileno()
        self.new_term, self.old_term = tcgetattr(self.fd), tcgetattr(self.fd)
        self.new_term[3] = (self.new_term[3] & ~ICANON & ~ECHO)

    def normal(self):
        """Set 'normal' terminal settings."""
        tcsetattr(self.fd, TCSAFLUSH, self.old_term)

    def clear(self):
        """Clear screen."""
        os.system("clear")

    def cline(self):
        """Clear line."""
        stdout.write('\r' + ' '*self.size()[1])
        stdout.flush()

    def curses(self):
        """Set 'curses' terminal settings. (noecho, something else?)"""
        tcsetattr(self.fd, TCSAFLUSH, self.new_term)

    def getch(self, prompt=None):
        """ Get one character at a time.

            NOTE: if the user suspends (^Z) running program, then brings it back to foreground,
            you have to instantiate Term class again.  Otherwise getch() won't work. Even after
            that, the user has to hit 'enter' once before he can enter commands.
        """
        if prompt:
            stdout.write(prompt)
            stdout.flush()
        self.curses()
        c = os.read(self.fd, 3)
        self.normal()
        try:
            return unicode(c)[2:-1]
        except NameError:
            return str(c)[2:-1]

    def size(self):
        """Return terminal size as tuple (height, width)."""
        import struct, fcntl
        h, w = struct.unpack("hhhh", fcntl.ioctl(0, TIOCGWINSZ, "\000"*8))[0:2]
        if not h:
            h, w = 24, 80
        return h, w

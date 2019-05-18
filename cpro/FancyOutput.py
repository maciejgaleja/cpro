from typing import Dict, Any
import sys
import os
from types import SimpleNamespace


colors = SimpleNamespace()
colors.black = lambda text: color(30, text)
colors.red = lambda text: color(31, text)
colors.green = lambda text: color(32, text)
colors.yellow = lambda text: color(33, text)
colors.blue = lambda text: color(34, text)
colors.magenta = lambda text: color(35, text)
colors.cyan = lambda text: color(36, text)
colors.white = lambda text: color(37, text)
colors.bright_black = lambda text: color(90, text)
colors.bright_red = lambda text: color(91, text)
colors.bright_green = lambda text: color(92, text)
colors.bright_yellow = lambda text: color(93, text)
colors.bright_blue = lambda text: color(94, text)
colors.bright_magenta = lambda text: color(95, text)
colors.bright_cyan = lambda text: color(96, text)
colors.bright_white = lambda text: color(97, text)


signs = SimpleNamespace()
signs.block_solid = '\u2588'
signs.check_box = '\u2611'
signs.check_box_heavy = '\u2705'
signs.check = '\u2713'
signs.check_heavy = '\u2714'


def init() ->None:
    if sys.platform == "win32":
        os.system('color')


def color(code: int, text: str = '', restoreNeutral: bool = True)->str:
    ret: str = text
    try:
        ret = '\033[' + str(code) + 'm' + text
        if restoreNeutral:
            ret = ret + '\033[0m'
    except:
        pass
    return ret


if __name__ == "__main__":
    print(repr(signs))
#     for sign in signs:
    # print(repr(sign))

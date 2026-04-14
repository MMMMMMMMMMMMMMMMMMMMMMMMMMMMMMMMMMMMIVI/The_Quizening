import curses

def init_colors():
    curses.start_color()
    curses.use_default_colors()  # -1 = transparent terminal background

    # curses.init_pair(id, foreground, background)
    curses.init_pair(1, curses.COLOR_CYAN,    -1)   # player 1
    curses.init_pair(2, curses.COLOR_GREEN,   -1)   # player 2
    curses.init_pair(3, curses.COLOR_YELLOW,  -1)   # player 3
    curses.init_pair(4, curses.COLOR_MAGENTA, -1)   # player 4
    curses.init_pair(5, curses.COLOR_WHITE,   -1)   # normal text
    curses.init_pair(6, curses.COLOR_BLACK,   curses.COLOR_BLUE)  # title bar
    curses.init_pair(7, curses.COLOR_BLUE,    -1)   # accent / prompts

def main(stdscr):

    stdscr.addstr(0, 0, "Player 1", curses.color_pair(1))
    stdscr.refresh()
    stdscr.getch()


curses.wrapper(main)
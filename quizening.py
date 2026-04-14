import curses

def main(stdscr):

    stdscr.addstr(0, 0, "Hello, curses!")
    stdscr.refresh()
    stdscr.getch()


curses.wrapper(main)
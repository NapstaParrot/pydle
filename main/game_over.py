import curses

stdscr = curses.initscr()
STD_X = stdscr.getmaxyx()[1]

scr = curses.newwin(1, STD_X, 7, 0)

def game_over(*args) :
    win = args[0]
    if win :
        txt = f"Congratulations! You found the word in {args[1] + 1} attempts."
        col = curses.color_pair(1)
    
    else :
        from pydle import ANSWER
        txt = f"Game Over! The answer was \"{ANSWER}\"."
        col = curses.color_pair(4)

    scr.clear()
    scr.resize(2, 100)

    txt_mid = STD_X // 2 - len(txt) // 2
    scr.addstr(0, txt_mid, txt, col)

    box = "[Press any key to continue]"
    box_mid = STD_X // 2 - len(box) // 2
    scr.addstr(1, box_mid, box, curses.color_pair(3) | curses.A_BOLD)
    
    scr.refresh()
    scr.getch()

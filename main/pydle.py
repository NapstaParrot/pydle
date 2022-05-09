import curses
from pathlib import Path
import random

main_dir = Path(__file__).resolve().parent
with open(main_dir / "words.txt", "r") as f :
    words = [x.strip() for x in f.readlines()]

with open(main_dir / "answers.txt", "r") as f :
    answers = [x.strip() for x in f.readlines()]
ANSWER = random.choice(answers)
# ANSWER = "fifty"



def game_over(*args) :
    scr, win = args[:2]
    if win :
        txt = f"Congratulations! You found the word in {args[2] + 1} attempts."
        col = curses.color_pair(1)
    else :
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


error_state = 0
# error handling
def error(*args) :
    """
    take error window, error code and 
    board row(optional) as inputs

    ERROR CODES :
    1. length error
    2. invalid word

    no error code == unspecified error occurred
    """
    scr, code = args[:2]
    if code == 1 :
        err = "Insufficient letters"

    elif code == 2 :
        err = "Invaid word"

    scr.clear()
    mid = STD_X // 2 - len(err) // 2
    scr.addstr(0, mid, err, curses.color_pair(4))
    scr.refresh()


# word coloring
def color_word(scr, row, word) :
    # remove white letters
    scr.move(0, 0)
    scr.clrtoeol()

    ans = ANSWER # temp answer
    wrd = word   # temp word
    colors = [*range(5)]
    attrs = [*range(5)]
    # check for green and gray first
    for i, lttr in enumerate(wrd) :
        if lttr == ans[i] :
            colors[i] = curses.color_pair(1) # green
            attrs[i] = curses.A_NORMAL

            # removing the letter from the amswer
            # and word so that other color wont 
            # check the same letter twice
            ans = ans[:i] + "_" + ans[i + 1:]
            wrd = wrd[:i] + "-" + wrd[i + 1:]
             
        else :
            colors[i] = curses.color_pair(3) # gray
            attrs[i] = curses.A_BOLD 
            
    for i, lttr in enumerate(wrd) :
        if lttr in ans :
            colors[i] = curses.color_pair(2) # yellow
            attrs[i] = curses.A_NORMAL

            # removing the letter from the amswer
            # and word so that other color wont 
            # check the same letter twice
            ans = ans.replace(lttr, "_", 1)
            wrd = wrd.replace(lttr, "-", 1)
    
    for i, (c, a) in enumerate(zip(colors, attrs)) :
        scr.addstr(0, i * 2, word[i], c | a)




def main(stdscr) :
    curses.curs_set(0)

    stdscr.nodelay(True)
    stdscr.clear()
    stdscr.refresh()

    # std screen size
    global STD_Y, STD_X
    STD_Y, STD_X = stdscr.getmaxyx()

    # colors
    curses.init_pair(1, curses.COLOR_GREEN, 0)
    curses.init_pair(2, curses.COLOR_YELLOW, 0)
    curses.init_pair(3, curses.COLOR_BLACK, 0)
    curses.init_pair(4, curses.COLOR_RED, 0)
    curses.init_pair(5, curses.COLOR_WHITE, 0)

    red = curses.color_pair(4)

    # windows and pad
    board_x = STD_X // 2 - 5

    board_win = curses.newwin(7, 10, 0, board_x)
    debug_win = curses.newwin(1, STD_X, 15, 0)
    out_win = curses.newwin(1, STD_X, 7, 0)
    guess_win = curses.newwin(1, 1, 0, 0)
    err_color_win = curses.newpad(6, STD_X)

    # drawing empty board
    for i in range(6) :
        board_win.addstr('_ ' * 4)
        board_win.addstr('_' if i == 5 else '_\n')
    board_win.refresh()


    # main game loop
    QWERTY = "qwertyuiopasdfghjklzxcvbnm"
    word = []
    row = 0
    while True :
        debug_win.move(0, 0)
        debug_win.clrtoeol()
        debug_win.addstr(str((QWERTY, len(word))))
        debug_win.refresh() 

        key = stdscr.getch()
        
        # colors the word red if its not a valid word
        if len(word) == 5 and not("".join(word) in words) :
            wrd = " ".join(word)
            err_color_win.addstr(row, board_x, wrd, red)
            err_color_win.refresh(row, 0, row, 0, row, STD_X)
        
        else :
            # overwriting err color window 
            guess_win.refresh()


        # lowercase'd
        if 65 <= key <= 90 :
            key += 32

        # if key isnt the alphabet
        elif not (97 <= key <= 122) :
            # if key is escape
            if key == 27 :
                break

            # if key is backspace or delete
            elif key in (8, 127) and len(word) > 0:
                word.pop()

                guess_win.move(0, len(word) * 2)
                guess_win.addstr("_")
                guess_win.refresh()
                guess_win.resize(1, len(word) * 2 + 1)

            # if key is enter
            elif key == 10 :
                # insufficient letters
                if len(word) < 5 :
                    error(out_win, 1)
                    curses.beep()
                    continue

                # invalid word
                elif not "".join(word) in words :
                    error(out_win, 2)
                    continue

                color_word(guess_win, row, "".join(word))
                guess_win.refresh()

                # if answer is found
                if "".join(word) == ANSWER :
                    game_over(out_win, True, row)
                    break

                # if attempts limit reached
                elif row == 5 :
                    game_over(out_win, False)
                    break
                
                for i in word :
                    QWERTY = QWERTY.replace(i, "")
                    
                row += 1
                word.clear()

            continue


        # dont add any new letter if word length is 5
        elif len(word) == 5 :
            continue
            
        guess_win.mvwin(row, board_x)
        guess_win.resize(1, len(word) * 2 + 2)
        guess_win.move(0, len(word) * 2)
        guess_win.addstr(chr(key))
        guess_win.refresh()

        word.append(chr(key))



curses.wrapper(main)
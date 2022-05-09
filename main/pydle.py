import curses
from pathlib import Path
import random
import time

main_dir = Path(__file__).resolve().parent
with open(main_dir / "words.txt", "r") as f :
    words = [x.strip() for x in f.readlines()]

with open(main_dir / "answers.txt", "r") as f :
    answers = [x.strip() for x in f.readlines()]
ANSWER = random.choice(answers)
# ANSWER = "fifteen"



QWERTY = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM←"]
# copying the qwerty list and changing the letters with curses color pair id
# in color_word()
key_colors = QWERTY[:]
def draw_keyboard(scr, *args) :
    for i, (keys_row, colors_row) in enumerate(zip(QWERTY, key_colors)) :
        for j, (key, color) in enumerate(zip(keys_row, colors_row)) :
            attr = curses.A_NORMAL

            # highlights the pressed key
            if args :
                if chr(args[0]) == key.lower() :
                    attr = curses.A_REVERSE
                        
                # if pressed key is the spacebar or del key
                elif key == "←" and args[0] in (8, 127) :
                    attr = curses.A_REVERSE

            try :
                color = int(color)
            except ValueError :
                color = 5 # white

            # gray
            bold = 0
            if color == 3 :
                bold = curses.A_BOLD

            scr.addstr(i, j * 2 + i, key, curses.color_pair(color) | attr | bold)
    scr.refresh()


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
def color_word(scr, word) :
    # remove white letters
    scr.move(0, 0)
    scr.clrtoeol()

    ans = ANSWER # temp answer
    wrd = word   # temp word
    colors, attrs = [], []
    # check for green and gray first
    for i, lttr in enumerate(wrd) :
        if lttr == ans[i] :
            colors.append(1) # green
            attrs.append(curses.A_NORMAL)

            # removing the letter from the amswer
            # and word so that other color wont 
            # check the same letter twice
            ans = ans[:i] + "_" + ans[i + 1:]
            wrd = wrd[:i] + "-" + wrd[i + 1:]

             
        else :
            colors.append(3) # gray
            attrs.append(curses.A_BOLD) 
    
    # overwriting existing colors with yellows
    for i, lttr in enumerate(wrd) :
        if lttr in ans :
            colors[i] = 2 # yellow
            attrs[i] = curses.A_NORMAL

            # removing the letter from the amswer
            # and word so that other color wont 
            # check the same letter twice
            ans = ans.replace(lttr, "_", 1)
            wrd = wrd.replace(lttr, "-", 1)
    
    global key_colors
    for i, (c, a) in enumerate(zip(colors, attrs)) :
        scr.addstr(0, i * 2, word[i], curses.color_pair(c) | a)
        # changing keyboard color
        x = '|'.join(key_colors).replace(word[i].upper(), str(c))
        key_colors = x.split('|')



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
    guess_win = curses.newwin(1, 1, 0, board_x - 1)
    keyboard_win = curses.newwin(3, 20, 2, 5)
    err_color_pad = curses.newpad(6, STD_X)

    # drawing empty board
    for i in range(6) :
        board_win.addstr('_ ' * 4)
        board_win.addstr('_' if i == 5 else '_\n')
    board_win.refresh()

    # default keyboard
    draw_keyboard(keyboard_win)

    # main game loop
    word = []
    row = 0
    time_start = 0
    time_current = 0
    while True :
        debug_win.move(0, 0)
        debug_win.clrtoeol()
        debug_win.addstr(0, 0, str())
        debug_win.refresh() 

        key = stdscr.getch()

        # keyboard highlighting :flushed:
        time_current = time.perf_counter()
        if round(time_current - time_start, 1) == 0.2 :
            # resets the keyboard after 500ms
            draw_keyboard(keyboard_win) 

        if key > 0 :
            time_start = time.perf_counter()
            draw_keyboard(keyboard_win, key) # highlithing pressed key
        

        # colors the word red if its not a valid word
        if len(word) == 5 and not("".join(word) in words) :
            wrd = " ".join(word)
            err_color_pad.addstr(row, 0, wrd, red)
            err_color_pad.refresh(row, 0, row, board_x, row, board_x + 10)
        
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

                color_word(guess_win, "".join(word))
                guess_win.refresh()

                # if answer is found
                if "".join(word) == ANSWER :
                    game_over(out_win, True, row)
                    break

                # if attempts limit reached
                elif row == 5 :
                    game_over(out_win, False)
                    break
                
                #for i in word :
                #    QWERTY = QWERTY.replace(i, "")
                    
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
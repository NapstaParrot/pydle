import curses
import random
from pathlib import Path

import keyboard
from game_over import game_over


main_dir = Path(__file__).resolve().parent
with open(main_dir / "words.txt", "r") as f :
    words = [x.strip() for x in f.readlines()]

with open(main_dir / "answers.txt", "r") as f :
    answers = [x.strip() for x in f.readlines()]
ANSWER = random.choice(answers)
# ANSWER = "fifteen"


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
    
    for i, (c, a) in enumerate(zip(colors, attrs)) :
        scr.addstr(0, i * 2, word[i], curses.color_pair(c) | a)

    keyboard.change_color(word, colors)


# main menu
def menu() :
    scr = curses.newwin(STD_Y, STD_X, 0, 0)
    scr.addstr(0, 0, "Welcome to pydle, a wordle remake by Napstaparrot")

    # options
    scr.addstr(2, 0, "0) Help Page ")
    scr.addstr(3, 0, "1) Normal    ")
    scr.addstr(4, 0, "2) Endless   ")

    while 1 :
        key = scr.getkey()

        if key == 27 :
            break

        elif key == 0 :
            pass

    scr.clear()
    scr.refresh()


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

    # top left board coords
    board_x = STD_X // 2 - 5

    # windows and pad
    board_win     = curses.newwin(7, 10, 0, board_x)
    debug_win     = curses.newwin(1, STD_X, 15, 0)
    guess_win     = curses.newwin(1, 1, 0, board_x - 1)
    out_win       = curses.newwin(1, STD_X, 7, 0)
    err_color_pad = curses.newpad(6, STD_X)

    # choice menu / main menu
    #menu()

    # drawing empty board
    for i in range(6) :
        board_win.addstr('_ ' * 4)
        board_win.addstr('_' if i == 5 else '_\n')
    board_win.refresh()

    # default keyboard
    keyboard.draw()

    # main game loop
    word = []
    row = 0
    while True :
        debug_win.move(0, 0)
        debug_win.clrtoeol()
        debug_win.addstr(0, 0, str())
        debug_win.refresh() 

        key = stdscr.getch()
        
        # keyboard highlighting :flushed:
        keyboard.key_press(key)

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

        elif 97 <= key <= 122 :
            # prints the words one by one :D
            guess_win.mvwin(row, board_x)
            guess_win.resize(1, len(word) * 2 + 2)
            guess_win.move(0, len(word) * 2)
            guess_win.addstr(chr(key))
            guess_win.refresh()

            word.append(chr(key))

        # if key is escape
        elif key == 27 :
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
                continue

            # invalid word
            elif not "".join(word) in words :
                error(out_win, 2)
                continue

            color_word(guess_win, "".join(word))
            guess_win.refresh()
            
            # if answer is found
            if "".join(word) == ANSWER :
                game_over(True, row)
                break

            # if attempts limit reached
            elif row == 5 :
                game_over(False)
                break

            #for i in word :
            #    QWERTY = QWERTY.replace(i, "")
   
            row += 1
            word.clear()

        # dont add any new letter if word length is 5
        elif len(word) == 5 :
            continue



curses.wrapper(main)
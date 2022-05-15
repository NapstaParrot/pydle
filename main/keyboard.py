import curses
import time


QWERTY = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM←"]
# copying the qwerty list and changing the letters with curses color pair id
# in color_word()
key_colors = QWERTY[:]

stdscr = curses.initscr()
STD_X = stdscr.getmaxyx()[1]

scr = curses.newwin(3, 20, 10, STD_X // 2 - 10)

def draw(*args) :
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


start_time = 0
def key_press(key) :
    global start_time
    if key > 0 :
        start_time = time.perf_counter()
        draw(key) # highlithing pressed key

    current_time = time.perf_counter()
    if round(current_time - start_time, 1) == 0.2 :
        # resets the keyboard after 200ms
        draw()


def change_color(word, colors) :
    global key_colors

    for i, col in (enumerate(colors)) :
        # joins the list into a string with '|' as a seperator for later
        x = '|'.join(key_colors)

        # replace letter with curses color id
        x = x.replace(word[i].upper(), str(col))

        # seperate them back into a list using the seperator
        key_colors = x.split('|')
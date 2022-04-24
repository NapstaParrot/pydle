from random import randint as rand
from os import get_terminal_size as term_size

with open("words.txt", "r") as f:
    words = [x.strip() for x in f.readlines()]

with open("answers.txt", "r") as f:
    answers = [x.strip() for x in f.readlines()]

# ansi colors
red = "\u001b[31m"
green = "\u001b[32m"
yellow = "\u001b[33m"
gray = "\u001b[30;1m"
bold = "\u001b[0;1m"
white = "\u001b[0m"
key_color = {}

# const
MARKER = "O"
QWERTY = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
GUIDE = [
    f"{green}{MARKER} {white}= Correct Placement    ",
    f"{yellow}{MARKER} {white}= Misplaced             ",
    f"{gray}{MARKER} {white}= Not In The Word         ",
]

endless_score = 0


# for starting/restarting the game
def start(*prev_guess):
    global guesses
    guesses = 0
    global guess
    guess = []
    global guess_color
    guess_color = []
    global ans
    ans = answers[rand(0, len(answers))]
    global game_state
    game_state = "running"
    global used
    used = set({})

    # for keyboard coloring
    for line in QWERTY:
        for key in line:
            key_color[key] = white

    # for endless gamemode

    if gamemode == "endless" and prev_guess:
        color_word(*prev_guess)


# clearing the console
def clear():
    print("\n" * (term_size()[1] // 2))


# drawing the board
def draw(*err):
    # guide + keyboard
    for i in range(len(GUIDE)):
        print(GUIDE[i], end=" ")

        for line in QWERTY[i]:
            for key in line:
                print(key_color[key] + key, end=" ")

        print("")

    print(white)

    if game_state == "win":
        print(
            f"{green}Congratulations, you found the answer in {guesses} "
            f"attempt{'s' if guesses > 1 else ''}!\n" + white
        )

    elif err:
        print(f"{red}{err[0]} {white}")

    if gamemode == "endless":
        print(
            f"{green}Word{'' if endless_score == 1 else 's'} found : ",
            endless_score,
            white,
        )

    # guessed words
    for i in range(len(guess)):
        print(*guess[i], end="  |  ")
        print(*guess_color[i], end="")
        print(white)

    # other lines
    if game_state == "running":
        for i in range(6 - guesses):
            print("_ " * 5 + " |  " + f"{gray}{MARKER} " * 5 + white)


# coloring the words
def color_word(word):
    global ans
    global guesses

    # word coloring
    temp_arr = [*range(5)]
    temp_ans = list(ans)
    temp_word = list(word)

    # checking for green letters
    for i in range(len(word)):
        if temp_word[i] == temp_ans[i]:
            temp_arr[i] = green + MARKER
            key_color[temp_word[i]] = green

            # remove the letter so that yellow
            # doesn't check the same letter
            temp_word[i], temp_ans[i] = "-", "_"

    # checking for yellow letters
    for i in range(len(word)):
        if temp_word[i] in temp_ans:
            temp_arr[i] = yellow + MARKER
            if key_color[temp_word[i]] == white:
                key_color[temp_word[i]] = yellow

            temp_ans = str(temp_ans).replace(temp_word[i], "/", 1)
            temp_word[i] = "-"

    # gray letters
    for i in range(len(word)):
        if not temp_word[i] in temp_ans:
            if temp_word[i] == "-":
                continue
            temp_arr[i] = gray + MARKER
            if key_color[temp_word[i]] == white:
                key_color[temp_word[i]] = gray

    guess_color.append(temp_arr)

    guesses += 1
    guess.append(word)

    # answer found
    if word == ans:
        global game_state
        game_state = "win"


# help manual
def help_page():
    while 1:
        clear()
        print("Help page for wordle remake\n")
        print("What do you need help with?")
        print("1. How to play wordle.")
        print("2. What does these gamemodes mean.")
        print("3. Exit the manual.")

        inp = input("\n>")

        if inp == "1":
            clear()
            print(
                "How to play wordle: ",
                "A mystery word is chosen when the program starts. "
                "Its your job to find that mystery word.\n"
                "You have 6 total tries. You must enter a valid 5 letter word. "
                "Said word will give you color\n"
                "indentification at the side. \n\nFor example :\n"
                f"{bold}c r a t e  |  {green}0 {gray}0 0 0 0 {white}\n"
                "This means that the letter c is at the correct spot.\n\n"
                f"{bold}t r e e s  |  {gray}0 0 {yellow}0 {gray}0 0 {white}\n"
                f"{bold}t r e e s  |  {gray}0 0 {yellow}0 {gray}0 0 {white}\n"
                f"{bold}t r e e s  |  {gray}0 0 {yellow}0 {gray}0 0 {white}\n"
                "This means that one of the two letter e is in the word, but isn't at the correct spot.\n\n"
                "And if the letter is gray, it means that the letter isn't in the word.\n\n",
            )

            input(f"{gray}[Press enter to continue]{white}")

        elif inp == "2":
            clear()
            print(
                "Normal : \n\tNormal wordle gamemode based on the nytimes.com version.\n\n"
                "Endless : \n\tLike normal wordle, but when you found the hidden word, that word will become\n"
                "your next guess. Try to get the most wordle possible.\n\n"
                "Multi Wordle : \n\tSolve multiple wordles at once.\n\n"
            )

            input(f"{gray}[Press enter to continue]{white}")

        elif inp == "3":
            break


# --- MAIN GAME CODES ---#


# main menu
print("Welcome to wordle remake in python by napstaparrot")
while 1:
    print("\nPlease choose a gamemode, type 'help' if you need help : ")
    print("0. help")
    print("1. normal")
    print("2. endless")
    print("3. multi wordle")

    inp = input("\n> ").lower()

    if inp in ["0", "help"]:
        help_page()
        clear()

    elif inp in ["1", "normal"]:
        gamemode = "normal"
        break

    elif inp in ["2", "endless"]:
        gamemode = "endless"
        break

    elif inp in ["3", "multi wordle"]:
        gamemode = "multi"
        clear()
        print(red + "Multi Wordle : TBA" + white)
        continue

    else:
        clear()
        print(red + "Please enter a number or the gamemode's name" + white)


start()
# main game loop
while 1:
    clear()
    # print(ans)
    draw()

    # max num of attempts reached
    if guesses == 6 and game_state == "running":
        clear()
        draw(f'\nGame Over! The answer was "{ans}"')
        game_state = "lose"
        print("\n")
        exit()

    if game_state == "win":
        if gamemode == "endless":
            endless_score += 1
            start(guess[-1])
            continue

        print("\n")
        exit()

    # checking for input errors
    while True:
        inp = input("\n").lower()
        if len(inp) != 5:
            clear()
            draw("Please input a 5 letters word\n")

        elif inp not in words:
            clear()
            draw(f"{inp} is not in the word list\n")

        else:
            break

    for i in inp:
        used.add(i)

    color_word(inp)

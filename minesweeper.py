"""
Final assignment for the Programming 1 course
in Oulu University made in python by Juuso Kärnä.
"""
from copy import deepcopy
import datetime
import os
import sys
import random as rnd
import haravasto as h

START_TIME = None
STATISTICS_FILE = "stats.txt"
mines_map = [] # Contains all map information, including mines
player_map = [] # Used to draw the map to the player, hiding mines ("X")

mouse_keys = {
    h.HIIRI_VASEN:"left",
    h.HIIRI_KESKI:"middle",
    h.HIIRI_OIKEA:"right"
}
menu_choises = {
    "(P)lay": "play",
    "(E)xit": "exit",
    "(S)tatistics": "statistics",
    "p": "play",
    "e": "exit",
    "s": "statistics"
}
# Array to store statistics of the current game
current_game = [
    None, # Start_time 0
    None, # Game lenght 1
    0, # Moves made 2
    "", # Win or loss 3
    0, # Mine amount 4
    0, # Map size x 5
    0 # Map size y 6
]
def main():
    """
    Initialize and display the game graphics, create the game window, 
    and set the necessary event handlers before starting the game.
    """
    h.lataa_kuvat('./spritet')
    ## Creates a window relative to the games map size.
    h.luo_ikkuna(40 * len(mines_map[0]), 40 * len(mines_map))
    h.aseta_piirto_kasittelija(draw_graphics)
    h.aseta_hiiri_kasittelija(mouse_click_event_handler)
    h.aloita()

def get_inputs():
    """
    Return user inputs for width, height and amount of mines.
    Make sure inputs are integers.
    """
    width = None
    height = None
    mine_amount = None
    print("Welcome! Before playing, please choose the map size and amount of mines.")
    print("Please do not type 0 or negative numbers.")

    while not (isinstance(width, int)) or (width <= 0):
        try:
            width = int(input("Please choose grid width: "))
            if width <= 0:
                print("Please give only integers greater than 0.")
        except ValueError:
            print("Please give only integers greater than 0.")
    while not (isinstance(height, int)) or (height <= 0):
        try:
            height = int(input("Please choose grid height: "))
            if height <= 0:
                print("Please give only integers greater than 0.")
        except ValueError:
            print("Please give only integers greater than 0.")
    while not (isinstance(mine_amount, int)) or (mine_amount <= 0):
        try:
            mine_amount = int(input("Please choose amount of mines: "))
            if mine_amount <= 0:
                print("Please give only integers greater than 0.")
            if mine_amount > width * height:
                print("Mine amount cannot exceed the map size.")
                mine_amount = 0
        except ValueError:
            print("Please give only integers greater than 0.")
    return width, height, mine_amount

def play_game():
    """
    Initialize and start a new game session.
    """
    global START_TIME
    mines_map.clear()
    player_map.clear()
    width, height, mine_amount = get_inputs()
    # Save player affected game statistics
    current_game[5], current_game[6], current_game[4] = width, height, mine_amount
    current_game[0] = str(datetime.datetime.now().replace(microsecond=0))
    START_TIME = datetime.datetime.now()

    create_map = []
    for _ in range(height):
        create_map.append([])
        for _ in range(width):
            create_map[-1].append(" ")
    mines_map.extend(create_map)

    open_cells = []
    for x in range(width):
        for y in range(height):
            open_cells.append((x, y))

    place_mines(mines_map, open_cells, mine_amount)

    player_map.extend(deepcopy(mines_map))
    for x, row in enumerate(player_map):
        for y, _ in enumerate(row):
            if player_map[x][y] == "x":
                player_map[x][y] = " "
    main()

def place_mines(game_map, open_squares, mine_amount):
    """
    Randomly place N mines in the game map.
    """
    while not mine_amount == 0:
        square = rnd.randint(0, len(open_squares) - 1)
        game_map[(open_squares[square][1])][(open_squares[square][0])] = "x"
        open_squares.remove(open_squares[square])
        mine_amount -= 1

def flood_fill(mine_map, start_x, start_y):
    """
    Open cells and their neighbors when no neighboring mines are found.
    """
    # Check if the starting cell is a mine. Continue or trigger a losing condition.
    if mine_map[start_y][start_x] == "x":
        save_statistics(current_game, "./stats.txt", False)
        print("\nYou lost, you stepped on a mine!\n")
        h.lopeta()
        main_menu()
        return
    # Do not flood fill if the cell is not "empty".
    if check_surrounding_mines(start_x, start_y, mine_map) != 0:
        mine_map[start_y][start_x] = "0"
        return
    squares = []
    squares.append((start_x, start_y))
    while len(squares) > 0:
        x, y = squares.pop()
        mine_map[y][x] = "0"
        if check_surrounding_mines(x, y, mine_map) == 0 or (x == start_x and y == start_y):
            to_discover = check_squares(x, y, mine_map)
            # Check if the cell to open is not already in the list
            # to avoid looping through the same cells multiple times.
            for i in to_discover:
                if i not in squares:
                    squares.append(i)

def check_squares(y, x, space):
    """
    Return a list of unopened safe cells around a given point.
    """
    safe_squares = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    for dir_x, dir_y in directions:
        cell_x, cell_y = x + dir_x, y + dir_y
        if (0 <= cell_x < len(space) and 0 <= cell_y < len(space[0])
            and space[cell_x][cell_y] == ' '):
            safe_squares.append((cell_y, cell_x))
    return safe_squares

def check_surrounding_mines(y, x, space):
    """
    Returns the amount of neighboring mines.
    """
    mine_squares = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    for dir_x, dir_y in directions:
        cell_x, cell_y = x + dir_x, y + dir_y
        if (0 <= cell_x < len(space) and 0 <= cell_y < len(space[0])
            and space[cell_x][cell_y] == 'x'):
            mine_squares.append((cell_y, cell_x))
    return len(mine_squares)

def draw_graphics():
    """
    Graphics handler that draws the game map to the player based on player_map.
    """
    h.tyhjaa_ikkuna()
    h.piirra_tausta()
    h.aloita_ruutujen_piirto()
    for x_1, row in enumerate(player_map):
        for y_1, cell in enumerate(row):
            h.lisaa_piirrettava_ruutu(cell, y_1 * 40, x_1 * 40)
    h.piirra_ruudut()

def mouse_click_event_handler(mouse_x, mouse_y, mouse_key_index, _):
    """
    Mouse event handler for handling left-click and right-click events.
    Left-click opens a cell, and right-click places or removes a flag.
    """
    if str(mouse_keys[mouse_key_index]) == "left":
        ## We dont explore the cell if there is a flag on it.
        if not player_map[mouse_y//40][mouse_x//40] == "f":
            current_game[2] += 1
            flood_fill(mines_map, mouse_x//40, mouse_y//40)
        for x, row in enumerate(player_map):
            for y, _ in enumerate(row):
                if mines_map[x][y] == "0":
                    player_map[x][y] = str(check_surrounding_mines(y, x, mines_map))

    if (str(mouse_keys[mouse_key_index]) == "right"
        and player_map[mouse_y//40][mouse_x//40] == "f"):
        player_map[mouse_y//40][mouse_x//40] = " "
    elif (str(mouse_keys[mouse_key_index]) == "right"
        and player_map[mouse_y//40][mouse_x//40] == " "):
        player_map[mouse_y//40][mouse_x//40] = "f"

    if check_win_condition():
        save_statistics(current_game, "stats.txt", True)
        print("\nYou won! You found all mines!\n")
        h.lopeta()

def check_win_condition():
    """
    Checks the games win condition by cheking if all safe cells are opened.
    """
    while True:
        for _, row in enumerate(mines_map):
            for y, _ in enumerate(row):
                if row[y] == " ":
                    return False
        return True

def save_statistics(game, file, win):
    """
    Saves statistics to a .txt file.
    """
    time = (datetime.datetime.now() - START_TIME).total_seconds()
    current_game[1] = round(float(time), 2)
    if win:
        current_game[3] = "Win"
    else:
        current_game[3] = "Loss"
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
        with open(path, "a", encoding='utf-8') as source:
            for i, stat in enumerate(game):
                if i < len(game) - 1:
                    source.write(str(stat) + ", ")
                else:
                    source.write(str(stat))
            source.write("\n")
    except IOError:
        print("Ran into a problem while opening the statistics file.")
    current_game[2] = 0

def show_statistics(file):
    """
    Prints statistics from .txt file to the terminal window.
    """
    statistics = []
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
        with open(path, "r", encoding='utf-8') as source:
            for row in source.readlines():
                (play_date, play_time, played_moves, win_state,
                mines_amount, map_size_x, map_size_y) = row.split(",")
                game = {
                    "date": play_date.strip().ljust(20),
                    "time": play_time.strip().ljust(14),
                    "moves": played_moves.strip().ljust(8),
                    "win": win_state.strip().ljust(12),
                    "mines": mines_amount.strip().ljust(12),
                    "map_x": map_size_x.strip().ljust(12),
                    "map_y": map_size_y.strip().ljust(12),
                }
                statistics.append(game)
        for game in statistics:
            print_value = list(game.values())
            print(" ".join(print_value))
    except IOError:
        print("Ran into a problem while opening the statistics file.")

def main_menu():
    """
    The main menu for the Minesweeper game. Call functions based on user input.
    """
    print("Welcome to minesweeper programmed in Python by Juuso Kärnä.")
    print("This is the main menu for the game. From here you can start a new game,"
    "statistics from past games from a .txt file, or exit the app.")
    print("Please pick from the following options: "+", ".join(menu_choises))
    while True:
        choice = input("Go: ").lower()
        try:
            if menu_choises["(P)lay"] == choice or menu_choises[choice] == "play":
                play_game()
        except KeyError:
            pass
        try:
            if menu_choises["(E)xit"] == choice or menu_choises[choice] == "exit":
                sys.exit()
        except KeyError:
            pass
        try:
            if menu_choises["(S)tatistics"] == choice or menu_choises[choice] == "statistics":
                show_statistics(STATISTICS_FILE)
        except KeyError:
            pass
        print("Please input only text, and pick from the options provided.")

if __name__ == "__main__":
    main_menu()

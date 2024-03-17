import pygame
import random
import math
import os
from ludo_algo import dfs_movement, minimax
pygame.init()
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 600 # 700, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ludo game")

display_font = pygame.font.SysFont("comicsans", 16)
winner_font = pygame.font.SysFont("comicsans", 40)

GREY = (200, 200, 200)

HOUSE_WIDTH = 230 # 250
HOUSE_HEIGHT = 230 # 250
COLOR_VALUE = {"red": 5, "blue": 6, "yellow": 8, "green": 9}
HOME_VALUE = {"red": 1, "blue": 2, "yellow": 3, "green": 4}
excluded_tile_pos = {"red": (6, 0), "blue": (0, 2), "yellow": (14, 0), "green": (8, 14)}

BOX_WIDTH = 60
BOX_HEIGHT = 44
BOX_WIDTH2 = 40 # 46
BOX_HEIGHT2 = 40 # 46

ROWS = 3
COLS = 15

DICE_WIDTH = 36
DICE_HEIGHT = 36
SEED_RADIUS = 14
PLACEMENT_RADIUS = 18

LOGO_WIDTH = BOX_WIDTH2 * 3 + 40
LOGO_HEIGHT = BOX_HEIGHT2 * 3 + 40

seed_capture = pygame.USEREVENT + 1
seed_capture_sound = pygame.mixer.Sound(os.path.join("Assets", "mixkit-arcade-game-jump-coin-216.wav"))

seed_movement = pygame.USEREVENT + 2
seed_movement_sound = pygame.mixer.Sound(os.path.join("Assets", "mixkit-game-coin-touch-3217.wav"))

die_roll = pygame.USEREVENT + 3
die_roll_sound = pygame.mixer.Sound(os.path.join("Assets", "gamemisc_dice-roll-on-wood_jaku5-37414.mp3"))

FPS = 60

NUM_OF_PLAYERS = 4
MAX_NUM_OF_PLAYERS = 4

assets_dir = os.path.abspath("Assets")

red_image  = pygame.image.load(os.path.join(assets_dir, "red.png"))
blue_image  = pygame.image.load(os.path.join(assets_dir, "blue.png"))
green_image  = pygame.image.load(os.path.join(assets_dir, "green.png"))
yellow_image  = pygame.image.load(os.path.join(assets_dir, "yellow.png"))
logo_image = pygame.image.load(os.path.join(assets_dir, "logo.png"))


red_house = pygame.transform.scale(red_image, (HOUSE_WIDTH, HOUSE_HEIGHT))
blue_house = pygame.transform.scale(blue_image, (HOUSE_WIDTH, HOUSE_HEIGHT))
green_house = pygame.transform.scale(green_image, (HOUSE_WIDTH, HOUSE_HEIGHT))
yellow_house = pygame.transform.scale(yellow_image, (HOUSE_WIDTH, HOUSE_HEIGHT))
logo = pygame.transform.scale(logo_image, (LOGO_WIDTH, LOGO_HEIGHT))


class Tiles:
    def __init__(self, value, x, y, width, height, grid_pos):
        self.rect = pygame.Rect(x, y, width, height) #dimensions for the rectangle
        self.grid_position = i, j = grid_pos
        self.selected = False
        self.value = value
        self.safe = False
        self.special = False
        self.highlight = False
        self.color = "white"
        self.special_tile_color = None
        self.special_tile_circle_color = "white"
        self.highlight_color = "brown"

    def draw(self, win):
        '''Draws a tile on the board'''
        pygame.draw.rect(win, self.color, self.rect)
        pygame.draw.rect(win, "black", (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2) 
    
    def draw_special_tiles(self, win):
        '''Draws a tile on the board'''
        pygame.draw.rect(win, self.special_tile_color, self.rect)
        pygame.draw.rect(win, "black", (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
        pygame.draw.circle(win, self.special_tile_circle_color, (self.rect.x + (self.rect.width//2), self.rect.y + (self.rect.height//2)), 16)

    def clicked(self, mousePos):
        '''Checks if a tile has been clicked'''
        if self.rect.collidepoint(mousePos): #checks if a point is inside a rect
            self.selected = True
        return self.selected
    
    def toggle_tile_highlight(self):
        if not self.highlight:

            if not self.special:
                self.color = "orange" if self.safe else self.highlight_color
        

            self.highlight = not self.highlight
            return

        if self.highlight:

            if not self.special:
                self.color = "white"
             
            self.highlight = not self.highlight
        
    def is_special_tiles_hor(self):
        i, j = self.grid_position
        if (i == 7 and 1 <= j <= 5) and not self.highlight:
            self.special = True
            self.special_tile_color = "red"
        
        elif (i == 7 and 14 > j > 8) and not self.highlight:
            self.special = True
            self.special_tile_color = "green"
        
        elif self.highlight:
            self.special_tile_color = self.highlight_color
    
        return self.special
    
    def is_special_tiles_ver(self):
        i, j = self.grid_position
        if (j == 1 and 1 <= i <= 5) and not self.highlight:
            self.special = True
            self.special_tile_color = "blue"

        elif (j == 1 and 14 > i > 8) and not self.highlight:
            self.special = True
            self.special_tile_color = "yellow"
            
        elif self.highlight:
            self.special_tile_color = self.highlight_color

        return self.special
        

class House:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self,  win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))


class Seed:
    PADDING = -2
    OUTLINE = 3

    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.out = False
        self.current_pos = None
        self.visited = set()
        self.clicked = False
        self.player = None
        self.lst_visited = list(self.visited)
        self.valid_grid_nums = {-1}

        self.visited.add(excluded_tile_pos[self.color])


    def draw(self, win):
        pygame.draw.circle(win, GREY, (self.x, self.y), self.radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius - self.PADDING)
        # pygame.draw.circle(win, self.house_pos_color, (self.x, self.y), self.radius, 7)
    
    def set_seed_position(self, x, y):
        self.x = x
        self.y = y
    
    def is_clicked(self, pos_x, pos_y):
        distance = math.sqrt((pos_x - self.x)**2 + (pos_y - self.y)**2)

        if distance <= self.radius:
            self.clicked = True
        
        return self.clicked
    
    def __str__(self):
        return f"Seed({self.color})"
    
    def __repr__(self):
        return f"Seed({self.color})"
        

class SeedPlacement:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = "white"
    
    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

class Dice:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = "grey"
        self.moves = [0, 0]
    
    def roll_dice(self):
        first_move = random.randint(1, 6)
        second_move = random.randint(1, 6)
        self.moves = [first_move, second_move]
        return self.moves
    
    def draw(self, win):
        num1 = display_font.render(str(self.moves[0]), 1, "black")
        num2 = display_font.render(str(self.moves[1]), 1, "black")
        second_dice = pygame.Rect(self.x + self.width + 2, self.y, self.width, self.height)
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(win, self.color, second_dice)

        win.blit(num1, (self.x + (self.width//2) - num1.get_width(), self.y - (self.height//2)  + num1.get_height()))
        win.blit(num2, (second_dice.x + (self.width//2) - num1.get_width(), self.y - (self.height//2) + num1.get_height()))


class Player:
    def __init__(self, id,  seeds):
        self.name = f"Player {id}"
        self.seeds = seeds
        self.score = 2
        self.num_of_seeds = 4 if len(seeds) == 1 else 8
        self.num_of_active_seeds = 0
        self.seed_grid_value = set()
        self.seeds_at_goal_area = []
        self.seed_at_risk = []
        self.ai = False

        for seed_group in self.seeds:

            for seed in self.seeds[seed_group]:
                    
                    if COLOR_VALUE[seed.color] not in self.seed_grid_value:
                        # self.seed_grid_value.add(HOME_VALUE[seed.color])
                        self.seed_grid_value.add(COLOR_VALUE[seed.color])

                    seed.player = self

    def check_seed_home_or_goal(self, box_grid):
        for seed_group in self.seeds:
            for seed in self.seeds[seed_group]:

                if seed.out:
                    i, j = seed.current_pos

                    
                    if box_grid[i][j] == HOME_VALUE[seed.color]:
                        self.seeds_at_goal_area.append(seed)

    def __str__(self):
        return self.name


class Board:
    def __init__(self):
        self.seeds_out = {}
        self.seeds_home = {}
        self.current_player = None
        self.seed_leave_board = 0
        self.seed_at_safety = 0
        self.seeds = []
        self.box_pos = None
        self.opp_at_safety = 0
        self.capture = {}
        self.create_grid()

    def create_grid(self):
        
        self.box_grid2 = [[-1, -1, -1], 
                    [-1, 2, -1], 
                    [-1, 2, -1], 
                    [-1, 2, -1], 
                    [-1, 2, -1], 
                    [-1, 2, -1], 
                    [-1, -1, -1, -1, -1, -1, 7, 7, 7, -1, -1, -1, -1, -1, -1], 
                    [-1, 1, 1, 1, 1, 1, 7, 7, 7, 4, 4, 4, 4, 4, -1], 
                    [-1, -1, -1, -1, -1, -1, 7, 7, 7, -1, -1, -1, -1, -1, -1], 
                    [-1, 3, -1], 
                    [-1, 3, -1], 
                    [-1, 3, -1], 
                    [-1, 3, -1], 
                    [-1, 3, -1], 
                    [-1, -1, -1]]
    
        box_positon = {}
        lst_of_boxes = []
        safe_boxes = 0
    
        for i in range(len((self.box_grid2))):
            y = (i * BOX_HEIGHT2) + 4.5 # 10
                
            for j in range(len(self.box_grid2[i])):
                if 6 <= i <= 8:
                    y = BOX_HEIGHT2 - 36 + i * BOX_HEIGHT2 # 36
                    x = (j * BOX_WIDTH2) + 1.0 # 4  
                else:
                    x = (WIDTH//2 - BOX_WIDTH2 - 20) + 2.5 + j * BOX_WIDTH2 # 2.5, 25

                pos = i, j
                box = Tiles(self.box_grid2[i][j], x, y, BOX_WIDTH2, BOX_HEIGHT2, (i, j))
                box_positon[pos] = box
                lst_of_boxes.append(box)

        k = 0

        while k < safe_boxes:
            tile = random.choice(lst_of_boxes)
            i, j = tile.grid_position

            if not tile.safe and not tile.special and self.box_grid2[i][j] != 7:
                tile.safe = True
                k += 1
            
    
        self.box_pos = box_positon
        return self.box_grid2, lst_of_boxes, box_positon
    
    def update_num_seeds(self):

        for row in self.box_grid2:
            for value in row:
                if not isinstance(value, Seed):
                    continue
                self.seeds_out[value.color] = self.seeds_out.get(value.color, 0) + 1

                if value.color in self.current_player.seeds:
                    if len(value.visited) > 49:
                        self.seed_leave_board += 1
                
                    if self.box_pos[value.current_pos].safe:
                        self.seed_at_safety += 1

                else:
                    if self.box_pos[value.current_pos].safe:
                        self.opp_at_safety += 1

                self.seeds.append(value)

        for seed_color in self.seeds_out:
            if len(self.current_player.seeds) == 1:
                    self.seeds_home[seed_color] = 4 - self.seeds_out[seed_color]
                
            else:
                self.seeds_home[seed_color] = 8 - self.seeds_out[seed_color]
    
    def capture_(self, seed, pos):
        capture = False
        i, j = pos
        value = self.box_grid2[i][j]

        if not isinstance(value, int):
            if value.player != seed.player:
                self.box_grid2[i][j] = -1
                capture = True


        return capture
    
    def evaluate(self):

            self.update_num_seeds()

            """
            Evaluate the current state of the Ludo board for a given player.

            Parameters:
            - board: The current state of the Ludo board.
            - current_player: The player for whom the evaluation is done.
            - opponents: List of opponents.

            Returns:
            - A numeric value indicating the desirability of the current state for the player.
            """ 
            # Weight values for different factors
            weight_home_tokens = 2 #2
            weight_tokens_in_safety = 1 #1
            weight_opponent_tokens_in_safety = -4 #-1
            weight_tokens_on_board = 5.5 #0.5
            weight_tokens_to_safety = 1  #1 New weight for prioritizing safety
            weight_tokens_to_leave_board = 2 #2 New weight for leaving the board
            weight_seed_captures = 40  #5 New weight for seed captures

            current_player_color = list(self.current_player.seeds.keys())

            # Evaluate based on the number of tokens in the home column
            home_tokens = sum(self.seeds_home.get(color, 0) for color in current_player_color)
            evaluation = weight_home_tokens * home_tokens

            # # Evaluate based on the number of tokens in safety zones
            # tokens_in_safety = sum(1 for color in self.seeds for seed in self.seeds[color] if token.is_in_safety())
            # evaluation += weight_tokens_in_safety * tokens_in_safety

            # Penalize for opponents' tokens in safety zones
            opponent_tokens_in_safety = self.opp_at_safety
            evaluation += weight_opponent_tokens_in_safety * opponent_tokens_in_safety

            # Evaluate based on the number of tokens on the board
            tokens_on_board = sum(self.seeds_out.get(color, 0) for color in current_player_color)
            evaluation += weight_tokens_on_board * tokens_on_board

            # Evaluate based on the priority to reach safety
            tokens_to_safety = self.seed_at_safety
            evaluation += weight_tokens_to_safety * tokens_to_safety

            # Evaluate based on the priority to leave the board
            tokens_to_leave_board = self.seed_leave_board
            evaluation += weight_tokens_to_leave_board * tokens_to_leave_board

             # Evaluate based on the number of seed captures
            seed_captures = sum(self.capture.get(color, 0) for color in current_player_color)
            evaluation += weight_seed_captures * seed_captures


            return evaluation



def handle_seed_movement(seeds_to_move, box_positons, event, mouse_pos, box_grid, seed_groups, seed_placement, unused_move, current_player):
    moved = False
    seed_moved = None
    seed_outside = [0 for seeds in current_player.seeds.values() for seed in seeds if seed.out]
    num_seeds_out = len(seed_outside)

    for seed in seeds_to_move:
        for idx, move in enumerate(seeds_to_move[seed]):
            i, j = move
            tile = box_positons[move]
            value = box_grid[i][j]
            
            if isinstance(value, int):
                pass

            elif value.color in current_player.seeds:
                continue

            if num_seeds_out == 1 and tile.safe and isinstance(value, Seed):
                unused_move.clear()
                continue

            if event.button == 1 and tile.clicked(mouse_pos) and tile.highlight:
        
             if not(tile.safe and isinstance(value, Seed)) or value == -1:
                new_pos_x = tile.rect.x + (tile.rect.width//2)
                new_pos_y = tile.rect.y + (tile.rect.height//2)
                seed.set_seed_position(new_pos_x, new_pos_y)
                pygame.event.post(pygame.event.Event(seed_movement))
    
                if seed.out:
                    r, c = seed.current_pos
                    if box_grid[r][c] not in [HOME_VALUE[seed.color], 7]:
                        box_grid[r][c] = -1

                    if sum(unused_move) == idx:
                        unused_move.clear()
                    
                    elif idx in unused_move:
                        unused_move.remove(idx)

                if not seed.out:
                    unused_move.remove(6)
                    if len(unused_move):
                        if unused_move[0] == idx:
                            unused_move.clear()

                    seed.out = True
                    current_player.num_of_active_seeds += 1
                    
                seed.current_pos = move

                if box_grid[i][j] != HOME_VALUE[seed.color] and box_grid[i][j] != 7:
                    box_grid[i][j] = seed

                else:
                    current_player.num_of_active_seeds -= 1

                skipped_pos = seeds_to_move[seed][:idx]

                if len(seeds_to_move[seed]) > 1:
                    for pos in skipped_pos:
                        seed.visited.add(pos)
                 
                moved = True
                seed_moved = seed
                seed.clicked = False
                tile.selected = False

                if handle_enemy_capture(seed_groups, seed_placement, move, seed, current_player, box_grid, unused_move):
                    if box_grid[i][j] != 7:
                        box_grid[i][j] = -1


    if moved:
        for tile_pos in seeds_to_move[seed]:
            if box_positons[tile_pos].highlight:
                box_positons[tile_pos].toggle_tile_highlight()

    print(box_grid)
    print()

    return moved, seed_moved


def handle_enemy_capture(seed_groups, seed_placement, move, current_seed, current_player, box_grid, unused_move):
    capture = False
    a, b  = move

    for seed_color in seed_groups:

        if seed_color in current_player.seeds:
            continue

        for i, seed in enumerate(seed_groups[seed_color]):
            if seed == current_seed:
                continue

            if seed.current_pos == move:
                placement = seed_placement[seed.color][i]
                seed.set_seed_position(placement.x, placement.y)
                seed.current_pos = None
                seed.out = False
                seed.visited = {excluded_tile_pos[seed.color]}
                opponet = seed.player
                opponet.num_of_active_seeds -= 1
                opponet.score -= 1
                capture = True
                pygame.event.post(pygame.event.Event(seed_capture))

                break

    if capture:
        if current_seed in seed_groups[current_seed.color]:
            seed_groups[current_seed.color].remove(current_seed)  
            current_player.num_of_active_seeds -= 1
            current_player.num_of_seeds -= 1
            current_player.score += 1 
    
    elif box_grid[a][b] == 7 and current_seed in seed_groups[current_seed.color]:
        seed_groups[current_seed.color].remove(current_seed)
        current_player.num_of_active_seeds -= 1
        current_player.num_of_seeds -= 1
        current_player.score += 1
        unused_move.clear()
        pygame.event.post(pygame.event.Event(seed_capture))


    return capture


def handle_current_player_seeds(current_player, num_movement, box_positions, box_grid, unused_moves, seeds_to_move):
    pos_x, pos_y = pygame.mouse.get_pos()

    for seed_color in current_player.seeds:
        for seed in current_player.seeds[seed_color]:

            if seed.is_clicked(pos_x, pos_y):
                moves_to_make, _ = show_valid_moves(num_movement, box_positions, seed, box_grid, unused_moves, current_player)
            
                if seed in seeds_to_move:
                    seed.clicked = False
                    del seeds_to_move[seed]

                elif not(seed in seeds_to_move) and len(moves_to_make) and len(unused_moves):    
                    seeds_to_move[seed] = moves_to_make


def handle_current_player_and_opponent(current_player, unused_moves, players, lucky, opponents, current_player_idx):
    if current_player.num_of_active_seeds >= 1 and not(len(unused_moves)) or current_player.num_of_active_seeds < 1 and 6 not in unused_moves:
        current_player_idx = handle_player_turn(players, current_player_idx, lucky)
        lucky = False
        
        current_player = players[current_player_idx]
        

        opponents = []
        for player in players:
            if player != current_player:
                opponents.append(player)

    return lucky, current_player_idx



def show_valid_moves(dice_roll, box_positions, seed, box_grid, unused_moves, current_player, display = True):
    first_value, second_value = dice_roll
    pair_nums = [first_value, second_value]
    start_value = 6
    opening_moves = {"red": [(6, 1), "right"], "blue": [(1, 2), "down"], "green": [(8, 13), "left"], "yellow": [(13, 0), "up"]}
    contains_6 = False
    valid_moves = []
    main_moves = []

    if not seed.out:
        for num in pair_nums:

            if num == start_value:
                contains_6 = True
                pair_nums.remove(num)
                break

    if contains_6 and len(unused_moves) or seed.out:
        valid_moves = dfs_movement(box_grid, dice_roll, seed, opening_moves, pair_nums, HOME_VALUE)
        
        if not seed.out:
                if start_value in unused_moves and current_player.num_of_active_seeds >= 1:
                    if display:
                        box_positions[valid_moves[0]].toggle_tile_highlight()

                    main_moves.append(valid_moves[0])

                if  pair_nums[0] in unused_moves and start_value in unused_moves and len(unused_moves) == 2 and 0 <= pair_nums[0] <= len(valid_moves) - 1:
                    if display:
                        box_positions[valid_moves[pair_nums[0]]].toggle_tile_highlight()

                    main_moves.append(valid_moves[pair_nums[0]])
            
        elif seed.out and pair_nums[0] == pair_nums[1]:
                total = sum(pair_nums)
                if pair_nums[0] in unused_moves and current_player.num_of_active_seeds > 1 and 0 <= pair_nums[0] <= len(valid_moves) - 1:
                        if display:
                            box_positions[valid_moves[pair_nums[0]]].toggle_tile_highlight()

                        main_moves.append(valid_moves[pair_nums[0]])
                        # box_positions[valid_moves[-1]].toggle_tile_highlight()

                if len(unused_moves) == len(pair_nums):
                    if total == len(valid_moves) - 1:
                        if display:
                            box_positions[valid_moves[total]].toggle_tile_highlight() 

                        main_moves.append(valid_moves[total])

                    else:
                     if display:
                        box_positions[valid_moves[-1]].toggle_tile_highlight()

                     main_moves.append(valid_moves[-1])

        else:
            total = sum(pair_nums)

            if len(unused_moves) == len(pair_nums):
                if total == len(valid_moves) - 1:
                    if display:
                        box_positions[valid_moves[total]].toggle_tile_highlight()

                    main_moves.append(valid_moves[total])
                
                else:
                     if display:
                        box_positions[valid_moves[-1]].toggle_tile_highlight()

                     main_moves.append(valid_moves[-1])

            for num in unused_moves: 
                    if len(unused_moves) == 1 or current_player.num_of_active_seeds > 1:
                            if 0 <= num <= len(valid_moves) - 1:
                                if display:
                                    box_positions[valid_moves[num]].toggle_tile_highlight()

                                main_moves.append(valid_moves[num])


    if not(len(unused_moves)) or not(contains_6 and len(unused_moves) or seed.out):
        seed.clicked = False

    return valid_moves, main_moves


def handle_player_turn(players, current_player_idx, lucky):
    if not lucky:
        current_player_idx = (current_player_idx + 1) % len(players)

    return current_player_idx


def regulate_current_player_and_opponent(self, change_player, players, current_player_idx, lucky, lucky_roll, num_movement):
    if change_player:
            current_player_idx = handle_player_turn(players, current_player_idx, lucky)
            lucky = False 
            
            current_player = players[current_player_idx]
            self.current_player = current_player

            if num_movement == lucky_roll:
                lucky = True

            self.opponets = [player for player in players if player != current_player]
    


class SimulateGame:
    def __init__(self, dice_roll,  box_positions, box_grid, opponents):
        self.unused_move = dice_roll[:]
        self.dice_roll = dice_roll
        self.box_positions = box_positions
        self.box_grid = box_grid
        self.opponents = opponents
        self.unused_opp_move = None
    
    def get_opp_seed_moves(self):
        dice_roll_possiblities = self.simulate_dice_roll()
        seed_move = {}

        for opp in self.opponents:
            for dice_roll in dice_roll_possiblities:
                self.simulate_move(opp, dice_roll, seed_move)
            
        return seed_move


    def simulate_seed_movement(self, seeds_to_move, seed_groups, seed_placement, unused_move, current_player, seed, best_move):
    
        moved = False
        seed_moved = None
        seed_outside = [0 for seeds in current_player.seeds.values() for seed in seeds if seed.out]
        print(seed_outside)
        num_seeds_out = len(seed_outside)

        for idx, move in enumerate(seeds_to_move[seed][1]):
                i, j = move
                tile = self.box_positions[move]
                value = self.box_grid[i][j]
                print(tile.safe)

                if move == best_move:
                
                    if isinstance(value, int):
                        pass

                    elif value.color in current_player.seeds:
                        continue

                    if num_seeds_out == 1 and tile.safe and isinstance(value, Seed):
                        unused_move.clear()
                        continue
                
                    if not(tile.safe and isinstance(value, Seed)) or value == -1:
                        new_pos_x = tile.rect.x + (tile.rect.width//2)
                        new_pos_y = tile.rect.y + (tile.rect.height//2)
                        seed.set_seed_position(new_pos_x, new_pos_y)
                        pygame.event.post(pygame.event.Event(seed_movement))
            
                        if seed.out:
                            r, c = seed.current_pos
                            if self.box_grid[r][c] not in [HOME_VALUE[seed.color], 7]:
                                self.box_grid[r][c] = -1

                            if sum(unused_move) == idx or idx == len(seeds_to_move[seed][1]) -1:
                                unused_move.clear()
                            
                            elif idx in unused_move:
                                unused_move.remove(idx)

                        if not seed.out:
                            unused_move.remove(6)
                            if len(unused_move):
                                if unused_move[0] == idx:
                                    unused_move.clear()

                            seed.out = True
                            current_player.num_of_active_seeds += 1
                            
                        seed.current_pos = move

                        if self.box_grid[i][j] != HOME_VALUE[seed.color] and self.box_grid[i][j] != 7:
                            self.box_grid[i][j] = seed

                        else:
                            current_player.num_of_active_seeds -= 1

                        skipped_pos = seeds_to_move[seed][1][:idx]
                        print(skipped_pos)

                        if len(seeds_to_move[seed][1]) > 1:
                            
                            for pos in skipped_pos:
                                seed.visited.add(pos)
                            
                        
                        moved = True
                        seed_moved = seed

                        if handle_enemy_capture(seed_groups, seed_placement, move, seed, current_player, self.box_grid, unused_move):
                            if self.box_grid[i][j] != 7:
                                self.box_grid[i][j] = -1
                    
        if moved:
            for tile_pos in seeds_to_move[seed][1]:
                if self.box_positions[tile_pos].highlight:
                    self.box_positions[tile_pos].toggle_tile_highlight()

        return moved, seed_moved


    def get_ai_seed_moves(self, current_player):
         seeds_moves = {}
         for seed_color in current_player.seeds:
            for seed in current_player.seeds[seed_color]:
                valid_moves, possible_moves = show_valid_moves(self.dice_roll, self.box_positions, seed, self.box_grid, self.unused_move, current_player, display= False)
                if len(possible_moves) and len(valid_moves):
                    seeds_moves[seed] = possible_moves, valid_moves
        
        #  print(seeds_moves)

         return seeds_moves

    
    def simulate_dice_roll(self):
        dice_roll_possiblites = []
        for i in range(1, 7):
            for j in range(1, 7):
                if j <= i - 1:
                    continue
                dice_roll = i, j
                dice_roll_possiblites.append(dice_roll)
        
        return dice_roll_possiblites
    
    def simulate_move(self, opp, dice_roll, seed_move): 
        num = 0
        self.unused_opp_move = dice_roll[:]
        for seed_color in opp.seeds:
            for seed in opp.seeds[seed_color]:
                valid_moves, main_m = show_valid_moves(dice_roll, self.box_positions, seed, self.box_grid, self.unused_opp_move, opp, display=False)
                num += 1
                seed_move[num] = [seed, main_m, valid_moves]
        

def group_players(num_of_players, colors, seed_groups, max_num_of_players, players):
    for i in range(num_of_players):
            groups = {}
            for color in colors[:]:

                if color in colors:
                    groups[color] = seed_groups[color]
                    colors.remove(color)

                if num_of_players == max_num_of_players:
                    break

                if len(groups) == 2:
                    break

            player = Player(i+1, groups)
            players.append(player)


    
def draw(win, lst_of_houses, lst_of_ver_boxes, dice, seed_groups, seed_placement, current_player):
    gap = 5
    # backgrd = pygame.Rect(WIDTH // 2 + BOX_HEIGHT2 * 3 - 208, HEIGHT // 2 - BOX_WIDTH2 * 3 + 75, BOX_HEIGHT2 * 3, BOX_WIDTH2 * 3)
    player = display_font.render(str(current_player), 1, "black")
    win.fill("white")
   
    for house in lst_of_houses.values():
        house.draw(win)
    
    win.blit(red_house, (gap, 20))
    win.blit(blue_house, (WIDTH - HOUSE_WIDTH - gap, 20))
    win.blit(green_house, (WIDTH - HOUSE_WIDTH - gap, HEIGHT - HOUSE_HEIGHT - gap)) 
    win.blit(yellow_house, (gap, HEIGHT - HOUSE_HEIGHT - gap))
    
    for box in lst_of_ver_boxes:
            if box.is_special_tiles_ver() or box.is_special_tiles_hor():
                box.draw_special_tiles(win)
            
            else:
                box.draw(win)
    
    # pygame.draw.rect(win, "white", backgrd)

    win.blit(logo, (WIDTH//2 - LOGO_WIDTH + 90, HEIGHT//2 - LOGO_HEIGHT + 80))
    win.blit(player, (WIDTH // 2 - player.get_width() + 30, -2)) # 10, 30


    for group in seed_placement:
        for seed_pos in seed_placement[group]:
            seed_pos.draw(win)

    for group in seed_groups:
        for seed in seed_groups[group]:  
            seed.draw(win)

    dice.draw(win)

    pygame.display.update()


 
def draw_winner_text(winner):
    text = f"{winner} WINS"
    winner_text = winner_font.render(text, 1, "black")
    WIN.blit(winner_text, ((WIDTH // 2) - winner_text.get_width() // 2, (HEIGHT // 2) - winner_text.get_height() // 2))
    pygame.display.update()



class LudoGame:
    def __init__(self, width, height, window):
        self.width = width
        self.height = height
        self.window = window
        self.opponets = []
        self.current_player = None

    
    def main(self):
        run = True
        gap = 5
        clock = pygame.time.Clock()
        lst_of_houses = {"red": House(gap, 20, HOUSE_WIDTH, HOUSE_HEIGHT, "red"),# top left
                        "blue": House(WIDTH - HOUSE_WIDTH - gap, 20, HOUSE_WIDTH, HOUSE_HEIGHT, "blue"), # top right
                        "yellow": House(gap, HEIGHT - HOUSE_HEIGHT - gap, HOUSE_WIDTH, HOUSE_HEIGHT, "yellow"),#bottom left
                        "green": House(WIDTH - HOUSE_WIDTH - gap, HEIGHT - HOUSE_HEIGHT - gap, HOUSE_WIDTH, HOUSE_HEIGHT, "green")# bottom right
        }
        
        lucky_roll = [6, 6]
        lucky = False
        square_size = 50
        seeds_to_move = {}
        winner = None 
        human_played = True
        s = None
        unused_empty = False

        num_movement = [0, 0]
        unused_moves = []
        board = Board()
        box_grid, lst_of_ver_boxes, box_positions = board.create_grid() 
        self.box_positions = box_positions
        self.box_grid = box_grid
        dice = Dice((WIDTH//2) - DICE_WIDTH, (HEIGHT//2) - DICE_HEIGHT, DICE_WIDTH, DICE_HEIGHT)
        seed_groups = {"red": [], "blue": [], "yellow": [], "green": []}
        seed_placement = {"red": [], "blue": [], "yellow": [], "green": []}
        colors  = ["red", "blue", "green", "yellow"] 
        

        
        for house in lst_of_houses.values():
            seeds = [Seed(house.x + (house.width//2) - square_size // 2 , house.y + house.height//2 - square_size // 2, SEED_RADIUS, house.color),
                Seed(house.x + (house.width//2) + square_size // 2 , house.y + house.height//2 - square_size // 2, SEED_RADIUS, house.color),
                Seed(house.x + (house.width//2) - square_size // 2 , house.y + house.height//2 + square_size // 2, SEED_RADIUS, house.color),
                Seed(house.x + (house.width//2) + square_size // 2 , house.y + house.height//2 + square_size // 2, SEED_RADIUS, house.color)]
            
            placement = [SeedPlacement(house.x + (house.width//2) - square_size // 2 , house.y + house.height//2 - square_size // 2, PLACEMENT_RADIUS),
                SeedPlacement(house.x + (house.width//2) + square_size // 2 , house.y + house.height//2 - square_size // 2, PLACEMENT_RADIUS),
                SeedPlacement(house.x + (house.width//2) - square_size // 2 , house.y + house.height//2 + square_size // 2, PLACEMENT_RADIUS),
                SeedPlacement(house.x + (house.width//2) + square_size // 2 , house.y + house.height//2 + square_size // 2, PLACEMENT_RADIUS)]
            
            seed_placement[house.color].extend(placement)     
            seed_groups[house.color].extend(seeds)
        
        players = []
        num_of_players = 4
        ai_palyers = 3 if num_of_players == 4 else 1
        max_num_of_players = 4
        current_player_idx = num_of_players - 1

        group_players(num_of_players, colors, seed_groups, max_num_of_players, players)
        
        for i in range(ai_palyers):
            players[i].ai = True

        current_player = players[current_player_idx]   

        
        while run: 
            clock.tick(FPS)

            
            has_openining_move = 6 not in unused_moves
            has_no_active_seed = current_player.num_of_active_seeds < 1 
            has_active_seed = current_player.num_of_active_seeds >= 1
            has_no_unused_move = not(len(unused_moves))

            change_player = has_active_seed and has_no_unused_move or has_no_active_seed and has_openining_move
            player_allowed = has_no_unused_move or has_no_active_seed and not(6 in num_movement)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()

                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL and player_allowed:

                            num_movement = dice.roll_dice()
                            pygame.event.post(pygame.event.Event(die_roll))


                            lucky, current_player, current_player_idx = self.regulate_current_player_and_opponent(change_player, players, current_player_idx, lucky, lucky_roll, num_movement)
                                     
                            unused_moves = num_movement[:]

                if event.type == seed_capture:
                    seed_capture_sound.play()
                
                elif event.type == seed_movement:
                    seed_movement_sound.play()

                if event.type == die_roll:
                    die_roll_sound.play()


                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        handle_current_player_seeds(current_player, num_movement, box_positions, box_grid, unused_moves, seeds_to_move)
            
                    mouse_pos = pygame.mouse.get_pos()
                    moved, seed = handle_seed_movement(seeds_to_move, box_positions, event, mouse_pos, box_grid, seed_groups, seed_placement, unused_moves, current_player) 
                    
                    if moved:
                        del seeds_to_move[seed]
                        

            if winner:
                draw_winner_text(winner)
                pygame.time.delay(5000)       
                break

            board.current_player = current_player

            if True: # change to false to player game against yourself.

                # pygame.time.delay(500)  

                if not(unused_empty):
                    s = SimulateGame(num_movement, box_positions, box_grid, self.opponets)
                
                else:
                    unused_empty = False
                
                has_openining_move_ai = 6 not in s.unused_move
                has_no_unused_move_ai = not(len(s.unused_move))
                change_player_ai = has_active_seed and has_no_unused_move or has_no_active_seed and has_openining_move_ai
                ai_allowed = has_no_unused_move_ai or has_no_active_seed and not(6 in num_movement)



                if ai_allowed:
                    print(num_movement, s.unused_move)
                    num_movement = dice.roll_dice()
                    pygame.event.post(pygame.event.Event(die_roll))

                
                    lucky, current_player, current_player_idx = self.regulate_current_player_and_opponent(change_player_ai, players, current_player_idx, lucky, lucky_roll, num_movement)
                            
                            
                elif not(ai_allowed):
                    ai_moves = s.get_ai_seed_moves(current_player)
                    opp_moves = s.get_opp_seed_moves()
                    
                    value, s_m = minimax(board, current_player, 2, current_player, winner, ai_moves, opp_moves, self.opponets, s.unused_move[:])
                    seed, best_board, best_move = s_m

                    if best_move:
                        tile = box_positions[best_move]
                        new_pos_x = tile.rect.x + (tile.rect.width//2)
                        new_pos_y = tile.rect.y + (tile.rect.height//2)
                        pygame.draw.circle(self.window, "black", (seed.x, seed.y), 16, 2)
                        pygame.draw.circle(self.window, seed.color, (new_pos_x, new_pos_y), 19, 2)
                        pygame.display.update()
                        pygame.time.delay(900)
                    
                    print(value, "error")
                    print(unused_empty)
                    print(num_movement, s.unused_move)
                    print(current_player.num_of_active_seeds)

                    if seed != None:
        
                        s.simulate_seed_movement(ai_moves, seed_groups, seed_placement, s.unused_move, current_player, seed, best_move)
                        
                        unused_empty = True
                        
                        

            keys_pressed = pygame.key.get_pressed()

            if keys_pressed[pygame.K_SPACE]:
                current_player.num_of_seeds = 0          
            
            for player in players:
                if player.num_of_seeds == 0:
                    winner = player 

            draw(WIN, lst_of_houses, lst_of_ver_boxes, dice, seed_groups, seed_placement, current_player) 
            

        self.main()


    
    def regulate_current_player_and_opponent(self, change_player, players, current_player_idx, lucky, lucky_roll, num_movement):
        if change_player:
                current_player_idx = handle_player_turn(players, current_player_idx, lucky)
                lucky = False 
                
                current_player = players[current_player_idx]
                self.current_player = current_player

                if num_movement == lucky_roll:
                    lucky = True

                self.opponets = [player for player in players if player != current_player]

        return lucky, current_player, current_player_idx


if __name__ == "__main__":
    ludo = LudoGame(WIDTH, HEIGHT, WIN)
    ludo.main()
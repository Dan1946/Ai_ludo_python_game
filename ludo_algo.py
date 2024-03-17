from copy import deepcopy
import pygame
 
def minimax(position, current_player, depth, max_player, winner, possible_moves, opp_moves, opponents, unused_move):
    current_seed = None
    if depth == 0 or winner: 
        return position.evaluate(), position
    
    if max_player:
        max_eval = float('-inf')
        best_move = None
        choosen_move = None
        for move in get_all_moves(position, possible_moves, unused_move):
            evaluation = minimax(move[0], current_player, depth-1, False, winner, possible_moves, opp_moves, opponents, unused_move)[0]
            max_eval = max(max_eval, evaluation)
            if max_eval == evaluation:
                best_move = move[0]
                current_seed = move[1]
                choosen_move = move[2]
        
        return max_eval, [current_seed, best_move, choosen_move]
        
    else:
        current_opp_seed = None
        choosen_move = None
        min_eval = float('inf')
        best_move = None
        for move in get_all_opp_moves(position, opp_moves, unused_move):
                evaluation = minimax(move[0], current_player, depth-1, True, winner, possible_moves, opp_moves, opponents, unused_move)[0]
                min_eval = min(min_eval, evaluation)
                if min_eval == evaluation: 
                    best_move = move[0]
                    current_opp_seed = move[1]
                    choosen_move = move[2]
    
        return min_eval, [current_opp_seed, best_move, choosen_move]

             


def dfs_movement(box_grid, dice_roll, seed, opening_moves, pair_nums, hom_val):
    second_value = pair_nums[0]
    valid_tiles = []

    if seed.current_pos == None:
        total_sum = second_value + 1
        start_pos = opening_moves[seed.color][0]

    else:
        total_sum = sum(dice_roll) + 1
        start_pos = seed.current_pos
    
    x = 0
    stack = [(start_pos)]
    visited = set()

    while x < total_sum and len(stack):
        row, col = stack.pop()

        if box_grid[row][col] not in seed.valid_grid_nums and isinstance(box_grid[row][col], int):
            continue


        if (row, col) in seed.visited or (row, col) in visited:
            continue
        
        visited.add((row, col))
        print()

        valid_tiles.append((row, col))

        if box_grid[row][col] == 7 and hom_val[seed.color] in seed.valid_grid_nums:
            break

        if seed.color == "blue" and not(len(stack)) and (5, 1) in valid_tiles:
            valid_tiles.remove((5, 1))
            valid_tiles.append((6, 8))
            break

        x += 1
        neighbours = find_neighbours(box_grid, row, col)

        if len(seed.visited) + 2 >= 53:
            seed.valid_grid_nums.add(hom_val[seed.color])
            seed.valid_grid_nums.add(7)
            
        for neighbour in neighbours:
            stack.append(neighbour)

   
    return valid_tiles


def find_neighbours(box_grid, row, col):
    neighbours = [] 
    up_limit = 9
    down_limit = 5
    left_limit = 9
    right_limit = 5

    if row > 0 : # up
        if len(box_grid[row]) == len(box_grid[row - 1]):
            neighbours.append((row - 1, col)) 

    if row > 0 and row == up_limit: # up diagonal
        if  not(len(box_grid[row]) == len(box_grid[row - 1])):
            neighbours.append((row - 1, col + 5))
    
    if row < len(box_grid) - 1: # down
        if len(box_grid[row]) == len(box_grid[row + 1]):
            neighbours.append((row + 1, col))

    if row < len(box_grid) - 1 and row == down_limit and col != 0: # down diagonal
        if not(len(box_grid[row]) == len(box_grid[row + 1])):
            neighbours.append((row + 1, up_limit))
    
    if col > 0: # left
        neighbours.append((row, col - 1))
    
    if col == left_limit: # left diagonal
        if len(box_grid[row]) != len(box_grid[row + 1]):
            neighbours.append((row + 1, col - 7))
    
    if col < len(box_grid[row]) - 1: # right
        neighbours.append((row, col + 1))
    
    if col == right_limit: # right diagonal
        if len(box_grid[row]) != len(box_grid[row - 1]):
            neighbours.append((row - 1, col - col))
    
    return neighbours


def simulate_move(possible_moves, seed, move, box_grid, unused_move, board):
    HOME_VALUE = {"red": 1, "blue": 2, "yellow": 3, "green": 4}
    i, j = move
    value = box_grid[i][j]
    idx = possible_moves.index(move)
    # print(value)
    if len(unused_move):
        if not isinstance(value, int):
            if str(value.player) != str(seed.player) and not(board.box_pos[move].safe):
                board.capture[seed.color] = board.capture.get(seed.color, 0) + 1
                print(board.capture)
                box_grid[i][j] = -1
            
            else:
                print("false")
                return False

        if seed.out:
            r, c = seed.current_pos
            if box_grid[r][c] not in [HOME_VALUE[seed.color], 7]:
                box_grid[r][c] = -1

            if sum(unused_move) == idx:
                unused_move.clear()
            
            elif idx in unused_move:
                unused_move.remove(idx)

        if not seed.out and 6 in unused_move:
            print(unused_move)
            unused_move.remove(6)
            if len(unused_move):
                if unused_move[0] == idx:
                    unused_move.clear()

            seed.out = True
           
        seed.current_pos = move

        if box_grid[i][j] != HOME_VALUE[seed.color] and box_grid[i][j] != 7:
            box_grid[i][j] = seed

        skipped_pos = possible_moves[:idx]

        if len(possible_moves) > 1:
            for pos in skipped_pos:
                seed.visited.add(pos)


        return True


def get_all_moves(position, possible_moves, unused_move):
    moves = []
    u_n = unused_move[:]

    for seed in possible_moves:
            for idx, move in enumerate(possible_moves[seed][0]):
                temp_board = deepcopy(position)

               
                temp_seed = deepcopy(seed)
        
                moved = simulate_move(possible_moves[seed][1], temp_seed, move, temp_board.box_grid2, unused_move, temp_board)
                new_pos = temp_seed.current_pos
                new_board = temp_board

                if moved:
                    moves.append([new_board, seed, new_pos])
                
                unused_move = u_n[:]
    
    return moves


def get_all_opp_moves(position, opp_moves, unused_move):
    moves = []
    u_n = unused_move[:]
    print(unused_move)

    for num in opp_moves:
            for move in opp_moves[num][1]:
                seed = opp_moves[num][0]
                temp_board = deepcopy(position)
                
                temp_seed = deepcopy(seed)
                

                moved = simulate_move(opp_moves[num][2], temp_seed, move, temp_board.box_grid2, unused_move, temp_board)
                new_board = temp_board
                new_pos = temp_seed.current_pos

                if moved:
                    moves.append([new_board, seed, new_pos])
                
                unused_move = u_n[:]
    
    return moves


def draw(seed, win):
    seed.draw(win)
    pygame.draw.circle(win, "black", (seed.x, seed.y), 16, 2)
    pygame.display.update()
    # pygame.time.delay(200)
   



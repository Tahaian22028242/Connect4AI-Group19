import numpy as np
import pygame
import sys
import math
import random

## game colors
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
##board size
ROW_COUNT = 6
COLUMN_COUNT = 7
#player identifiers for whos turn it is
PLAYER = 0
AI = 1
#piece identifiers for moves made by each player
PLAYER_PIECE = 1
AI_PIECE = 2
#used for AI calculating/evaluating moves 
WINDOW_LENGTH = 4
EMPTY = 0

##numpy method to create 2D array which is fundamental shape of game
def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board
## function for making a move
def drop_piece(board, row, col, piece):
    board[row][col] = piece
## makes sure drop piece function is valid by checking that value of location is 0 and not a piece
def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board,0))

def winning_move(board, piece):
    #check horizontal
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    #check vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    #check positive slope diagonal matches
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    #check negative slope diagonal matches
    for c in range(COLUMN_COUNT-3):
        for r in range(3,ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score 

def score_position(board, piece):
    score = 0
    ## Prefer Center Board Moves for overall increase in combination setup potential
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 4

    ## Calculate Horizontal Score
    
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    
    ##Calculate Vertical Score
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0


def minimax(board,depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000)   
            else: #game over no more moves  
                return (None, 0)
        else: #depth is zero
            return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: #minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(board, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value
       



def get_valid_locations(board):
     valid_locations = []
     for col in range(COLUMN_COUNT):
         if is_valid_location(board, col):
             valid_locations.append(col)
     return valid_locations


def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = 0
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        ## if new score found but potential position is better than current best score, update best score and best col position
        if score > best_score:
            best_score = score
            best_col = col
            
    return best_col


def draw_board(board):
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			if board[r][c] == PLAYER_PIECE:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_PIECE: 
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()


board = create_board()
print_board(board)
game_over = False

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)
RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(PLAYER, AI)

while not game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
               
            #Ask for p1 input
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx/SQUARESIZE))  

                if is_valid_location(board,col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board,PLAYER_PIECE):
                        label = myfont.render("Player 1 wins!", 1, BLUE)
                        screen.blit(label, (40,10))
                        game_over = True

                    turn += 1
                    turn = turn % 2 

                    print_board(board) 
                    draw_board(board)

                    if game_over:
                        pygame.time.wait(3000)
        #AI INPUT   
        if turn == AI and not game_over:

            # if you want to make the AI process more in depth possiblities, increase the depth passed into the minimax call. increased depth will take longer to process.
            col, minimax_score = minimax(board, 4, -math.inf, math.inf, True)

            if is_valid_location(board,col):
                # pygame.time.wait(500)
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                label = myfont.render("Player 2 wins!", 1, BLUE)
                screen.blit(label, (40,10))
                game_over = True
                    

            print_board(board) 
            draw_board(board)

            turn += 1
            turn = turn % 2 

            if game_over:
                pygame.time.wait(3000)



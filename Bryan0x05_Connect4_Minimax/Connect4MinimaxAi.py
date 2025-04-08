import numpy as np
import random
import sys
import math

#grid rows and cols numbers
ROWS_NUM = 6
COLS_NUM = 7
#constants to make code easier to read
PLAYER_TURN = 0
PLAYER_TOKEN = 1

AI_TURN = 1
AI_TOKEN = 2
EMPTY = 0

def create_board():
    """Init a 2D arries of zeros"""
    board = np.zeros((ROWS_NUM, COLS_NUM))
    return board

def clear_board(board):
    """Sets all values in the 2D array to 0(Empty)"""
    board.fill(0)
    
def clear_token(board, row, col):
    """Clear tokens in 2D array at given row and column"""
    board[row,col] = EMPTY
 
def drop_token(board, row,col, token):
    """Sets given location in 2D array to given token value"""
    board[row][col] = token
     

def get_next_open_row(board, col):
    """find next unfilled row in the given column"""
    for row in range(ROWS_NUM):
       if board[row][col] == 0:
          return row

def print_board(board):
    """Flips 2D array to mimic apperance of gameboard"""
    print(np.flip(board, 0))
    print("c:1  2  3  4  5  6  7")

def winning_move(board, token):
    """Check if anyone has won or draw"""
	# Check horizontal locations for win
    for c in range(COLS_NUM-3):
       for row in range(ROWS_NUM):
           if board[row][c] == token and board[row][c+1] == token and board[row][c+2] == token and board[row][c+3] == token:
               return True
	# Check vertical locations for win
    for c in range(COLS_NUM):
       for row in range(ROWS_NUM-3):
           if board[row][c] == token and board[row+1][c] == token and board[row+2][c] == token and board[row+3][c] == token:
               return True

	# Check positively sloped diaganols
    for c in range(COLS_NUM-3):
       for row in range(ROWS_NUM-3):
           if board[row][c] == token and board[row+1][c+1] == token and board[row+2][c+2] == token and board[row+3][c+3] == token:
               return True

	# Check negatively sloped diaganols
    for c in range(COLS_NUM-3):
       for row in range(3, ROWS_NUM):
           if board[row][c] == token and board[row-1][c+1] == token and board[row-2][c+2] == token and board[row-3][c+3] == token:
               return True
    locs = get_potential_locs(board)
    if len(locs) == 0:
        return True



#evaluates the whole board for the position for a given player(derived from token)
def utility(board, token):
	"""Calculates herestic based on the given token positions across the whole board"""
	WINDOW_LEN = 4
	score = 0
	# Score center column, favors the center column
	center_ray = [int(i) for i in list(board[:, COLS_NUM//2])]
	center_count = center_ray.count(token)
	score += center_count * 3

	# Score Horizontal
	for row in range(ROWS_NUM):
		row_ray = [int(i) for i in list(board[row, :])]
		for col in range(COLS_NUM-3):
			window = row_ray[col:col+WINDOW_LEN]
			score += evaluate_window(window, token)

	# Score Vertical
	for col in range(COLS_NUM):
		col_ray = [int(i) for i in list(board[:, col])]
		for row in range(ROWS_NUM-3):
			window = col_ray[row:row+WINDOW_LEN]
			score += evaluate_window(window, token)

	# Score positive sloped diagonal
	for row in range(ROWS_NUM-3):
		for col in range(COLS_NUM-3):
			window = [board[row+i][col+i] for i in range(WINDOW_LEN)]
			score += evaluate_window(window, token)
   
	# score negative sloped diaognals
	for row in range(ROWS_NUM-3):
		for col in range(COLS_NUM-3):
			window = [board[row+3-i][col+i] for i in range(WINDOW_LEN)]
			score += evaluate_window(window, token)
	return score

#returns a list of potential locations the AI can drop tokens
def get_potential_locs(board):
    """Returns all available spaces for a token to be placed"""
    potential_loc = []
    for col in range(COLS_NUM):
       if col_is_not_full(board,col):
           potential_loc.append(col)
    return potential_loc
            
def evaluate_window(window, token):
    """Evaluate the 4 space long slices taken from utility function"""
    score = 0
    opp_token = PLAYER_TOKEN
    if token == PLAYER_TOKEN:
        opp_token = AI_TOKEN
    # 4 token group, e.g. if the next move is the winning move.
    if window.count(token) == 4:
        score += 1000
    # 3 token group
    elif window.count(token) == 3 and window.count(EMPTY) == 1:
        score += 3
    # 2 token token group
    elif window.count(token) == 2 and window.count(EMPTY) == 2:
        score += 2
    #encouarges blocking the player from winning by reducing value of moves that do not block the player
    if window.count(opp_token) == 3 and window.count(EMPTY) == 1:
        score -= 30
    return score

def col_is_not_full(board,col):
    return board[ROWS_NUM-1,col] == 0

#checks to see if this current node is a leaf or not, e.g. if the game can keep going
def is_terminal_node(board):
    """Checks to see if it is a leaf node or not"""
    if winning_move(board, PLAYER_TOKEN) or winning_move(board, AI_TOKEN) or get_potential_locs == 0:
        return True
    else:
        return False
    
# picks the best move from a list of potential locations
def find_best_move(board, token):
    """Best move with no look ahead"""
    bestscore = -math.inf
    locs = get_potential_locs(board)
    bestcol = random.choice(locs)
    for col in locs:
        row = get_next_open_row(board, col)
        #drop a token in current board and evaluate position
        drop_token(board, row, col, token)
        score = utility(board, token)
        #clear drop token to restore board to orginial stat
        clear_token(board, row, col)
        if score > bestscore:
            bestscore = score
            bestcol = col
    return bestcol, bestscore

def minimax(board, depth, maximizingPlayer, alpha = -math.inf, beta = math.inf):
    """Looks ahead to find the best move up to the depth, and use alpha-beta pruning to improve runtime"""
    leaf = is_terminal_node(board)
    if depth == 0 or leaf:
        if leaf:
            if winning_move(board,AI_TOKEN):
                return (None, math.inf)
            elif winning_move(board,PLAYER_TOKEN):
                return(None, -math.inf)
            # no possible moves left
            else:
                return(None, 0)
        #if not leaf and depth is 0, then play with no look ahead
        else:
            #find best move returns bestcol, bestscore
            # find best move does evaluate the current to find what it think is the best placement it does not traverse minimax however
            return (None, utility(board,AI_TOKEN))

    locs = get_potential_locs(board)
    #if maximizing player (e.g. the AI)
    if maximizingPlayer:
        maxval = -math.inf
        maxcol = random.choice(locs)
        #for each open column
        for col in locs:
            row = get_next_open_row(board,col)
            #drops a token to then score the resulting position
            drop_token(board, row, col, AI_TOKEN)
            score = minimax(board, depth-1, False, alpha, beta)[1]
            #returns board to orginal state	
            clear_token(board, row, col)
            if score > maxval:
                maxval = score
                maxcol = col
            alpha = max(alpha, maxval)
            #beta purning check, if true stop exploring this branch, as it will not affect the final decision
            if alpha >= beta: 
                break
        return maxcol, maxval
    #else the minimizing player, e.g. the human
    else:
        minval = math.inf
        mincol = random.choice(locs)
        for col in locs:
            row = get_next_open_row(board,col)
            drop_token(board, row, col, PLAYER_TOKEN)
            score = minimax(board, depth - 1, True, alpha, beta)[1]
            clear_token(board, row, col)
            if score < minval:
                minval = score
                mincol = col
            beta = min(beta, minval)
            #alpha purning check, if true stop exploring this branch, as it will not affect the final decision
            if beta <= alpha:
                break
        return mincol,minval
	     
# draws the current state of the board
def draw_board(board):
    pass

board = create_board()

game = True

#first turn is randomly given to AI or player
turn = random.randint(PLAYER_TURN, AI_TURN)
print("How to play: Select a column(1-7), to drop a token.\nConnect 4 tokens in a straight line in any direction to win(horizontal,vertical or diagonal)")
print("Human player(you) tokens are presented as 1's. AI tokens are 2's. Empty spaces are 0's. ")

print_board(board)
while game:
    if turn == PLAYER_TURN:
        print("Player's turn!")
        user_col = -1
        while user_col < 0 or user_col > 7:
            user_in = input("Pick a column to drop a token(left to right, 1-7): ")
            #if the input is not in the alphabet then cast to int
            if not user_in.isalpha():
                user_col = int(user_in)
            #if input is an the alphabet, set user_col to something invalid to repromp user input
            else: 
                user_col = -1
            user_col -= 1  # off set user input since addresses start at 0
            if user_col < 0 or user_col > 7 or not col_is_not_full(board,user_col):
                print("invalid input, pick an open column")
                user_col = -1
        row = get_next_open_row(board,user_col)
        drop_token(board,row,user_col,PLAYER_TOKEN)
    
    if turn == AI_TURN:
        print("AI's turn!")
        col = minimax(board, depth = 4, maximizingPlayer=True)[0]
        row = get_next_open_row(board,col)
        drop_token(board,row,col,AI_TOKEN)

    print_board(board)
    #turn+1 adjusts turn to have the corresponding token value for that player
    if winning_move(board, turn+1):
        locs = get_potential_locs(board)
        if len(locs) == 0:
            print("Draw! no one", end = "")
        elif turn == AI_TURN:
            print("AI",end = "")
        #else player's turn
        else:
            print("Player",end = "")
        print(" wins!")
        play_again = input("Play again? Y/N: ")
        if play_again == "Y" or play_again == "y":
            clear_board(board)
            print_board(board)
        else:
            game = False
    turn += 1
    turn %= 2
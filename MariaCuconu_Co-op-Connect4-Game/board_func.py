import random
# import pygame

import math
from copy import deepcopy

class Board_Service:

    def __init__(self,board):
        '''

        :param board: board
        '''
        self.__COLUMN_COUNT=board.COLUMN_COUNT
        self.__ROW_COUNT = board.ROW_COUNT
        self.__board=board.board

    @property
    def board(self):
        return self.__board

    @property
    def COLUMN_COUNT(self):
        return self.__COLUMN_COUNT

    @property
    def ROW_COUNT(self):
        return self.__ROW_COUNT

    def is_valid_location(self,board, col):
        '''
        Check if move on given col is possible
        :param board: board
        :param col: col to be checked
        :return: false is the location is not valid, true otherwise
        '''
        if col not in range(0, 7):
            return False
        # if col == None:
        #     return False
        return board[self.ROW_COUNT - 1][col] == 0

    def get_next_open_row(self,board, col):
        '''
        Get the next free row on which a move can be made
        :param board: board
        :param col: col to be checked
        :return: next unoccupied row or None if no more rows free on that col
        '''
        for r in range(self.ROW_COUNT):
            if board[r][col] == 0:
                return r

    def print_board(self):
        '''
        Flips board representation to prepare it for printing
        :return: call to the function that makes a string representation of board
        '''
        flipped = self.board[:]
        for i in range(self.ROW_COUNT // 2):
            flipped[i], flipped[self.ROW_COUNT - i - 1] = flipped[self.ROW_COUNT - i - 1], flipped[i]
        return str_board(flipped)
        #print(str_board(flipped))

    def winning_move(self,board, piece):
        '''
        Check if there is a win on the board for piece
        :param board: board
        :param piece: piece to check if it has a win on the board
        :return: True if there is a win on the board for piece, False otherwise
        '''
        # Check horizontal locations for win
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(self.ROW_COUNT):
                if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][
                    c + 3] == piece:
                    return True

        # Check vertical locations for win
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT - 3):
                if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][
                    c] == piece:
                    return True

        # Check positively sloped diaganols /
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(self.ROW_COUNT - 3):
                if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and \
                        board[r + 3][c + 3] == piece:
                    return True

        # Check negatively sloped diaganols \
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(3, self.ROW_COUNT):
                if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and \
                        board[r - 3][c + 3] == piece:
                    return True

    def evaluate_window(self,window, piece):
        '''
        Evaluate given window and return score
        :param window: board window to be evaluated
        :param piece: piece to evaluate window for
        :return: score
        '''
        score = 0
        opp_piece = 1 #PLAYER_PIECE
        if piece == 1:#PLAYER_PIECE:
            opp_piece = 2#AI_PIECE
        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 10
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(0) == 1:
            score -= 50
            # score-=15 loses in 15
            # score-=20 loses in 14
            # score-=25 #loses in 15
            # score -= 50#loses in 14 moves

        return score

    def score_position(self,board, piece):
        '''
        Return score of the board state
        :param board: board
        :param piece: piece to evaluate board for
        :return: score
        '''
        score = 0

        ## Score center column
        # center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
        center_array = [int(board[i][self.COLUMN_COUNT // 2]) for i in range(self.COLUMN_COUNT - 1)]
        center_count = center_array.count(piece)
        score += center_count * 2.25
        # todo attempt this after hwk^^^
        # score += center_count * 2.5#pretty good,beats hard on other site
        # score += center_count * 3
        # score += center_count * 5

        ## Score Horizontal
        for r in range(self.ROW_COUNT):
            # row_array = [int(i) for i in list(board[r, :])]
            row_array = board[r]
            for c in range(self.COLUMN_COUNT - 3):
                window = row_array[c:c + 4] #4 is window length
                score += self.evaluate_window(window, piece)

        ## Score Vertical
        for c in range(self.COLUMN_COUNT):
            # col_array = [int(i) for i in list(board[:, c])]
            col_array = [int(board[i][c]) for i in range(self.COLUMN_COUNT - 1)]
            for r in range(self.ROW_COUNT - 3):
                window = col_array[r:r + 4]#4 is window length
                score += self.evaluate_window(window, piece)

        ## Score posiive sloped diagonal /
        for r in range(self.ROW_COUNT - 3):
            for c in range(self.COLUMN_COUNT - 3):
                window = [board[r + i][c + i] for i in range(4)]#4 is window length
                score += self.evaluate_window(window, piece)
        ## Score negative sloped diagonal \

        for r in range(self.ROW_COUNT - 3):
            for c in range(self.COLUMN_COUNT - 3):
                window = [board[r + 3 - i][c + i] for i in range(4)]#4 is window length
                score += self.evaluate_window(window, piece)

        return score

    def is_tie(self,board):
        for i in range(self.COLUMN_COUNT):
            if board[self.ROW_COUNT-1][i]==0:
                return False
        return True

    def is_terminal_node(self,board):
        return self.winning_move(board,1) or self.winning_move(board,2) or len(self.get_valid_locations(board)) == 0
        #0 is player, 1 is computer

    def get_valid_locations(self,board):
        valid_locations = []
        for col in range(self.COLUMN_COUNT):
            if self.is_valid_location(board,col):
                valid_locations.append(col)
        return valid_locations

    def minimax(self,board, depth, alpha, beta, maximizingPlayer):
        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board,2):
                    return (None, 100000000000000)
                elif self.winning_move(board,1):
                    return (None, -10000000000000)
                else:  # Game is over, no more valid moves
                    return (None, 0)
            else:  # Depth is zero
                return (None, self.score_position(board,2))
        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board,col)
                # b_copy = board.copy()
                b_copy = deepcopy(board)
                drop_piece(b_copy, row, col, 2)
                new_score = self.minimax(b_copy, depth - 1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                    # nonweightedrow=row
                # if new_score==value:
                #     if weight>row:
                #         weight=row
                #         weightedcol=weight
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            # if weight<nonweightedrow:
            #     return weightedcol,value
            return column, value

        else:  # Minimizing player
            value = math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board,col)
                # b_copy = board.copy()
                b_copy = deepcopy(board)
                drop_piece(b_copy, row, col, 1)
                new_score = self.minimax(b_copy, depth - 1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value


def str_board(board):
    result = ""
    result = result + "0 1 2 3 4 5 6" + '\n'
    for row in range(6):
        for column in range(7):
            result = result + str(board[row][column]) + ' '
        result = result + '\n'
    return result

def drop_piece(board, row, col, piece):
    board[row][col] = piece
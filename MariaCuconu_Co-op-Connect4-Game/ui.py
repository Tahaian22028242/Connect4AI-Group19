from domain.board import Board
from service.board_func import Board_Service, drop_piece
import pygame
import random
import sys
import math
from random import randint

class GUI:

    def __init__(self,board,service):
        self.__board=board
        self.__service=service
        self.BLUE=(0, 0, 255)
        self.BLACK=(0, 0, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.SQUARESIZE = 100
        self.RADIUS = int(self.SQUARESIZE / 2 - 5)
        self.width = self.board.COLUMN_COUNT * self.SQUARESIZE
        self.height = (self.board.ROW_COUNT + 1) * self.SQUARESIZE
        self.size = (self.width,self.height)

    @property
    def board(self):
        return self.__board

    @board.setter
    def board(self,value):
        self.__board=value

    @property
    def service(self):
        return self.__service

    def draw_board(self,screen):
        # screen = pygame.display.set_mode(self.size)
        for c in range(self.board.COLUMN_COUNT):
            for r in range(self.board.ROW_COUNT):
                pygame.draw.rect(screen, self.BLUE, (c * self.SQUARESIZE, r * self.SQUARESIZE + self.SQUARESIZE, self.SQUARESIZE, self.SQUARESIZE))
                pygame.draw.circle(screen, self.BLACK, (
                    int(c * self.SQUARESIZE + self.SQUARESIZE / 2), int(r * self.SQUARESIZE + self.SQUARESIZE + self.SQUARESIZE / 2)), self.RADIUS)

        for c in range(self.board.COLUMN_COUNT):
            for r in range(self.board.ROW_COUNT):
                if self.board.board[r][c] == 1: #player piece
                    pygame.draw.circle(screen, self.RED, (
                        int(c * self.SQUARESIZE + self.SQUARESIZE / 2), self.height - int(r * self.SQUARESIZE + self.SQUARESIZE / 2)), self.RADIUS)
                elif self.board.board[r][c] == 2: #ai piece
                    pygame.draw.circle(screen, self.YELLOW, (
                        int(c * self.SQUARESIZE + self.SQUARESIZE / 2), self.height - int(r * self.SQUARESIZE + self.SQUARESIZE / 2)), self.RADIUS)
        pygame.display.update()

    def start(self):
        PLAYER=0
        AI=1
        PLAYER_PIECE = 1
        AI_PIECE = 2
        game_over = False
        pygame.init()
        screen = pygame.display.set_mode(self.size)
        self.draw_board(screen)
        pygame.display.update()
        myfont = pygame.font.SysFont("monospace", 75)
        #turn = random.randint(PLAYER, AI) #0 is player 1 is ai
        turn=0
        while not game_over:

            for event in pygame.event.get():

                # pygame.event.wait(500)

                if self.service.is_tie(self.board.board) == True:
                    label = myfont.render("Tie!", 1, self.BLUE)
                    screen.blit(label, (40, 10))
                    game_over = True

                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, self.BLACK, (0, 0, self.width, self.SQUARESIZE))
                    posx = event.pos[0]
                    if turn == PLAYER:
                        pygame.draw.circle(screen, self.RED, (posx, int(self.SQUARESIZE / 2)), self.RADIUS)

                pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, self.BLACK, (0, 0, self.width, self.SQUARESIZE))
                    # print(event.pos)
                    # Ask for Player 1 Input
                    if turn == PLAYER:
                        posx = event.pos[0]
                        col = int(math.floor(posx / self.SQUARESIZE))

                        if self.service.is_valid_location(self.board.board,col):
                            row = self.service.get_next_open_row(self.board.board, col)
                            drop_piece(self.board.board, row, col, PLAYER_PIECE)

                            if self.service.winning_move(self.board.board,PLAYER_PIECE):
                                label = myfont.render("Player wins!!", 1, self.RED)
                                screen.blit(label, (40, 10))
                                game_over = True

                            turn += 1
                            turn = turn % 2

                            #self.print_board(board)
                            self.draw_board(screen)

                        else:
                            label = myfont.render("Invalid move", 1, self.RED)
                            screen.blit(label, (40, 10))
                            continue
                break

            # # Ask for Player 2 Input
            if turn == AI and not game_over:

                # col = random.randint(0, COLUMN_COUNT-1)
                # col = pick_best_move(board, AI_PIECE)
                col, minimax_score = self.service.minimax(self.board.board,2, -math.inf, math.inf, True)
                # todo works really well with 2

                # col, minimax_score = minimax(board, 5, -math.inf, math.inf, False)

                if self.service.is_valid_location(self.board.board,col):
                    # pygame.time.wait(500)
                    row = self.service.get_next_open_row(self.board.board,col)
                    drop_piece(self.board.board, row, col, AI_PIECE)

                    if self.service.winning_move(self.board.board, AI_PIECE):
                        label = myfont.render("Computer wins!", 1, self.YELLOW)
                        screen.blit(label, (40, 10))
                        game_over = True

                    #print_board(board)
                    self.draw_board(screen)

                    turn += 1
                    turn = turn % 2

            if game_over:
                pygame.time.wait(3000)


class UI:
    def __init__(self,board,service):
        self.__board=board
        self.__service=service

    @property
    def board(self):
        return self.__board

    @board.setter
    def board(self,value):
        self.__board=value

    @property
    def service(self):
        return self.__service

    def start(self):
        PLAYER=0
        AI=1
        PLAYER_PIECE = 1
        AI_PIECE = 2
        print(self.service.print_board())
        not_game_over = 1
        turn = randint(PLAYER,AI)
        if turn==PLAYER:
            print("PLayer starts first\n")
        else:
            print("Computer starts first\n")
        while not_game_over:

            if self.service.is_tie(self.board.board) == True:
                print("Tie!")
                not_game_over = 0
                break

            if turn == 0:
                player_move=-1
                while player_move==-1:
                    try:
                        player_move = int(input("Enter a move 0-6\n"))
                    except ValueError:
                        print("Invalid input, enter an integer 0-6\n")

                while self.service.is_valid_location(self.board.board,player_move) is False:
                    print("Invalid move\n")
                    try:
                        player_move = int(input("Enter a move 0-6\n"))
                    except ValueError:
                        print("Invalid input, enter an integer 0-6\n")

                row = self.service.get_next_open_row(self.board.board, player_move)
                drop_piece(self.board.board, row, player_move, PLAYER_PIECE)
                if self.service.winning_move(self.board.board, PLAYER_PIECE):
                    print("Player won")
                    not_game_over = 0

                turn += 1
                turn = turn % 2
                print(self.service.print_board())
            else:
                computer_move, minimax_score = self.service.minimax(self.board.board, 2, -math.inf, math.inf, True)

                if self.service.is_valid_location(self.board.board, computer_move):
                    row = self.service.get_next_open_row(self.board.board, computer_move)
                    drop_piece(self.board.board, row, computer_move, AI_PIECE)

                    if self.service.winning_move(self.board.board, AI_PIECE):
                        print("Computer won")
                        not_game_over = 0

                    print(self.service.print_board())
                    turn += 1
                    turn = turn % 2







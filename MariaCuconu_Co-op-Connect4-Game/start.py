from domain.board import Board
from service.board_func import Board_Service
from ui.ui import GUI,UI
import sys
import pygame



# def start():
#     ui.start()


def start():
    while True:
        try:
            option=input("Choose ui option      -UI             -GUI        -exit\n")
            board = Board(6, 7)
            service = Board_Service(board)
            if option=='GUI':
                ui = GUI(board, service)
                ui.start()
                pygame.quit()
            elif option=='UI':
                ui= UI(board,service)
                ui.start()
            elif option=='exit':
                exit()
            else:
                print("Invalid option, try again")
        except TypeError:
            print("Invalid option, try again")
        if option=='GUI' or option=='UI':
            ask=0
            while ask!='y' or ask!='n':
                ask=input("Do you wish to play again?       y/n\n")
                if ask=='n':
                    exit()
                elif ask=='y':
                    break
                else:
                    print("Invalid option, try again")

start()

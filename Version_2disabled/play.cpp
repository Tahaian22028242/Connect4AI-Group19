// play.cpp - Interactive 1-vs-AI console game supporting disabled cells
#include "Position.hpp"
#include "Solver.hpp"
#include <iostream>
#include <sstream>
#include <cstdlib>
#include <ctime>

using namespace GameSolver::Connect4;

static void printBoard(const Position &P) {
    bool userToPlay = (P.nbMoves() % 2 == 0); // user always plays first
    for(int r = Position::HEIGHT - 1; r >= 0; --r) {
        std::cout << "|";
        for(int c = 0; c < Position::WIDTH; ++c) {
            Position::position_t bit = Position::position_t(1) << (c * (Position::HEIGHT + 1) + r);
            char ch = '.';
            if(P.disabled_cells & bit) ch = '*';
            else if(P.mask & bit) {
                bool inCur = P.current_position & bit;
                bool isUserStone = (inCur && userToPlay) || (!inCur && !userToPlay);
                ch = isUserStone ? '1' : '2';
            }
            std::cout << ch << " ";
        }
        std::cout << "|" << std::endl;
    }
    // column numbers
    std::cout << " 1 2 3 4 5 6 7" << std::endl;
}

int main() {
    std::srand(static_cast<unsigned int>(std::time(nullptr)));
    Solver solver;
    solver.loadBook("7x6.book");

    Position P;

    std::cout << "Enter disabled cells as four integers (row1 col1 row2 col2) or press Enter for random:" << std::endl;
    std::string line;
    std::getline(std::cin, line);
    if(line.empty()) {
        int r1 = std::rand() % Position::HEIGHT;
        int c1 = std::rand() % Position::WIDTH;
        int r2, c2;
        do {
            r2 = std::rand() % Position::HEIGHT;
            c2 = std::rand() % Position::WIDTH;
        } while(r1 == r2 && c1 == c2);
        P.disableCell(r1, c1);
        P.disableCell(r2, c2);
        std::cerr << "Random disabled cells: (" << r1 << "," << c1 << ") (" << r2 << "," << c2 << ")" << std::endl;
    } else {
        std::istringstream iss(line);
        int r1, c1, r2, c2;
        if(!(iss >> r1 >> c1 >> r2 >> c2)) {
            std::cerr << "Invalid format" << std::endl;
            return 1;
        }
        P.disableCell(r1, c1);
        P.disableCell(r2, c2);
    }

    std::cout << "You are player 1 (marker '1'). AI is player 2 ('2'). Disabled cells are '*'." << std::endl;

    while(true) {
        printBoard(P);
        bool userTurn = (P.nbMoves() % 2 == 0);
        if(!userTurn) {
            int colInput;
            while(true) {
                std::cout << "Your move (1-7): ";
                std::cin >> colInput;
                if(std::cin.fail()) return 0;
                colInput--; // to 0-based
                if(colInput >= 0 && colInput < Position::WIDTH && P.canPlay(colInput)) break;
                std::cout << "Invalid column, try again." << std::endl;
            }
            if(P.isWinningMove(colInput)) {
                std::cout << "You win!" << std::endl;
                break;
            }
            P.playCol(colInput);
        } else {
            auto scores = solver.analyze(P);
            int bestCol = -1; int bestScore = Solver::INVALID_MOVE;
            for(int c = 0; c < Position::WIDTH; ++c) {
                if(scores[c] != Solver::INVALID_MOVE && (bestCol == -1 || scores[c] > bestScore)) {
                    bestScore = scores[c];
                    bestCol = c;
                }
            }
            std::cout << "AI plays column " << (bestCol + 1) << std::endl;
            if(P.isWinningMove(bestCol)) {
                std::cout << "AI wins!" << std::endl;
                break;
            }
            P.playCol(bestCol);
        }

        if(P.nbMoves() >= P.playableCellCount()) {
            printBoard(P);
            std::cout << "Game is a draw!" << std::endl;
            break;
        }
    }
    return 0;
} 
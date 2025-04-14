// main.cpp
#include "Position.hpp"
#include "Solver.hpp"
#include <iostream>
#include <string>
#include <vector>

using namespace GameSolver::Connect4;

int main()
{
    std::string move_sequence;
    int current_player;
    Solver solver;
    std::string opening_book = "7x6.book";
    solver.loadBook(opening_book);

    // Read move sequence and current player
    std::getline(std::cin, move_sequence);

    // Create Position and replay the game
    Position P;
    for (char move : move_sequence)
    {
        int col = move - '1';
        P.playCol(col);
    }

    // Get best move
    std::vector<int> scores = solver.analyze(P);
    int best_move = 0;
    int best_score = scores[0];

    for (int move = 0; move < Position::WIDTH; move++)
    {
        if (scores[move] > best_score)
        {
            best_score = scores[move];
            best_move = move;
        }
    }

    std::cout << best_move << std::endl;

    return 0;
}
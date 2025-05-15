
#include <cassert>
#include "Solver.hpp"
#include "MoveSorter.hpp"
#ifdef _OPENMP
#include <omp.h>
#endif

using namespace GameSolver::Connect4;
namespace {

inline int popcount64(Position::position_t x) {
    return __builtin_popcountll(x);
}

inline int evaluate(const Position& P)
{
    // Check for immediate win to avoid assertion failure
    if (P.canWinNext()) {
        return -(P.playableCellCount() + 1 - P.nbMoves()) / 2;
    }

    using position_t = Position::position_t;
    
    // Determine game phase (early, mid, late)
    const int totalCells = P.playableCellCount();
    const int moveCount = P.nbMoves();
    const int movePercent = (moveCount * 100) / totalCells;
    const bool earlyGame = movePercent < 30;
    const bool lateGame = movePercent > 70;
    
    // Weights for each column (center is more valuable, edges less valuable)
    // Adjust weights based on game phase
    int colW[Position::WIDTH];
    if (earlyGame) {
        // Early game - emphasize center control even more
        colW[0] = 2; colW[1] = 3; colW[2] = 5; colW[3] = 11; colW[4] = 5; colW[5] = 3; colW[6] = 2;
    } else if (lateGame) {
        // Late game - more balanced column values as threats become more important
        colW[0] = 3; colW[1] = 4; colW[2] = 5; colW[3] = 7; colW[4] = 5; colW[5] = 4; colW[6] = 3;
    } else {
        // Mid game - standard weights
        colW[0] = 2; colW[1] = 3; colW[2] = 5; colW[3] = 9; colW[4] = 5; colW[5] = 3; colW[6] = 2;
    }
    
    int score = 0;
    
    // Cache common values
    position_t myPieces = P.current_position;
    position_t oppPieces = P.mask ^ myPieces & ~P.disabled_cells;
    
    // Column-based evaluation
    for (int c = 0; c < Position::WIDTH; ++c) {
        position_t colBits = Position::column_mask(c);
        
        // Count my pieces and opponent pieces in the column
        int my = popcount64(myPieces & colBits);
        int opp = popcount64(oppPieces & colBits);
        
        // Apply column weights with diminishing returns for overcrowded columns
        int diff = my - opp;
        if (diff > 0) {
            score += colW[c] * (diff > 2 ? 2 + (diff - 2) / 2 : diff); // Diminishing returns
        } else {
            score += colW[c] * (diff < -2 ? -2 + (diff + 2) / 2 : diff); // Diminishing returns
        }
        
        // NEW: Height-based evaluation - pieces higher up have more strategic value
        for (int h = 0; h < Position::HEIGHT; ++h) {
            position_t cellBit = 1ULL << (h + c * (Position::HEIGHT + 1));
            
            if (myPieces & cellBit) {
                // My pieces get value based on height
                score += h / 2; // Higher pieces worth more
            } else if (oppPieces & cellBit) {
                // Opponent pieces get negative value based on height
                score -= h / 2;
            }
        }
        
        // Adjust for disabled cells in this column - more penalty
        int disabledInCol = popcount64(P.disabled_cells & colBits);
        if (disabledInCol > 0) {
            // Reduce value of columns with disabled cells (harder to make connect-4)
            score -= colW[c] * disabledInCol;
            
            // More penalty for disabled cells near the bottom (blocking key squares)
            position_t bottomCells = colBits & ((1ULL << 3) - 1) << (c * (Position::HEIGHT + 1));
            if (P.disabled_cells & bottomCells) {
                score -= 4; // Increased penalty for bottom disabled cells
            }
        }
    }
    
    // Evaluate potential winning positions
    position_t myWinPos = P.winning_position();
    position_t oppWinPos = P.opponent_winning_position();
    
    // Count potential winning positions
    int myWinCount = popcount64(myWinPos);
    int oppWinCount = popcount64(oppWinPos);
    
    // Strongly favor having more winning opportunities (adjusted weight)
    int winPosWeight = lateGame ? 6 : 5; // More important in late game
    score += (myWinCount - oppWinCount) * winPosWeight;
    
    // Evaluate threats - connected pieces that could become winning next
    position_t myThreats = 0, oppThreats = 0;
    
    // Check for 3-in-a-row patterns that could become 4
    for (int dir = 0; dir < 4; dir++) { // Horizontal, vertical, 2 diagonals
        int shift = dir == 0 ? 1 : (dir == 1 ? Position::HEIGHT + 1 : (dir == 2 ? Position::HEIGHT + 2 : Position::HEIGHT));
        
        // Check for my "three-in-a-row" with open fourth spot
        position_t three1 = myPieces & (myPieces >> shift) & (myPieces >> (2 * shift));
        myThreats |= three1 | (three1 >> shift);
        
        // Check for opponent's "three-in-a-row" with open fourth spot
        position_t three2 = oppPieces & (oppPieces >> shift) & (oppPieces >> (2 * shift));
        oppThreats |= three2 | (three2 >> shift);
        
        // NEW: Check for 2-in-a-row patterns with potential
        position_t two1 = myPieces & (myPieces >> shift) & ~(oppPieces | P.disabled_cells);
        position_t two2 = oppPieces & (oppPieces >> shift) & ~(myPieces | P.disabled_cells);
        
        // Add to score based on 2-in-row patterns (with less weight)
        score += popcount64(two1 & P.possible()) - popcount64(two2 & P.possible());
    }
    
    // Only count threats that are currently possible to complete
    myThreats &= P.possible();
    oppThreats &= P.possible();
    
    int myThreatCount = popcount64(myThreats);
    int oppThreatCount = popcount64(oppThreats);
    
    // Adjusted threat weights based on game phase
    int doubleThreatValue = lateGame ? 20 : 16;
    int singleThreatValue = lateGame ? 7 : 5;
    
    // Double-threat is extremely valuable
    if (myThreatCount >= 2) score += doubleThreatValue;
    if (oppThreatCount >= 2) score -= doubleThreatValue;
    
    // Add score for single threats
    score += (myThreatCount - oppThreatCount) * singleThreatValue;
    
    // NEW: Evaluate connectivity of pieces
    int myConnectivity = 0, oppConnectivity = 0;
    
    // Check adjacent pieces (horizontal, vertical, diagonal)
    for (int dir = 0; dir < 4; dir++) {
        int shift = dir == 0 ? 1 : (dir == 1 ? Position::HEIGHT + 1 : (dir == 2 ? Position::HEIGHT + 2 : Position::HEIGHT));
        
        // Count adjacent pairs
        position_t myPairs = myPieces & (myPieces >> shift);
        position_t oppPairs = oppPieces & (oppPieces >> shift);
        
        myConnectivity += popcount64(myPairs);
        oppConnectivity += popcount64(oppPairs);
    }
    
    // Add connectivity score (with moderate weight)
    score += (myConnectivity - oppConnectivity) * 2;
    
    // NEW: Evaluate trapped opponent pieces (surrounded by my pieces or disabled cells)
    position_t trapped = 0;
    for (int c = 1; c < Position::WIDTH - 1; c++) {
        for (int r = 1; r < Position::HEIGHT - 1; r++) {
            position_t cellBit = 1ULL << (r + c * (Position::HEIGHT + 1));
            if (oppPieces & cellBit) {
                // Check if surrounded on multiple sides
                int surrounded = 0;
                for (int dx = -1; dx <= 1; dx++) {
                    for (int dy = -1; dy <= 1; dy++) {
                        if (dx == 0 && dy == 0) continue;
                        position_t neighborBit = 1ULL << ((r + dy) + (c + dx) * (Position::HEIGHT + 1));
                        if (myPieces & neighborBit || P.disabled_cells & neighborBit) {
                            surrounded++;
                        }
                    }
                }
                if (surrounded >= 4) {
                    trapped |= cellBit;
                }
            }
        }
    }
    
    // Add trapped piece score
    score += popcount64(trapped) * 3;
    
    // Evaluate best moves
    position_t myMoves = P.possibleNonLosingMoves();   
    position_t oppMoves = P.possible() & ~myMoves;    
    int bestMy = 0, bestOpp = 0;
    
    // Find best move scores
    position_t m = myMoves;
    while (m) {
        position_t move = m & -m;
        bestMy = std::max(bestMy, P.moveScore(move));
        m &= m - 1; // Clear least significant bit
    }
    
    m = oppMoves;
    while (m) {
        position_t move = m & -m;
        bestOpp = std::max(bestOpp, P.moveScore(move));
        m &= m - 1; // Clear least significant bit
    }
    
    // Adjusted weight for best move differential
    int bestMoveWeight = earlyGame ? 2 : (lateGame ? 4 : 3);
    score += (bestMy - bestOpp) * bestMoveWeight;
    
    // Special handling for disabled cells
    if (P.disabledCount() > 0) {
        // Credit for controlling columns around disabled cells
        position_t disabledCellMask = P.disabled_cells;
        while (disabledCellMask) {
            position_t cell = disabledCellMask & -disabledCellMask;
            disabledCellMask &= disabledCellMask - 1;
            
            // Find neighboring columns of this disabled cell
            int col = 0;
            position_t temp = cell;
            while (temp >>= (Position::HEIGHT + 1)) col++;
            
            // Award points for controlling columns adjacent to disabled cells
            if (col > 0) { // Check left column
                position_t leftCol = Position::column_mask(col - 1);
                int myLeft = popcount64(myPieces & leftCol);
                int oppLeft = popcount64(oppPieces & leftCol);
                score += (myLeft - oppLeft) * 3; // Increased importance
            }
            
            if (col < Position::WIDTH - 1) { // Check right column
                position_t rightCol = Position::column_mask(col + 1);
                int myRight = popcount64(myPieces & rightCol);
                int oppRight = popcount64(oppPieces & rightCol);
                score += (myRight - oppRight) * 3; // Increased importance
            }
            
            // NEW: Check if disabled cell is blocking a potential connect-4
            // This checks if the disabled cell could be part of a winning line
            for (int dir = 0; dir < 4; dir++) {
                int shift = dir == 0 ? 1 : (dir == 1 ? Position::HEIGHT + 1 : (dir == 2 ? Position::HEIGHT + 2 : Position::HEIGHT));
                
                // Check if disabled cell is blocking my potential win
                if (((cell >> shift) & myPieces) && ((cell >> (2*shift)) & myPieces) && ((cell >> (3*shift)) & myPieces)) {
                    score -= 5; // I'm blocked by disabled cell
                }
                
                // Check if disabled cell is blocking opponent's potential win
                if (((cell >> shift) & oppPieces) && ((cell >> (2*shift)) & oppPieces) && ((cell >> (3*shift)) & oppPieces)) {
                    score += 5; // Opponent is blocked
                }
            }
        }
        
        // Special bonus for middle columns when there are disabled cells
        for (int c = 2; c <= 4; ++c) {
            if (P.canPlay(c) && !P.isWinningMove(c)) {
                score += 5;  // Increased bonus for middle columns
            }
        }
        
        // Special penalty for column 0 to avoid overplaying it
        if (P.canPlay(0) && !P.isWinningMove(0)) {
            score -= 7;
        }
        
        // NEW: Evaluate forced moves due to disabled cell configurations
        position_t forcedDefense = oppThreats;
        if (popcount64(forcedDefense) == 1) {
            // Having exactly one forced defensive move is bad
            score -= 6;
        }
    }
    
    // Detect and reward key patterns with disabled cells
    if (myWinCount > oppWinCount + 1) {
        score += 12; // Increased reward for multiple winning threats
    }
    
    // Mobility evaluation - prefer positions with more move options
    int myMobility = popcount64(myMoves);
    int oppMobility = popcount64(oppMoves);
    
    // Adjust mobility importance based on game phase
    int mobilityWeight = earlyGame ? 2 : 1;
    score += (myMobility - oppMobility) * mobilityWeight;
    
    // NEW: Penalty for limited mobility in late game
    if (lateGame && myMobility <= 2) {
        score -= 5; // Significant penalty for low mobility in late game
    }
    
    return score / 18;  // Adjusted normalization to keep score in reasonable range
}

} // anonymous namespace

namespace GameSolver {
namespace Connect4 {

/**
 * Reccursively score connect 4 position using negamax variant of alpha-beta algorithm.
 * @param: position to evaluate, this function assumes nobody already won and
 *         current player cannot win next move. This has to be checked before
 * @param: alpha < beta, a score window within which we are evaluating the position.
 *
 * @return the exact score, an upper or lower bound score depending of the case:
 * - if actual score of position <= alpha then actual score <= return value <= alpha
 * - if actual score of position >= beta then beta <= return value <= actual score
 * - if alpha <= actual score <= beta then return value = actual score
 */
int Solver::negamax(const Position &P, int alpha, int beta, int depthLeft) {
  assert(alpha < beta);
  if (P.canWinNext()) {
    return -(P.playableCellCount() + 1 - P.nbMoves()) / 2;
  }
  if (depthLeft == 0) {
    return evaluate(P);
  }

  nodeCount++; // increment counter of explored nodes

  const int totalCells = P.playableCellCount();
  Position::position_t possible = P.possibleNonLosingMoves();
  if(possible == 0)     // if no possible non losing move, opponent wins next move
    return -(totalCells - P.nbMoves()) / 2;

  if(P.nbMoves() >= totalCells - 2) // check for draw game
    return 0;

  int min = -(totalCells - 2 - P.nbMoves()) / 2;	// lower bound of score as opponent cannot win next move
  if(alpha < min) {
    alpha = min;                     // there is no need to keep alpha below our max possible score.
    if(alpha >= beta) return alpha;  // prune the exploration if the [alpha;beta] window is empty.
  }

  int max = (totalCells - 1 - P.nbMoves()) / 2;	// upper bound of our score as we cannot win immediately
  if(beta > max) {
    beta = max;                     // there is no need to keep beta above our max possible score.
    if(alpha >= beta) return beta;  // prune the exploration if the [alpha;beta] window is empty.
  }

  const Position::position_t key = P.key();
   
  if(int val = transTable.get(key)) {
    if(val > Position::MAX_SCORE - Position::MIN_SCORE + 1) { // we have an lower bound
      min = val + 2 * Position::MIN_SCORE - Position::MAX_SCORE - 2;
      if(alpha < min) {
        alpha = min;                     // there is no need to keep beta above our max possible score.
        if(alpha >= beta) return alpha;  // prune the exploration if the [alpha;beta] window is empty.
      }
    } else { // we have an upper bound
      max = val + Position::MIN_SCORE - 1;
      if(beta > max) {
        beta = max;                     // there is no need to keep beta above our max possible score.
        if(alpha >= beta) return beta;  // prune the exploration if the [alpha;beta] window is empty.
      }
    }
  }

  if(int val = book.get(P)) return val + Position::MIN_SCORE - 1; // look for solutions stored in opening book

  MoveSorter moves;
  for(int i = Position::WIDTH; i--;)
    if(Position::position_t move = possible & Position::column_mask(columnOrder[i]))
      moves.add(move, P.moveScore(move));

  while(Position::position_t next = moves.getNext()) {
    Position P2(P);
    P2.play(next);  // It's opponent turn in P2 position after current player plays x column.
    int score = -negamax(P2, -beta, -alpha, depthLeft - 1); // explore opponent's score within [-beta;-alpha] windows:
    // no need to have good precision for score better than beta (opponent's score worse than -beta)
    // no need to check for score worse than alpha (opponent's score worse better than -alpha)

    if(score >= beta) {
      transTable.put(key, score + Position::MAX_SCORE - 2 * Position::MIN_SCORE + 2); // save the lower bound of the position
      return score;  // prune the exploration if we find a possible move better than what we were looking for.
    }
    if(score > alpha) alpha = score; // reduce the [alpha;beta] window for next exploration, as we only
    // need to search for a position that is better than the best so far.
  }

  transTable.put(key, alpha - Position::MIN_SCORE + 1); // save the upper bound of the position
  return alpha;
}

int Solver::solve(const Position &P, bool weak, int maxDepth) {
  const int totalCells = P.playableCellCount();
  if(P.canWinNext()) // check if win in one move as the Negamax function does not support this case.
    return (totalCells + 1 - P.nbMoves()) / 2;
  int min = -(totalCells - P.nbMoves()) / 2;
  int max = (totalCells + 1 - P.nbMoves()) / 2;
  if(weak) {
    min = -1;
    max = 1;
  }

  while(min < max) {                    // iteratively narrow the min-max exploration window
    int med = min + (max - min) / 2;
    if(med <= 0 && min / 2 < med) med = min / 2;
    else if(med >= 0 && max / 2 > med) med = max / 2;
    int r = negamax(P, med, med + 1, maxDepth);   // use a null depth window to know if the actual score is greater or smaller than med
    if(r <= med) max = r;
    else min = r;
  }
  return min;
}

std::vector<int> Solver::analyze(const Position &P, bool weak) {
  std::vector<int> scores(Position::WIDTH, Solver::INVALID_MOVE);

  // Exploit mirror symmetry: evaluate only half columns

  bool earlyGame      = (P.nbMoves() < 6);

  for(int col = 0; col < Position::WIDTH; ++col) {
   
    if(!P.canPlay(col)) continue;

    int val;
    if(P.isWinningMove(col)) val = (P.playableCellCount() + 1 - P.nbMoves()) / 2;
    else {
      Position P2(P);
      P2.playCol(col);
      int maxDepth = earlyGame ? 20 : 99;
      val = -solve(P2, weak, maxDepth);
    }

    scores[col] = val;

    
  }

  return scores;
}

// Constructor
Solver::Solver() : nodeCount{0} {
  for(int i = 0; i < Position::WIDTH; i++) // initialize the column exploration order, starting with center columns
    columnOrder[i] = Position::WIDTH / 2 + (1 - 2 * (i % 2)) * (i + 1) / 2; // example for WIDTH=7: columnOrder = {3, 4, 2, 5, 1, 6, 0}
}
  
// mirror helper to exploit board symmetry (disabled cells + pieces layout)
static Position::position_t mirror_bitboard(Position::position_t m) {
  using position_t = Position::position_t;
  position_t res = 0;
  constexpr position_t columnBase = (position_t(1) << Position::HEIGHT) - 1;
  for(int c = 0; c < Position::WIDTH; ++c) {
    position_t mask = columnBase << c * (Position::HEIGHT + 1);
    position_t bits = m & mask;
    if(bits) {
      int dest = Position::WIDTH - 1 - c;
      int shift = (dest - c) * (Position::HEIGHT + 1);
      res |= (shift > 0) ? (bits << shift) : (bits >> (-shift));
    }
  }
  return res;
}

} // namespace Connect4
} // namespace GameSolver

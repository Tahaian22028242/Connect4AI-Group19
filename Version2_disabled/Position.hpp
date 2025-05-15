
#ifndef POSITION_HPP
#define POSITION_HPP

#include <string>
#include <cstdint>
#include <cassert>

namespace GameSolver {
namespace Connect4 {

class Position {
 public:
  static constexpr int WIDTH = 7;  // width of the board
  static constexpr int HEIGHT = 6; // height of the board

  // Board size is 64bits or 128 bits depending on WIDTH and HEIGHT
  using position_t = typename std::conditional < WIDTH * (HEIGHT + 1) <= 64, uint64_t, __int128>::type;
  // __int128 is a g++ non portable type. Use the following line limited to 64bits board for C++ compatibility
  // using position_t = uint64_t;

  static constexpr int MIN_SCORE = -(WIDTH*HEIGHT) / 2 + 3;
  static constexpr int MAX_SCORE = (WIDTH * HEIGHT + 1) / 2 - 3;

  static_assert(WIDTH < 10, "Board's width must be less than 10");
  static_assert(WIDTH * (HEIGHT + 1) <= sizeof(position_t)*8, "Board does not fit into position_t bitmask");

  /**
   * Plays a possible move given by its bitmap representation
   *
   * @param move: a possible move given by its bitmap representation
   *        only one bit of the bitmap should be set to 1
   *        the move should be a valid possible move for the current player
   */
  void play(position_t move) {
    current_position ^= mask;
    mask |= move;
    moves++;
  }

  /*
   * Plays a sequence of successive played columns, mainly used to initilize a board.
   * @param seq: a sequence of digits corresponding to the 1-based index of the column played.
   *
   * @return number of played moves. Processing will stop at first invalid move that can be:
   *           - invalid character (non digit, or digit >= WIDTH)
   *           - playing a colum the is already full
   *           - playing a column that makes an alignment (we only solve non).
   *         Caller can check if the move sequence was valid by comparing the number of
   *         processed moves to the length of the sequence.
   */
  unsigned int play(const std::string &seq) {
    for(unsigned int i = 0; i < seq.size(); i++) {
      int col = seq[i] - '1';
      if(col < 0 || col >= Position::WIDTH || !canPlay(col) || isWinningMove(col)) return i; // invalid move
      playCol(col);
    }
    return seq.size();
  }

  /**
   * return true if current player can win next move
   */
  bool canWinNext() const {
    return winning_position() & possible();
  }


  /**
   * @return number of moves played from the beginning of the game.
   */
  int nbMoves() const {
    return moves;
  }

  // Number of disabled cells (bits set in disabled_cells)
  int disabledCount() const {
    return popcount(disabled_cells);
  }

  // Total playable cells in this game (board cells minus disabled ones)
  int playableCellCount() const {
    return WIDTH * HEIGHT - disabledCount();
  }

  // Remaining free playable cells (not disabled and not occupied)
  int remainingPlayableCells() const {
    return playableCellCount() - nbMoves();
  }

  /**
   * @return a compact representation of a position on WIDTH*(HEIGHT+1) bits.
   */
  position_t key() const {
    // Include disabled_cells in the unique key so positions that differ only by disabled layout are distinguished.
    return current_position + mask + (disabled_cells << 1);
  }

 
  uint64_t key3() const {
    uint64_t key_forward = 0;
    for(int i = 0; i < Position::WIDTH; i++) partialKey3(key_forward, i);  // compute key in increasing order of columns

    uint64_t key_reverse = 0;
    for(int i = Position::WIDTH; i--;) partialKey3(key_reverse, i);  // compute key in decreasing order of columns

    return key_forward < key_reverse ? key_forward / 3 : key_reverse / 3; // take the smallest key and divide per 3 as the last base3 digit is always 0
  }

  /**
   * Symmetry-aware key that ALSO encodes the disabled mask so two positions that differ only
   * by the layout of blocked cells do NOT collide.  It keeps the mirror-symmetry property by
   * computing the key for both directions and taking the minimum.
   */
  uint64_t key3Disabled() const {
    // Base-3 key part (without disabled mask)
    uint64_t k_fwd = 0;
    for(int i = 0; i < Position::WIDTH; i++) partialKey3(k_fwd, i);
    uint64_t k_rev = 0;
    for(int i = Position::WIDTH; i--;) partialKey3(k_rev, i);
    k_fwd /= 3; // remove trailing 0
    k_rev /= 3;

    // Prepare disabled masks for forward and mirrored boards
    auto mirror_mask = [](position_t m) {
      position_t res = 0;
      constexpr position_t columnBase = (position_t(1) << HEIGHT) - 1; // HEIGHT ones
      for(int c = 0; c < WIDTH; ++c) {
        position_t colMask = columnBase << c * (HEIGHT + 1);
        position_t colBits = m & colMask;
        int dest = WIDTH - 1 - c;
        int shift = (dest - c) * (HEIGHT + 1);
        if(shift > 0) res |= colBits << shift;
        else if(shift < 0) res |= colBits >> (-shift);
        else res |= colBits;
      }
      return res;
    };
    uint64_t d_fwd = static_cast<uint64_t>(disabled_cells);
    uint64_t d_rev = static_cast<uint64_t>(mirror_mask(disabled_cells));

    constexpr uint64_t MIX = 0x9e3779b97f4a7c15ULL; // golden ratio constant for hashing
    uint64_t key_forward = k_fwd ^ (d_fwd * MIX);
    uint64_t key_reverse = k_rev ^ (d_rev * MIX);

    return key_forward < key_reverse ? key_forward : key_reverse;
  }

  /**
   * Return a bitmap of all the possible next moves the do not lose in one turn.
   * A losing move is a move leaving the possibility for the opponent to win directly.
   *
   * Warning this function is intended to test position where you cannot win in one turn
   * If you have a winning move, this function can miss it and prefer to prevent the opponent
   * to make an alignment.
   */
  position_t possibleNonLosingMoves() const {
    assert(!canWinNext());
    position_t possible_mask = possible();
    position_t opponent_win = opponent_winning_position();
    position_t forced_moves = possible_mask & opponent_win;
    if(forced_moves) {
      if(forced_moves & (forced_moves - 1)) // check if there is more than one forced move
        return 0;                           // the opponnent has two winning moves and you cannot stop him
      else possible_mask = forced_moves;    // enforce to play the single forced move
    }
    return possible_mask & ~(opponent_win >> 1);  // avoid to play below an opponent winning spot
  }

  /**
   * Score a possible move.
   *
   * @param move, a possible move given in a bitmap format.
   *
   * The score we are using is the number of winning spots
   * the current player has after playing the move.
   */
  int moveScore(position_t move) const {
    return popcount(compute_winning_position(current_position | move, mask | disabled_cells));
  }

  /**
   * Default constructor, build an empty position.
   */
  Position() : current_position{0}, mask{0}, disabled_cells{0}, moves{0} {}

  /**
   * Convenience constructor when the set of disabled cells is already known as a bitboard
   */
  explicit Position(position_t disabled) : current_position{0}, mask{0}, disabled_cells{disabled}, moves{0} {}

  /**
   * Helper to disable a single cell by its (row, col) coordinate (0-based)
   */
  void disableCell(int row, int col) {
    assert(row >= 0 && row < HEIGHT && col >= 0 && col < WIDTH);
    disabled_cells |= position_t(1) << (col * (HEIGHT + 1) + row);
  }

  /**
   * Indicates whether a column is playable.
   * @param col: 0-based index of column to play
   * @return true if the column is playable, false if the column is already full.
   */
  bool canPlay(int col) const {
    position_t col_mask = column_mask(col);
    position_t filled = mask | disabled_cells;
    return ((filled + bottom_mask_col(col)) & col_mask & ~filled) != 0;
  }

  /**
   * Plays a playable column.
   * This function should not be called on a non-playable column or a column making an alignment.
   *
   * @param col: 0-based index of a playable column.
   */
  void playCol(int col) {
    position_t col_mask = column_mask(col);
    position_t filled   = mask | disabled_cells; // treat disabled cells as filled for drop computation
    position_t move = (filled + bottom_mask_col(col)) & col_mask & ~disabled_cells; // ensure we never place on a disabled cell
    play(move);
  }

  /**
   * Indicates whether the current player wins by playing a given column.
   * This function should never be called on a non-playable column.
   * @param col: 0-based index of a playable column.
   * @return true if current player makes an alignment by playing the corresponding column col.
   */
  bool isWinningMove(int col) const {
    return winning_position() & possible() & column_mask(col);
  }

 public:
  position_t current_position; // bitmap of the current_player stones
  position_t mask;             // bitmap of all the already palyed spots
  unsigned int moves;        // number of moves played since the beinning of the game.

  /**
    * Compute a partial base 3 key for a given column
    */
  void partialKey3(uint64_t &key, int col) const {
    for(position_t pos = UINT64_C(1) << (col * (Position::HEIGHT + 1)); pos & mask; pos <<= 1) {
      key *= 3;
      if(pos & current_position) key += 1;
      else key += 2;
    }
    key *= 3;
  }

  /**
   * Return a bitmask of the possible winning positions for the current player
   */
  position_t winning_position() const {
    return compute_winning_position(current_position, mask | disabled_cells);
  }

  /**
   * Return a bitmask of the possible winning positions for the opponent
   */
  position_t opponent_winning_position() const {
    return compute_winning_position(current_position ^ mask, mask | disabled_cells);
  }

  /**
   * Bitmap of the next possible valid moves for the current player
   * Including losing moves.
   */
  position_t possible() const {
    position_t filled = mask | disabled_cells;
    return ((filled + bottom_mask) & board_mask) & ~filled; // remove already filled & disabled cells
  }

  /**
   * counts number of bit set to one in a 64bits integer
   */
  static unsigned int popcount(position_t m) {
    unsigned int c = 0;
    for(c = 0; m; c++) m &= m - 1;
    return c;
  }

  /**
   * @parmam position, a bitmap of the player to evaluate the winning pos
   * @param mask, a mask of the already played spots
   *
   * @return a bitmap of all the winning free spots making an alignment
   */
  static position_t compute_winning_position(position_t position, position_t mask) {
    // vertical;
    position_t r = (position << 1) & (position << 2) & (position << 3);

    //horizontal
    position_t p = (position << (HEIGHT + 1)) & (position << 2 * (HEIGHT + 1));
    r |= p & (position << 3 * (HEIGHT + 1));
    r |= p & (position >> (HEIGHT + 1));
    p = (position >> (HEIGHT + 1)) & (position >> 2 * (HEIGHT + 1));
    r |= p & (position << (HEIGHT + 1));
    r |= p & (position >> 3 * (HEIGHT + 1));

    //diagonal 1
    p = (position << HEIGHT) & (position << 2 * HEIGHT);
    r |= p & (position << 3 * HEIGHT);
    r |= p & (position >> HEIGHT);
    p = (position >> HEIGHT) & (position >> 2 * HEIGHT);
    r |= p & (position << HEIGHT);
    r |= p & (position >> 3 * HEIGHT);

    //diagonal 2
    p = (position << (HEIGHT + 2)) & (position << 2 * (HEIGHT + 2));
    r |= p & (position << 3 * (HEIGHT + 2));
    r |= p & (position >> (HEIGHT + 2));
    p = (position >> (HEIGHT + 2)) & (position >> 2 * (HEIGHT + 2));
    r |= p & (position << (HEIGHT + 2));
    r |= p & (position >> 3 * (HEIGHT + 2));

    return r & (board_mask ^ mask);
  }

  // Static bitmaps
  template<int width, int height> struct bottom {static constexpr position_t mask = bottom<width-1, height>::mask | position_t(1) << (width - 1) * (height + 1);};
  template <int height> struct bottom<0, height> {static constexpr position_t mask = 0;};

  static constexpr position_t bottom_mask = bottom<WIDTH, HEIGHT>::mask;
  static constexpr position_t board_mask = bottom_mask * ((1LL << HEIGHT) - 1);

  // return a bitmask containg a single 1 corresponding to the top cel of a given column
  static constexpr position_t top_mask_col(int col) {
    return UINT64_C(1) << ((HEIGHT - 1) + col * (HEIGHT + 1));
  }

  // return a bitmask containg a single 1 corresponding to the bottom cell of a given column
  static constexpr position_t bottom_mask_col(int col) {
    return UINT64_C(1) << col * (HEIGHT + 1);
  }

 public:
  // return a bitmask 1 on all the cells of a given column
  static constexpr position_t column_mask(int col) {
    return ((UINT64_C(1) << HEIGHT) - 1) << col * (HEIGHT + 1);
  }

  // Bitboard of disabled (blocked) cells – these cells can never hold a piece. Exactly TWO bits are set per game but
  // we keep it general-purpose.
  position_t disabled_cells{0};
};

} // namespace Connect4
} // namespace GameSolver
#endif

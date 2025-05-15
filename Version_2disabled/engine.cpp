// engine.cpp
#include "Solver.hpp"        // định nghĩa Solver, Position, v.v. :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}
#include <string>
#include <vector>
// g++ -O3 -std=c++17 -shared -static -static-libgcc -static-libstdc++ -lwinpthread engine.cpp Solver.cpp -o connect.dll

#ifdef _WIN32
  #define EXPORT __declspec(dllexport)
#else
  #define EXPORT __attribute__((visibility("default")))
#endif

extern "C" {

// Trả về cột tốt nhất 0–6, seq là chuỗi "123…" (1‑indexed)
EXPORT int best_move(const char* seq_cstr, int row1, int col1, int row2, int col2) {
    using namespace GameSolver::Connect4;
    static Solver solver;
    static bool   book_loaded = false;
    
    if (seq_cstr == "") {
        // print flag
        std::cerr << "seq_cstr is NULL" << std::endl;
        return -1; // Trả về -1 nếu seq_cstr là NULL
    }
    // Nếu seq_cstr là NULL, trả về cột giữa
    // ALWAYS replay full sequence into a fresh Position
    std::string seq = seq_cstr ? seq_cstr : "";
    std::cerr << row1 << " " << col1 << " " << row2 << " " << col2 << std::endl;
    
    Position pos;
    if (row1 >= 0 && col1 >= 0 && row1 < Position::HEIGHT && col1 < Position::WIDTH) {
        pos.disableCell(row1, col1);
    }
    if (row2 >= 0 && col2 >= 0 && row2 < Position::HEIGHT && col2 < Position::WIDTH) {
        pos.disableCell(row2, col2);
    }
    
    for (char ch : seq) {
        int col = ch - '1';
        pos.playCol(col);
    }

    // Phân tích và chọn nước
    std::vector<int> scores = solver.analyze(pos);
    int best_col   = 0;
    int best_score = scores[0];
    for (int c = 1; c < Position::WIDTH; ++c) {
        if (scores[c] > best_score) {
            best_score = scores[c];
            best_col   = c;
        }
    }

    return best_col;
}

} // extern "C"

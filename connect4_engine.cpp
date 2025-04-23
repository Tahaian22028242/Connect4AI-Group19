// engine.cpp
#include "connect4_algorithm.hpp" // định nghĩa Solver, Position, v.v. :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}
#include <string>
#include <vector>
#include <random> // để dùng random_device, mt19937, uniform_int_distribution
// g++ -O3 -std=c++17 -shared -static -static-libgcc -static-libstdc++ -lwinpthread engine.cpp Solver.cpp -o connect.dll

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __attribute__((visibility("default")))
#endif

extern "C"
{

    // Trả về cột tốt nhất 0–6, seq là chuỗi “123…” (1‑indexed)
    EXPORT int best_move(const char *seq_cstr)
    {
        using namespace GameSolver::Connect4;
        static Solver solver;
        static bool book_loaded = false;
        if (!book_loaded)
        {
            solver.loadBook("7x6.book");
            book_loaded = true;
        }
        if (!seq_cstr || seq_cstr[0] == '\0')
        {
            {
                // print flag
                std::cerr << "seq_cstr is NULL or empty" << std::endl;
                return -1; // Trả về -1 nếu seq_cstr là NULL hoặc rỗng
            }
            // Nếu seq_cstr là NULL, trả về cột giữa
            // ALWAYS replay full sequence into a fresh Position
            std::string seq = seq_cstr ? seq_cstr : "";
            Position pos;
            for (char ch : seq)
            {
                if (ch < '1' || ch > '7')
                    continue; // hoặc return -1;
                int col = ch - '1';
                pos.playCol(col);
            }

            // Phân tích và chọn nước
            std::vector<int> scores = solver.analyze(pos);
            std::vector<int> best_cols;
            int best_score = scores[0];
            best_cols.push_back(0);
            for (int c = 1; c < Position::WIDTH; ++c)
            {
                if (scores[c] > best_score)
                {
                    best_score = scores[c];
                    best_cols.clear();
                    best_cols.push_back(c);
                }
                else if (scores[c] == best_score)
                {
                    best_cols.push_back(c);
                }
            }
            // Chọn ngẫu nhiên 1 cột trong best_cols
            int best_col = best_cols[0];
            if (best_cols.size() > 1)
            {
                static std::random_device rd;
                static std::mt19937 gen(rd());
                std::uniform_int_distribution<> dis(0, best_cols.size() - 1);
                best_col = best_cols[dis(gen)];
            }

            return best_col;
        }

    } // extern "C"
}
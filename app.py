import asyncio
import time
import ctypes
import os
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple

# ——————————————————————————————————————————————————————————————————
# Load engine & cache
# ——————————————————————————————————————————————————————————————————
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DLL_NAME = "connect.dll" if os.name == "nt" else "libconnect.so"
DLL_PATH = os.path.join(BASE_DIR, DLL_NAME)


# load or init cache


loader = ctypes.WinDLL if os.name == "nt" else ctypes.CDLL
_lib = loader(DLL_PATH)
_lib.best_move.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
_lib.best_move.restype  = ctypes.c_int

def call_engine(seq: str, disabled_cells: List[Tuple[int, int]]) -> int:
    # Mặc định nếu không có ô khóa
    row1, col1, row2, col2 = -1, -1, -1, -1
    
    # Lấy tọa độ 2 ô bị khóa
    if len(disabled_cells) >= 1:
        row1, col1 = disabled_cells[0]
    if len(disabled_cells) >= 2:
        row2, col2 = disabled_cells[1]
    
    print(f"seq: {seq}, row1: {row1}, col1: {col1}, row2: {row2}, col2: {col2}")
    # Gọi hàm best_move từ engine
    mv = _lib.best_move(seq.encode(), row1, col1, row2, col2)
    
    return mv

# ——————————————————————————————————————————————————————————————————
# FastAPI & Models
# ——————————————————————————————————————————————————————————————————
app = FastAPI()
state_lock = asyncio.Lock()

# initial state
app.state.board = [[0]*7 for _ in range(6)]
app.state.seq = ""
app.state.total_elapsed = 0.0   # tổng thời gian đã tốn (giây)
app.state.disabled_cells = []   # lưu tọa độ các ô bị khóa

class GameState(BaseModel):
    board: List[List[int]]
    current_player: int
    valid_moves: List[int]
    is_new_game: bool = False

class AIResponse(BaseModel):
    move: int
    total_elapsed: float  # trả về tổng thời gian đã tốn cho cả ván

def find_disabled_cells(board: List[List[int]]) -> List[Tuple[int, int]]:
    """Tìm các ô bị khóa (giá trị -1) trong bàn cờ"""
    disabled_cells = []
    for r in range(6):
        for c in range(7):
            if board[r][c] == -1:
                disabled_cells.append((5-r, c))
    return disabled_cells

@app.on_event("startup")
async def preload_book():
    # warm‑up và cache seq = ""
    empty_board = [[0]*7 for _ in range(6)]
    call_engine("", [])
    
    # Initialize previous disabled cells
    app.state.previous_disabled_cells = []

@app.get("/api/test")
async def health_check():
    return {"status": "ok", "message": "running"}

@app.post("/api/connect4-move", response_model=AIResponse)
async def make_move(gs: GameState):
    start = time.time()

    async with state_lock:
        # Tìm các ô bị khóa từ bàn cờ hiện tại
        current_disabled_cells = find_disabled_cells(gs.board)
        
        # Kiểm tra xem có phải game mới không bằng cách so sánh ô khóa
        is_different_game = (
            gs.is_new_game or 
            sorted(current_disabled_cells) != sorted(getattr(app.state, 'previous_disabled_cells', []))
        )
        
        if is_different_game:
            print("New game detected (different disabled cells or is_new_game flag)")
            app.state.board = [row[:] for row in gs.board]  # Sao chép board từ request
            app.state.seq = ""
            app.state.total_elapsed = 0.0
            app.state.disabled_cells = current_disabled_cells
            app.state.previous_disabled_cells = current_disabled_cells
            print(f"Disabled cells: {app.state.disabled_cells}")
        else:
            app.state.disabled_cells = current_disabled_cells
            app.state.previous_disabled_cells = current_disabled_cells
            print(f"Disabled cells: {app.state.disabled_cells}")
            prev_board = app.state.board
            seq = app.state.seq

            # tìm nước người chơi vừa đi
            last = -1
            for c in range(7):
                for r in range(5, -1, -1):
                    if prev_board[r][c] != gs.board[r][c] and gs.board[r][c] > 0:  # Chỉ tính nước đi thực sự, không phải ô khóa
                        last = c
                        break
                if last >= 0:
                    break
            if last >= 0:
                seq += str(last+1)
                app.state.seq = seq

            # Cập nhật board
            app.state.board = [row[:] for row in gs.board]

        # gọi engine với tọa độ các ô bị khóa đã được xác định trước
        try:
            ai_col = call_engine(app.state.seq, app.state.disabled_cells)
        except Exception as e:
            raise HTTPException(500, f"Engine error: {e}")

        # áp dụng nước AI lên board
        board = [row[:] for row in app.state.board]
        for r in range(5, -1, -1):
            if board[r][ai_col] == 0:
                board[r][ai_col] = gs.current_player
                break

        # cập nhật seq và board
        app.state.seq += str(ai_col+1)
        app.state.board = board

    # đo thời gian cho lần này, cộng dồn rồi trả về
    elapsed = time.time() - start
    app.state.total_elapsed += elapsed
    print(f"⏱ Move took {elapsed:.6f}s, total elapsed so far: {app.state.total_elapsed:.6f}s")

    return AIResponse(move=ai_col, total_elapsed=app.state.total_elapsed)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)

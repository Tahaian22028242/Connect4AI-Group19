import asyncio
import time
import ctypes
import os
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

import threading # để ghi cache không block request

import logging # để ghi log vào file thay cho print (stdout) 
logging.basicConfig(level=logging.INFO)

# ——————————————————————————————————————————————————————————————————
# Load engine & cache
# ——————————————————————————————————————————————————————————————————
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DLL_NAME = "connect.dll" if os.name == "nt" else "libconnect.so"
DLL_PATH = os.path.join(BASE_DIR, DLL_NAME)
CACHE_PATH = os.path.join(BASE_DIR, "connect4_cache.json")

# kiểm tra xem file DLL có tồn tại không
if not os.path.exists(DLL_PATH):
    raise RuntimeError(f"Engine library not found at {DLL_PATH}")

# load or init cache
try:
    with open(CACHE_PATH, "r") as f:
        ENGINE_CACHE = json.load(f)
except:
    ENGINE_CACHE = {}

loader = ctypes.WinDLL if os.name == "nt" else ctypes.CDLL
_lib = loader(DLL_PATH)
_lib.best_move.argtypes = [ctypes.c_char_p]
_lib.best_move.restype  = ctypes.c_int

# load engine
def call_engine(seq: str) -> int:
    if seq in ENGINE_CACHE:
        return ENGINE_CACHE[seq]
    mv = _lib.best_move(seq.encode())
    ENGINE_CACHE[seq] = mv
    # with open(CACHE_PATH, "w") as f:
    #     json.dump(ENGINE_CACHE, f)
    return mv

# Lưu cache định kỳ
# Ghi cache vào file không block request
def periodic_save_cache(interval=10):
    while True:
        time.sleep(interval)
        try:
            with open(CACHE_PATH, "w") as f:
                json.dump(ENGINE_CACHE, f)
        except Exception as e:
            print(f"Warning: Failed to save cache: {e}")

# Chạy thread ghi cache định kỳ khi khởi động
threading.Thread(target=periodic_save_cache, args=(10,), daemon=True).start()

# ——————————————————————————————————————————————————————————————————
# FastAPI & Models
# ——————————————————————————————————————————————————————————————————
app = FastAPI()
state_lock = asyncio.Lock()

# initial state
app.state.board         = [[0]*7 for _ in range(6)]
app.state.seq           = ""
app.state.total_elapsed = 0.0   # tổng thời gian đã tốn (giây)

class GameState(BaseModel):
    board: List[List[int]]
    current_player: int
    valid_moves: List[int]
    is_new_game: bool = False

class AIResponse(BaseModel):
    move: int
    total_elapsed: float  # trả về tổng thời gian đã tốn cho cả ván

@app.on_event("startup")
async def preload_book():
    # warm‑up và cache seq = ""
    call_engine("")

@app.get("/api/test")
async def health_check():
    return {"status": "ok", "message": "running"}

@app.post("/api/connect4-move", response_model=AIResponse)
async def make_move(gs: GameState):
    start = time.time()

    async with state_lock:
        # nếu ván mới thì reset cả state và bộ đếm
        if gs.is_new_game:
            app.state.board         = [[0]*7 for _ in range(6)]
            app.state.seq           = ""
            app.state.total_elapsed = 0.0

        prev_board = app.state.board
        seq        = app.state.seq

        # tìm nước người chơi vừa đi
        last = -1
        for c in range(7):
            for r in range(5, -1, -1):
                if prev_board[r][c] != gs.board[r][c]:
                    last = c
                    break
            if last >= 0:
                break
        if last >= 0:
            seq += str(last+1)

        # gọi engine (có cache)
        try:
            ai_col = call_engine(seq)
        except Exception as e:
            raise HTTPException(500, f"Engine error: {e}")

        # áp dụng nước AI lên board
        board = [row[:] for row in gs.board]
        for r in range(5, -1, -1):
            if board[r][ai_col] == 0:
                board[r][ai_col] = gs.current_player
                break

        # cập nhật seq và board
        seq += str(ai_col+1)
        app.state.board = board
        app.state.seq   = seq

    # đo thời gian cho lần này, cộng dồn rồi trả về
    elapsed = time.time() - start
    app.state.total_elapsed += elapsed
    # print(f"⏱ Move took {elapsed:.6f}s, total elapsed so far: {app.state.total_elapsed:.6f}s")

    # Thay print bằng logging.info
    logging.info(f"⏱ Move took {elapsed:.6f}s, total elapsed so far: {app.state.total_elapsed:.6f}s")

    return AIResponse(move=ai_col, total_elapsed=app.state.total_elapsed)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)

from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import List
import subprocess
from fastapi.middleware.cors import CORSMiddleware
import json
import os

# This is a FastAPI application for a Connect 4 game.
# It handles the game state, including moves made by players and the AI.
app = FastAPI()
STATE_FILE = "game_state.json" # File to save the game state

# Middleware to handle CORS (Cross-Origin Resource Sharing)
# This allows the API to be accessed from different origins, which is useful for frontend applications.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the data model for the game state and AI response using Pydantic
class Connect4State(BaseModel):
    board: List[List[int]]
    current_player: int
    valid_moves: List[int]

class AIMove(BaseModel):
    move: int

def save_state(board: List[List[int]], sequence: str):
    """Save current game state to file"""
    state = {
        "board": board,
        "move_sequence": sequence
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)
def check_endgame(board: List[List[int]]) -> bool:
    """Check if the game has ended"""
    for row in range(6):
        for col in range(7):
            if board[row][col] == 0:
                continue

            if col + 3 < 7 and all(board[row][col + i] == board[row][col] for i in range(4)):
                return True

            if row + 3 < 6 and all(board[row + i][col] == board[row][col] for i in range(4)):
                return True

            if row - 3 >= 0 and col + 3 < 7 and all(board[row - i][col + i] == board[row][col] for i in range(4)):
                return True

            if row + 3 < 6 and col + 3 < 7 and all(board[row + i][col + i] == board[row][col] for i in range(4)):
                return True
    return False
def load_state() -> tuple:

    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            return state["board"], state["move_sequence"]
    except:
        return [[0] * 7 for _ in range(6)], ""

def clear_state():

    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

def start_ai_process() -> subprocess.Popen:
    """Start the AI process"""
    return subprocess.Popen(
        ["./connect"],     # File thực thi được biên dịch từ connect4_solver.cpp
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

@app.post("/api/connect4-move")
async def make_move(game_state: Connect4State) -> AIMove:
    try:
        if not game_state.valid_moves:
            raise ValueError("No valid moves")

        # Load current state


        previous_board, move_sequence = load_state()
        print(f"Previous board: {previous_board}")
        print(f"Current board: {game_state.board}")
        print(f"Move sequence: {move_sequence}")
        # Start new AI process
        process = start_ai_process()
        if not process:
            raise ValueError("Failed to start AI process")

        try:
            # Find and record human's move
            last_move = -1
            for col in range(7):
                for row in range(5, -1, -1):
                    if previous_board[row][col] != game_state.board[row][col]:
                        last_move = col
                        break
                if last_move >= 0:
                    break

            if last_move >= 0:
                move_sequence += str(last_move + 1)

            print(f"Move sequence: {move_sequence}")
            
            # Gửi chuỗi nước đi đến AI
            process.stdin.write(f"{move_sequence}\n")
            process.stdin.flush()

            # Nhận nước đi từ AI
            selected_move = -1
            while True:
                line = process.stdout.readline().strip()
                print(line)
                if not line:
                    break
                try:
                    selected_move = int(line)
                    # Cập nhật bảng với nước đi của AI
                    game_state.board = [row[:] for row in game_state.board]
                    for row in range(5, -1, -1):
                        if game_state.board[row][selected_move] == 0:
                            game_state.board[row][selected_move] = game_state.current_player
                            break
                    break
                except ValueError:
                    continue

            if selected_move == -1 or selected_move not in game_state.valid_moves:
                selected_move = game_state.valid_moves[0]
                clear_state()

            # Update state
            move_sequence += str(selected_move + 1)
            print("saved here")
            
            save_state(game_state.board, move_sequence)

            with open(STATE_FILE, 'r') as f:
                saved_state = json.load(f)
                if saved_state["move_sequence"] != move_sequence:
                    raise ValueError("Failed to save state correctly")

            if len(game_state.valid_moves) <= 1:
                clear_state()
            if(check_endgame(game_state.board)):
                clear_state()
                print("Game Over")
                return AIMove(move=selected_move)
            return AIMove(move=selected_move)

        finally:
            if process:
                process.terminate()

    except Exception as e:
        print(f"Error: {str(e)}")
        if game_state.valid_moves:
            return AIMove(move=game_state.valid_moves[0])
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
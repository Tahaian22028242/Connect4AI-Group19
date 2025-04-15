@REM This script builds the Connect4 AI project using g++ compiler.
@REM It compiles the source files connect4_solver.cpp and connect4_algorithm.cpp

@echo off
echo Building Connect4 AI...
g++ -std=c++17 -O2 -o connect.exe connect4_solver.cpp connect4_algorithm.cpp
if %ERRORLEVEL% == 0 (
    echo Build successful!
) else (
    echo Build failed!
)
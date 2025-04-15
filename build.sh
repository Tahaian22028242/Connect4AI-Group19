#!/bin/bash
# This script builds the Connect4 AI project on Linux/macOS

echo "Building Connect4 AI..."
g++ -std=c++17 -O2 -o connect connect4_solver.cpp connect4_algorithm.cpp

if [ $? -eq 0 ]; then
    echo "Build successful!"
else
    echo "Build failed!"
fi
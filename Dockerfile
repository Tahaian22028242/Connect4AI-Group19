# Stage 1: build C++ engine as Linux shared object
FROM python:3.12-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# Copy engine sources, headers and opening book
COPY engine.cpp connect4_algorithm.cpp connect4_algorithm.hpp OpeningBook.hpp TranspositionTable.hpp MoveSorter.hpp Position.hpp 7x6.book ./

# Compile into .so for Linux
RUN g++ -O3 -std=c++17 -shared -fPIC \
       connect4_algorithm.cpp engine.cpp \
       -o libconnect.so

# Stage 2: application image
FROM python:3.12-slim
WORKDIR /app

# Copy shared library and application code
COPY --from=builder /app/libconnect.so ./libconnect.so
COPY app.py 7x6.book ./

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydantic typing

EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
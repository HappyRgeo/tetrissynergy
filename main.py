import os
import random
import time
import sys
import msvcrt
import threading
from typing import List, Tuple

# Game constants
WIDTH = 10
HEIGHT = 20
EMPTY = ' '
BLOCK = '█'
BORDER = '│'

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

class Tetris:
    def __init__(self):
        self.board = [[EMPTY for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.score = 0
        self.game_over = False
        self.lock = threading.Lock()
        self.last_key = None
        self.key_pressed = False
        
    def new_piece(self):
        shape = random.choice(SHAPES)
        self.current_piece = shape
        self.current_x = WIDTH // 2 - len(shape[0]) // 2
        self.current_y = 0
        
        if not self.is_valid_move(self.current_x, self.current_y):
            self.game_over = True
    
    def rotate_piece(self):
        if not self.current_piece:
            return
            
        rows = len(self.current_piece)
        cols = len(self.current_piece[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows-1-r] = self.current_piece[r][c]
                
        old_piece = self.current_piece
        self.current_piece = rotated
        
        if not self.is_valid_move(self.current_x, self.current_y):
            self.current_piece = old_piece
    
    def is_valid_move(self, x: int, y: int) -> bool:
        if not self.current_piece:
            return False
            
        for i in range(len(self.current_piece)):
            for j in range(len(self.current_piece[0])):
                if self.current_piece[i][j]:
                    new_x = x + j
                    new_y = y + i
                    
                    if (new_x < 0 or new_x >= WIDTH or 
                        new_y >= HEIGHT or 
                        (new_y >= 0 and self.board[new_y][new_x] != EMPTY)):
                        return False
        return True
    
    def merge_piece(self):
        if not self.current_piece:
            return
            
        for i in range(len(self.current_piece)):
            for j in range(len(self.current_piece[0])):
                if self.current_piece[i][j]:
                    self.board[self.current_y + i][self.current_x + j] = BLOCK
        
        self.clear_lines()
        self.new_piece()
    
    def clear_lines(self):
        lines_cleared = 0
        y = HEIGHT - 1
        while y >= 0:
            if all(cell != EMPTY for cell in self.board[y]):
                del self.board[y]
                self.board.insert(0, [EMPTY for _ in range(WIDTH)])
                lines_cleared += 1
            else:
                y -= 1
        
        if lines_cleared > 0:
            self.score += (100 * lines_cleared * lines_cleared)
    
    def move(self, dx: int, dy: int):
        if not self.current_piece:
            return
            
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        
        if self.is_valid_move(new_x, new_y):
            self.current_x = new_x
            self.current_y = new_y
            return True
        return False
    
    def handle_input(self):
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\xe0':  # Arrow key
                key = msvcrt.getch()
                if key == b'K':  # Left
                    self.move(-1, 0)
                elif key == b'M':  # Right
                    self.move(1, 0)
                elif key == b'P':  # Down
                    self.move(0, 1)
                elif key == b'H':  # Up
                    self.rotate_piece()
            elif key == b'q':  # Quit
                self.game_over = True
    
    def draw(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print('┌' + '─' * (WIDTH * 2) + '┐')
        
        for y in range(HEIGHT):
            print(BORDER, end='')
            for x in range(WIDTH):
                if (self.current_piece and 
                    0 <= y - self.current_y < len(self.current_piece) and 
                    0 <= x - self.current_x < len(self.current_piece[0]) and 
                    self.current_piece[y - self.current_y][x - self.current_x]):
                    print(BLOCK * 2, end='')
                else:
                    print(self.board[y][x] * 2, end='')
            print(BORDER)
        
        print('└' + '─' * (WIDTH * 2) + '┘')
        
        # Draw score and debug info
        print(f'Score: {self.score}')
        print(f'Current Position: ({self.current_x}, {self.current_y})')
        print('\nControls:')
        print('← → : Move left/right')
        print('↑ : Rotate')
        print('↓ : Move down faster')
        print('q : Quit')

def main():
    game = Tetris()
    game.new_piece()
    
    last_drop = time.time()
    while not game.game_over:
        with game.lock:
            game.handle_input()
            
            current_time = time.time()
            if current_time - last_drop > 0.5: 
                if not game.move(0, 1):
                    game.merge_piece()
                last_drop = current_time
            
            game.draw()
            time.sleep(0.1)
    
    print("\nGame Over!")
    print(f"Final Score: {game.score}")

if __name__ == "__main__":
    main()

import pygame
import random

# initialise the window for the game
pygame.init()
WIDTH, HEIGHT = 400, 60
WIN = pygame.display.set_mode(WIDTH,HEIGHT)
pygame.display.set_caption("Crazy Tetris")
clock = pygame.time.clock()

#Grid setup
ROWS = 20
COLS = 10
BLOCK_SIZE = WIDTH // COLS
grid = [[(0,0,0) for _ in range(COLS)] for _ in range(ROWS)]

# Shapes for the tetris game

SHAPES = [
  [[1,1,1,1]],
  [[1,1], [1,1]],
  [[0, 1, 0], [1, 1, 1]],             
  [[1, 0, 0], [1, 1, 1]],             
  [[0, 0, 1], [1, 1, 1]],             
  [[0, 1, 1], [1, 1, 0]],            
  [[1, 1, 0], [0, 1, 1]],  

]

# Colors
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
          (255, 255, 0), (0, 255, 255), (255, 0, 255), (128, 128, 128)]
# Tetromino class
class Tetromino:
    def _init_(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = COLS // 2 - len(self.shape[0])  // 2
        self.y = 0





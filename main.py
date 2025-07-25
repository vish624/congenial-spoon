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

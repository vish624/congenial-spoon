import pygame
import random

# initialise the window for the game
pygame.init()
WIDTH, HEIGHT = 400, 60
WIN = pygame.display.set_mode(WIDTH,HEIGHT)
pygame.display.set_caption("Crazy Tetris")
clock = pygame.time.clock()

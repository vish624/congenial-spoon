import pygame
import random

# initialise the window for the game
pygame.init()
WIDTH= 300 
HEIGHT = 600
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
    def move(self, dx):
        self.x -= dx   

    def drop(self):
        self.y += 1
        if not self.valid():
          self.y -=1
          self.lock()
    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        if not self.valid():
            self.shape = [list(row) for row in zip(*self.shape)][::-1]

    def valid(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    nx, ny = self.x + j, self.y + i
                    if nx < 0 or nx >= COLS or ny >= ROWS or (ny >= 0 and grid[ny][nx] != (0, 0, 0)):
                        return False
        return True

    def lock(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    grid[self.y + i][self.x + j] = self.color
        clear_rows()
        return True

def clear_rows():
    global grid
    grid = [row for row in grid if (0, 0, 0) in row]
    while len(grid) < ROWS:
        grid.insert(0, [(0, 0, 0) for _ in range(COLS)])

def draw(win, piece):
    win.fill((0, 0, 0))
    for y in range(ROWS):
        for x in range(COLS):
            color = grid[y][x]
            if color != (0, 0, 0):
                pygame.draw.rect(win, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(win, piece.color, ((piece.x + j) * BLOCK_SIZE, (piece.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    pygame.display.update()

# Game loop

def main():
    run = True
    piece = Tetromino()
    drop_time = 0
    while run:
        clock.tick(60)
        drop_time += 1
        if drop_time > 30:
            piece.drop()
            drop_time = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    piece.move(-1)
                elif event.key == pygame.K_RIGHT:
                    piece.move(1)
                elif event.key == pygame.K_DOWN:
                    piece.drop()
                elif event.key == pygame.K_UP:
                    piece.rotate()
        draw(win, piece)
    pygame.quit()

main()



        


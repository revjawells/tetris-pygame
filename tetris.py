import pygame
import random

pygame.font.init()

SCREENWIDTH = 800
SCREENHEIGHT = 700
BLOCKSIZE = 30

WIDTH = 10
HEIGHT = 20

TOPLEFTX = (SCREENWIDTH - WIDTH * BLOCKSIZE) // 2
TOPLEFTY = (SCREENHEIGHT - HEIGHT * BLOCKSIZE) - BLOCKSIZE

FONT = pygame.font.Font("PressStart2P.ttf", 18)

PIECES = [
    # I piece
    [[0, 0, 0, 0],
     [1, 1, 1, 1],
     [0, 0, 0, 0],
     [0, 0, 0, 0]],

    # J piece
    [[0, 0, 1],
     [1, 1, 1],
     [0, 0, 0]],

    # L piece
    [[1, 0, 0],
     [1, 1, 1],
     [0, 0, 0]],

    # O piece
    [[1, 1],
     [1, 1]],

    # S piece
    [[0, 1, 1],
     [1, 1, 0],
     [0, 0, 0]],

    # T piece
    [[0, 1, 0],
     [1, 1, 1],
     [0, 0, 0]],

    # Z piece
    [[1, 1, 0],
     [0, 1, 1],
     [0, 0, 0]]]

PIECE_COLORS = [pygame.Color("Cyan"),   # I piece
        pygame.Color("Blue"),   # J piece
        pygame.Color("Orange"), # L piece
        pygame.Color("Yellow"), # O piece
        pygame.Color("Green"),  # S piece
        pygame.Color("Purple"), # T piece
        pygame.Color("Red")]    # Z piece

class Piece:
    def __init__(self, x = WIDTH // 2, y = 0):
        self.x = x
        self.y = y
        self.shape = random.choice(PIECES)
        self.color = PIECE_COLORS[PIECES.index(self.shape)]

    def handle(self, key, grid):
        if key == pygame.K_LEFT:
            self.move(-1, 0)
            if not grid.isvalid(self):
                self.move(+1, 0)

        if key == pygame.K_RIGHT:
            self.move(+1, 0)
            if not grid.isvalid(self):
                self.move(-1, 0)
                    
        if key == pygame.K_DOWN:
            self.move(0, +1)
            if not grid.isvalid(self):
                self.move(0, -1)

        if key == pygame.K_UP:
            self.rotate()

    def rotate(self):
        N = len(self.shape)
        newshape = []

        # Transpose
        for i in range(N):
            row = []
            for j in range(N):
                row.append(self.shape[j][i])
            newshape.append(row)

        for i in range(N):
            newshape[i].reverse()

        self.shape = newshape

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        
    def draw(self, surface, next=False):
        if next:
            # Set sx, sy for outside the grid
            sx = SCREENWIDTH - 200
            sy = 250    
            pass
        else:
            # Set sx, sy for inside the grid
            sx = TOPLEFTX + self.x * BLOCKSIZE
            sy = TOPLEFTY + self.y * BLOCKSIZE
            pass
               
        # Draw the piece
        for i, row in enumerate(self.shape):
            for j, column in enumerate(row):
                if column == 1:
                    pygame.draw.rect(surface, self.color,
                             (sx + j * BLOCKSIZE, sy + i * BLOCKSIZE,
                              BLOCKSIZE, BLOCKSIZE), 0)

class Grid:
    def __init__(self, width = WIDTH, height = HEIGHT):
        self.grid = [[pygame.Color("Black") for x in range(width)] for x in range(height)]

    def isvalid(self, piece):
        dim = len(piece.shape)

        # Starting at p.x and p.y, compare against self.grid and check for non BLACK
        for i in range(dim):
            for j in range(dim):    # Could be len(piece.shape[i]) but these pieces are all square
                if piece.shape[i][j] == 1:
                    # Check to make sure all 1's are in the grid bounds
                    margin = 0
                    if piece.shape[i][0] == 0:
                        margin += 1
                        if piece.shape[i][1] == 0:
                            margin += 1

                    if (piece.y < 0) or (piece.y + i >= HEIGHT) or (piece.x + margin < 0) or (piece.x + j >= WIDTH):
                        return False

                    # Check to make sure we aren't hitting a (non-black) piece
                    if self.grid[piece.y + i][piece.x + j] != pygame.Color("Black"):
                        return False 
            
        return True

    def isfull(self):
        # Game is lost if the grid is full
        return (self.grid[0][5] != pygame.Color("Black"))
    
    def lock(self, piece):
        for i in range(len(piece.shape)):
            for j in range(len(piece.shape[i])):
                if piece.shape[i][j] == 1:
                    self.grid[piece.y + i][piece.x + j] = piece.color
                    
    def draw(self, surface):    
        # Color in the grid squares
        for i in range(HEIGHT):
            for j in range(WIDTH):
                pygame.draw.rect(surface, self.grid[i][j],
                                 (TOPLEFTX + j * BLOCKSIZE, TOPLEFTY + i * BLOCKSIZE,
                                 BLOCKSIZE, BLOCKSIZE), 0)

    def clear(self):
        nlines = 0

        # Count through all rows, bottow to top
        for i in range(len(self.grid) - 1, -1, -1):
            if not pygame.Color("Black") in self.grid[i]:
                del self.grid[i]
                self.grid.insert(0, [pygame.Color("Black")] * WIDTH)
                nlines += 1

        # Return number of rows cleared
        return nlines
    
# Set up a background surface
def setup_background(bg):
    bg.fill(pygame.Color("Black"))

    # Draw game title
    label = FONT.render("Tetris", 1, pygame.Color("White"))
    bg.blit(label, (SCREENWIDTH / 2 - (label.get_width() / 2), 20))

    # Draw Next label
    label = FONT.render("Next", 1, pygame.Color("White"))
    bg.blit(label, (610, 200))
    
    # Draw red border
    pygame.draw.rect(bg, pygame.Color("Red"), (TOPLEFTX, TOPLEFTY, WIDTH * BLOCKSIZE, HEIGHT * BLOCKSIZE), 6)

def draw_text(surface, text, size, x, y, centered=False):
    label = FONT.render(text, 1, pygame.Color("White"))

    if centered:
        surface.blit(label, ((SCREENWIDTH / 2) - (label.get_width() / 2),
                             (SCREENHEIGHT / 2) - (label.get_height() / 2)))
    else:
        surface.blit(label, (x, y))

def main(win):   
    change_piece = False
    over = False 
    fall_time = 0
    fall_speed = 0.25
    level_time = 0
    frames = 0

    level = 0
    score = 0
    lines = 0

    clock = pygame.time.Clock()
    
    current = Piece()
    next = Piece()
    grid = Grid()

    bg = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))
    setup_background(bg)
    
    while not over:
        # READ
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                over = True

            if event.type == pygame.KEYDOWN:
                current.handle(event.key, grid)

        # EVALUATE
        level_time += clock.get_rawtime()

        if level_time / 1000 > 5:
            level_time = 0
            if level_time > 0.12:
                    level_time -= 0.005
                    
        fall_time += clock.get_rawtime()
        clock.tick()

        # The current piece drops according to fall_speed.
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current.move(0, +1)
            if not grid.isvalid(current):       # We hit another piece
                current.move(0, -1)
                change_piece = True

        if change_piece:
            grid.lock(current)
            nlines = grid.clear()
            lines += nlines
            score += 10 * nlines

            current = next
            next = Piece()
            change_piece = False

            if lines > 0 and lines % 10 == 0:
                # Advance to next level
                level += 1
                fall_speed /= 100
                pass

        if grid.isfull():
            over = True
            draw_text(win, "YOU LOST!", 80, 0, 0, centered=True)

        # PRINT    
        win.fill((0, 0, 0))     # Fill with black
        win.blit(bg, (0, 0))    # Blit the background

        draw_text(win, "Level: {:0>4d}".format(level), 24, 575, 400)
        draw_text(win, "Score: {:0>4d}".format(score), 24, 575, 450)
        draw_text(win, "Lines: {:0>4d}".format(lines), 24, 575, 500)

        grid.draw(win)
        current.draw(win)
        next.draw(win, next=True)

        # Draw grid lines
        for i in range(WIDTH - 1):
            sx = TOPLEFTX + (i + 1) * BLOCKSIZE
            pygame.draw.line(win, pygame.Color("Grey"), (sx, TOPLEFTY),  (sx, TOPLEFTY + HEIGHT * BLOCKSIZE))

        for i in range(HEIGHT - 1):
            sy = TOPLEFTY + (i + 1) * BLOCKSIZE
            pygame.draw.line(win, pygame.Color("Grey"), (TOPLEFTX, sy),  (TOPLEFTX + WIDTH * BLOCKSIZE, sy))

        pygame.display.update()
        frames += 1

    pygame.display.quit()

def main_menu(win):
    run = True
    while run:
        win.fill(pygame.Color("Black"))
        draw_text(win, "Press any key to play", 60, 0, 0, centered=True)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)

    pygame.display.quit()
    
win = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
bg = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption("Tetris")
main_menu(win)

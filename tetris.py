import pygame
import random
import os

pygame.init()

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
GRID_SIZE = 30

# Colors
BLACK = (0, 0, 0)
grey = (105, 105, 105)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Shapes and their colors
SHAPES = [
    ([[1, 1, 1], [0, 1, 0]], (255, 0, 0)),  # T-shape, Red
    ([[1, 1, 1, 1]], (0, 255, 0)),  # I-shape, Green
    ([[1, 1], [1, 1]], (0, 0, 255)),  # O-shape, Blue
    ([[1, 1, 0], [0, 1, 1]], (255, 255, 0)),  # S-shape, Yellow
    ([[0, 1, 1], [1, 1, 0]], (255, 165, 0)),  # Z-shape, Orange
    ([[1, 1, 1], [1, 0, 0]], (128, 0, 128)),  # L-shape, Purple
    ([[1, 1, 1], [0, 0, 1]], (0, 255, 255))   # J-shape, Cyan
]

HIGHSCORE_FILE = 'highscore.txt'

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(SCREEN_WIDTH // GRID_SIZE)] for _ in range(SCREEN_HEIGHT // GRID_SIZE)]
        self.current_shape, self.current_color = self.new_shape()
        self.shape_pos = [0, SCREEN_WIDTH // GRID_SIZE // 2]
        self.score = 1  # Start with a score of 1 to allow multiplication
        self.highscore = self.load_highscore()
        self.game_over = False
        self.font = pygame.font.SysFont('Arial', 24)  # Initialize font
        self.fall_delay = 30  # Adjust this value to control the speed of the shapes
        self.fall_counter = 0

    def load_highscore(self):
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, 'r') as file:
                return int(file.read().strip())
        return 1  # Return 1 if no highscore file exists

    def save_highscore(self):
        with open(HIGHSCORE_FILE, 'w') as file:
            file.write(str(self.highscore))

    def new_shape(self):
        shape, color = random.choice(SHAPES)
        if self.collides([0, SCREEN_WIDTH // GRID_SIZE // 2], shape):
            self.game_over = True
        return shape, color

    def draw_grid(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, grey if self.grid[y][x] else BLACK, rect)
                pygame.draw.rect(self.screen, grey, rect, 1)

    def draw_shape(self):
        shape = self.current_shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect((self.shape_pos[1] + x) * GRID_SIZE, (self.shape_pos[0] + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                    pygame.draw.rect(self.screen, self.current_color, rect)

    def move_shape(self, dx, dy):
        new_pos = [self.shape_pos[0] + dy, self.shape_pos[1] + dx]
        if not self.collides(new_pos, self.current_shape):
            self.shape_pos = new_pos

    def rotate_shape(self):
        rotated_shape = list(zip(*self.current_shape[::-1]))
        if not self.collides(self.shape_pos, rotated_shape):
            self.current_shape = rotated_shape

    def collides(self, pos, shape):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = pos[1] + x
                    new_y = pos[0] + y
                    if new_x < 0 or new_x >= SCREEN_WIDTH // GRID_SIZE or new_y >= SCREEN_HEIGHT // GRID_SIZE or self.grid[new_y][new_x]:
                        return True
        return False

    def freeze_shape(self):
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.shape_pos[0] + y][self.shape_pos[1] + x] = cell
        self.clear_lines()
        self.current_shape, self.current_color = self.new_shape()
        self.shape_pos = [0, SCREEN_WIDTH // GRID_SIZE // 2]

    def clear_lines(self):
        lines_to_clear = [y for y, row in enumerate(self.grid) if all(row)]
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [0 for _ in range(SCREEN_WIDTH // GRID_SIZE)])
        self.score *= 2 ** len(lines_to_clear)  # Multiply score by 2 for each line cleared

    def drop_shape(self):
        while not self.collides([self.shape_pos[0] + 1, self.shape_pos[1]], self.current_shape):
            self.shape_pos[0] += 1
        self.freeze_shape()

    def draw_score(self):
        # Draw score box
        pygame.draw.rect(self.screen, grey, pygame.Rect(10, 10, 150, 40)) 
        pygame.draw.rect(self.screen, GREEN, pygame.Rect(10, 10, 150, 40), 2)
        # Draw score text
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (20, 20))

    def draw_highscore(self):
        # Draw highscore box
        pygame.draw.rect(self.screen, grey, pygame.Rect(10, 60, 150, 40))
        pygame.draw.rect(self.screen, GREEN, pygame.Rect(10, 60, 150, 40), 2)
        # Draw highscore text
        highscore_text = self.font.render(f"Highscore: {self.highscore}", True, BLACK)
        self.screen.blit(highscore_text, (20, 70))

    def run(self):
        running = True
        while running:
            self.screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move_shape(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_shape(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move_shape(0, 1)
                    elif event.key == pygame.K_UP:
                        self.rotate_shape()
                    elif event.key == pygame.K_SPACE:
                        self.drop_shape()

            self.fall_counter += 1
            if self.fall_counter >= self.fall_delay:
                self.fall_counter = 0
                if not self.collides([self.shape_pos[0] + 1, self.shape_pos[1]], self.current_shape):
                    self.shape_pos[0] += 1
                else:
                    self.freeze_shape()

            self.draw_grid()
            self.draw_shape()
            self.draw_score()
            self.draw_highscore()
            pygame.display.flip()
            self.clock.tick(60)  # Increase the tick rate for smoother rendering

            if self.game_over:
                if self.score > self.highscore:
                    self.highscore = self.score
                    self.save_highscore()
                running = False
                print("Game Over! Your score: ", self.score)

if __name__ == "__main__":
    game = Tetris()
    game.run()
    pygame.quit()

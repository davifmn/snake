import pygame

class mapa:
    BLACK = (0, 0, 0)

    def __init__(self, rows, cols, cell_size):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

        # todas as células começam pretas
        self.grid = [
            [self.BLACK for _ in range(cols)]
            for _ in range(rows)
        ]

    def draw_grid(self, surface):
        """Desenha apenas as células, sem linhas de grade."""
        for row in range(self.rows):
            for col in range(self.cols):
                color = self.grid[row][col]
                self.draw_cell(surface, row, col, color)

    def draw_cell(self, surface, row, col, color):
        rect = pygame.Rect(
            col * self.cell_size,
            row * self.cell_size,
            self.cell_size,
            self.cell_size,
        )
        pygame.draw.rect(surface, color, rect)



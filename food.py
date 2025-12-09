import pygame
import random

class food:
    YELLOW = (255, 255, 0)

    def __init__(self, rows, cols, cell_size):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.POS = None  # (row, col)

    def draw_food(self, surface):
        if self.POS is None:
            return
        row, col = self.POS
        rect = pygame.Rect(
            col * self.cell_size,
            row * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        pygame.draw.rect(surface, self.YELLOW, rect)

    def relocate_food(self, occupied_cells):
        """
        Escolhe uma nova posição para a comida que não esteja em 'occupied_cells'.
        occupied_cells: conjunto de tuplas (row, col) ocupadas pela snake ou outras foods.
        """
        free_cells = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in occupied_cells
        ]

        if not free_cells:
            # sem espaço livre
            self.POS = None
            return

        self.POS = random.choice(free_cells)
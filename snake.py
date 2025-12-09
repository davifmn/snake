import pygame

class snake:
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)

    def __init__(self, rows, cols, cell_size):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

        # posição lógica em termos de célula (row, col)
        center_row = rows // 2
        center_col = cols // 2

        # POS: posição da cabeça (row, col)
        self.POS = (center_row, center_col)

        # orientação inicial
        self.orientation = "right"  # up, down, left, right

        # corpo = lista de (row, col) da cabeça até a cauda
        self.body = [
            (center_row, center_col),         # cabeça (azul)
            (center_row, center_col - 1),     # corpo
            (center_row, center_col - 2),     # corpo
        ]

    def draw_snake(self, surface):
        # desenha corpo (branco) e por último a cabeça (azul)
        for index, (row, col) in enumerate(self.body):
            x = col * self.cell_size
            y = row * self.cell_size
            rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

            if index == 0:
                color = self.BLUE   # cabeça
            else:
                color = self.WHITE  # corpo

            pygame.draw.rect(surface, color, rect)

    def grow_snake(self):
        """Adiciona uma nova célula ao final do corpo da snake."""
        tail = self.body[-1]
        # adiciona mais uma célula na mesma posição da cauda;
        # na próxima movimentação, ela "cresce" para trás
        self.body.append(tail)

    def move_snake(self):
        """Move a snake 1 célula na direção atual com wrap nas bordas."""
        head_row, head_col = self.POS

        if self.orientation == "right":
            new_head = (head_row, head_col + 1)
        elif self.orientation == "left":
            new_head = (head_row, head_col - 1)
        elif self.orientation == "up":
            new_head = (head_row - 1, head_col)
        elif self.orientation == "down":
            new_head = (head_row + 1, head_col)
        else:
            new_head = self.POS

        # aplica wrap nas bordas do grid
        new_row = new_head[0] % self.rows
        new_col = new_head[1] % self.cols
        new_head = (new_row, new_col)

        # novo POS da cabeça
        self.POS = new_head

        # mover corpo
        new_body = [new_head]
        for i in range(1, len(self.body)):
            new_body.append(self.body[i - 1])

        self.body = new_body

    # def user_move(self):
    #     """Lê as teclas e ajusta a orientação da snake."""
    #     keys = pygame.key.get_pressed()

    #     # evita virar diretamente para o lado oposto
    #     if keys[pygame.K_RIGHT] and self.orientation != "left":
    #         self.orientation = "right"
    #     elif keys[pygame.K_LEFT] and self.orientation != "right":
    #         self.orientation = "left"
    #     elif keys[pygame.K_UP] and self.orientation != "down":
    #         self.orientation = "up"
    #     elif keys[pygame.K_DOWN] and self.orientation != "up":
    #         self.orientation = "down"

import pygame

class UserController:
    """Responsável por ler o input do usuário e mudar a orientação da snake."""
    def __init__(self, snake_ref):
        self.snake = snake_ref

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] and self.snake.orientation != "left":
            self.snake.orientation = "right"
        elif keys[pygame.K_LEFT] and self.snake.orientation != "right":
            self.snake.orientation = "left"
        elif keys[pygame.K_UP] and self.snake.orientation != "down":
            self.snake.orientation = "up"
        elif keys[pygame.K_DOWN] and self.snake.orientation != "up":
            self.snake.orientation = "down"
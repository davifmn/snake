import pygame
import grid
from snake import snake
from food import food
from menu import Menu
from ALGO_PLAYS.game_info import game_info
from ALGO_PLAYS.A_STAR import A_Star
from ALGO_PLAYS.A_NEW_STAR import A_NEW_Star 
from user import UserController

# --------------------------- FUNÇÕES AUXILIARES ---------------------------

def check_colision(player_snake, foods, info=None):
    head = player_snake.POS

    if head in player_snake.body[2:]:
        if info is not None:
            info.game_condition = "loss"
        return "self", None

    for f in foods:
        if f.POS == head:
            return True, f

    return False, None


def check_win(player_snake, rows, cols, info=None):
    if len(player_snake.body) == rows * cols:
        if info is not None:
            info.game_condition = "win"
        return True
    return False


# --------------------------- CLASSE GAME ---------------------------

class Game:
    def __init__(self, screen, rows, cols, cell_size, mode):
        self.screen = screen
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.mode = mode

        self.game_map = grid.mapa(rows, cols, cell_size)
        self.player_snake = snake(rows, cols, cell_size)
        self.foods = [food(rows, cols, cell_size) for _ in range(3)]
        
        occupied = set(self.player_snake.body)
        for f in self.foods:
            f.relocate_food(occupied)
            if f.POS is not None:
                occupied.add(f.POS)

        if self.mode == "A_STAR":
            self.ai = A_Star(rows, cols)
            self.info = game_info(rows, cols)
        elif self.mode == "A_NEW_STAR":
            self.ai = A_NEW_Star(rows, cols) 
            self.info = game_info(rows, cols)  
        else:
            self.user_controller = UserController(self.player_snake)
            self.ai = None
            self.info = None

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # controle de movimento
            if self.mode == "JOGAR":
                self.user_controller.handle_input()
                fps = 10
            elif self.mode in ("A_STAR", "A_NEW_STAR"):
                self._handle_ai()
                fps = 15  

            self.player_snake.move_snake()

            if self.info is not None:
                self.info.update(self.player_snake, self.foods)

            colision_result, eaten_food = check_colision(
                self.player_snake,
                self.foods,
                self.info
            )

            if colision_result == "self":
                running = False
            elif colision_result is True and eaten_food is not None:
                self.player_snake.grow_snake()
                occupied = set(self.player_snake.body)
                for f in self.foods:
                    if f is not eaten_food and f.POS is not None:
                        occupied.add(f.POS)
                eaten_food.relocate_food(occupied)

            if check_win(self.player_snake, self.rows, self.cols, self.info):
                running = False

            if self.info is not None and self.info.game_condition in ("win", "loss"):
                running = False

            self.draw()
            clock.tick(fps)

    # ---------------------- modos de controle ----------------------

    def _apply_direction(self, direction: str):
        """Aplica a direção à snake evitando virar 180°."""
        if direction == "up" and self.player_snake.orientation != "down":
            self.player_snake.orientation = "up"
        elif direction == "down" and self.player_snake.orientation != "up":
            self.player_snake.orientation = "down"
        elif direction == "left" and self.player_snake.orientation != "right":
            self.player_snake.orientation = "left"
        elif direction == "right" and self.player_snake.orientation != "left":
            self.player_snake.orientation = "right"

    def _handle_ai(self):
        if self.ai is None:
            return

        start = self.player_snake.POS
        food_positions = [f.POS for f in self.foods if f.POS is not None]
        snake_body = self.player_snake.body

        direction = self.ai.next_direction(start, food_positions, snake_body)
        if direction is None:
            return

        self._apply_direction(direction)

    # ---------------------- desenho ----------------------

    def draw(self):
        self.screen.fill(grid.mapa.BLACK)
        self.game_map.draw_grid(self.screen)
        self.player_snake.draw_snake(self.screen)
        for f in self.foods:
            f.draw_food(self.screen)
        pygame.display.flip()

# ---------------------------  main ---------------------------

def main():
    pygame.init()

    CELL_SIZE = 20
    ROWS, COLS = 30, 40 
    WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake AI Optimized")

    font = pygame.font.SysFont(None, 48)

    menu = Menu(screen, font)
    mode = menu.run()
    if mode is None:
        pygame.quit()
        return

    game = Game(screen, ROWS, COLS, CELL_SIZE, mode)
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()
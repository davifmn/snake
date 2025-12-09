import pygame
import grid
from snake import snake
from food import food
from menu import Menu
from ALGO_PLAYS.game_info import game_info
from ALGO_PLAYS.A_STAR import A_Star
from ALGO_PLAYS.A_NEW_STAR import A_Star as A_NewStar  # usa o A_Star novo com outro nome
from user import UserController

# --------------------------- FUNÇÕES AUXILIARES ---------------------------

def check_colision(player_snake, foods, info=None):
    """
    Verifica:
      - se a head da snake colidiu com alguma food
      - se a head colidiu com o próprio corpo
    Retorna:
      - (True, food_obj) se comeu alguma food
      - ("self", None)  se colidiu com o próprio corpo
      - (False, None)   caso contrário
    Se info for passado, atualiza info.game_condition para "loss" se bater no corpo.
    """
    head = player_snake.POS

    # colisão com o próprio corpo (ignorando a cabeça e o próximo segmento)
    if head in player_snake.body[2:]:
        if info is not None:
            info.game_condition = "loss"
        return "self", None

    # colisão com alguma food
    for f in foods:
        if f.POS == head:
            return True, f

    return False, None


def check_win(player_snake, rows, cols, info=None):
    """
    Vitória quando o tamanho da snake for igual a ROWS * COLS
    (todas as células do grid ocupadas).
    Se info for passado, atualiza info.game_condition para "win".
    """
    if len(player_snake.body) == rows * cols:
        if info is not None:
            info.game_condition = "win"
        return True
    return False


# --------------------------- CLASSE GAME ---------------------------

class Game:
    def __init__(self, screen, rows, cols, cell_size, mode):
        """
        mode: "JOGAR", "A_STAR", "A_NEWSTAR"
        """
        self.screen = screen
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.mode = mode

        self.game_map = grid.mapa(rows, cols, cell_size)
        self.player_snake = snake(rows, cols, cell_size)
        self.foods = [food(rows, cols, cell_size) for _ in range(3)]

        # posiciona as foods em células livres
        occupied = set(self.player_snake.body)
        for f in self.foods:
            f.relocate_food(occupied)
            if f.POS is not None:
                occupied.add(f.POS)

        # controlador de input do usuário (sempre existe, mas só é usado no modo JOGAR ou fallback)
        self.user_controller = UserController(self.player_snake)

        # game_info só é usado em modos com IA
        if self.mode in ("A_STAR", "A_NEWSTAR"):
            self.info = game_info(rows, cols)
        else:
            self.info = None

        # instância dos algoritmos de IA (quando usados)
        if self.mode == "A_STAR":
            self.ai = A_Star(rows, cols)
        elif self.mode == "A_NEWSTAR":
            self.ai = A_NewStar(rows, cols)   # <---- usa o novo algoritmo
        else:
            self.ai = None

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(10)  # velocidade da snake

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Seleciona a lógica de controle conforme o modo
            if self.mode == "JOGAR":
                self.user_controller.handle_input()
            elif self.mode in ("A_STAR", "A_NEWSTAR"):
                self._handle_ai()
            else:
                self.user_controller.handle_input()  # fallback

            # move fisicamente a snake
            self.player_snake.move_snake()

            # atualiza info se estiver em modo IA
            if self.info is not None:
                self.info.update(self.player_snake, self.foods)

            # colisões
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

            # condição de vitória
            if check_win(self.player_snake, self.rows, self.cols, self.info):
                running = False

            # se info existir, também verifica estado
            if self.info is not None and self.info.game_condition in ("win", "loss"):
                running = False

            # desenha tudo
            self.draw()

    # ---------------------- modos de controle ----------------------

    def _handle_ai(self):
        """Lógica comum para A_STAR e A_NEWSTAR."""
        if self.ai is None:
            return

        start = self.player_snake.POS
        objectives = [f.POS for f in self.foods if f.POS is not None]
        obstacles = self.player_snake.body

        best_path = self.ai.find_best_path_tsp(start, objectives, obstacles)

        if best_path and len(best_path) > 1:
            next_step = best_path[1]
            curr_r, curr_c = start
            next_r, next_c = next_step

            if next_r < curr_r:
                self.player_snake.orientation = "up"
            elif next_r > curr_r:
                self.player_snake.orientation = "down"
            elif next_c < curr_c:
                self.player_snake.orientation = "left"
            elif next_c > curr_c:
                self.player_snake.orientation = "right"

    # ---------------------- desenho ----------------------

    def draw(self):
        self.screen.fill(grid.mapa.BLACK)
        self.game_map.draw_grid(self.screen)
        self.player_snake.draw_snake(self.screen)
        for f in self.foods:
            f.draw_food(self.screen)
        pygame.display.flip()


# --------------------------- FUNÇÃO main ---------------------------

def main():
    pygame.init()

    CELL_SIZE = 20
    ROWS, COLS = 20, 30
    WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Menu")

    font = pygame.font.SysFont(None, 48)

    # 1) roda o menu e pega o modo
    menu = Menu(screen, font)
    mode = menu.run()

    if mode is None:
        pygame.quit()
        return

    # 2) roda o jogo no modo escolhido
    game = Game(screen, ROWS, COLS, CELL_SIZE, mode)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
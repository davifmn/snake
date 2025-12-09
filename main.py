import pygame
import grid
from snake import snake
from food import food
from menu import Menu
from ALGO_PLAYS.game_info import game_info
from ALGO_PLAYS.A_STAR import A_Star
from ALGO_PLAYS.A_NEW_STAR import A_NEW_Star as A_NEW_STAR  # usa o A_Star novo com outro nome
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
        mode: "JOGAR", "A_STAR", "A_NEW_STAR"
        """
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
            self.info = game_info(rows, cols)
            self.ai = A_Star(rows, cols)
        elif self.mode == "A_NEW_STAR":
            self.ai = A_NEW_STAR(rows, cols) 
            self.info = game_info(rows, cols)  
        else:
            self.user_controller = UserController(self.player_snake)
            self.ai = None
            self.info = None

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(10) # controla a velocidade do jogo (10 FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Seleciona a lógica de controle conforme o modo
            if self.mode == "JOGAR":
                self.user_controller.handle_input()
            elif self.mode in ("A_STAR", "A_NEW_STAR"):
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

    # ---------------------- modos de controle ----------------------

    def _handle_ai(self):
        """
        Lógica comum para A_STAR e A_NEW_STAR. 
        CORRIGIDA para usar a lógica de wrap-around na definição da orientação.
        """
        if self.ai is None:
            return

        start = self.player_snake.POS
        # Pega a lista de posições das comidas
        objectives = [f.POS for f in self.foods if f.POS is not None]
        obstacles = self.player_snake.body

        # Roda o A* + TSP para encontrar o melhor caminho
        best_path = self.ai.find_best_path_tsp(start, objectives, obstacles)

        if best_path and len(best_path) > 1:
            next_step = best_path[1]
            curr_r, curr_c = start
            next_r, next_c = next_step
            
            # --- LÓGICA CORRIGIDA COM WRAP-AROUND (MÓDULO) ---
            
            # 1. Movimento Vertical
            # Verifica se next_r é o resultado de (curr_r -/+ 1) com wrap
            if next_r == (curr_r - 1) % self.rows:
                self.player_snake.orientation = "up"
            elif next_r == (curr_r + 1) % self.rows:
                self.player_snake.orientation = "down"
            
            # 2. Movimento Horizontal
            # Verifica se next_c é o resultado de (curr_c -/+ 1) com wrap
            elif next_c == (curr_c - 1) % self.cols:
                self.player_snake.orientation = "left"
            elif next_c == (curr_c + 1) % self.cols:
                self.player_snake.orientation = "right"
            

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
    ROWS, COLS = 20, 30 # Ajuste o tamanho do grid conforme necessário
    WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Menu")

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
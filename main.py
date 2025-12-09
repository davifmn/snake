import pygame
import grid
from snake import snake
from food import food  # <- novo import

def check_colision(player_snake, foods):
    """
    Verifica:
      - se a head da snake colidiu com alguma food
      - se a head colidiu com o próprio corpo
    Retorna:
      - (True, food_obj) se comeu alguma food
      - ("self", None)  se colidiu com o próprio corpo
      - (False, None)   caso contrário
    """
    head = player_snake.POS
    if head in player_snake.body[2:]:
        return "self", None
    for f in foods:
        if f.POS == head:
            return True, f

    return False, None


def check_win(player_snake, rows, cols):
    """
    Vitória quando o tamanho da snake for igual a ROWS * COLS
    (todas as células do grid ocupadas).
    """
    return len(player_snake.body) == rows * cols


def main():
    pygame.init()

    CELL_SIZE = 20
    ROWS, COLS = 20, 40  # --------------- DEFINIR TAMANHO DO GRID ---------------
    WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")

    game_map = grid.mapa(ROWS, COLS, CELL_SIZE)
    player_snake = snake(ROWS, COLS, CELL_SIZE)
    foods = [food(ROWS, COLS, CELL_SIZE) for _ in range(3)]

    # posiciona as 3 comidas em células livres
    occupied = set(player_snake.body)  
    for f in foods:
        f.relocate_food(occupied)
        if f.POS is not None:
            occupied.add(f.POS)

    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(10)  # velocidade da snake
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # lê input do usuário:muda apenas a orientação
        player_snake.user_move()
        player_snake.move_snake()

        # verifica colisões depois de mover
        colision_result, eaten_food = check_colision(player_snake, foods)

        if colision_result == "self":  # bateu no próprio corpo: fim de jogo
            running = False
        elif colision_result is True and eaten_food is not None:  # comeu uma food
            player_snake.grow_snake()
            occupied = set(player_snake.body)
            for f in foods:
                if f is not eaten_food and f.POS is not None:
                    occupied.add(f.POS)
            eaten_food.relocate_food(occupied)

        # verifica condição de vitória
        if check_win(player_snake, ROWS, COLS):
            running = False

        # DESENHAR O JOGO
        screen.fill(grid.mapa.BLACK)       # FUNDO
        game_map.draw_grid(screen)         # GRID
        player_snake.draw_snake(screen)    # SNAKE 
        for f in foods:                    # FOODS
            f.draw_food(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
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

    # colisão com o próprio corpo (ignorando índice 0, que é a cabeça)
    if head in player_snake.body[1:]:
        return "self", None

    # colisão com alguma food
    for f in foods:
        if f.POS == head:
            return True, f

    return False, None

def main():
    pygame.init()

    CELL_SIZE = 20
    ROWS, COLS = 20, 35  # --------------- DEFINIR TAMANHO DO GRID ---------------
    WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")

    game_map = grid.mapa(ROWS, COLS, CELL_SIZE)
    player_snake = snake(ROWS, COLS, CELL_SIZE)

    # cria 3 comidas
    foods = [food(ROWS, COLS, CELL_SIZE) for _ in range(3)]

    # posiciona as 3 comidas em células livres
    occupied = set(player_snake.body)  # todas as células ocupadas pela snake
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

        # lê input do usuário (muda apenas a orientação)
        player_snake.user_move()

        # move a snake na direção atual
        player_snake.move_snake()

        # verifica colisões depois de mover
        colision_result, eaten_food = check_colision(player_snake, foods)

        if colision_result == "self":
            # bateu no próprio corpo: fim de jogo
            running = False
        elif colision_result is True and eaten_food is not None:
            # comeu uma food
            player_snake.grow_snake()

            # atualizar células ocupadas (snake + todas as foods)
            occupied = set(player_snake.body)
            for f in foods:
                if f is not eaten_food and f.POS is not None:
                    occupied.add(f.POS)

            # realoca apenas a food que foi comida
            eaten_food.relocate_food(occupied)

        # fundo
        screen.fill(grid.mapa.BLACK)

        # desenhar mapa (grid) e snake
        game_map.draw_grid(screen)
        player_snake.draw_snake(screen)

        # desenhar foods
        for f in foods:
            f.draw_food(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
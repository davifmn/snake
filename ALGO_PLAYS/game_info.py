class game_info:
    """
    Armazena informações do estado atual do jogo:
      - posições da snake
      - orientação da cabeça
      - posições das foods
      - condição do jogo: "alive", "win", "loss"
    """

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

        self.snake_positions = []      # lista de tuplas (row, col)
        self.food_positions = []       # lista de tuplas (row, col), tamanho 3
        self.orientation = "right"     # "up", "down", "left", "right"
        self.game_condition = "alive"  # "alive", "win", "loss"

    def update(self, snake, foods):
        """
        Atualiza os dados com base no estado atual da snake e das foods.
        """
        self.snake_positions = list(snake.body)
        self.orientation = snake.orientation
        # pega POS de cada food (ignorando None)
        self.food_positions = [f.POS for f in foods if f.POS is not None]
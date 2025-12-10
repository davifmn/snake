import os
import pickle
import neat

from ALGO_PLAYS.game_info import game_info


class NEAT_AI:
    """
    Controla a evolução NEAT e controla a snake em tempo de execução.
    """

    def __init__(self, rows, cols, config_path):
        self.rows = rows
        self.cols = cols
        self.config_path = config_path
        self.config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path,
        )

        self.population = None
        self.best_genome = None
        self.net = None  # rede do melhor genome para jogar

        # caminhos para salvar/ler melhor indivíduo
        self.checkpoint_dir = os.path.join(os.path.dirname(config_path), "checkpoints")
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        self.best_path = os.path.join(os.path.dirname(config_path), "current_best.pickle")

        # se já existe um melhor genome salvo, carrega
        if os.path.isfile(self.best_path):
            with open(self.best_path, "rb") as f:
                self.best_genome = pickle.load(f)
                self.net = neat.nn.FeedForwardNetwork.create(self.best_genome, self.config)

    # ----------------------------------------------------------------------
    #  TREINO (RODADO EM SCRIPT SEPARADO, NÃO NO LOOP DO JOGO INTERATIVO)
    # ----------------------------------------------------------------------

    def _evaluate_genomes(self, genomes, config):
        """
        Função de fitness: usada pelo NEAT para treinar.
        Aqui você simula jogos automaticamente (sem render) para cada genome.
        Para manter simples, deixo uma “casca” para você expandir depois.
        """
        for genome_id, genome in genomes:
            genome.fitness = 0.0

            # Aqui você teria um loop de simulação (sem pygame) usando
            # as mesmas regras do seu Game, mas sem desenhar.
            #
            # Durante a simulação:
            #   - colidir com o próprio corpo -> genome.fitness -= X
            #   - comer comida -> genome.fitness += Y
            #
            # Deixo apenas um esqueleto para não explodir o código:

            # Exemplo mínimo (substitua por simulação real):
            genome.fitness -= 1.0  # penalização pequena só para não ficar 0

    def train(self, n_generations=50):
        """
        Treina uma população NEAT, salva o melhor indivíduo em current_best.pickle.
        Essa função deve ser rodada em um script separado (não no loop pygame).
        """
        self.population = neat.Population(self.config)
        self.population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        self.population.add_reporter(stats)

        winner = self.population.run(self._evaluate_genomes, n_generations)

        # salva melhor genome
        with open(self.best_path, "wb") as f:
            pickle.dump(winner, f)

        self.best_genome = winner
        self.net = neat.nn.FeedForwardNetwork.create(winner, self.config)

    # ----------------------------------------------------------------------
    #  USO EM TEMPO DE JOGO (NO LOOP PYGAME)
    # ----------------------------------------------------------------------

    def ensure_net_loaded(self):
        """
        Garante que self.net está carregada (carrega current_best.pickle se preciso).
        """
        if self.net is not None:
            return

        if os.path.isfile(self.best_path):
            with open(self.best_path, "rb") as f:
                self.best_genome = pickle.load(f)
                self.net = neat.nn.FeedForwardNetwork.create(self.best_genome, self.config)

    def choose_action(self, info: game_info):
        """
        Usa a rede NEAT treinada para escolher a direção.
        Inputs:
          - posição normalizada da cabeça
          - posição normalizada da primeira comida (se existir)
          - orientação atual (one-hot)
          - tamanho atual da snake (normalizado)
        Output:
          - 4 saídas (up, down, left, right) -> pega o argmax.
        """
        self.ensure_net_loaded()
        if self.net is None:
            return None  # sem rede -> não altera movimento

        if not info.snake_positions:
            return None

        head_r, head_c = info.snake_positions[0]

        # normaliza posições em [0, 1]
        head_r_n = head_r / max(1, info.rows - 1)
        head_c_n = head_c / max(1, info.cols - 1)

        # primeira food (se tiver)
        if info.food_positions:
            f_r, f_c = info.food_positions[0]
            food_r_n = f_r / max(1, info.rows - 1)
            food_c_n = f_c / max(1, info.cols - 1)
        else:
            food_r_n = 0.0
            food_c_n = 0.0

        # orientação one-hot
        ori_up = 1.0 if info.orientation == "up" else 0.0
        ori_down = 1.0 if info.orientation == "down" else 0.0
        ori_left = 1.0 if info.orientation == "left" else 0.0
        ori_right = 1.0 if info.orientation == "right" else 0.0

        # tamanho da snake
        size_n = len(info.snake_positions) / float(info.rows * info.cols)

        inputs = [
            head_r_n,
            head_c_n,
            food_r_n,
            food_c_n,
            ori_up,
            ori_down,
            ori_left,
            ori_right,
            size_n,
        ]

        outputs = self.net.activate(inputs)
        # esperamos 4 saídas: [up, down, left, right]
        if len(outputs) != 4:
            return None

        idx = max(range(4), key=lambda i: outputs[i])
        if idx == 0:
            return "up"
        elif idx == 1:
            return "down"
        elif idx == 2:
            return "left"
        else:
            return "right"
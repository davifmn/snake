from ALGO_PLAYS.A_STAR import A_Star

class A_NEW_Star(A_Star):
    """
    Variante de A* que considera:
    1. Grid Toroide (Wrap-around)
    2. Obstáculos Dinâmicos (Time-Aware): A cauda sai do caminho conforme andamos.
    """

    def __init__(self, rows, cols):
        super().__init__(rows, cols)

    def heuristic(self, a, b):
        """Distância Manhattan com wrap-around."""
        # Se as posições não forem válidas (ex: None), retorna infinito
        if not a or not b:
            return float('inf')

        r1, c1 = a
        r2, c2 = b
        
        dr = abs(r1 - r2)
        dc = abs(c1 - c2)
        
        # O wrap considera a menor distância: direta ou dando a volta
        dr = min(dr, self.rows - dr)
        dc = min(dc, self.cols - dc)
        
        return dr + dc

    def get_neighbors(self, node, obstacles_info):
        """
        Retorna vizinhos considerando wrap e a movimentação da cauda.
        
        obstacles_info: Espera-se que seja um Dicionário {posicao: indice_no_corpo}
        para a snake, ou um Set normal para outros obstáculos estáticos.
        """
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] 
        
        # O custo 'g' do nó atual representa quantos "frames" se passaram.
        # No próximo passo, teremos andado (node.g + 1) vezes.
        steps_taken = node.g + 1

        # Verifica se obstacles_info é o nosso mapa especial de índices (dict)
        # Se for set, é obstáculo estático padrão.
        is_dynamic_snake = isinstance(obstacles_info, dict)
        snake_len = len(obstacles_info) if is_dynamic_snake else 0

        for dr, dc in directions:
            # Posição crua
            raw_r = node.position[0] + dr
            raw_c = node.position[1] + dc

            # Aplica wrap (mundo infinito)
            r = raw_r % self.rows
            c = raw_c % self.cols
            next_pos = (r, c)

            is_valid = True

            # --- LÓGICA TIME-AWARE ---
            if next_pos in obstacles_info:
                if is_dynamic_snake:
                    # Se está no corpo da cobra, verificamos em qual parte.
                    # Index 0 = Cabeça, Index N = Cauda.
                    part_index = obstacles_info[next_pos]
                    
                    # Quantos turnos faltam para essa parte do corpo sair daí?
                    # Ex: Cobra tam 5. Parte índice 3 (quase na cauda). 
                    # Ela sai em (5 - 3) = 2 turnos.
                    turns_to_clear = snake_len - part_index
                    
                    # Se já andamos passos suficientes para ela sumir, NÃO é obstáculo.
                    # Caso contrário (steps_taken < turns_to_clear), ainda é parede.
                    if steps_taken < turns_to_clear:
                        is_valid = False
                else:
                    # Obstáculo estático (Set)
                    is_valid = False

            if is_valid:
                neighbors.append(next_pos)

        return neighbors


    def find_best_path_tsp(self, start_pos, food_positions, snake_body):

        snake_body_map = {pos: i for i, pos in enumerate(snake_body)}
        return super().find_best_path_tsp(start_pos, food_positions, snake_body_map)


    def next_direction(self, start_pos, food_positions, snake_body):
        """
        Calcula a próxima direção baseada no caminho otimizado.
        """
        if not self.current_path:
            objectives = [pos for pos in food_positions if pos is not None]
            path = self.find_best_path_tsp(start_pos, objectives, snake_body)
            if path and len(path) > 1:
                self.current_path = path[1:]
            else:
                return None

        if not self.current_path:
            return None

        next_step = self.current_path.pop(0)
        curr_r, curr_c = start_pos
        next_r, next_c = next_step

        # Comparações considerando o wrap (módulo) para definir a direção
        if next_r == (curr_r - 1) % self.rows:
            return "up"
        if next_r == (curr_r + 1) % self.rows:
            return "down"
        if next_c == (curr_c - 1) % self.cols:
            return "left"
        if next_c == (curr_c + 1) % self.cols:
            return "right"

        return None
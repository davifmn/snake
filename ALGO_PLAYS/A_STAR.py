import heapq
import itertools

class Node:
    """Classe auxiliar para o algoritmo A*"""
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Custo do início até aqui
        self.h = 0  # Heurística (distância estimada até o fim)
        self.f = 0  # Custo total (g + h)

    def __lt__(self, other):
        return self.f < other.f

class A_Star:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # cache simples para não recalcular caminho a cada passo
        self.current_path = []

    def _in_bounds(self, pos):
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols

    def heuristic(self, a, b):
        """Calcula a distância Manhattan (grid)"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, node, obstacles):
        """Retorna vizinhos válidos (não são obstáculos e estão dentro do grid)"""
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] 

        for dr, dc in directions:
            r, c = node.position[0] + dr, node.position[1] + dc

            if self._in_bounds((r, c)) and (r, c) not in obstacles:
                neighbors.append((r, c))
        return neighbors

    def a_star_search(self, start, end, obstacles):
        """
        Executa o A* entre start e end.
        Retorna: (caminho_lista, custo) ou (None, infinity) se falhar.
        """
        open_list = []
        closed_set = set()

        start_node = Node(start)
        end_node = Node(end)
        
        heapq.heappush(open_list, start_node)

        while open_list:
            current_node = heapq.heappop(open_list)
            closed_set.add(current_node.position)

            if current_node.position == end:
                path = []
                current = current_node
                while current:
                    path.append(current.position)
                    current = current.parent
                return path[::-1], len(path)

            neighbors = self.get_neighbors(current_node, obstacles)
            
            for next_pos in neighbors:
                if next_pos in closed_set:
                    continue

                neighbor = Node(next_pos, current_node)
                neighbor.g = current_node.g + 1
                neighbor.h = self.heuristic(neighbor.position, end_node.position)
                neighbor.f = neighbor.g + neighbor.h

                heapq.heappush(open_list, neighbor)

        return None, float('inf')

    def find_best_path_tsp(self, start_pos, food_positions, snake_body):
        """
        Resolve o TSP sobre as foods e devolve o caminho da cabeça até a 1ª food
        da melhor ordem.
        """
        if not food_positions:
            return []

        obstacles = set(snake_body)
        if start_pos in obstacles:
            obstacles.remove(start_pos)

        perms = list(itertools.permutations(food_positions))
        
        best_cost = float('inf')
        best_first_path = None
        distance_cache = {} 

        def get_path_cost(p1, p2):
            key = (p1, p2)
            if key not in distance_cache:
                path, cost = self.a_star_search(p1, p2, obstacles)
                distance_cache[key] = (path, cost)
            return distance_cache[key]

        for perm in perms:
            current_cost = 0
            current_pos = start_pos
            possible = True
            first_segment_path = None

            for i, target in enumerate(perm):
                path, cost = get_path_cost(current_pos, target)
                if path is None or cost == float('inf'):
                    possible = False
                    break

                if i == 0:
                    first_segment_path = path

                current_cost += cost
                current_pos = target

            if possible and current_cost < best_cost:
                best_cost = current_cost
                best_first_path = first_segment_path

        return best_first_path

    # ------------------------ NOVO: interface para o Game ------------------------

    def next_direction(self, start_pos, food_positions, snake_body):
        """
        Decide a próxima direção ('up','down','left','right') a partir do estado atual.
        Reaproveita/mantém um caminho interno em self.current_path.
        """
        # 1. Se não temos caminho, calcula um novo
        if not self.current_path:
            objectives = [pos for pos in food_positions if pos is not None]
            path = self.find_best_path_tsp(start_pos, objectives, snake_body)
            if path and len(path) > 1:
                # ignorar a posição atual (start_pos) no caminho
                self.current_path = path[1:]
            else:
                return None  # sem caminho

        # 2. Se ainda temos passos no caminho, pega o próximo
        if not self.current_path:
            return None

        next_step = self.current_path.pop(0)
        curr_r, curr_c = start_pos
        next_r, next_c = next_step

        # sem wrap aqui – A_NEW_Star sobrescreve se precisar
        if next_r == curr_r - 1:
            return "up"
        if next_r == curr_r + 1:
            return "down"
        if next_c == curr_c - 1:
            return "left"
        if next_c == curr_c + 1:
            return "right"

        return None
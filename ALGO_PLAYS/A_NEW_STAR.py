import heapq
import itertools

class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

class A_Star:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def heuristic(self, a, b):
        """
        Calcula a distância Manhattan considerando o wrap-around.
        O algoritmo escolhe o menor caminho: direto ou dando a volta no mundo.
        """
        r1, c1 = a
        r2, c2 = b
        
        # Distância absoluta linear
        dr = abs(r1 - r2)
        dc = abs(c1 - c2)
        
        # Escolhe o menor entre: distância direta vs dar a volta pelo outro lado
        dr = min(dr, self.rows - dr)
        dc = min(dc, self.cols - dc)
        
        return dr + dc

    def get_neighbors(self, node, obstacles):
        """
        Retorna vizinhos considerando que o grid 'dá a volta' (toroide).
        """
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] 

        for dr, dc in directions:
            # Calcula posição crua
            raw_r = node.position[0] + dr
            raw_c = node.position[1] + dc
            
            # Aplica o wrap (módulo)
            # Se raw_r for -1, vira rows-1. Se for rows, vira 0.
            r = raw_r % self.rows
            c = raw_c % self.cols

            # Verifica se não é obstáculo
            if (r, c) not in obstacles:
                neighbors.append((r, c))
                
        return neighbors

    def a_star_search(self, start, end, obstacles):
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

                # Nota: Em implementações completas do A*, verificaríamos se 
                # o vizinho já está na open_list com um g menor. 
                # Para grid simples uniformes, adicionar direto funciona bem.
                heapq.heappush(open_list, neighbor)

        return None, float('inf')

    def find_best_path_tsp(self, start_pos, food_positions, snake_body):
        """
        Lógica do Caixeiro Viajante (igual à anterior, mas usando o A* atualizado).
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
                
                if path is None:
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
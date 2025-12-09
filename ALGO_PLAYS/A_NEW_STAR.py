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

class A_NEW_Star:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def _in_bounds(self, pos):
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols

    def heuristic(self, a, b):
        """Distância Manhattan com wrap-around."""
        if not (self._in_bounds(a) and self._in_bounds(b)):
            # se algo sair da grade, devolve custo alto pra forçar descartar
            return float('inf')

        r1, c1 = a
        r2, c2 = b
        
        dr = abs(r1 - r2)
        dc = abs(c1 - c2)
        
        dr = min(dr, self.rows - dr)
        dc = min(dc, self.cols - dc)
        
        return dr + dc

    def get_neighbors(self, node, obstacles):
        """Vizinhos com wrap (toroide), ignorando obstáculos."""
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] 

        for dr, dc in directions:
            raw_r = node.position[0] + dr
            raw_c = node.position[1] + dc
            
            r = raw_r % self.rows
            c = raw_c % self.cols

            if (r, c) not in obstacles:
                neighbors.append((r, c))
                
        return neighbors

    def a_star_search(self, start, end, obstacles):
        # validações de entrada
        if not (self._in_bounds(start) and self._in_bounds(end)):
            return None, float('inf')

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

                if neighbor.h == float('inf'):
                    continue  # algo inválido, ignora

                neighbor.f = neighbor.g + neighbor.h
                heapq.heappush(open_list, neighbor)

        return None, float('inf')

    def find_best_path_tsp(self, start_pos, food_positions, snake_body):
        if not food_positions:
            return []

        obstacles = set(snake_body)
        if start_pos in obstacles:
            obstacles.remove(start_pos)

        # filtra foods fora do grid por segurança
        valid_foods = [
            pos for pos in food_positions
            if pos is not None and self._in_bounds(pos)
        ]
        if not valid_foods:
            return []

        perms = list(itertools.permutations(valid_foods))
        
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

    def _handle_ai(self):
        """Lógica comum para A_STAR e A_NEW_STAR."""
        if self.ai is None:
            return

        start = self.player_snake.POS

        # objetivos válidos (dentro do grid e não None)
        objectives = [
            f.POS for f in self.foods
            if f.POS is not None
            and 0 <= f.POS[0] < self.rows
            and 0 <= f.POS[1] < self.cols
        ]

        if not objectives:
            # sem objetivo -> não altera orientação
            return

        # obstáculos = corpo atual da snake, sempre dentro do grid
        obstacles = list(self.player_snake.body)

        best_path = self.ai.find_best_path_tsp(start, objectives, obstacles)

        if not best_path or len(best_path) <= 1:
            return

        next_step = best_path[1]
        # sanity check: se vier algo estranho, ignora
        if not (0 <= next_step[0] < self.rows and 0 <= next_step[1] < self.cols):
            return

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
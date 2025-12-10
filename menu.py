import pygame

class Menu:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.options = ["JOGAR", "A_STAR", "A_NEW_STAR", "NEAT"]
        self.selected_index = 0

    def run(self):
        """Loop do menu. Retorna o modo escolhido como string ou None se sair."""
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return self.options[self.selected_index]

            self.draw()
        return None

    def draw(self):
        self.screen.fill((0, 0, 0))
        title_surf = self.font.render("SNAKE", True, (0, 255, 0))
        title_rect = title_surf.get_rect(center=(self.screen.get_width() // 2, 80))
        self.screen.blit(title_surf, title_rect)

        start_y = 160
        for i, text in enumerate(self.options):
            color = (255, 255, 255) if i != self.selected_index else (255, 255, 0)
            surf = self.font.render(text, True, color)
            rect = surf.get_rect(center=(self.screen.get_width() // 2,
                                         start_y + i * 50))
            self.screen.blit(surf, rect)

        pygame.display.flip()
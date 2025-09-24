import pygame
import sys

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.font = game.assets.get_font("default")
        self.options = ["Iniciar Jogo", "Características", "Sair"]
        self.selected = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.selected == 0:
                        self.game.change_state("JOGO_PRINCIPAL")
                    elif self.selected == 1:
                        self.game.change_state("CARACTERISTICAS")
                    elif self.selected == 2:
                        pygame.quit()
                        sys.exit()

    def update(self):
        pass

    def draw(self, surface):
        surface.fill((30, 30, 30))
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(option, True, color)
            surface.blit(text, (300, 200 + i * 60))

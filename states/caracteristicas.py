import pygame
import sys

class Caracteristicas:
    def __init__(self, game):
        self.game = game
        self.font = game.assets.get_font("default")
        self.atributos = {"Força": 10, "Destreza": 8, "Inteligência": 12}

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state("MENU_PRINCIPAL")

    def update(self):
        pass

    def draw(self, surface):
        surface.fill((50, 50, 100))
        y = 200
        for nome, valor in self.atributos.items():
            text = self.font.render(f"{nome}: {valor}", True, (255, 255, 255))
            surface.blit(text, (250, y))
            y += 50

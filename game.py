import pygame
from assets import Assets
from states.main_menu import MainMenu
from states.jogo_principal import JogoPrincipal
from states.caracteristicas import Caracteristicas
from characters.player import Player
from characters.deck import generate_deck  # Ou de onde você gera o deck
from states.batalha import Batalha
from config import font_path

class Game:
    def __init__(self):
        pygame.init()
        self.SCREEN = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Meu RPG com Pygame")
        self.CLOCK = pygame.time.Clock()
        self.assets = Assets()
        self.running = True  # <-- controle de loop principal

        # Carregar recursos principais
        self.assets.load_font("default", font_path, 18)

        # Cria o jogador PRIMEIRO (antes dos estados)
        self.player = Player("Jogador", max_energy= 3, max_health= 15)

        # Configura o deck do jogador
        deck = generate_deck()
        self.player.set_deck(deck)
        self.player.draw_card(5)  # Compra cartas iniciais

        # Estados
        self.states = {
            "MENU_PRINCIPAL": MainMenu(self),
            "JOGO_PRINCIPAL": JogoPrincipal(self),
            "CARACTERISTICAS": Caracteristicas(self),
            "BATALHA": Batalha(self),
        }
        self.current_state = self.states["MENU_PRINCIPAL"]

    def change_state(self, state_name):
        self.current_state = self.states[state_name]

    def run(self):
        while True:
            events = pygame.event.get()
            self.current_state.handle_events(events)
            self.current_state.update()
            self.current_state.draw(self.SCREEN)

            pygame.display.flip()
            self.CLOCK.tick(60)

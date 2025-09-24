import pygame
import sys

# Importa as classes de gerenciamento e os dados do jogador
from assets import Assets
from characters.player import Player
from characters.deck import generate_deck
# Importa as constantes de configuração
from config import SCREEN_WIDTH, SCREEN_HEIGHT

# Importa as classes de estado que serão usadas
from states.base_state import BaseState
from states.main_menu import MainMenu
from states.jogo_principal import JogoPrincipal
from states.caracteristicas import Caracteristicas
# A classe Batalha será importada dinamicamente quando necessária

class Game:
    """
    Classe principal que gerencia a janela, o loop do jogo, os assets
    e a pilha de estados (telas).
    """
    def __init__(self):
        """Inicializa o Pygame, a tela e os componentes centrais do jogo."""
        pygame.init()
        
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.SCREEN = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Card Game RPG")

        self.CLOCK = pygame.time.Clock()
        self.running = True

        self.assets = Assets()
        self.player = self.create_player()
        
        self.state_stack = []
        self.load_initial_state()

    def create_player(self):
        """Cria a instância do jogador e configura seu deck inicial."""
        player = Player("Herói", max_energy=3, max_health=100)
        player.attributes = {"Força": 10, "Destreza": 8, "Inteligência": 12}
        deck = generate_deck()
        player.set_deck(deck)
        player.draw_card(5)
        print("Jogador criado e deck configurado.")
        return player

    def load_initial_state(self):
        """Cria e carrega o estado inicial do jogo na pilha."""
        self.push_state(MainMenu(self))

    def get_active_state(self):
        """Retorna o estado que está no topo da pilha."""
        return self.state_stack[-1] if self.state_stack else None

    # --- Gerenciamento da Pilha de Estados ---

    def push_state(self, state):
        """
        Adiciona um novo estado ao topo da pilha.
        Pode receber uma string com o nome do estado ou uma instância de estado já criada.
        """
        if isinstance(state, str):
            if state == "MENU_PRINCIPAL":
                new_state = MainMenu(self)
            elif state == "JOGO_PRINCIPAL":
                new_state = JogoPrincipal(self)
            elif state == "CARACTERISTICAS":
                new_state = Caracteristicas(self)
            else:
                print(f"Erro: Tentativa de criar estado desconhecido pelo nome: '{state}'")
                return
            
            # ========================================================================
            # CORREÇÃO PRINCIPAL ESTÁ AQUI
            # Estávamos adicionando 'state' (a string) em vez de 'new_state' (o objeto)
            # ========================================================================
            self.state_stack.append(new_state)

        else:
            # Se 'state' já for um objeto (como no caso da Batalha), apenas o adiciona
            self.state_stack.append(state)

    def pop_state(self):
        """Remove o estado do topo da pilha."""
        if self.state_stack:
            self.state_stack.pop()
        if not self.state_stack:
            self.running = False

    def change_state(self, new_state):
        """Limpa a pilha de estados e adiciona um novo estado."""
        while self.state_stack:
            self.state_stack.pop()
        self.push_state(new_state)

    # --- Loop Principal ---

    def game_loop(self):
        """O loop principal do jogo que roda continuamente."""
        while self.running:
            events = pygame.event.get()
            active_state = self.get_active_state()

            if active_state:
                active_state.handle_events(events)
                active_state.update()
                active_state.draw(self.SCREEN)
            else:
                self.running = False

            pygame.display.flip()
            self.CLOCK.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jogo = Game()
    jogo.game_loop()
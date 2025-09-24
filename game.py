import pygame
import sys

# Importações de classes e configurações
from assets import Assets
from characters.player import Player
from characters.deck import generate_deck
from config import font_path

# Importações dos estados do jogo
from states.main_menu import MainMenu
from states.jogo_principal import JogoPrincipal
from states.caracteristicas import Caracteristicas
# A Batalha não é mais criada aqui, mas recebida como um objeto
# from states.batalha import Batalha 

class Game:
    """
    Classe principal que gerencia o jogo, os estados e o loop principal.
    Utiliza uma pilha de estados para um gerenciamento mais flexível das telas.
    """
    def __init__(self):
        """Inicializa o Pygame, a tela e os componentes centrais do jogo."""
        pygame.init()
        
        self.screen_width = 800
        self.screen_height = 600
        self.SCREEN = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Meu Card Game RPG")

        self.CLOCK = pygame.time.Clock()
        self.running = True

        self.assets = Assets()
        self.player = None
        self.state_stack = []

        self.load_assets()
        self.create_player()
        self.load_initial_state()

    def load_assets(self):
        """Carrega todos os assets iniciais necessários para o jogo."""
        print("Carregando fontes...")
        self.assets.load_font("default", font_path, 18)
        self.assets.load_font("small", font_path, 12)
        self.assets.load_font("large", font_path, 24)
        print("Assets carregados com sucesso!")

    def create_player(self):
        """Cria a instância do jogador e configura seu deck inicial."""
        self.player = Player("Herói", max_energy=3, max_health=100)
        deck = generate_deck()
        self.player.set_deck(deck)
        self.player.draw_card(5)
        print("Jogador criado e deck configurado.")

    def load_initial_state(self):
        """Cria e carrega o estado inicial do jogo na pilha."""
        self.push_state("MENU_PRINCIPAL")

    def get_active_state(self):
        """Retorna o estado que está no topo da pilha."""
        return self.state_stack[-1] if self.state_stack else None

    # ========================================================================
    # CORREÇÃO PRINCIPAL ESTÁ AQUI
    # ========================================================================
    def push_state(self, state):
        """
        Adiciona um novo estado ao topo da pilha.
        Pode receber uma string com o nome do estado ou uma instância de estado já criada.
        """
        # Se 'state' for uma string, cria a instância correspondente
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
            self.state_stack.append(new_state)

        # Se 'state' já for uma instância de um estado, apenas a adiciona
        else:
            self.state_stack.append(state)

    def pop_state(self):
        """Remove o estado do topo da pilha."""
        if self.state_stack:
            self.state_stack.pop()
        if not self.state_stack:
            self.running = False

    def change_state(self, state):
        """Muda o estado atual, limpando a pilha e adicionando um novo."""
        while self.state_stack:
            self.state_stack.pop()
        self.push_state(state)

    def game_loop(self):
        """O loop principal do jogo."""
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
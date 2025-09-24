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
from states.batalha import Batalha

class Game:
    """
    Classe principal que gerencia o jogo, os estados e o loop principal.
    Utiliza uma pilha de estados para um gerenciamento mais flexível das telas.
    """
    def __init__(self):
        """Inicializa o Pygame, a tela e os componentes centrais do jogo."""
        pygame.init()
        
        # Configurações da tela
        self.screen_width = 800
        self.screen_height = 600
        self.SCREEN = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Meu Card Game RPG")

        # Controle de tempo e FPS
        self.CLOCK = pygame.time.Clock()
        self.running = True

        # Gerenciador de assets e dados do jogador
        self.assets = Assets()
        self.player = None  # O jogador será criado após o carregamento dos assets

        # Pilha de estados (State Stack)
        self.state_stack = []

        # Carregamento inicial de recursos
        self.load_assets()
        self.create_player()
        
        # Inicia o jogo carregando o menu principal na pilha
        self.load_states()

    def load_assets(self):
        """Carrega todos os assets iniciais necessários para o jogo."""
        print("Carregando fontes...")
        self.assets.load_font("default", font_path, 18)
        self.assets.load_font("small", font_path, 12)
        self.assets.load_font("large", font_path, 24)
        # Futuramente, você pode adicionar o carregamento de imagens e sons aqui
        # self.assets.load_image("player_sprite", "assets/player.png")
        # self.assets.load_sound("menu_music", "assets/music/menu.ogg")
        print("Assets carregados com sucesso!")

    def create_player(self):
        """Cria a instância do jogador e configura seu deck inicial."""
        self.player = Player("Herói", max_energy=3, max_health=100)
        deck = generate_deck()
        self.player.set_deck(deck)
        self.player.draw_card(5)  # Compra a mão inicial de cartas
        print("Jogador criado e deck configurado.")

    def load_states(self):
        """Cria e carrega o estado inicial do jogo na pilha."""
        # O primeiro estado a ser adicionado é o menu principal
        main_menu_state = MainMenu(self)
        self.state_stack.append(main_menu_state)

    def get_active_state(self):
        """Retorna o estado que está no topo da pilha."""
        return self.state_stack[-1] if self.state_stack else None

    def push_state(self, state_name):
        """Adiciona um novo estado ao topo da pilha."""
        if state_name == "MENU_PRINCIPAL":
            new_state = MainMenu(self)
        elif state_name == "JOGO_PRINCIPAL":
            new_state = JogoPrincipal(self)
        elif state_name == "CARACTERISTICAS":
            new_state = Caracteristicas(self)
        elif state_name == "BATALHA":
            new_state = Batalha(self)
        else:
            print(f"Erro: Estado '{state_name}' desconhecido.")
            return

        self.state_stack.append(new_state)

    def pop_state(self):
        """Remove o estado do topo da pilha."""
        if self.state_stack:
            self.state_stack.pop()
        if not self.state_stack:
            # Se a pilha ficar vazia, encerra o jogo
            self.running = False

    def change_state(self, state_name):
        """Muda o estado atual, limpando a pilha e adicionando um novo."""
        # Limpa todos os estados atuais
        while self.state_stack:
            self.state_stack.pop()
        # Adiciona o novo estado
        self.push_state(state_name)

    def game_loop(self):
        """O loop principal do jogo."""
        while self.running:
            # Pega os eventos
            events = pygame.event.get()

            # Pega o estado ativo (o que está no topo da pilha)
            active_state = self.get_active_state()

            if active_state:
                # Processa os eventos, atualiza a lógica e desenha o estado ativo
                active_state.handle_events(events)
                active_state.update()
                active_state.draw(self.SCREEN)
            else:
                # Se não houver estados, encerra o jogo
                self.running = False

            # Atualiza a tela e controla o FPS
            pygame.display.flip()
            self.CLOCK.tick(60)

        # Encerra o Pygame ao sair do loop
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jogo = Game()
    jogo.game_loop()
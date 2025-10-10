import pygame
import sys

# Importações de classes e configurações
from assets import Assets
from characters.player import Player
from characters.cards import generate_deck
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
        
        # 🔥 GRUPO DE SPRITES PARA GERENCIAR O PLAYER VISUALMENTE
        self.all_sprites = pygame.sprite.Group()

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
        # 🔥 AGORA O PLAYER É UM SPRITE E PRECISA DE POSIÇÃO
        self.player = Player("Herói", max_energy=3, max_health=100, x=100, y=300)
        
        # 🔥 ADICIONA O PLAYER AO GRUPO DE SPRITES
        self.all_sprites.add(self.player)
        
        deck = generate_deck(size=6)
        self.player.set_deck(deck)
        self.player.draw_card(3)
        print("Jogador criado e deck configurado.")
        print(f"Player position: {self.player.rect.topleft}")  # Debug

    def load_initial_state(self):
        """Cria e carrega o estado inicial do jogo na pilha."""
        self.push_state("MENU_PRINCIPAL")

    def get_active_state(self):
        """Retorna o estado que está no topo da pilha."""
        return self.state_stack[-1] if self.state_stack else None

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
            dt = self.CLOCK.tick(30) / 1000  # Tempo decorrido em segundos (ex: 0.016 para 60 FPS)
            events = pygame.event.get()
            active_state = self.get_active_state()
            
            # 🔥 ATUALIZA TODOS OS SPRITES (INCLUINDO O PLAYER)
            self.all_sprites.update()

            if active_state:
                active_state.handle_events(events)
                active_state.update(dt)
                active_state.draw(self.SCREEN)
                
                # 🔥 DESENHA OS SPRITES NO ESTADO ATIVO (se necessário)
                # Isso permite que cada estado decida quando desenhar os sprites
                if hasattr(active_state, 'draw_sprites'):
                    active_state.draw_sprites(self.SCREEN)
            else:
                self.running = False

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    jogo = Game()
    jogo.game_loop()
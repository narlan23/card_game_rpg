import pygame
import sys

class BaseState:
    """
    Classe base para todos os estados (telas) do jogo.

    Esta classe serve como um modelo, garantindo que todos os estados 
    tenham uma estrutura e métodos consistentes. Ela gerencia a referência
    ao objeto principal do jogo e define os métodos essenciais que o 
    loop principal irá chamar.
    """
    def __init__(self, game):
        """
        Inicializa o estado.
        
        Args:
            game (Game): A instância principal do jogo, que contém
                         recursos compartilhados como a tela, o jogador e os assets.
        """
        self.game = game

    def handle_events(self, events):
        """
        Processa todos os eventos de entrada (teclado, mouse, etc.).
        Este método é chamado a cada frame pelo loop principal do jogo.
        
        Args:
            events (list): A lista de eventos do Pygame capturados no frame.
        """
        # Comportamento padrão: permite fechar o jogo de qualquer estado.
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Ação padrão do ESC pode ser sair do jogo,
                    # mas cada estado filho pode sobrescrever isso.
                    self.game.pop_state()

    def update(self, dt):
        """
        Atualiza a lógica interna do estado.
        Este método é chamado a cada frame e é onde a lógica do jogo,
        como movimento de personagens ou timers, deve ser atualizada.
        """
        pass # Cada estado filho implementará sua própria lógica de atualização.

    def draw(self, surface):
        """
        Desenha todos os elementos visuais do estado na tela.
        
        Args:
            surface (pygame.Surface): A superfície principal da tela onde
                                      tudo será desenhado.
        """
        pass # Cada estado filho implementará sua própria lógica de renderização.
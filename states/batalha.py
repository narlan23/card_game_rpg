import pygame
import sys
from batalha.battle_manager import BattleManager
from batalha.battle_state import BattleState
from states.base_state import BaseState # <-- 1. Importe a classe base

class Batalha(BaseState):
    """
    Representa o estado de combate do jogo.
    Este estado é inicializado com os dados dos inimigos que o jogador enfrentará.
    """
    def __init__(self, game, enemies_data):
        """
        Inicializa o estado de batalha.
        
        Args:
            game (Game): A instância principal do jogo.
            enemies_data (list): Uma lista de dicionários, cada um contendo
                                 os dados de um inimigo para esta batalha.
        """
        super().__init__(game)
        
        # O BattleManager gerencia toda a lógica complexa da batalha
        self.battle_manager = BattleManager(game)
        
        # Configura a batalha com os inimigos específicos que foram passados
        self.battle_manager.setup_battle(enemies_data)

    def handle_events(self, events):
        """Gerencia a entrada do usuário durante a batalha."""
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            
            # Se a batalha terminou (vitória ou derrota), ESC fecha a tela
            if self.battle_manager.state in [BattleState.VICTORY, BattleState.DEFEAT]:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.game.pop_state() # Retorna ao estado anterior (mapa)
            
            # Durante o turno do jogador, processa cliques do mouse
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.battle_manager.handle_click(event.pos)
        pass

    def update(self,dt):
        """Delega a atualização da lógica para o battle_manager."""
        self.battle_manager.update(dt)

    def draw(self, surface):
        """Delega a renderização da cena de batalha para o battle_manager."""
        self.battle_manager.draw(surface)
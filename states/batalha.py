import pygame
import sys
from batalha.battle_manager import BattleManager
from batalha.enemy import Enemy

class Batalha:
    def __init__(self, game):
        self.game = game
        self.battle_manager = BattleManager(game)
        
        # Dados dos inimigos para esta batalha
        self.enemies_data = [
            {"name": "Goblin", "health": 30, "attack": 1, "image": "goblin.png"},
            {"name": "Orc", "health": 50, "attack": 1, "image": "orc.png"},
            {"name": "Slime", "health": 20, "attack": 1, "image": "slime.png"}
        ]
        
        # Configura a batalha
        self.battle_manager.setup_battle(self.enemies_data)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state("JOGO_PRINCIPAL")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Delega o tratamento de cliques para o battle_manager
                self.battle_manager.handle_click(event.pos)

    def update(self):
        # Delega a atualização para o battle_manager
        self.battle_manager.update()

    def draw(self, surface):
        # Delega o desenho para o battle_manager
        self.battle_manager.draw(surface)
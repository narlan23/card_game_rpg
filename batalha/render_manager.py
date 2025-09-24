import pygame
from batalha.battle_state import BattleState
from batalha.ui import draw_end_turn_button, draw_player_status
# A função draw_card não é mais importada ou usada diretamente aqui

class RenderManager:
    def __init__(self, battle_manager):
        self.battle_manager = battle_manager
        self.game = battle_manager.game # Atalho para o objeto principal do jogo

    def draw(self, surface):
        """Renderiza toda a cena da batalha."""
        surface.fill((50, 50, 80))
        
        # Desenha os componentes do jogo
        self._draw_enemies(surface)
        self._draw_player_status(surface)
        self._draw_enemy_status(surface)
        
        # ========================================================================
        # CORREÇÃO PRINCIPAL ESTÁ AQUI
        # Removemos o argumento extra 'draw_card' da chamada.
        # ========================================================================
        if self.battle_manager.state == BattleState.PLAYER_TURN:
            self.battle_manager.hand_renderer.draw_hand(surface)
        
        # Desenha as animações por cima de tudo
        self.battle_manager.animation_manager.draw(surface)
        
        # Desenha o botão de encerrar turno
        if (self.battle_manager.state == BattleState.PLAYER_TURN and 
            not self.battle_manager.animation_manager.has_active_animations()):
            draw_end_turn_button(surface, self.game)

        # Desenha mensagens de estado (Vitória/Derrota)
        self._draw_battle_state(surface)

    def _draw_enemies(self, surface):
        """Desenha os inimigos e suas barras de vida."""
        for enemy in self.battle_manager.enemies:
            surface.blit(enemy.image, enemy.rect)
            if enemy.health > 0:
                self._draw_health_bar(surface, enemy)

    def _draw_health_bar(self, surface, enemy):
        """Desenha a barra de vida de um inimigo."""
        if enemy.health < enemy.max_health:
            ratio = enemy.health / enemy.max_health
            bar_x = enemy.rect.x
            bar_y = enemy.rect.y - 20
            bar_width = enemy.rect.width
            bar_height = 10
            
            pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, bar_width * ratio, bar_height))

    def _draw_player_status(self, surface):
        """Desenha o painel de status do jogador."""
        draw_player_status(surface, self.game, self.game.player, 50, 340)

    def _draw_enemy_status(self, surface):
        """Desenha os efeitos de status ativos nos inimigos."""
        font = self.game.assets.get_font("small")
        for enemy in self.battle_manager.enemies:
            if enemy.health > 0 and hasattr(enemy, 'status_effects') and enemy.status_effects:
                status_y = enemy.rect.y - 40
                for status, data in enemy.status_effects.items():
                    duration = data.get('duration', '∞')
                    text = f"{status.capitalize()}: {duration}"
                    status_surface = font.render(text, True, (255, 255, 0))
                    surface.blit(status_surface, (enemy.rect.x, status_y))
                    status_y -= 15

    def _draw_battle_state(self, surface):
        """Desenha mensagens de vitória, derrota ou turno na tela."""
        state = self.battle_manager.state
        if state in [BattleState.VICTORY, BattleState.DEFEAT]:
            message = "VITÓRIA!" if state == BattleState.VICTORY else "DERROTA!"
            color = (255, 215, 0) if state == BattleState.VICTORY else (255, 0, 0)
            self._draw_overlay_message(message, color)
            self._draw_text_center(surface, "Pressione ESC para continuar", (255, 255, 255), y_offset=40)
        else:
            text = "Seu Turno" if state == BattleState.PLAYER_TURN else "Turno do Inimigo"
            self._draw_text_center(surface, text, (255, 255, 255), y=20)

    def _draw_overlay_message(self, text, color):
        """Cria uma sobreposição escura e exibe uma mensagem no centro."""
        overlay = pygame.Surface((self.game.screen_width, self.game.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.game.SCREEN.blit(overlay, (0, 0))
        self._draw_text_center(self.game.SCREEN, text, color)

    def _draw_text_center(self, surface, text, color, y=None, y_offset=0):
        """Função auxiliar para desenhar texto centralizado."""
        font = self.game.assets.get_font("large" if y is None else "default")
        rendered = font.render(text, True, color)
        
        x = self.game.screen_width // 2 - rendered.get_width() // 2
        
        if y is not None:
            final_y = y
        else:
            final_y = self.game.screen_height // 2 - rendered.get_height() // 2
        
        surface.blit(rendered, (x, final_y + y_offset))
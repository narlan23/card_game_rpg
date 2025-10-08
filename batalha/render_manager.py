import pygame
from batalha.battle_state import BattleState
from batalha.ui import draw_end_turn_button, draw_player_status, draw_reshuffle_button
from characters.hand_renderer import draw_card


class RenderManager:
    def __init__(self, battle_manager):
        self.battle_manager = battle_manager
        self._cached_bg = None      # Cache para background
        self._bg_loaded = False     # Flag para evitar recarregar a imagem

    # -------------------------
    # 🔹 Carregamento e cache de background
    # -------------------------
    def _load_background(self, surface):
        """Carrega o background com cache e tratamento de erro."""
        if self._cached_bg and self._bg_loaded:
            return self._cached_bg

        try:
            bg_image = pygame.image.load("assets/battle_background.png").convert()
            self._cached_bg = pygame.transform.scale(bg_image, surface.get_size())
            self._bg_loaded = True
            return self._cached_bg
        except (pygame.error, FileNotFoundError) as e:
            print(f"[RenderManager] Erro ao carregar background: {e}")
            # Fallback: cria uma cor sólida de fundo
            fallback = pygame.Surface(surface.get_size())
            fallback.fill((30, 30, 60))
            return fallback

    # -------------------------
    # 🔹 Render principal
    # -------------------------
    def draw(self, surface):
        """Renderiza toda a cena da batalha."""
        bg_image = self._load_background(surface)
        surface.blit(bg_image, (0, 0))

        # Desenha inimigos
        self._draw_enemies(surface)

        # Desenha mão do jogador apenas no turno do jogador
        if self.battle_manager.state == BattleState.PLAYER_TURN:
            self.battle_manager.hand_renderer.draw_hand(surface, draw_card)

        # Status do jogador e inimigos
        self._draw_player_status(surface)
        self._draw_enemy_status(surface)

        # Desenha animações (dano, buffs, etc.)
        self.battle_manager.animation_manager.draw(surface)

        # Botão "Encerrar Turno" — apenas quando não há animações ativas
        if (self.battle_manager.state == BattleState.PLAYER_TURN and
            not self.battle_manager.animation_manager.has_active_animations()):
            draw_reshuffle_button(surface, self.battle_manager.font, self.battle_manager)
            draw_end_turn_button(surface, self.battle_manager.font, self.battle_manager)

        # Estado da batalha (Vitória/Derrota)
        self._draw_battle_state(surface)

    # -------------------------
    # 🔹 Desenho de inimigos
    # -------------------------
    def _draw_enemies(self, surface):
        self.battle_manager.enemies.draw(surface)
        for enemy in self.battle_manager.enemies:
            if enemy.health > 0:
                self._draw_health_bar(surface, enemy)

    def _draw_health_bar(self, surface, enemy):
        ratio = enemy.health / enemy.max_health
        pygame.draw.rect(surface, (255, 0, 0),
                         (enemy.rect.x, enemy.rect.y - 20, enemy.rect.width, 10))
        pygame.draw.rect(surface, (0, 255, 0),
                         (enemy.rect.x, enemy.rect.y - 20, enemy.rect.width * ratio, 10))

    # -------------------------
    # 🔹 Status do jogador e inimigos
    # -------------------------
    def _draw_player_status(self, surface):
        draw_player_status(surface, self.battle_manager.game.player, 50, 340)

    def _draw_enemy_status(self, surface):
        for enemy in self.battle_manager.enemies:
            if enemy.health > 0 and hasattr(enemy, 'status_effects'):
                status_y = enemy.rect.y - 40
                for status, data in enemy.status_effects.items():
                    duration = data.get('duration', '∞')

                    # Se for duração em ms → converte para segundos
                    if isinstance(duration, (int, float)):
                        duration = max(0, round(duration / 1000, 1))

                    text = f"{status}: {duration}"
                    status_surface = self.battle_manager.font.render(text, True, (255, 255, 0))
                    surface.blit(status_surface, (enemy.rect.x, status_y))
                    status_y -= 15

    # -------------------------
    # 🔹 Mensagens de estado da batalha
    # -------------------------
    def _draw_battle_state(self, surface):
        if self.battle_manager.state in [BattleState.VICTORY, BattleState.DEFEAT]:
            self._draw_overlay_message(
                "VITÓRIA! Pressione ESC para voltar." if self.battle_manager.state == BattleState.VICTORY
                else "DERROTA! Pressione ESC para voltar.",
                (255, 215, 0) if self.battle_manager.state == BattleState.VICTORY else (255, 0, 0)
            )
        else:
            # Mensagem de instrução no topo
            if self.battle_manager.state == BattleState.PLAYER_TURN:
                text = "Seu turno! Selecione cartas e ataque os inimigos."
            else:
                text = "Turno do inimigo! Aguarde..."
            # self._draw_text_center(surface, text, (255, 255, 255), y=10)  # opcional

    def _draw_overlay_message(self, text, color):
        overlay = pygame.Surface(
            (self.battle_manager.game.screen_width, self.battle_manager.game.screen_height),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 150))
        self.battle_manager.game.SCREEN.blit(overlay, (0, 0))
        self._draw_text_center(self.battle_manager.game.SCREEN, text, color)

    def _draw_text_center(self, surface, text, color, y=None):
        rendered = self.battle_manager.font.render(text, True, color)
        x = self.battle_manager.game.screen_width // 2 - rendered.get_width() // 2
        y = y if y is not None else self.battle_manager.game.screen_height // 2 - rendered.get_height() // 2
        surface.blit(rendered, (x, y))

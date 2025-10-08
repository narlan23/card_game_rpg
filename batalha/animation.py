import pygame
import math

class DamageAnimation:
    """Animação de dano flutuante, com movimento suave e fade-out."""

    def __init__(self, target, amount, is_player=False, screen_width=800, hand_y=400):
        self.target = target
        self.amount = amount
        self.is_player = is_player
        self.screen_width = screen_width
        self.hand_y = hand_y

        # Define posição inicial
        if is_player:
            self.start_y = hand_y - 100
        else:
            self.start_y = target.rect.top - 30

        self.position = (target.rect.centerx, self.start_y)

        # Movimento vertical e duração
        self.end_y = self.start_y - 40  # sobe 40 pixels
        self.duration = 0.6             # duração total em segundos
        self.elapsed = 0.0              # tempo acumulado

        # Estado visual
        self.alpha = 255
        self.is_finished = False

        # Fonte padrão (pode ser trocada por uma do sistema de assets)
        self.font = pygame.font.SysFont(None, 36)

    def update(self, dt: float):
        """Atualiza a animação com base no tempo decorrido (dt em segundos)."""
        if self.is_finished:
            return

        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.duration)

        # 🌀 Suavização (ease-out cúbico)
        eased_progress = 1 - (1 - progress) ** 3

        # ✨ Efeito bounce (leve quique no início)
        bounce_offset = math.sin(eased_progress * math.pi) * 8

        # Atualiza posição (subindo com suavização e bounce)
        new_y = self.start_y + (self.end_y - self.start_y) * eased_progress - bounce_offset
        self.position = (self.position[0], new_y)

        # Fade-out gradual
        self.alpha = max(0, int(255 * (1 - progress)))

        if progress >= 1.0:
            self.is_finished = True

    def draw(self, surface: pygame.Surface):
        """Desenha o número do dano na tela."""
        color = (255, 0, 0) if self.amount > 0 else (0, 255, 0)
        text = self.font.render(str(self.amount), True, color)
        text.set_alpha(self.alpha)
        x = self.position[0] - text.get_width() // 2
        y = self.position[1]
        surface.blit(text, (x, y))

import pygame

class DamageAnimation:
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

        # Define o deslocamento vertical e duração
        self.end_y = self.start_y - 40   # sobe 40 pixels
        self.duration = 600              # duração total em ms
        self.elapsed = 0                 # tempo acumulado

        # Estado
        self.alpha = 255
        self.is_finished = False

    def update(self, dt):
        """Atualiza a animação com base no tempo decorrido (dt em ms)."""
        if self.is_finished:
            return

        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.duration)

        # Interpolação linear
        new_y = self.start_y + (self.end_y - self.start_y) * progress
        self.alpha = 255 * (1 - progress)
        self.position = (self.position[0], new_y)

        if self.elapsed >= self.duration:
            self.is_finished = True

    def draw(self, surface):
        """Desenha o texto do dano na tela."""
        font = pygame.font.SysFont(None, 36)
        color = (255, 0, 0) if self.amount > 0 else (0, 255, 0)
        text = font.render(str(self.amount), True, color)
        text.set_alpha(int(self.alpha))
        surface.blit(text, (self.position[0] - text.get_width() // 2, self.position[1]))

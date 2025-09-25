import pygame
from config import CARD_COLORS, TEXT_COLOR, ELEMENT_COLORS, GOLD, BLACK, WHITE, get_element_icons

class HandRenderer:
    """Renderiza a mão de um jogador com hover e escala animada."""

    CARD_WIDTH = 90
    CARD_HEIGHT = 124
    HOVER_SCALE = 1.2
    SCALE_SPEED = 0.1

    def __init__(self, player, screen_width=800, hand_y=400, align="center"):
        self.player = player
        self.screen_width = screen_width
        self.hand_y = hand_y
        self.align = align
        self.card_positions = []
        self.card_scales = []
        self.update_card_positions()

    def set_alignment(self, align, y=None):
        self.align = align
        if y is not None:
            self.hand_y = y
        self.update_card_positions()

    def update_card_positions(self):
        num_cards = len(self.player.hand)
        if num_cards == 0:
            self.card_positions = []
            self.card_scales = []
            return

        spacing = min(self.CARD_WIDTH, self.screen_width // (num_cards + 1))
        total_width = spacing * (num_cards - 1)

        if self.align == "left":
            start_x = 50
        elif self.align == "right":
            start_x = self.screen_width - total_width - 50
        else:
            start_x = (self.screen_width - total_width) // 2

        self.card_positions = [(start_x + i * spacing, self.hand_y) for i in range(num_cards)]
        self.card_scales = [1.0 for _ in range(num_cards)]

    def draw_hand(self, screen, draw_card_func):
        """Desenha todas as cartas da mão."""
        mouse_pos = pygame.mouse.get_pos()

        for idx, card in enumerate(self.player.hand):
            x, y = self.card_positions[idx]
            card_rect = pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT)

            hovering = card_rect.collidepoint(mouse_pos)
            target_scale = self.HOVER_SCALE if hovering else 1.0
            self.card_scales[idx] += (target_scale - self.card_scales[idx]) * self.SCALE_SPEED

            scaled_width = int(self.CARD_WIDTH * self.card_scales[idx])
            scaled_height = int(self.CARD_HEIGHT * self.card_scales[idx])

            offset_x = (scaled_width - self.CARD_WIDTH) // 2
            offset_y = (scaled_height - self.CARD_HEIGHT) // 2
            hover_offset_y = -20 if hovering else 0

            draw_card_func(
                screen,
                card,
                x - offset_x,
                y - offset_y + hover_offset_y,
                selected=(card.state == "selected"),
                width=scaled_width,
                height=scaled_height
            )



# Largura da borda da carta
CARD_BORDER_WIDTH = 3

# -----------------------------
# Função draw_card
# -----------------------------
def draw_card(screen, card, x, y, selected=False, width=100, height=150):
    """Desenha uma carta na tela com Pygame com visual melhorado."""
    # Desenha a sombra da carta
    shadow_rect = pygame.Rect(x + 4, y + 4, width, height)
    pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=10)
    
    # Define cores baseadas no elemento
    card_color = WHITE
    border_color = ELEMENT_COLORS.get(card.element, BLACK)
    
    # Se a carta está selecionada, destaque-a
    if selected:
        border_color = GOLD
        card_color = (240, 240, 240)  # Branco mais brilhante
    
    # Desenha o corpo principal da carta
    card_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, card_color, card_rect, border_radius=10)
    pygame.draw.rect(screen, border_color, card_rect, CARD_BORDER_WIDTH, border_radius=10)
    
    # Fonte para textos
    font_small = pygame.font.SysFont("arial", 12, bold=True)
    font_medium = pygame.font.SysFont("arial", 14, bold=True)
    font_large = pygame.font.SysFont("arial", 16, bold=True)
    
    # Desenha o tipo da carta (no topo)
    type_text = font_medium.render(card.card_type.value, True, BLACK)
    screen.blit(type_text, (x + width//2 - type_text.get_width()//2, y + 10))
    
    # Desenha o elemento (círculo colorido)
    pygame.draw.circle(screen, border_color, (x + width//2, y + 35), 12)
    element_text = font_small.render(card.element[0], True, WHITE)  # Primeira letra do elemento
    screen.blit(element_text, (x + width//2 - element_text.get_width()//2, y + 35 - element_text.get_height()//2))
    
    # Desenha o valor da carta (centralizado)
    value_text = font_large.render(f"{card.value}", True, BLACK)
    screen.blit(value_text, (x + width//2 - value_text.get_width()//2, y + 60))
    
    # CUSTO DE ENERGIA - ÍCONE CIRCULAR CENTRALIZADO NA BASE
    energy_circle_radius = 12
    energy_circle_x = x + width // 2
    energy_circle_y = y + height - energy_circle_radius - 8
    
    # Círculo de fundo para o custo de energia
    pygame.draw.circle(screen, (240, 230, 100), (energy_circle_x, energy_circle_y), energy_circle_radius)
    pygame.draw.circle(screen, (180, 160, 60), (energy_circle_x, energy_circle_y), energy_circle_radius, 2)
    
    # Texto do custo dentro do círculo
    energy_font = pygame.font.SysFont("arial", 12, bold=True)
    energy_text = energy_font.render(str(card.energy_cost), True, BLACK)
    screen.blit(energy_text, (energy_circle_x - energy_text.get_width()//2, 
                             energy_circle_y - energy_text.get_height()//2))
    
    # COMBINAÇÃO: BARRA + NÚMERO (acima da carta)
    if card.max_uses > 1:  # Só mostra se a carta tiver sistema de usos
        # Barra de progresso
        bar_width = width - 20
        bar_height = 3
        bar_x = x + 10
        bar_y = y - 10
        
        pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height))
        if card.uses_left > 0:
            use_ratio = card.uses_left / card.max_uses
            filled_width = int(bar_width * use_ratio)
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, filled_width, bar_height))
        
        # Texto com usos (acima da barra)
        uses_font = pygame.font.SysFont("arial", 10)
        uses_text = uses_font.render(f"{card.uses_left}/{card.max_uses}", True, WHITE)
        text_bg = pygame.Rect(bar_x + bar_width//2 - uses_text.get_width()//2 - 2, 
                             bar_y - uses_text.get_height() - 2,
                             uses_text.get_width() + 4, 
                             uses_text.get_height() + 2)
        pygame.draw.rect(screen, (50, 50, 50), text_bg, border_radius=2)
        screen.blit(uses_text, (bar_x + bar_width//2 - uses_text.get_width()//2, bar_y - uses_text.get_height() - 1))
    
     # Desenha o ícone do elemento (se disponível)
    element_icons = get_element_icons()
    if card.element in element_icons:
        icon = element_icons[card.element]
        icon_x = x + width//2 - icon.get_width()//2
        icon_y = y + 35 - icon.get_height()//2
        screen.blit(icon, (icon_x, icon_y))
    else:
        # Fallback: desenha um círculo representando o elemento
        pygame.draw.circle(screen, border_color, (x + width//2, y + 35), 12)


    # Adiciona decoração nos cantos
    pygame.draw.circle(screen, border_color, (x + 10, y + 10), 4)
    pygame.draw.circle(screen, border_color, (x + width - 10, y + 10), 4)
    pygame.draw.circle(screen, border_color, (x + 10, y + height - 10), 4)
    pygame.draw.circle(screen, border_color, (x + width - 10, y + height - 10), 4)

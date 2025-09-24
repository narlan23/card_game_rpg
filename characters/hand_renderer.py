import pygame
from config import CARD_STATE_COLORS, ELEMENT_COLORS, GOLD, BLACK, WHITE, BLUE

class HandRenderer:
    """Renderiza a mão de um jogador com hover e escala animada."""

    CARD_WIDTH = 90
    CARD_HEIGHT = 124
    HOVER_SCALE = 1.2
    SCALE_SPEED = 0.1

    def __init__(self, game, player, hand_y, align="center"):
        """
        Inicializa o renderizador da mão.
        
        Args:
            game (Game): A instância principal do jogo para acessar assets.
            player (Player): O objeto do jogador cuja mão será renderizada.
            hand_y (int): A posição vertical (Y) da mão na tela.
            align (str): O alinhamento da mão ('center', 'left', 'right').
        """
        self.game = game
        self.player = player
        self.screen_width = self.game.screen_width
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
        """Calcula e atualiza a posição de cada carta na mão."""
        num_cards = len(self.player.hand)
        if num_cards == 0:
            self.card_positions = []
            self.card_scales = []
            return

        spacing = min(self.CARD_WIDTH + 10, self.screen_width / (num_cards + 1))
        total_width = spacing * (num_cards - 1)

        if self.align == "left":
            start_x = 50
        elif self.align == "right":
            start_x = self.screen_width - total_width - 50
        else:
            start_x = (self.screen_width - total_width) / 2

        self.card_positions = [(start_x + i * spacing, self.hand_y) for i in range(num_cards)]
        self.card_scales = [1.0 for _ in range(num_cards)]

    def draw_hand(self, screen):
        """Desenha todas as cartas da mão na tela."""
        mouse_pos = pygame.mouse.get_pos()

        for idx, card in enumerate(self.player.hand):
            x, y = self.card_positions[idx]
            
            hovering = pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT).collidepoint(mouse_pos)
            target_scale = self.HOVER_SCALE if hovering else 1.0
            self.card_scales[idx] += (target_scale - self.card_scales[idx]) * self.SCALE_SPEED

            scaled_width = int(self.CARD_WIDTH * self.card_scales[idx])
            scaled_height = int(self.CARD_HEIGHT * self.card_scales[idx])

            offset_x = (scaled_width - self.CARD_WIDTH) / 2
            offset_y = (scaled_height - self.CARD_HEIGHT) / 2
            hover_offset_y = -30 if hovering else 0

            draw_card(
                self.game, screen, card,
                x - offset_x,
                y - offset_y + hover_offset_y,
                selected=(card.state.value == "selected"),
                width=scaled_width,
                height=scaled_height
            )

# Largura da borda da carta
CARD_BORDER_WIDTH = 3

def draw_card(game, screen, card, x, y, selected=False, width=100, height=150):
    """Desenha uma única carta na tela com visual aprimorado."""
    shadow_rect = pygame.Rect(x + 5, y + 5, width, height)
    pygame.draw.rect(screen, (BLACK[0], BLACK[1], BLACK[2], 100), shadow_rect, border_radius=12)
    
    card_color = WHITE
    border_color = ELEMENT_COLORS.get(card.element, BLACK)
    
    if selected:
        border_color = GOLD
        card_color = (245, 245, 220) # Um tom de marfim
    
    card_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, card_color, card_rect, border_radius=10)
    pygame.draw.rect(screen, border_color, card_rect, CARD_BORDER_WIDTH, border_radius=10)
    
    # Busca as fontes diretamente do gerenciador de assets
    font_small = game.assets.get_font("small")
    font_medium = game.assets.get_font("default")
    
    # Desenha o tipo da carta (no topo)
    if font_medium:
        type_text = font_medium.render(card.card_type, True, BLACK)
        screen.blit(type_text, (x + width/2 - type_text.get_width()/2, y + 10))
    
    # Busca o ícone do elemento no gerenciador de assets
    icon = game.assets.get_element_icon(card.element)
    if icon:
        screen.blit(icon, (x + width/2 - icon.get_width()/2, y + 40 - icon.get_height()/2))
    else: # Fallback se o ícone não existir
        pygame.draw.circle(screen, border_color, (x + width/2, y + 40), 12)

    # Desenha o valor da carta (centralizado)
    if font_medium:
        value_text = font_medium.render(str(card.value), True, BLACK)
        screen.blit(value_text, (x + width/2 - value_text.get_width()/2, y + 70))
    
    # Custo de energia na parte inferior
    if font_small:
        energy_text = font_small.render(str(card.energy_cost), True, WHITE)
        energy_bg = pygame.Rect(x + width/2 - 12, y + height - 22, 24, 24)
        pygame.draw.circle(screen, BLUE, energy_bg.center, 12)
        screen.blit(energy_text, (energy_bg.centerx - energy_text.get_width()/2, energy_bg.centery - energy_text.get_height()/2))
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


# -------------------------------------------
# ⚙️ Configurações visuais da carta
# -------------------------------------------
CARD_BORDER_WIDTH = 3

def draw_card(screen, card, x, y, selected=False, width=100, height=150):
    """Desenha uma carta com imagem, efeitos e destaque suave quando selecionada."""
    border_color = ELEMENT_COLORS.get(card.element, BLACK)

    # 1️⃣ Sombra
    shadow_rect = pygame.Rect(x + 4, y + 4, width, height)
    pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=10)

    # 2️⃣ Fundo da carta
    try:
        bg_image = pygame.image.load("assets/card.png").convert_alpha()
        bg_image = pygame.transform.scale(bg_image, (width, height))
        screen.blit(bg_image, (x, y))
    except:
        pygame.draw.rect(screen, WHITE, (x, y, width, height), border_radius=10)

    # -----------------------------------------
    # 3️⃣ Borda com fade suave (apenas se selecionada)
    # -----------------------------------------
    if not hasattr(card, "_border_alpha"):
        card._border_alpha = 0  # inicializa o fade da borda

    target_alpha = 120 if selected else 0
    # Transição suave de opacidade
    card._border_alpha += (target_alpha - card._border_alpha) * 0.2

    if card._border_alpha > 1:  # só desenha se visível
        border_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        transparent_gold = (255, 215, 0, int(card._border_alpha))
        pygame.draw.rect(
            border_surface,
            transparent_gold,
            border_surface.get_rect(),
            CARD_BORDER_WIDTH + 1,
            border_radius=10,
        )
        screen.blit(border_surface, (x, y))

    # -----------------------------------------
    # 4️⃣ Fontes e textos
    # -----------------------------------------
    font_small = pygame.font.SysFont("arial", 12, bold=True)
    font_medium = pygame.font.SysFont("arial", 14, bold=True)
    font_large = pygame.font.SysFont("arial", 16, bold=True)

    # 5️⃣ Tipo da carta
    type_text = font_medium.render(card.card_type.value, True, BLACK)
    screen.blit(type_text, (x + width // 2 - type_text.get_width() // 2, y + 10))

    # -----------------------------------------
    # 6️⃣ Ícone do elemento
    # -----------------------------------------
    ELEMENT_ICON_SIZE = 48  # 🧭 tamanho do ícone do elemento
    element_icons = get_element_icons()

    if card.element in element_icons:
        icon = element_icons[card.element]
        icon = pygame.transform.scale(icon, (ELEMENT_ICON_SIZE, ELEMENT_ICON_SIZE))
        icon_x = x + width // 2 - icon.get_width() // 2
        icon_y = y + 35 - icon.get_height() // 2
        screen.blit(icon, (icon_x, icon_y))
    else:
        pygame.draw.circle(screen, border_color, (x + width // 2, y + 35), ELEMENT_ICON_SIZE // 2)
        element_text = font_small.render(card.element[0], True, WHITE)
        screen.blit(
            element_text,
            (x + width // 2 - element_text.get_width() // 2, y + 35 - element_text.get_height() // 2),
        )

    # 7️⃣ Valor central
    value_text = font_large.render(f"{card.value}", True, BLACK)
    screen.blit(value_text, (x + width // 2 - value_text.get_width() // 2, y + 60))

    # -----------------------------------------
    # 8️⃣ Indicador de custo de energia
    # -----------------------------------------
    # 🔋 Localização: parte inferior central da carta
    # Círculo amarelo com número do custo dentro
    energy_circle_radius = 12
    energy_circle_x = x + width // 2
    energy_circle_y = y + height - energy_circle_radius - 8

    pygame.draw.circle(screen, (240, 230, 100), (energy_circle_x, energy_circle_y), energy_circle_radius)
    pygame.draw.circle(screen, (180, 160, 60), (energy_circle_x, energy_circle_y), energy_circle_radius, 2)

    energy_font = pygame.font.SysFont("arial", 12, bold=True)
    energy_text = energy_font.render(str(card.energy_cost), True, BLACK)
    screen.blit(
        energy_text,
        (
            energy_circle_x - energy_text.get_width() // 2,
            energy_circle_y - energy_text.get_height() // 2,
        ),
    )

    # -----------------------------------------
    # 9️⃣ Barra e contador de usos (no topo)
    # -----------------------------------------
    if card.max_uses > 1:
        bar_width = width - 20
        bar_height = 3
        bar_x = x + 10
        bar_y = y - 10

        pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height))
        if card.uses_left > 0:
            use_ratio = card.uses_left / card.max_uses
            filled_width = int(bar_width * use_ratio)
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, filled_width, bar_height))

        uses_font = pygame.font.SysFont("arial", 10)
        uses_text = uses_font.render(f"{card.uses_left}/{card.max_uses}", True, WHITE)
        text_bg = pygame.Rect(
            bar_x + bar_width // 2 - uses_text.get_width() // 2 - 2,
            bar_y - uses_text.get_height() - 2,
            uses_text.get_width() + 4,
            uses_text.get_height() + 2,
        )
        pygame.draw.rect(screen, (50, 50, 50), text_bg, border_radius=2)
        screen.blit(
            uses_text,
            (bar_x + bar_width // 2 - uses_text.get_width() // 2, bar_y - uses_text.get_height() - 1),
        )

    # -----------------------------------------
    # 🔹 10️⃣ Decoração nos cantos (cosmética)
    # -----------------------------------------
    for (dx, dy) in [(10, 10), (width - 10, 10), (10, height - 10), (width - 10, height - 10)]:
        pygame.draw.circle(screen, border_color, (x + dx, y + dy), 4)

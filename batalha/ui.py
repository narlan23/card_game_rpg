import pygame
from config import WHITE, FONT

def draw_player_status(surface, player, x, y):
    """
    Desenha o status completo do jogador:
    - Nome
    - Barra de vida com shield sobreposto (transparente)
    - Barra de energia
    - Ícones de efeitos ativos (status_effects)
    - Define player.rect para permitir clique no jogador
    """
    # Nome
    name_text = FONT.render(player.name, True, WHITE)
    surface.blit(name_text, (x, y))

    # ------------------- VIDA -------------------
    bar_width = 150
    bar_height = 15
    life_ratio = max(0, player.health / player.max_health)

    # Fundo vermelho
    pygame.draw.rect(surface, (100, 0, 0), (x, y + 30, bar_width, bar_height), border_radius=4)
    # Vida verde
    pygame.draw.rect(surface, (0, 200, 0), (x, y + 30, int(bar_width * life_ratio), bar_height), border_radius=4)

    # ------------------- SHIELD SOBRE A VIDA -------------------
    if getattr(player, "shield", 0) > 0:
        shield_ratio = min(1, player.shield / player.max_health)
        shield_surface = pygame.Surface((int(bar_width * shield_ratio), bar_height), pygame.SRCALPHA)
        shield_surface.fill((0, 150, 255, 120))  # azul semi-transparente
        surface.blit(shield_surface, (x, y + 30))

    # Contorno
    pygame.draw.rect(surface, WHITE, (x, y + 30, bar_width, bar_height), 2, border_radius=4)

    # Texto centralizado da vida
    if player.shield > 0:
        text_str = f"{player.health}/{player.max_health} (+{player.shield})"
    else:
        text_str = f"{player.health}/{player.max_health}"

    life_text = FONT.render(text_str, True, WHITE)
    shadow = FONT.render(text_str, True, (0, 0, 0))
    shadow_rect = shadow.get_rect(center=(x + bar_width // 2 + 1, y + 30 + bar_height // 2 + 1))
    surface.blit(shadow, shadow_rect)
    life_rect = life_text.get_rect(center=(x + bar_width // 2, y + 30 + bar_height // 2))
    surface.blit(life_text, life_rect)

    # ------------------- ENERGIA -------------------
    energy_ratio = max(0, player.energy / player.max_energy)

    pygame.draw.rect(surface, (60, 60, 60), (x, y + 55, bar_width, bar_height), border_radius=4)
    pygame.draw.rect(surface, (0, 200, 255), (x, y + 55, int(bar_width * energy_ratio), bar_height), border_radius=4)
    pygame.draw.rect(surface, WHITE, (x, y + 55, bar_width, bar_height), 2, border_radius=4)

    energy_text = FONT.render(f"{player.energy}/{player.max_energy}", True, WHITE)
    shadow = FONT.render(f"{player.energy}/{player.max_energy}", True, (0, 0, 0))
    shadow_rect = shadow.get_rect(center=(x + bar_width // 2 + 1, y + 55 + bar_height // 2 + 1))
    surface.blit(shadow, shadow_rect)
    energy_rect = energy_text.get_rect(center=(x + bar_width // 2, y + 55 + bar_height // 2))
    surface.blit(energy_text, energy_rect)

    # ------------------- STATUS EFFECTS COM ÍCONES -------------------
    if hasattr(player, "status_effects") and player.status_effects:
        icon_size = 16
        spacing = 5
        offset_x = x + bar_width + 10
        offset_y = y + 28

        for i, (effect, data) in enumerate(player.status_effects.items()):
            color = (0, 200, 255) if "buff" in effect.lower() else (200, 50, 50)

            pygame.draw.rect(surface, color, (offset_x, offset_y + i * (icon_size + spacing), icon_size, icon_size), border_radius=3)
            pygame.draw.rect(surface, WHITE, (offset_x, offset_y + i * (icon_size + spacing), icon_size, icon_size), 2, border_radius=3)

            duration = str(data.get("duration", 0))
            duration_text = FONT.render(duration, True, WHITE)
            duration_rect = duration_text.get_rect(center=(offset_x + icon_size // 2, offset_y + i * (icon_size + spacing) + icon_size // 2))
            surface.blit(duration_text, duration_rect)

    # ------------------- DEFINIR RECT PARA CLIQUE -------------------
    # Rect que cobre a "área clicável" do player (pode ser ajustado)
    player.rect = pygame.Rect(x, y, bar_width, 80)  
    # Agora o InputManager pode usar player.rect.collidepoint(pos)


# Configuração do botão End Turn
END_TURN_BUTTON = pygame.Rect(650, 500, 140, 40)  # posição e tamanho

END_TURN_LAYOUT = {
    "color": (200, 50, 50),
    "hover_color": (220, 70, 70),
    "hover_scale": 1.1,
    "shadow_offset": (4, 4),
}


def draw_end_turn_button(surface, font, battle_manager):
    """Desenha o botão End Turn, parecido com o botão Confirm"""
    cfg = END_TURN_LAYOUT
    mouse_pos = pygame.mouse.get_pos()
    is_hover = END_TURN_BUTTON.collidepoint(mouse_pos)

    # Escala no hover
    scale = cfg["hover_scale"] if is_hover else 1.0
    button_rect = pygame.Rect(
        END_TURN_BUTTON.x,
        END_TURN_BUTTON.y,
        int(END_TURN_BUTTON.width * scale),
        int(END_TURN_BUTTON.height * scale),
    )
    button_rect.center = END_TURN_BUTTON.center

    # ---------------- SOMBRA ----------------
    shadow = button_rect.copy()
    shadow.x += cfg["shadow_offset"][0]
    shadow.y += cfg["shadow_offset"][1]
    pygame.draw.rect(surface, (0, 0, 0, 150), shadow, border_radius=10)

    # ---------------- FUNDO ----------------
    base_color = cfg["hover_color"] if is_hover else cfg["color"]
    pygame.draw.rect(surface, base_color, button_rect, border_radius=10)

    # ---------------- TEXTO ----------------
    label = font.render("Encerrar", True, (255, 255, 255))
    surface.blit(
        label,
        (button_rect.centerx - label.get_width() // 2,
         button_rect.centery - label.get_height() // 2),
    )


def handle_end_turn_click(pos, battle_manager):
    """Verifica clique no botão End Turn"""
    if battle_manager.state == battle_manager.state.PLAYER_TURN:
        if END_TURN_BUTTON.collidepoint(pos):
            battle_manager.end_player_turn()
            return True
    return False
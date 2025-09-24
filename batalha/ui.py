import pygame
from config import WHITE, BLACK, RED, GREEN # Importa apenas as cores necessárias

# --- HUD DO JOGADOR ---

def draw_player_status(surface, game, player, x, y):
    """
    Desenha o status completo do jogador na tela de batalha.
    
    Args:
        surface (pygame.Surface): A tela onde o status será desenhado.
        game (Game): A instância principal do jogo para acessar os assets (fontes).
        player (Player): O objeto do jogador cujos status serão exibidos.
        x (int): A coordenada X inicial para o desenho.
        y (int): A coordenada Y inicial para o desenho.
    """
    # Obtém as fontes necessárias a partir da classe Assets
    font_default = game.assets.get_font("default")
    font_small = game.assets.get_font("small")

    # Nome do Jogador
    name_text = font_default.render(player.name, True, WHITE)
    surface.blit(name_text, (x, y))

    # --- Barras de Status (Vida e Energia) ---
    bar_width = 150
    bar_height = 20
    y_offset = y + 35

    # Desenha a barra de vida
    draw_status_bar(surface, font_default, x, y_offset, bar_width, bar_height,
                      player.health, player.max_health, (100, 0, 0), GREEN)
    
    # Desenha a barra de energia
    draw_status_bar(surface, font_default, x, y_offset + 30, bar_width, bar_height,
                      player.energy, player.max_energy, (30, 30, 80), (0, 150, 255))

    # --- Efeitos de Status Ativos ---
    y_offset += 75
    effects_title = font_default.render("Efeitos:", True, WHITE)
    surface.blit(effects_title, (x, y_offset))
    y_offset += 25

    # CORREÇÃO: Itera sobre o dicionário 'status_effects'
    if player.status_effects:
        for status, data in player.status_effects.items():
            duration = data.get('duration', '∞')
            effect_text = f"- {status.capitalize()} (Duração: {duration})"
            effect_surface = font_small.render(effect_text, True, (200, 200, 0))
            surface.blit(effect_surface, (x, y_offset))
            y_offset += 20
    else:
        none_text = font_small.render("- Nenhum", True, (150, 150, 150))
        surface.blit(none_text, (x, y_offset))

def draw_status_bar(surface, font, x, y, width, height, current_val, max_val, bg_color, fg_color):
    """Função auxiliar para desenhar uma barra de status genérica (vida, energia, etc.)."""
    ratio = max(0, current_val / max_val)

    # Fundo da barra
    pygame.draw.rect(surface, bg_color, (x, y, width, height), border_radius=4)
    # Preenchimento da barra
    pygame.draw.rect(surface, fg_color, (x, y, int(width * ratio), height), border_radius=4)
    # Contorno
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2, border_radius=4)

    # Texto centralizado com sombra
    text_str = f"{current_val}/{max_val}"
    shadow = font.render(text_str, True, BLACK)
    text = font.render(text_str, True, WHITE)
    
    shadow_rect = shadow.get_rect(center=(x + width / 2 + 1, y + height / 2 + 1))
    text_rect = text.get_rect(center=(x + width / 2, y + height / 2))

    surface.blit(shadow, shadow_rect)
    surface.blit(text, text_rect)


# --- BOTÃO DE ENCERRAR TURNO ---

# Constantes de configuração do botão
END_TURN_BUTTON = pygame.Rect(650, 500, 140, 40)
END_TURN_LAYOUT = {
    "color": RED,
    "hover_color": (220, 70, 70),
    "shadow_color": (0, 0, 0, 150),
    "text_color": WHITE,
    "hover_scale": 1.05,
    "shadow_offset": (3, 3),
}

def draw_end_turn_button(surface, game):
    """Desenha o botão de encerrar o turno."""
    cfg = END_TURN_LAYOUT
    font = game.assets.get_font("default")
    mouse_pos = pygame.mouse.get_pos()
    is_hover = END_TURN_BUTTON.collidepoint(mouse_pos)

    # Lógica de escala ao passar o mouse
    scale = cfg["hover_scale"] if is_hover else 1.0
    scaled_width = int(END_TURN_BUTTON.width * scale)
    scaled_height = int(END_TURN_BUTTON.height * scale)
    
    button_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
    button_rect.center = END_TURN_BUTTON.center

    # Sombra
    shadow_rect = button_rect.copy()
    shadow_rect.x += cfg["shadow_offset"][0]
    shadow_rect.y += cfg["shadow_offset"][1]
    pygame.draw.rect(surface, cfg["shadow_color"], shadow_rect, border_radius=10)

    # Fundo do botão
    base_color = cfg["hover_color"] if is_hover else cfg["color"]
    pygame.draw.rect(surface, base_color, button_rect, border_radius=10)

    # Texto
    label = font.render("Encerrar Turno", True, cfg["text_color"])
    label_rect = label.get_rect(center=button_rect.center)
    surface.blit(label, label_rect)
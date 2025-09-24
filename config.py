# ============================================================
# CONFIGURAÇÕES DO JOGO - config.py
# ============================================================

import pygame

# Inicializar pygame ANTES de usar qualquer módulo
pygame.init()

# Carregando a fonte personalizada
font_path = "assets/Font.ttf"
FONT_SIZE       = 8
FONT_SMALL_SIZE = 12
FONT       = pygame.font.Font(font_path, FONT_SIZE)
FONT_SMALL = pygame.font.Font(font_path, FONT_SMALL_SIZE)

# Cores por estado
CARD_COLORS = {
    "idle": (180, 180, 180),
    "selected": (100, 200, 100),
    "exhausted": (150, 50, 50)
}

TEXT_COLOR = (0, 0, 0)

ELEMENTS = ['Fogo', 'Terra', 'Água', 'Ar']

PLAYER_HEALTH = 100   # Vida inicial do jogador

# ---------------------------
# Paleta de Cores
# ---------------------------
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
GREEN       = (0, 255,   0)
RED         = (255,   0,   0)
BLUE        = (0,   0, 255)
GRAY        = (150, 150, 150)
LIGHT_BLUE  = (173, 216, 230)
GOLD        = (255, 215,   0)
CARD_HOVER_COLOR = (100, 100, 100)  # Cor para efeito hover (cinza claro)

# Cores para representar elementos
ELEMENT_COLORS = {
    'Fogo': (255, 100, 100),
    'Terra': (165, 42, 42),
    'Água': (100, 100, 255),
    'Ar':   (200, 200, 255)
}

# ---------------------------
# Cartas
# ---------------------------
# Tipos de carta
CARD_TYPES = {
    'ATTACK':  'Ataque',
    'DEFENSE': 'Defesa',
    'DODGE':   'Esquiva'
}

# Composição padrão do baralho
DECK_COMPOSITION = {
    CARD_TYPES['ATTACK']: 5,
    CARD_TYPES['DEFENSE']: 2,
    CARD_TYPES['DODGE']:  0
}

# Faixa de valores possíveis por tipo de carta
CARD_VALUE_RANGES = {
    CARD_TYPES['ATTACK']:  (10, 15),
    CARD_TYPES['DEFENSE']: (1, 2),
    CARD_TYPES['DODGE']:   (0, 1)
}

# Tamanho das cartas
CARD_WIDTH  = 100
CARD_HEIGHT = 150

ELEMENT_ICONS = None

def get_element_icons():
    """Carrega os ícones apenas quando necessário"""
    global ELEMENT_ICONS
    if ELEMENT_ICONS is None:
        ELEMENT_ICONS = {
            "Fogo": pygame.image.load("assets/fogo.png").convert_alpha(),
            "Água": pygame.image.load("assets/agua.png").convert_alpha(),
            "Terra": pygame.image.load("assets/terra.png").convert_alpha(),
            "Ar": pygame.image.load("assets/ar.png").convert_alpha()
        }
        # Redimensiona os ícones
        for element, icon in ELEMENT_ICONS.items():
            ELEMENT_ICONS[element] = pygame.transform.scale(icon, (24, 24))
    return ELEMENT_ICONS
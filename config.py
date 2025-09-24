# ============================================================
# CONFIGURAÇÕES DO JOGO - config.py
# Contém apenas constantes e dados estáticos.
# Nenhuma lógica de inicialização ou carregamento de assets.
# ============================================================

# --- GERAL DO JOGO ---
PLAYER_HEALTH = 100   # Vida inicial do jogador

# --- TELA E FONTES ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FONT_PATH = "assets/Font.ttf"
FONT_SIZES = {
    "small": 12,
    "default": 18,
    "large": 24
}

# --- PALETA DE CORES ---
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
GREEN       = (0, 255,   0)
RED         = (255,   0,   0)
BLUE        = (0,   0, 255)
GRAY        = (150, 150, 150)
LIGHT_BLUE  = (173, 216, 230)
GOLD        = (255, 215,   0)

# --- CONFIGURAÇÕES DE CARTAS ---
CARD_WIDTH  = 100
CARD_HEIGHT = 150
ELEMENTS = ['Fogo', 'Terra', 'Água', 'Ar']

# Cores para representar elementos
ELEMENT_COLORS = {
    'Fogo': (255, 100, 100),
    'Terra': (165, 42, 42),
    'Água': (100, 100, 255),
    'Ar':   (200, 200, 255)
}

# Cores por estado da carta
CARD_STATE_COLORS = {
    "idle": (180, 180, 180),
    "selected": (100, 200, 100),
    "exhausted": (150, 50, 50)
}

# Composição padrão do baralho
DECK_COMPOSITION = {
    "Ataque": 5,
    "Defesa": 2,
    "Buff": 1,
    "Debuff": 1
}

# Faixa de valores possíveis por tipo de carta
CARD_VALUE_RANGES = {
    "Ataque":  (10, 15),
    "Defesa": (5, 10),
    "Buff": (1, 3),
    "Debuff": (1, 3)
}

# --- CAMINHOS DE ASSETS (para serem carregados pela classe Assets) ---
ELEMENT_ICON_PATHS = {
    "Fogo": "assets/fogo.png",
    "Água": "assets/agua.png",
    "Terra": "assets/terra.png",
    "Ar": "assets/ar.png"
}
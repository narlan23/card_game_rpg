import random  # Para a versão aleatória
# 1. Caminho base dos assets de inimigos
ENEMY_ASSET_PATH = "assets/enemy/"

CATALOGO_MONSTROS = {
    "goblin": {
        "nome_base": "Goblin",
        "health_base": 5,
        "attack_base": 5,
        "sprite_paths": [  # Lista direta dos sprites
            f"{ENEMY_ASSET_PATH}agua_frame_6.png",
            f"{ENEMY_ASSET_PATH}agua_frame_7.png", 
            f"{ENEMY_ASSET_PATH}agua_frame_8.png",
        ],
        "animation_speed_base": 150,
        "tamanho_base": (75, 150),
        "fator_crescimento": {"health": 2, "attack": 1}
    },
    "orc": {
        "nome_base": "Orc",
        "health_base": 3, 
        "attack_base": 3,
        "sprite_paths": [  # Lista direta dos sprites
            f"{ENEMY_ASSET_PATH}agua2_frame_1.png",
            f"{ENEMY_ASSET_PATH}agua2_frame_2.png",
            f"{ENEMY_ASSET_PATH}agua2_frame_3.png",
        ],
        "animation_speed_base": 200,
        "tamanho_base": (100, 150),
        "fator_crescimento": {"health": 4, "attack": 2}
    }
}

def gerar_monstro(tipo_monstro, nivel=1):
    """Versão simplificada e mais robusta."""
    if tipo_monstro not in CATALOGO_MONSTROS:
        raise ValueError(f"Monstro '{tipo_monstro}' não encontrado")
    
    base = CATALOGO_MONSTROS[tipo_monstro]
    
    # Calcular status
    health = base["health_base"] + (base["fator_crescimento"]["health"] * (nivel - 1))
    attack = base["attack_base"] + (base["fator_crescimento"]["attack"] * (nivel - 1))
    
    # Nome com nível
    nome = f"{base['nome_base']} Nv.{nivel}" if nivel > 1 else base['nome_base']
    
    return {
        "name": nome,
        "health": int(health),
        "attack": int(attack),
        "image_paths": base["sprite_paths"],  # Usa a lista direta
        "animation_speed": base["animation_speed_base"],
        "x_tam": base["tamanho_base"][0],
        "y_tam": base["tamanho_base"][1]
    }

# FUNÇÃO QUE FALTAVA:
def gerar_encontro_inimigos(tipos_monstros, nivel_desafio=1):
    """
    Gera uma lista de inimigos para um encontro.
    
    Args:
        tipos_monstros (list): Lista de tipos ["goblin", "orc", ...]
        nivel_desafio (int): Nível geral do encontro
    
    Returns:
        list: Lista de dicionários no formato compatível
    """
    encontro = []
    
    for tipo in tipos_monstros:
        monstro = gerar_monstro(tipo, nivel_desafio)
        encontro.append(monstro)
    
    return encontro



def gerar_encontro_aleatorio(nivel_desafio=1, quantidade=2):
    """Gera encontro com monstros aleatórios"""
    tipos_disponiveis = list(CATALOGO_MONSTROS.keys())
    tipos_escolhidos = random.choices(tipos_disponiveis, k=quantidade)
    return gerar_encontro_inimigos(tipos_escolhidos, nivel_desafio)


class ProgressaoTorre:
    def __init__(self):
        self.nivel_atual = 0
        self.max_inimigos = 3  # Máximo de inimigos por encontro
    
    def proximo_desafio(self):
        """Gera o próximo desafio na progressão"""
        self.nivel_atual += 1
        
        # Fórmula: nível 1-3 segue padrão, depois escala
        if self.nivel_atual <= 3:
            quantidade = self.nivel_atual  # 1, 2, 3
            nivel_desafio = self.nivel_atual  # 1, 2, 3
        else:
            quantidade = self.max_inimigos  # Sempre 3 monstros
            nivel_desafio = self.nivel_atual  # Nível continua subindo
        
        # Gera tipos aleatórios de monstros
        tipos = random.choices(list(CATALOGO_MONSTROS.keys()), k=quantidade)
        return gerar_encontro_inimigos(tipos, nivel_desafio)
    
    def get_texto_desafio(self):
        """Texto descritivo do desafio atual"""
        return f"Andar {self.nivel_atual + 1} da Torre - Preparado?"
    
    def resetar(self):
        """Reseta a progressão (usar quando jogador morrer ou completar)"""
        self.nivel_atual = 0


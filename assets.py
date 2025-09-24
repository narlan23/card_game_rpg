import pygame
# Importa as constantes do arquivo de configuração
from config import FONT_PATH, FONT_SIZES, ELEMENT_ICON_PATHS

class Assets:
    """
    Classe centralizada para carregar, gerenciar e fornecer todos os 
    assets do jogo, como imagens, fontes e sons.
    """
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.element_icons = {} # Dicionário específico para os ícones

        # Chama o método que carrega tudo ao inicializar
        self.load_all()

    def load_all(self):
        """
        Método mestre que executa todas as rotinas de carregamento de assets.
        É a única função que você precisará chamar de fora da classe.
        """
        print("Carregando assets...")
        self._load_fonts()
        self._load_element_icons()
        # Adicione aqui outras funções de carregamento no futuro (ex: _load_enemy_sprites)
        print("Assets carregados com sucesso!")

    def _load_fonts(self):
        """Carrega todas as fontes definidas no config.py."""
        try:
            for name, size in FONT_SIZES.items():
                self.fonts[name] = pygame.font.Font(FONT_PATH, size)
        except pygame.error as e:
            print(f"ERRO: Não foi possível carregar a fonte em '{FONT_PATH}'. Detalhes: {e}")
            # Em caso de erro, carrega uma fonte padrão do sistema para não travar
            for name, size in FONT_SIZES.items():
                self.fonts[name] = pygame.font.Font(None, size)

    def _load_element_icons(self):
        """Carrega e redimensiona os ícones dos elementos definidos no config.py."""
        for element, path in ELEMENT_ICON_PATHS.items():
            try:
                icon = pygame.image.load(path).convert_alpha()
                # Redimensiona o ícone para um tamanho padrão
                self.element_icons[element] = pygame.transform.scale(icon, (24, 24))
            except pygame.error as e:
                print(f"ERRO: Não foi possível carregar o ícone para '{element}' em '{path}'. Detalhes: {e}")

    # --- Métodos Públicos para Obter os Assets ---

    def get_font(self, name="default"):
        """Retorna um objeto de fonte carregado. Ex: self.assets.get_font('large')"""
        return self.fonts.get(name)

    def get_element_icon(self, element_name):
        """Retorna a imagem do ícone de um elemento. Ex: self.assets.get_element_icon('Fogo')"""
        return self.element_icons.get(element_name)

    def load_image(self, key, path):
        """Carrega uma imagem individualmente com tratamento de erro."""
        try:
            self.images[key] = pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"ERRO: Não foi possível carregar a imagem em '{path}'. Detalhes: {e}")

    def get_image(self, key):
        """Retorna uma imagem carregada individualmente."""
        return self.images.get(key)
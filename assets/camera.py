# camera.py
import pygame

class Camera:
    # 1. Adicionamos screen_width, screen_height (tamanho fixo da tela) e zoom_level
    def __init__(self, screen_width, screen_height, map_width, map_height, zoom_level=1.0):
        # Tamanho FÍSICO da tela (não muda)
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.map_width = map_width
        self.map_height = map_height
        
        self._zoom_level = zoom_level
        
        # 2. self.rect representa a ÁREA DE VISÃO NO MUNDO, ajustada pelo zoom.
        self.rect = pygame.Rect(
            0, 0, 
            screen_width / self._zoom_level,
            screen_height / self._zoom_level
        )
        
    @property
    def zoom_level(self):
        return self._zoom_level

    # 3. NOVO: Setter para alterar o zoom e recalcular o tamanho do viewport
    @zoom_level.setter
    def zoom_level(self, new_zoom):
        # Evita divisão por zero ou zoom negativo
        if new_zoom <= 0:
             new_zoom = 0.1 
        
        # Salva o centro da câmera para que o zoom aconteça nesse ponto
        center_x = self.rect.centerx
        center_y = self.rect.centery
        
        self._zoom_level = new_zoom
        
        # RECALCULA as dimensões da área de visão (viewport)
        self.rect.width = self.screen_width / new_zoom
        self.rect.height = self.screen_height / new_zoom
        
        # Restaura o centro para evitar um 'salto'
        self.rect.centerx = center_x
        self.rect.centery = center_y
        
    @property
    def width(self):
        # A largura do viewport (a área do mundo que estamos vendo)
        return self.rect.width

    @property
    def height(self):
        # A altura do viewport
        return self.rect.height

    def apply(self, pos_or_rect):
        """Aplica transformação da câmera a uma posição ou retângulo"""
        # A lógica de aplicação permanece a mesma: subtrai o offset da câmera
        if isinstance(pos_or_rect, pygame.Rect):
            return pygame.Rect(
                pos_or_rect.x - self.rect.x,
                pos_or_rect.y - self.rect.y,
                pos_or_rect.width,
                pos_or_rect.height
            )
        else:
            return (pos_or_rect[0] - self.rect.x, pos_or_rect[1] - self.rect.y)

    def apply_rect(self, rect):
        """Método específico para retângulos (alternativa)"""
        return pygame.Rect(
            rect.x - self.rect.x,
            rect.y - self.rect.y,
            rect.width,
            rect.height
        )

    def update(self, target_pos):
        """Atualiza a posição da câmera para seguir o alvo"""
        # Centraliza a câmera no alvo
        self.rect.centerx = target_pos[0]
        self.rect.centery = target_pos[1]

        # Mantém a câmera dentro dos limites do mapa (usa o novo self.rect.width/height)
        self.rect.x = max(0, min(self.rect.x, self.map_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, self.map_height - self.rect.height))

    def get_viewport(self):
        """Retorna a área visível da câmera no mundo"""
        return self.rect.copy()
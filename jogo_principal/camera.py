# camera.py
import pygame

class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.map_width = map_width
        self.map_height = map_height

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    def apply(self, pos_or_rect):
        """Aplica transformação da câmera a uma posição ou retângulo"""
        if isinstance(pos_or_rect, pygame.Rect):
            # Para retângulos: retorna novo rect com offset da câmera
            return pygame.Rect(
                pos_or_rect.x - self.rect.x,
                pos_or_rect.y - self.rect.y,
                pos_or_rect.width,
                pos_or_rect.height
            )
        else:
            # Para posições: retorna tupla (x, y)
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

        # Mantém a câmera dentro dos limites do mapa
        self.rect.x = max(0, min(self.rect.x, self.map_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, self.map_height - self.rect.height))

    def get_viewport(self):
        """Retorna a área visível da câmera no mundo"""
        return self.rect.copy()
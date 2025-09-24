# tiled_loader.py
import pygame
import json

class TiledMap:
    def __init__(self, map_file):
        with open(map_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.tilewidth = self.data["tilewidth"]
        self.tileheight = self.data["tileheight"]
        self.width = self.data["width"]
        self.height = self.data["height"]

        # Carregar todos os tilesets
        self.tilesets = []
        self.tile_images = {}
        for ts in self.data["tilesets"]:
            image = pygame.image.load(ts["image"]).convert_alpha()
            columns = ts["columns"]
            tilecount = ts["tilecount"]
            firstgid = ts["firstgid"]

            for i in range(tilecount):
                x = (i % columns) * self.tilewidth
                y = (i // columns) * self.tileheight
                rect = pygame.Rect(x, y, self.tilewidth, self.tileheight)
                tile = image.subsurface(rect)
                self.tile_images[firstgid + i] = tile

        self.layers = [layer for layer in self.data["layers"] if layer["type"] == "tilelayer"]

    def draw(self, surface, camera):
        """Desenha apenas os tiles visíveis pela câmera"""
        for layer in self.layers:
            for row in range(layer["height"]):
                for col in range(layer["width"]):
                    tile_id = layer["data"][row * layer["width"] + col]
                    if tile_id != 0:
                        tile = self.tile_images[tile_id]
                        x = col * self.tilewidth
                        y = row * self.tileheight
                        tile_rect = pygame.Rect(x, y, self.tilewidth, self.tileheight)

                        # Só desenha se o tile estiver na área da câmera
                        if camera.rect.colliderect(tile_rect):
                            screen_pos = camera.apply((x, y))
                            surface.blit(tile, screen_pos)


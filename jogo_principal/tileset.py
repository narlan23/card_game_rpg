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
            # Garante que o caminho da imagem esteja correto (pode precisar de ajuste dependendo de onde está assets)
            image_path = ts["image"]
            try:
                # Se a imagem não for encontrada, tentamos um caminho relativo mais genérico
                image = pygame.image.load(image_path).convert_alpha()
            except pygame.error:
                 # Esta linha pode ser útil se o TiledMap salva o caminho incorreto
                 print(f"Aviso: Não foi possível carregar a imagem do tileset: {image_path}. Verifique o caminho.")
                 continue 

            columns = ts["columns"]
            tilecount = ts["tilecount"]
            firstgid = ts["firstgid"]

            for i in range(tilecount):
                x = (i % columns) * self.tilewidth
                y = (i // columns) * self.tileheight
                rect = pygame.Rect(x, y, self.tilewidth, self.tileheight)
                tile = image.subsurface(rect)
                self.tile_images[firstgid + i] = tile

        # MODIFICAÇÃO: Armazenar as camadas em um dicionário para fácil acesso por nome.
        self.layers_dict = {}
        for layer in self.data["layers"]:
            self.layers_dict[layer["name"]] = layer
        
        # Filtra as camadas de tiles para o método draw (Mantido para compatibilidade)
        self.layers = [layer for layer in self.data["layers"] if layer["type"] == "tilelayer"]

    def draw(self, surface, camera):
        """Desenha apenas os tiles visíveis pela câmera"""
        for layer in self.layers:
            for row in range(layer["height"]):
                for col in range(layer["width"]):
                    tile_id = layer["data"][row * layer["width"] + col]
                    if tile_id != 0:
                        tile = self.tile_images.get(tile_id)
                        if tile: # Verifica se o tile_id realmente existe no cache
                            x = col * self.tilewidth
                            y = row * self.tileheight
                            tile_rect = pygame.Rect(x, y, self.tilewidth, self.tileheight)

                            # Só desenha se o tile estiver na área da câmera
                            if camera.rect.colliderect(tile_rect):
                                screen_pos = camera.apply((x, y))
                                surface.blit(tile, screen_pos)

    # NOVO MÉTODO ESSENCIAL PARA COLISÃO
    def get_collision_rects(self, layer_name):
        """
        Retorna uma lista de pygame.Rect para todos os tiles não vazios (ID != 0)
        em uma camada de tiles específica (ex: 'collision').
        """
        collision_rects = []
        
        # 1. Encontrar a camada pelo nome
        layer = self.layers_dict.get(layer_name)
        
        if not layer:
            print(f"ERRO: Camada de colisão '{layer_name}' não encontrada no mapa.")
            return []
        
        # Garante que é uma camada de tiles (Tile Layer)
        if layer["type"] != "tilelayer":
            print(f"ERRO: A camada '{layer_name}' não é do tipo 'tilelayer'.")
            return []

        # 2. Iterar sobre os dados da camada para criar os retângulos
        layer_width = layer["width"]
        layer_height = layer["height"]
        tile_data = layer["data"]

        for row in range(layer_height):
            for col in range(layer_width):
                # O Tiled armazena os dados em uma lista 1D
                tile_index = row * layer_width + col
                tile_id = tile_data[tile_index]
                
                # O ID 0 representa um tile vazio (sem colisão)
                if tile_id != 0:
                    x = col * self.tilewidth
                    y = row * self.tileheight
                    
                    # Cria o Rect de colisão com as dimensões do tile
                    rect = pygame.Rect(x, y, self.tilewidth, self.tileheight)
                    collision_rects.append(rect)
                    
        return collision_rects
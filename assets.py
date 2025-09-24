import pygame

class Assets:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}

    def load_image(self, key, path):
        self.images[key] = pygame.image.load(path).convert_alpha()

    def get_image(self, key):
        return self.images.get(key)

    def load_sound(self, key, path):
        self.sounds[key] = pygame.mixer.Sound(path)

    def get_sound(self, key):
        return self.sounds.get(key)

    def load_font(self, key, path, size):
        self.fonts[key] = pygame.font.Font(path, size)

    def get_font(self, key):
        return self.fonts.get(key)

import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, health, attack_value, image_path, position):
        super().__init__()
        self.name = name
        self.max_health = health
        self.health = health
        self.attack_value = attack_value
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (150, 150))
        self.rect = self.image.get_rect(center=position)
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return True  # Inimigo derrotado
        return False
        
    def choose_action(self):
        # Lógica simples de IA para o inimigo
        return "attack"  # Por enquanto, sempre ataca
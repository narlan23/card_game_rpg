import pygame



class DamageAnimation:
    def __init__(self, target, amount, is_player=False, screen_width=800, hand_y=400):
        self.target = target
        self.amount = amount
        self.is_player = is_player
        self.screen_width = screen_width
        self.hand_y = hand_y
        
        if is_player:
            self.position = (screen_width // 2, hand_y - 100)
        else:
            self.position = (target.rect.centerx, target.rect.top - 30)
            
        self.lifetime = 60  # frames
        self.current_frame = 0
        self.is_finished = False
        
        
    def update(self):
        self.current_frame += 1
        self.position = (self.position[0], self.position[1] - 1)  # Move para cima
        if self.current_frame >= self.lifetime:
            self.is_finished = True
            
    def draw(self, surface):
        alpha = 255 * (1 - self.current_frame / self.lifetime)  # Fade out
        font = pygame.font.SysFont(None, 36)
        color = (255, 0, 0) if self.amount > 0 else (0, 255, 0)
        text = font.render(str(self.amount), True, color)
        text.set_alpha(alpha)
        surface.blit(text, (self.position[0] - text.get_width()//2, self.position[1]))
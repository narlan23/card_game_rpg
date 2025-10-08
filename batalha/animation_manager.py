import pygame

class AnimationManager:
    """Gerencia todas as animações da batalha (dano, cura, status, etc.)."""

    def __init__(self, battle_manager):
        self.battle_manager = battle_manager
        self.animations = []

    def update(self, dt: float):
        """Atualiza todas as animações ativas."""
        for anim in self.animations[:]:
            anim.update(dt)
            if anim.is_finished:
                self.animations.remove(anim)

    def spawn_damage_animation(self, target, damage, is_player=False):
        """Cria uma animação de dano."""
        from .animation import DamageAnimation
        animation = DamageAnimation(
            target=target,
            amount=damage,
            is_player=is_player,
            screen_width=self.battle_manager.game.screen_width,
            hand_y=self.battle_manager.hand_renderer.hand_y
        )
        self.animations.append(animation)

    def spawn_status_animation(self, target, status_name):
        """Cria uma animação de status (texto flutuante dourado)."""
        from .animation import TextAnimation
        animation = TextAnimation(
            target=target,
            text=status_name.upper(),
            color=(255, 215, 0),  # dourado
            screen_width=self.battle_manager.game.screen_width,
            hand_y=self.battle_manager.hand_renderer.hand_y
        )
        self.animations.append(animation)

    def spawn_heal_animation(self, target, heal_amount):
        """Cria uma animação de cura (texto verde flutuante)."""
        from .animation import TextAnimation
        animation = TextAnimation(
            target=target,
            text=f"+{heal_amount}",
            color=(0, 255, 0),  # verde = cura
            screen_width=self.battle_manager.game.screen_width,
            hand_y=self.battle_manager.hand_renderer.hand_y
        )
        self.animations.append(animation)

    def has_active_animations(self) -> bool:
        """Retorna True se houver animações em andamento."""
        return any(not anim.is_finished for anim in self.animations)

    def draw(self, surface: pygame.Surface):
        """Desenha todas as animações na tela."""
        for anim in self.animations:
            anim.draw(surface)

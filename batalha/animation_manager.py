class AnimationManager:
    def __init__(self, battle_manager):
        self.battle_manager = battle_manager
        self.animations = []

    def update(self):
        """Atualiza todas as animações."""
        for anim in self.animations[:]:
            anim.update()
            if anim.is_finished:
                self.animations.remove(anim)

    def spawn_damage_animation(self, target, damage, is_player=False):
        """Cria animação de dano."""
        from .animation import DamageAnimation
        self.animations.append(DamageAnimation(
            target, damage,
            is_player=is_player,
            screen_width=self.battle_manager.game.screen_width,
            hand_y=self.battle_manager.hand_renderer.hand_y
        ))

    def spawn_status_animation(self, target, status_name):
        """Cria animação para indicar aplicação de status."""
        from .animation import TextAnimation
        self.animations.append(TextAnimation(
            target, status_name.upper(),
            color=(255, 215, 0),
            screen_width=self.battle_manager.game.screen_width,
            hand_y=self.battle_manager.hand_renderer.hand_y
        ))

    def has_active_animations(self):
        """Verifica se há animações em andamento."""
        return any(not anim.is_finished for anim in self.animations)

    def draw(self, surface):
        """Desenha todas as animações."""
        for anim in self.animations:
            anim.draw(surface)
import pygame
from .battle_state import BattleState
from .enemy import Enemy
from characters.hand_renderer import HandRenderer
from batalha.animation_manager import AnimationManager
from batalha.status_manager import StatusManager
from batalha.turn_manager import TurnManager
from batalha.render_manager import RenderManager
from batalha.input_manager import InputManager


class BattleManager:
    def __init__(self, game):
        self.game = game
        self.font = game.assets.get_font("default")
        self.state = BattleState.PLAYER_TURN
        
        # Módulos especializados
        self.animation_manager = AnimationManager(self)
        self.status_manager = StatusManager(self)
        self.turn_manager = TurnManager(self)
        self.render_manager = RenderManager(self)
        self.input_manager = InputManager(self)
        
        # Grupos de entidades
        self.enemies = pygame.sprite.Group()
        
        # Renderizador da mão
        self.hand_renderer = HandRenderer(
            game.player,
            screen_width=game.screen_width - 200,
            hand_y=game.screen_height - 150,
            align="center"
        )

    def setup_battle(self, enemies_data):
        """Inicializa os inimigos e reseta estado do jogador."""
        positions = self._enemy_positions()

        for i, data in enumerate(enemies_data[:len(positions)]):
            enemy = Enemy(
                data["name"], data["health"], data["attack"],
                data["image"], positions[i],data["x_tam"],data["y_tam"]
            )
            self.enemies.add(enemy)

        self.turn_manager.reset_player_turn()
        self.turn_manager.enemy_turn_started = False

    def _enemy_positions(self):
        """Retorna posições pré-definidas para até 3 inimigos."""
        return [
            (self.game.screen_width * (i + 1) // 4, self.game.screen_height // 4)
            for i in range(3)
        ]

    def handle_click(self, pos):
        """Delega o tratamento de clique para o input manager."""
        return self.input_manager.handle_click(pos)

    def update(self, dt=18):
        """Atualiza o estado da batalha."""
        self.animation_manager.update()

        self.enemies.update()
        
        if self.state in [BattleState.VICTORY, BattleState.DEFEAT]:
            return

        self.turn_manager.update(dt)

    def apply_damage_to_enemy(self, enemy, damage):
        """Aplica dano ao inimigo e verifica condições de fim de batalha."""
        enemy.take_damage(damage)
        self.animation_manager.spawn_damage_animation(enemy, damage, is_player=False)
        self.check_battle_end_conditions()
        

    def draw(self, surface):
        """Delega a renderização para o render manager."""
        self.render_manager.draw(surface)

    def check_battle_end_conditions(self):
        """Verifica condições de fim de batalha."""
        if all(enemy.health <= 0 for enemy in self.enemies):
            self.state = BattleState.VICTORY
            return True
        if self.game.player.health <= 0:
            self.state = BattleState.DEFEAT
            return True
        return False
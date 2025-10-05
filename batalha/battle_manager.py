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

        # Grupo de inimigos
        self.enemies = pygame.sprite.Group()

        # Renderizador da mão do jogador
        self.hand_renderer = HandRenderer(
            game.player,
            screen_width=game.screen_width - 200,
            hand_y=game.screen_height - 150,
            align="center"
        )

    # ------------------------------------------------------------
    # Inicialização da batalha
    # ------------------------------------------------------------
    def setup_battle(self, enemies_data):
        """Inicializa inimigos e reseta estado do turno."""
        positions = self._enemy_positions()

        # Cria inimigos com base nos dados fornecidos
        for i, data in enumerate(enemies_data[:len(positions)]):
            enemy = Enemy(
                name=data.get("name", "Inimigo"),
                health=data.get("health", 10),
                attack_value=data.get("attack", 2),
                image_path=data.get("image", "assets/enemy.png"),
                position=positions[i],
                x_tam=data.get("x_tam", 64),
                y_tam=data.get("y_tam", 64)
            )
            self.enemies.add(enemy)

        # Reseta o turno do jogador
        self.turn_manager.reset_player_turn()
        self.turn_manager.enemy_turn_started = False

    def _enemy_positions(self):
        """Posições padrão para até 3 inimigos."""
        width, height = self.game.screen_width, self.game.screen_height
        return [
            (width * (i + 1) // 4, height // 4)
            for i in range(3)
        ]

    # ------------------------------------------------------------
    # Entrada e atualização
    # ------------------------------------------------------------
    def handle_click(self, pos):
        """Delega o clique para o InputManager."""
        return self.input_manager.handle_click(pos)

    def update(self, dt=12):
        """Atualiza animações, inimigos e turnos."""
        self.animation_manager.update(dt)
        self.enemies.update(dt)

        # Evita atualização desnecessária após o fim da batalha
        if self.state in (BattleState.VICTORY, BattleState.DEFEAT):
            return

        self.turn_manager.update(dt)

    # ------------------------------------------------------------
    # Lógica de dano e fim de batalha
    # ------------------------------------------------------------
    def apply_damage_to_enemy(self, enemy, damage):
        """Aplica dano, gera animação e checa condições de vitória."""
        if not enemy or enemy.health <= 0:
            return  # evita atacar inimigos mortos

        enemy.take_damage(damage)
        self.animation_manager.spawn_damage_animation(enemy, damage, is_player=False)
        self.check_battle_end_conditions()

    def check_battle_end_conditions(self):
        """Verifica se todos os inimigos morreram ou o jogador perdeu."""
        if all(enemy.health <= 0 for enemy in self.enemies):
            self.state = BattleState.VICTORY
            return True
        if self.game.player.health <= 0:
            self.state = BattleState.DEFEAT
            return True
        return False

    # ------------------------------------------------------------
    # Renderização
    # ------------------------------------------------------------
    def draw(self, surface):
        """Delega renderização ao RenderManager."""
        self.render_manager.draw(surface)

import pygame
from batalha.battle_state import BattleState
from batalha.enemy import Enemy
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
        
        # ========================================================================
        # CORREÇÃO PRINCIPAL ESTÁ AQUI
        # A chamada ao construtor do HandRenderer foi atualizada.
        # ========================================================================
        self.hand_renderer = HandRenderer(
            game=self.game,
            player=self.game.player,
            hand_y=self.game.screen_height - 150,
            align="center"
        )

    def setup_battle(self, enemies_data):
        """Inicializa os inimigos e reseta o estado do jogador."""
        positions = self._enemy_positions()

        for i, data in enumerate(enemies_data[:len(positions)]):
            # Tenta carregar a imagem do inimigo individualmente
            self.game.assets.load_image(data["name"], data["image"])
            enemy_image = self.game.assets.get_image(data["name"])
            
            if enemy_image:
                enemy = Enemy(
                    data["name"], data["health"], data["attack"],
                    enemy_image, positions[i]
                )
                self.enemies.add(enemy)
            else:
                print(f"AVISO: Imagem para o inimigo '{data['name']}' não encontrada. Inimigo não foi criado.")

        self.turn_manager.reset_player_turn()
        self.turn_manager.enemy_turn_started = False

    def _enemy_positions(self):
        """Retorna posições pré-definidas para até 3 inimigos."""
        num_enemies = len(self.enemies.sprites())
        screen_width = self.game.screen_width
        screen_height = self.game.screen_height
        
        # Posições dinâmicas baseadas no número de inimigos
        return [
            ((screen_width * (i + 1)) / (num_enemies + 1), screen_height // 3)
            for i in range(num_enemies)
        ]

    def handle_click(self, pos):
        """Delega o tratamento de clique para o input manager."""
        return self.input_manager.handle_click(pos)

    def update(self, dt=16): # dt pode ser passado pelo loop principal para consistência
        """Atualiza o estado da batalha."""
        self.animation_manager.update()
        
        if self.state in [BattleState.VICTORY, BattleState.DEFEAT]:
            return

        self.turn_manager.update(dt)

    def draw(self, surface):
        """Delega a renderização para o render manager."""
        self.render_manager.draw(surface)

    def check_battle_end_conditions(self):
        """Verifica condições de fim de batalha."""
        if not self.enemies: # Se não houver inimigos
            self.state = BattleState.VICTORY
            return True
        if all(enemy.health <= 0 for enemy in self.enemies):
            self.state = BattleState.VICTORY
            return True
        if self.game.player.health <= 0:
            self.state = BattleState.DEFEAT
            return True
        return False
from batalha.battle_state import BattleState

class TurnManager:
    def __init__(self, battle_manager):
        self.battle_manager = battle_manager
        self.enemy_actions_queue = []
        self.enemy_attack_timer = 0
        self.enemy_attack_interval = 600
        self.enemy_turn_started = False

    def reset_player_turn(self):
        """Prepara o turno do jogador."""
        self.battle_manager.game.player.reset_energy()
        self.battle_manager.game.player.reset_selection()
        self.battle_manager.hand_renderer.set_alignment("center", 
            self.battle_manager.game.screen_height - 150)

    def end_player_turn(self):
        """Finaliza o turno do jogador."""
        if self.battle_manager.state == BattleState.PLAYER_TURN:
            self.battle_manager.state = BattleState.ENEMY_TURN
            self.enemy_turn_started = False

    def start_enemy_turn(self):
        """Inicia o turno dos inimigos."""
        if self.enemy_turn_started:
            return
            
        self.enemy_turn_started = True
        self.battle_manager.status_manager.apply_status_effects()
        self.battle_manager.game.player.tick_status()

        if self.battle_manager.check_battle_end_conditions():
            return

        # Coleta ações dos inimigos
        self.enemy_actions_queue = [
            (enemy, enemy.attack_value)
            for enemy in self.battle_manager.enemies 
            if enemy.health > 0 and enemy.choose_action() == "attack"
        ]

        if not self.enemy_actions_queue:
            self.end_enemy_turn()
        else:
            self.enemy_attack_timer = self.enemy_attack_interval

    def end_enemy_turn(self):
        """Finaliza o turno dos inimigos."""
        self.battle_manager.state = BattleState.PLAYER_TURN
        self.reset_player_turn()
        self.enemy_turn_started = False

    def update(self, dt):
        """Atualiza a lógica do turno."""
        if self.battle_manager.state == BattleState.ENEMY_TURN:
            if not self.enemy_turn_started:
                self.start_enemy_turn()
            self._process_enemy_actions(dt)

    def _process_enemy_actions(self, dt):
        """Processa as ações dos inimigos."""
        if not self.enemy_actions_queue:
            return

        self.enemy_attack_timer -= dt
        if self.enemy_attack_timer <= 0:
            enemy, base_damage = self.enemy_actions_queue.pop(0)
            
            final_damage = self.battle_manager.status_manager.calculate_enemy_damage(base_damage, enemy)
            self.battle_manager.game.player.take_damage(final_damage)
            self.battle_manager.animation_manager.spawn_damage_animation(
                self.battle_manager.game.player, final_damage, is_player=True)

            if self.battle_manager.check_battle_end_conditions():
                return

            self.enemy_attack_timer = self.enemy_attack_interval if self.enemy_actions_queue else 0
            if not self.enemy_actions_queue:
                self.end_enemy_turn()
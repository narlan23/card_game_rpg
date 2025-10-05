from batalha.battle_state import BattleState

class TurnManager:
    def __init__(self, battle_manager):
        self.battle_manager = battle_manager
        self.enemy_actions_queue = []
        self.enemy_attack_timer = 0
        self.enemy_attack_interval = 600  # ms entre ataques inimigos
        self.enemy_turn_started = False

    # ------------------------------------------------------------
    # Turno do jogador
    # ------------------------------------------------------------
    def reset_player_turn(self):
        """Prepara o turno do jogador."""
        player = self.battle_manager.game.player
        player.reset_energy()
        player.reset_selection()

        # Reposiciona a mão do jogador no centro
        self.battle_manager.hand_renderer.set_alignment(
            "center",
            self.battle_manager.game.screen_height - 150
        )

    def end_player_turn(self):
        """Finaliza o turno do jogador e inicia o dos inimigos."""
        if self.battle_manager.state == BattleState.PLAYER_TURN:
            self.battle_manager.state = BattleState.ENEMY_TURN
            self.enemy_turn_started = False

    # ------------------------------------------------------------
    # Turno dos inimigos
    # ------------------------------------------------------------
    def start_enemy_turn(self):
        """Inicia o turno dos inimigos (apenas uma vez por ciclo)."""
        if self.enemy_turn_started:
            return  # evita reentrância

        self.enemy_turn_started = True

        # Aplica status nos inimigos e jogador
        self.battle_manager.status_manager.apply_status_effects()
        self.battle_manager.game.player.tick_status()

        if self.battle_manager.check_battle_end_conditions():
            return  # encerra se alguém morreu durante efeitos

        # Coleta ações dos inimigos vivos
        self.enemy_actions_queue = [
            (enemy, enemy.attack_value)
            for enemy in self.battle_manager.enemies
            if enemy.health > 0 and enemy.choose_action() == "attack"
        ]

        # Se não houver ações, finaliza o turno imediatamente
        if not self.enemy_actions_queue:
            self.end_enemy_turn()
            return

        self.enemy_attack_timer = self.enemy_attack_interval

    def end_enemy_turn(self):
        """Finaliza o turno dos inimigos e retorna ao jogador."""
        if self.battle_manager.state == BattleState.ENEMY_TURN:
            self.battle_manager.state = BattleState.PLAYER_TURN
            self.enemy_turn_started = False
            self.reset_player_turn()
            self.enemy_actions_queue.clear()  # limpa fila antiga

    # ------------------------------------------------------------
    # Atualização por frame
    # ------------------------------------------------------------
    def update(self, dt):
        """Atualiza lógica de turno (chamado a cada frame)."""
        if self.battle_manager.state == BattleState.ENEMY_TURN:
            if not self.enemy_turn_started:
                self.start_enemy_turn()
            else:
                self._process_enemy_actions(dt)

    # ------------------------------------------------------------
    # Execução de ataques inimigos
    # ------------------------------------------------------------
    def _process_enemy_actions(self, dt):
        """Processa ações pendentes dos inimigos com intervalo controlado."""
        if not self.enemy_actions_queue:
            return

        self.enemy_attack_timer -= dt
        if self.enemy_attack_timer > 0:
            return  # ainda aguardando próximo ataque

        # Executa próxima ação da fila
        enemy, base_damage = self.enemy_actions_queue.pop(0)

        if enemy.health <= 0:
            # ignora inimigos mortos
            if not self.enemy_actions_queue:
                self.end_enemy_turn()
            return

        final_damage = self.battle_manager.status_manager.calculate_enemy_damage(base_damage, enemy)
        self.battle_manager.game.player.take_damage(final_damage)

        # Exibe animação de dano
        self.battle_manager.animation_manager.spawn_damage_animation(
            self.battle_manager.game.player, final_damage, is_player=True
        )

        # Checa fim da batalha após cada ataque
        if self.battle_manager.check_battle_end_conditions():
            return

        # Define tempo até próximo ataque
        self.enemy_attack_timer = self.enemy_attack_interval if self.enemy_actions_queue else 0

        # Se acabou a fila, encerra o turno inimigo
        if not self.enemy_actions_queue:
            self.end_enemy_turn()

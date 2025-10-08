from batalha.battle_state import BattleState

class TurnManager:
    """Gerencia os turnos do jogador e dos inimigos durante a batalha."""

    def __init__(self, battle_manager):
        self.battle_manager = battle_manager
        self.enemy_actions_queue = []
        self.enemy_attack_timer = 0
        self.enemy_attack_interval = 600  # ms entre ações dos inimigos
        self.enemy_turn_started = False

    # ===============================================================
    # 🔹 Turno do jogador
    # ===============================================================
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

    # ===============================================================
    # 🔹 Turno dos inimigos
    # ===============================================================
    def start_enemy_turn(self):
        """Inicia o turno dos inimigos (chamado uma única vez por ciclo)."""
        if self.enemy_turn_started:
            return  # evita reentrância
        self.enemy_turn_started = True

        # Aplica status e efeitos contínuos
        self.battle_manager.status_manager.apply_status_effects()
        self.battle_manager.game.player.tick_status()

        if self.battle_manager.check_battle_end_conditions():
            return  # alguém morreu durante status

        # Cria fila de ações dos inimigos
        self.enemy_actions_queue = []

        for enemy in self.battle_manager.enemies:
            if not enemy.is_alive():
                continue

            action = enemy.choose_action()

            # Ações possíveis conforme IA
            if action == "attack" or action == "power_attack":
                self.enemy_actions_queue.append(("attack", enemy))
            elif action == "heal":
                self.enemy_actions_queue.append(("heal", enemy))
            elif action == "buff":
                self.enemy_actions_queue.append(("buff", enemy))

        # Se não houver ações, encerra turno
        if not self.enemy_actions_queue:
            self.end_enemy_turn()
            return

        # Reinicia o timer de ataque
        self.enemy_attack_timer = self.enemy_attack_interval

    def end_enemy_turn(self):
        """Finaliza o turno dos inimigos e retorna o controle ao jogador."""
        if self.battle_manager.state == BattleState.ENEMY_TURN:
            self.battle_manager.state = BattleState.PLAYER_TURN
            self.enemy_turn_started = False
            self.enemy_actions_queue.clear()
            self.reset_player_turn()

    # ===============================================================
    # 🔹 Atualização por frame
    # ===============================================================
    def update(self, dt):
        """Atualiza lógica de turno (chamado a cada frame)."""
        if self.battle_manager.state == BattleState.ENEMY_TURN:
            if not self.enemy_turn_started:
                self.start_enemy_turn()
            else:
                self._process_enemy_actions(dt)

    # ===============================================================
    # 🔹 Execução das ações inimigas
    # ===============================================================
    def _process_enemy_actions(self, dt):
        """Processa a fila de ações dos inimigos com intervalo entre elas."""
        if not self.enemy_actions_queue:
            return

        # Converte dt para ms se necessário
        self.enemy_attack_timer -= dt * 1000
        if self.enemy_attack_timer > 0:
            return  # aguardando o intervalo

        action_type, enemy = self.enemy_actions_queue.pop(0)

        if not enemy.is_alive():
            if not self.enemy_actions_queue:
                self.end_enemy_turn()
            return

        if action_type == "attack":
            damage = enemy.calculate_attack()
            final_damage = self.battle_manager.status_manager.calculate_enemy_damage(damage, enemy)
            self.battle_manager.game.player.take_damage(final_damage)

            self.battle_manager.animation_manager.spawn_damage_animation(
                self.battle_manager.game.player, final_damage, is_player=True
            )

        elif action_type == "heal":
            heal_amount = int(enemy.max_health * 0.15)
            enemy.heal(heal_amount)
            self.battle_manager.animation_manager.spawn_heal_animation(enemy, heal_amount)

        elif action_type == "buff":
            enemy.add_status("fortalecido", power=2, duration=3)
            self.battle_manager.animation_manager.spawn_buff_animation(enemy, "fortalecido")

        # Checa se a batalha acabou após a ação
        if self.battle_manager.check_battle_end_conditions():
            return

        # Define tempo até próxima ação
        self.enemy_attack_timer = self.enemy_attack_interval if self.enemy_actions_queue else 0

        # Se acabou a fila, encerra o turno
        if not self.enemy_actions_queue:
            self.end_enemy_turn()

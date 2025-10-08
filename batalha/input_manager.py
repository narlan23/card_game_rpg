import pygame
from batalha.battle_state import BattleState
from characters.cards import CardType
from batalha.ui import END_TURN_BUTTON


class InputManager:
    """Gerencia toda a entrada de cliques e interações durante a batalha."""

    def __init__(self, battle_manager):
        self.battle_manager = battle_manager
        self.last_card_clicked = None
        self.last_click_time = 0
        self.double_click_threshold = 300  # tempo em ms
        self._debug_enabled = True  # alternador global de logs

    # ---------------------------------------------------------
    # 🧩 Utilitários de debug
    # ---------------------------------------------------------
    def _debug_print(self, message: str):
        if self._debug_enabled:
            print(f"[DEBUG] {message}")

    def enable_debug(self):
        self._debug_enabled = True

    def disable_debug(self):
        self._debug_enabled = False

    # ---------------------------------------------------------
    # 🖱️ Entrada principal
    # ---------------------------------------------------------
    def handle_click(self, pos: tuple[int, int]) -> bool:
        """Gerencia um clique do mouse em posição (x, y)."""
        self._debug_print(f"Clique detectado em {pos}, turno atual: {self.battle_manager.state}")

        if not self._can_process_click():
            return False

        # Ordem de prioridade dos cliques
        click_handlers = [
            self._handle_end_turn_click,
            self._handle_card_click,
            self._handle_enemy_click,
            self._handle_player_click
        ]

        for handler in click_handlers:
            if handler(pos):
                return True

        self._debug_print("Clique não atingiu nenhum alvo válido.")
        return False

    def _can_process_click(self) -> bool:
        """Verifica se o clique pode ser processado."""
        if self.battle_manager.state != BattleState.PLAYER_TURN:
            self._debug_print("Ignorado: não é turno do jogador.")
            return False

        if self.battle_manager.animation_manager.has_active_animations():
            self._debug_print("Ignorado: animação em execução.")
            return False

        return True

    # ---------------------------------------------------------
    # 🔘 Clique no botão "Fim de turno"
    # ---------------------------------------------------------
    def _handle_end_turn_click(self, pos):
        if END_TURN_BUTTON.collidepoint(pos):
            self._debug_print("Botão de fim de turno clicado.")
            self.battle_manager.turn_manager.end_player_turn()
            return True
        return False

    # ---------------------------------------------------------
    # 🃏 Clique em carta
    # ---------------------------------------------------------
    def _handle_card_click(self, pos):
        """Detecta clique em carta e executa ação correspondente."""
        hand_renderer = self.battle_manager.hand_renderer
        for i, card_pos in enumerate(hand_renderer.card_positions):
            rect = pygame.Rect(
                card_pos,
                (hand_renderer.CARD_WIDTH, hand_renderer.CARD_HEIGHT)
            )
            if rect.collidepoint(pos):
                self._debug_print(f"Carta {i} clicada na posição {card_pos}")
                return self._process_card_click(i)
        return False

    def _process_card_click(self, card_index: int) -> bool:
        """Processa o clique em uma carta específica."""
        player = self.battle_manager.game.player
        if not (0 <= card_index < len(player.hand)):
            self._debug_print(f"Índice de carta inválido: {card_index}")
            return False

        card = player.hand[card_index]
        self._log_card_details(card_index, card)
        player.select_card_by_index(card_index)

        card_handlers = {
            CardType.ATAQUE.value: self._handle_attack_card,
            CardType.DEFESA.value: self._handle_defense_card_click,
            CardType.BUFF.value: self._handle_buff_card,
            CardType.DEBUFF.value: self._handle_buff_card
        }

        handler = card_handlers.get(card.card_type)
        if handler:
            return handler(card_index)

        self._debug_print(f"Tipo de carta desconhecido: {card.card_type}")
        return False

    # ---------------------------------------------------------
    # ⚔️ Cartas de ataque
    # ---------------------------------------------------------
    def _handle_attack_card(self, card_index):
        self._debug_print("Carta de ATAQUE selecionada. Aguardando clique em inimigo.")
        return True

    # ---------------------------------------------------------
    # 🛡️ Cartas de defesa
    # ---------------------------------------------------------
    def _handle_defense_card_click(self, card_index):
        """Verifica se houve duplo clique para ativar carta de defesa."""
        now = pygame.time.get_ticks()
        if (
            self.last_card_clicked == card_index and
            (now - self.last_click_time) < self.double_click_threshold
        ):
            card = self.battle_manager.game.player.hand[card_index]
            self._debug_print("Duplo clique em carta de DEFESA. Aplicando efeito.")
            self._resolve_defense_card(card)
            return True

        # Marca o primeiro clique
        self.last_card_clicked = card_index
        self.last_click_time = now
        self._debug_print("Primeiro clique em carta de DEFESA.")
        return True

    # ---------------------------------------------------------
    # ✨ Buff / Debuff
    # ---------------------------------------------------------
    def _handle_buff_card(self, card_index):
        self._debug_print("Carta BUFF/DEBUFF selecionada. Aguardando clique em alvo.")
        return True

    # ---------------------------------------------------------
    # 🎯 Clique em inimigo
    # ---------------------------------------------------------
    def _handle_enemy_click(self, pos):
        selected_cards = self.battle_manager.game.player.get_selected_cards()
        if not selected_cards:
            return False

        for enemy in self.battle_manager.enemies:
            if hasattr(enemy, "rect") and enemy.rect.collidepoint(pos):
                return self._process_enemy_click(enemy)
        return False

    def _process_enemy_click(self, enemy):
        self._debug_print(f"Inimigo {getattr(enemy, 'name', '???')} clicado. HP={getattr(enemy, 'health', '?')}")
        if getattr(enemy, "health", 0) <= 0:
            self._debug_print("Inimigo morto. Cancelando ataque.")
            self._clear_selection()
            return False

        self._resolve_card_effects(enemy)
        self._clear_selection()
        return True

    # ---------------------------------------------------------
    # 🧍 Clique no jogador
    # ---------------------------------------------------------
    def _handle_player_click(self, pos):
        selected_cards = self.battle_manager.game.player.get_selected_cards()
        if not selected_cards:
            return False

        player = self.battle_manager.game.player
        if hasattr(player, "rect") and player.rect.collidepoint(pos):
            self._debug_print("Player clicado. Aplicando efeitos.")
            self._resolve_card_effects(player)
            self._clear_selection()
            return True

        return False

    # ---------------------------------------------------------
    # 🪄 Aplicação de efeitos
    # ---------------------------------------------------------
    def _resolve_card_effects(self, target):
        """Aplica os efeitos das cartas selecionadas ao alvo."""
        player = self.battle_manager.game.player
        if hasattr(target, "health") and target.health <= 0:
            self._debug_print("Alvo morto — efeito cancelado.")
            return

        for card in player.get_selected_cards():
            if not self._can_use_card(card, target):
                continue
            self._debug_print(f"Aplicando {card.card_type} em {getattr(target, 'name', 'Player')}")
            self._apply_card_effect(card, target)
            card.use()

    def _can_use_card(self, card, target):
        """Verifica se a carta pode ser usada neste alvo."""
        player = self.battle_manager.game.player
        if card.card_type == CardType.ATAQUE and target == player:
            self._debug_print("Ataque não pode ser usado no próprio jogador.")
            return False
        if card.card_type == CardType.DEFESA and target != player:
            self._debug_print("Defesa só pode ser usada no jogador.")
            return False
        return True

    # ---------------------------------------------------------
    # 💥 Aplicação de tipos específicos de efeito
    # ---------------------------------------------------------
    def _apply_card_effect(self, card, target):
        handlers = {
            CardType.ATAQUE: self._apply_attack_effect,
            CardType.DEFESA: self._apply_defense_effect,
            CardType.BUFF: self._apply_status_effect,
            CardType.DEBUFF: self._apply_status_effect
        }
        handler = handlers.get(card.card_type)
        if handler:
            handler(card, target)

    def _apply_attack_effect(self, card, target):
        if target == self.battle_manager.game.player:
            return

        base_damage = card.value
        final_damage = self.battle_manager.status_manager.calculate_player_damage(base_damage, card)
        self._debug_print(f"Dano final calculado: {final_damage}")
        self.battle_manager.apply_damage_to_enemy(target, final_damage)
        self.battle_manager.animation_manager.spawn_damage_animation(target, final_damage)

    def _apply_defense_effect(self, card, target):
        if target == self.battle_manager.game.player:
            self._resolve_defense_card(card)

    def _apply_status_effect(self, card, target):
        if hasattr(card, "status_effect") and card.status_effect:
            effect_type = "BUFF" if card.card_type == CardType.BUFF else "DEBUFF"
            self._debug_print(f"Aplicando {effect_type} {card.status_effect}")
            self.battle_manager.status_manager.apply_status_to_target(
                target, card.status_effect, **getattr(card, "status_kwargs", {})
            )

    def _resolve_defense_card(self, card):
        """Aplica o efeito de defesa diretamente no jogador."""
        player = self.battle_manager.game.player
        player.shield += card.value
        self._debug_print(f"DEFESA aplicada. Novo escudo: {player.shield}")

    # ---------------------------------------------------------
    # 🧹 Utilidades auxiliares
    # ---------------------------------------------------------
    def _clear_selection(self):
        """Limpa a seleção de cartas e atualiza o layout da mão."""
        player = self.battle_manager.game.player
        player.reset_selection()
        self.battle_manager.hand_renderer.update_card_positions()

    def _log_card_details(self, card_index, card):
        if not self._debug_enabled:
            return
        print("\n[DEBUG] ===== Carta Clicada =====")
        print(f"Índice: {card_index}")
        print(card)
        print(f"Estado: {getattr(card, 'state', 'N/A')}")
        print(f"Efeito: {getattr(card, 'status_effect', 'N/A')}")
        print(f"Args: {getattr(card, 'status_kwargs', 'N/A')}")
        print("===============================\n")

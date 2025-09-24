import pygame
from batalha.battle_state import BattleState
from batalha.ui import END_TURN_BUTTON

class InputManager:
    def __init__(self, battle_manager):
        self.battle_manager = battle_manager
        self.last_card_clicked = None
        self.last_click_time = 0
        self.double_click_threshold = 300

    def handle_click(self, pos):
        """Gerencia cliques durante o turno do jogador."""
        if self.battle_manager.state != BattleState.PLAYER_TURN:
            return False
            
        if self.battle_manager.animation_manager.has_active_animations():
            return False

        if END_TURN_BUTTON.collidepoint(pos):
            self.battle_manager.turn_manager.end_player_turn()
            return True

        if self._handle_card_click(pos):
            return True

        if self._handle_enemy_click(pos):
            return True

        return False

    def _handle_card_click(self, pos):
        """Verifica se clicou em carta e trata ataque/defesa."""
        for i, card_pos in enumerate(self.battle_manager.hand_renderer.card_positions):
            rect = pygame.Rect(card_pos, 
                (self.battle_manager.hand_renderer.CARD_WIDTH, 
                 self.battle_manager.hand_renderer.CARD_HEIGHT))
                 
            if rect.collidepoint(pos):
                return self._process_card_click(i, pos)
        return False

    def _process_card_click(self, card_index, pos):
        """Processa o clique em uma carta específica."""
        card = self.battle_manager.game.player.hand[card_index]
        self.battle_manager.game.player.select_card_by_index(card_index)

        if card.card_type == "Ataque":
            return True  # Aguarda seleção de alvo

        elif card.card_type == "Defesa":
            return self._handle_defense_card_click(card_index)

        elif card.card_type == "Status":
            return True  # Aguarda clique no alvo

        return False

    def _handle_defense_card_click(self, card_index):
        """Trata clique em carta de defesa (com duplo clique)."""
        now = pygame.time.get_ticks()
        if (self.last_card_clicked == card_index and 
            (now - self.last_click_time) < self.double_click_threshold):
            # Duplo clique -> aplicar defesa
            card = self.battle_manager.game.player.hand[card_index]
            self._resolve_defense_card(card)
            self.battle_manager.game.player.selected_card = None
            return True
        else:
            # Primeiro clique
            self.last_card_clicked = card_index
            self.last_click_time = now
            return True

    def _handle_enemy_click(self, pos):
        """Verifica se clicou em inimigo com carta selecionada."""
        selected_cards = self.battle_manager.game.player.get_selected_cards()
        if not selected_cards:
            return False
            
        for enemy in self.battle_manager.enemies:
            if enemy.rect.collidepoint(pos) and enemy.health > 0:
                self._resolve_card_effects(enemy)
                return True
        return False

    def _resolve_defense_card(self, card):
        """Aplica carta de defesa diretamente no jogador."""
        self.battle_manager.game.player.shield += card.value
        card.use()
        self.battle_manager.hand_renderer.update_card_positions()

    def _resolve_card_effects(self, target):
        """Aplica efeitos das cartas selecionadas no alvo."""
        if target.health <= 0:
            return

        for card in self.battle_manager.game.player.get_selected_cards():
            if card.card_type == "Ataque":
                base_damage = card.value
                final_damage = self.battle_manager.status_manager.calculate_player_damage(base_damage, card)
                target.take_damage(final_damage)
                self.battle_manager.animation_manager.spawn_damage_animation(target, final_damage)

            elif card.card_type == "Status" and hasattr(card, 'status_effect'):
                self.battle_manager.status_manager.apply_status_to_target(
                    target, card.status_effect, **card.status_kwargs)

            elif card.card_type == "Defesa" and target == self.battle_manager.game.player:
                self._resolve_defense_card(card)

            card.use()

        self.battle_manager.game.player.use_selected_cards()
        self.battle_manager.hand_renderer.update_card_positions()
        self.battle_manager.check_battle_end_conditions()
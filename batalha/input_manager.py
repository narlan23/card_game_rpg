import pygame
from batalha.battle_state import BattleState
from characters.cards import CardType
from batalha.ui import END_TURN_BUTTON


class InputManager:
    def __init__(self, battle_manager):
        self.battle_manager = battle_manager
        self.last_card_clicked = None
        self.last_click_time = 0
        self.double_click_threshold = 300  # ms

    def handle_click(self, pos):
        """Gerencia cliques durante o turno do jogador."""
        print(f"[DEBUG] Clique detectado em {pos}, turno atual: {self.battle_manager.state}")

        if self.battle_manager.state != BattleState.PLAYER_TURN:
            print("[DEBUG] Não é turno do jogador.")
            return False

        if self.battle_manager.animation_manager.has_active_animations():
            print("[DEBUG] Animação em execução, clique ignorado.")
            return False

        # Botão de fim de turno
        if END_TURN_BUTTON.collidepoint(pos):
            print("[DEBUG] Botão de fim de turno clicado.")
            self.battle_manager.turn_manager.end_player_turn()
            return True

        # Clique em carta
        if self._handle_card_click(pos):
            return True

        # Clique em inimigo
        if self._handle_enemy_click(pos):
            return True

        # Clique no próprio player
        if self._handle_player_click(pos):
            return True

        print("[DEBUG] Clique não atingiu nada válido.")
        return False

    # -------------------------
    # Clique em carta
    # -------------------------
    def _handle_card_click(self, pos):
        """Verifica se clicou em carta e trata ataque/defesa."""
        for i, card_pos in enumerate(self.battle_manager.hand_renderer.card_positions):
            rect = pygame.Rect(
                card_pos,
                (self.battle_manager.hand_renderer.CARD_WIDTH,
                 self.battle_manager.hand_renderer.CARD_HEIGHT)
            )
            if rect.collidepoint(pos):
                print(f"[DEBUG] Carta {i} clicada na posição {card_pos}")
                return self._process_card_click(i, pos)
        return False

    def _process_card_click(self, card_index, pos):
        """Processa o clique em uma carta específica."""
        card = self.battle_manager.game.player.hand[card_index]
        print(f"[DEBUG] Processando carta {card_index}: tipo={card.card_type}, valor={card.value}")

        self.battle_manager.game.player.select_card_by_index(card_index)

        if card.card_type == CardType.ATAQUE.value:
            print("[DEBUG] Carta de ATAQUE selecionada. Aguardando clique em inimigo.")
            return True

        elif card.card_type == CardType.DEFESA.value:
            print("[DEBUG] Carta de DEFESA selecionada. Esperando duplo clique.")
            return self._handle_defense_card_click(card_index)

        elif card.card_type in (CardType.BUFF.value, CardType.DEBUFF.value):
            print(f"[DEBUG] Carta {card.card_type} selecionada. Aguardando clique em alvo.")
            return True

        return False

    def _handle_defense_card_click(self, card_index):
        """Trata clique em carta de defesa (com duplo clique)."""
        now = pygame.time.get_ticks()
        if (self.last_card_clicked == card_index and
            (now - self.last_click_time) < self.double_click_threshold):
            card = self.battle_manager.game.player.hand[card_index]
            print("[DEBUG] Duplo clique detectado na carta de DEFESA. Aplicando defesa.")
            self._resolve_defense_card(card)
            return True
        else:
            self.last_card_clicked = card_index
            self.last_click_time = now
            print("[DEBUG] Primeiro clique em carta de DEFESA.")
            return True

    # -------------------------
    # Clique em inimigo (REVISADO)
    # -------------------------
    def _handle_enemy_click(self, pos):
        """Verifica se clicou em inimigo com carta selecionada."""
        selected_cards = self.battle_manager.game.player.get_selected_cards()
        if not selected_cards:
            return False

        for enemy in self.battle_manager.enemies:
            if enemy.rect.collidepoint(pos):
                print(f"[DEBUG] Inimigo {enemy.name} clicado. HP={enemy.health}")
                if enemy.health <= 0:
                    print("[DEBUG] Inimigo já está morto. Cancelando.")
                    self.battle_manager.game.player.reset_selection()
                    return False
                
                # A lógica agora está unificada aqui. Chama a função de resolução de efeito
                # para o primeiro inimigo clicado.
                self._resolve_card_effects(enemy)
                
                # Depois que o efeito for resolvido, limpa a seleção
                self.battle_manager.game.player.reset_selection()
                self.battle_manager.hand_renderer.update_card_positions()
                return True
                
        return False

    # -------------------------
    # Clique no player
    # -------------------------
    def _handle_player_click(self, pos):
        """Permite usar buffs e defesa no próprio player."""
        selected_cards = self.battle_manager.game.player.get_selected_cards()
        if not selected_cards:
            return False

        player = self.battle_manager.game.player
        # A nova lógica de clique em inimigo já tem a responsabilidade de limpar a seleção.
        # Esta função é para tratar cliques em cartas que afetam o próprio jogador.
        # A lógica para buffs e defesa deve ser chamada aqui.
        if player.rect.collidepoint(pos):
            print("[DEBUG] Player clicado. Aplicando efeitos.")
            self._resolve_card_effects(player)
            self.battle_manager.game.player.reset_selection()
            self.battle_manager.hand_renderer.update_card_positions()
            return True

        return False

    # -------------------------
    # Aplicação de efeitos (REVISADO)
    # -------------------------
    def _resolve_card_effects(self, target):
        """Aplica efeitos das cartas selecionadas no alvo."""
        if hasattr(target, "health") and target.health <= 0:
            print("[DEBUG] Tentou aplicar efeito em alvo morto. Cancelando.")
            return

        for card in self.battle_manager.game.player.get_selected_cards():
            print(f"[DEBUG] Aplicando {card.card_type} em {target.name if hasattr(target, 'name') else 'Player'}")

            # Lógica para cartas de ATAQUE
            if card.card_type == CardType.ATAQUE.value and target != self.battle_manager.game.player:
                base_damage = card.value
                final_damage = self.battle_manager.status_manager.calculate_player_damage(base_damage, card)
                print(f"[DEBUG] Dano calculado={final_damage}")
                
                # O dano está sendo aplicado corretamente aqui:
                target.take_damage(final_damage) 
                self.battle_manager.animation_manager.spawn_damage_animation(target, final_damage)

            # Lógica para cartas de DEFESA
            elif card.card_type == CardType.DEFESA.value and target == self.battle_manager.game.player:
                self._resolve_defense_card(card)

            # Lógica para cartas de BUFF
            elif card.card_type == CardType.BUFF.value: 
                if hasattr(card, 'status_effect'):
                    print(f"[DEBUG] Aplicando BUFF {card.status_effect}")
                    self.battle_manager.status_manager.apply_status_to_target(
                        target, card.status_effect, **card.status_kwargs)

            # Lógica para cartas de DEBUFF
            elif card.card_type == CardType.DEBUFF.value and target != self.battle_manager.game.player:
                if hasattr(card, 'status_effect'):
                    print(f"[DEBUG] Aplicando DEBUFF {card.status_effect}")
                    self.battle_manager.status_manager.apply_status_to_target(
                        target, card.status_effect, **card.status_kwargs)

            card.use()

    def _resolve_defense_card(self, card):
        """Aplica carta de defesa diretamente no jogador."""
        print(f"[DEBUG] Aplicando DEFESA ao jogador. Valor={card.value}")
        self.battle_manager.game.player.shield += card.value
        card.use()
        self.battle_manager.hand_renderer.update_card_positions()
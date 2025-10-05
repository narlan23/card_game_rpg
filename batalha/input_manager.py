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
        self._debug_enabled = True  # Controle centralizado para debug

    def _debug_print(self, message):
        """Print condicional para debug."""
        if self._debug_enabled:
            print(f"[DEBUG] {message}")

    def handle_click(self, pos):
        """Gerencia cliques durante o turno do jogador."""
        self._debug_print(f"Clique detectado em {pos}, turno atual: {self.battle_manager.state}")

        # Verificações iniciais
        if not self._can_process_click():
            return False

        # Hierarquia de processamento de cliques
        click_handlers = [
            self._handle_end_turn_click,
            self._handle_card_click,
            self._handle_enemy_click,
            self._handle_player_click
        ]

        for handler in click_handlers:
            if handler(pos):
                return True

        self._debug_print("Clique não atingiu nada válido.")
        return False

    def _can_process_click(self):
        """Verifica se o clique pode ser processado."""
        if self.battle_manager.state != BattleState.PLAYER_TURN:
            self._debug_print("Não é turno do jogador.")
            return False

        if self.battle_manager.animation_manager.has_active_animations():
            self._debug_print("Animação em execução, clique ignorado.")
            return False

        return True

    def _handle_end_turn_click(self, pos):
        """Verifica clique no botão de fim de turno."""
        if END_TURN_BUTTON.collidepoint(pos):
            self._debug_print("Botão de fim de turno clicado.")
            self.battle_manager.turn_manager.end_player_turn()
            return True
        return False

    def _handle_card_click(self, pos):
        """Verifica se clicou em carta e trata ataque/defesa."""
        for i, card_pos in enumerate(self.battle_manager.hand_renderer.card_positions):
            rect = pygame.Rect(
                card_pos,
                (self.battle_manager.hand_renderer.CARD_WIDTH,
                 self.battle_manager.hand_renderer.CARD_HEIGHT)
            )
            if rect.collidepoint(pos):
                self._debug_print(f"Carta {i} clicada na posição {card_pos}")
                return self._process_card_click(i)
        return False

    def _process_card_click(self, card_index):
        """Processa o clique em uma carta específica."""
        player = self.battle_manager.game.player
        
        # Validação do índice
        if not (0 <= card_index < len(player.hand)):
            self._debug_print(f"Índice de carta inválido: {card_index}")
            return False

        card = player.hand[card_index]
        self._log_card_details(card_index, card)
        
        player.select_card_by_index(card_index)

        # Mapeamento de tipos de carta para handlers
        card_handlers = {
            CardType.ATAQUE.value: self._handle_attack_card,
            CardType.DEFESA.value: self._handle_defense_card_click,
            CardType.BUFF.value: self._handle_buff_card,
            CardType.DEBUFF.value: self._handle_buff_card
        }

        handler = card_handlers.get(card.card_type)
        if handler:
            return handler(card_index)
        
        self._debug_print(f"Tipo de carta não reconhecido: {card.card_type}")
        return False

    def _handle_attack_card(self, card_index):
        """Handler para carta de ataque."""
        self._debug_print("Carta de ATAQUE selecionada. Aguardando clique em inimigo.")
        return True

    def _handle_buff_card(self, card_index):
        """Handler para cartas de buff/debuff."""
        self._debug_print("Carta BUFF/DEBUFF selecionada. Aguardando clique em alvo.")
        return True

    def _handle_defense_card_click(self, card_index):
        """Trata clique em carta de defesa (com duplo clique)."""
        now = pygame.time.get_ticks()
        
        # Verifica duplo clique
        if (self.last_card_clicked == card_index and 
            (now - self.last_click_time) < self.double_click_threshold):
            
            card = self.battle_manager.game.player.hand[card_index]
            self._debug_print("Duplo clique detectado na carta de DEFESA. Aplicando defesa.")
            self._resolve_defense_card(card)
            return True
        else:
            # Primeiro clique
            self.last_card_clicked = card_index
            self.last_click_time = now
            self._debug_print("Primeiro clique em carta de DEFESA.")
            return True

    def _handle_enemy_click(self, pos):
        """Verifica se clicou em inimigo com carta selecionada."""
        selected_cards = self.battle_manager.game.player.get_selected_cards()
        if not selected_cards:
            return False

        for enemy in self.battle_manager.enemies:
            if enemy.rect.collidepoint(pos):
                return self._process_enemy_click(enemy)
                
        return False

    def _process_enemy_click(self, enemy):
        """Processa clique em um inimigo específico."""
        self._debug_print(f"Inimigo {enemy.name} clicado. HP={enemy.health}")
        
        if enemy.health <= 0:
            self._debug_print("Inimigo já está morto. Cancelando.")
            self.battle_manager.game.player.reset_selection()
            return False
        
        # Aplica efeitos da carta e limpa seleção
        self._resolve_card_effects(enemy)
        self._clear_selection()
        return True

    def _handle_player_click(self, pos):
        """Permite usar buffs e defesa no próprio player."""
        selected_cards = self.battle_manager.game.player.get_selected_cards()
        if not selected_cards:
            return False

        player = self.battle_manager.game.player
        if player.rect.collidepoint(pos):
            self._debug_print("Player clicado. Aplicando efeitos.")
            self._resolve_card_effects(player)
            self._clear_selection()
            return True

        return False

    def _resolve_card_effects(self, target):
        """Aplica efeitos das cartas selecionadas no alvo."""
        if hasattr(target, "health") and target.health <= 0:
            self._debug_print("Tentou aplicar efeito em alvo morto. Cancelando.")
            return

        player = self.battle_manager.game.player
        
        for card in player.get_selected_cards():
            if not self._can_use_card(card, target):
                continue
                
            self._debug_print(f"Aplicando {card.card_type} em {getattr(target, 'name', 'Player')}")
            self._apply_card_effect(card, target)
            card.use()

    def _can_use_card(self, card, target):
        """Verifica se a carta pode ser usada no alvo."""
        # Cartas de ataque não podem ser usadas no jogador
        if card.card_type == CardType.ATAQUE and target == self.battle_manager.game.player:
            self._debug_print("Ataque não pode ser usado no próprio jogador.")
            return False
            
        # Cartas de defesa só podem ser usadas no jogador
        if card.card_type == CardType.DEFESA and target != self.battle_manager.game.player:
            self._debug_print("Defesa só pode ser usada no próprio jogador.")
            return False
            
        return True

    def _apply_card_effect(self, card, target):
        """Aplica o efeito específico da carta no alvo."""
        effect_handlers = {
            CardType.ATAQUE: self._apply_attack_effect,
            CardType.DEFESA: self._apply_defense_effect,
            CardType.BUFF: self._apply_status_effect,
            CardType.DEBUFF: self._apply_status_effect
        }
        
        handler = effect_handlers.get(card.card_type)
        if handler:
            handler(card, target)

    def _apply_attack_effect(self, card, target):
        """Aplica efeito de ataque."""
        if target == self.battle_manager.game.player:
            return  # Não atacar o próprio jogador

        base_damage = card.value
        final_damage = self.battle_manager.status_manager.calculate_player_damage(base_damage, card)
        self._debug_print(f"Dano calculado={final_damage}")
        
        self.battle_manager.apply_damage_to_enemy(target, final_damage)
        self.battle_manager.animation_manager.spawn_damage_animation(target, final_damage)

    def _apply_defense_effect(self, card, target):
        """Aplica efeito de defesa."""
        if target == self.battle_manager.game.player:
            self._resolve_defense_card(card)

    def _apply_status_effect(self, card, target):
        """Aplica efeitos de status (buff/debuff)."""
        if hasattr(card, 'status_effect') and card.status_effect:
            effect_type = "BUFF" if card.card_type == CardType.BUFF else "DEBUFF"
            self._debug_print(f"Aplicando {effect_type} {card.status_effect}")
            
            self.battle_manager.status_manager.apply_status_to_target(
                target, card.status_effect, **card.status_kwargs)

    def _resolve_defense_card(self, card):
        """Aplica carta de defesa diretamente no jogador."""
        self._debug_print(f"Aplicando DEFESA ao jogador. Valor={card.value}")
        self.battle_manager.game.player.shield += card.value
        # Não chamamos card.use() aqui pois já é chamado em _resolve_card_effects

    def _clear_selection(self):
        """Limpa a seleção de cartas e atualiza posições."""
        self.battle_manager.game.player.reset_selection()
        self.battle_manager.hand_renderer.update_card_positions()

    def _log_card_details(self, card_index, card):
        """Log detalhado das informações da carta."""
        if not self._debug_enabled:
            return
            
        print("\n[DEBUG] ===== Carta Clicada =====")
        print(f"Índice: {card_index}")
        print(card)  # usa __str__ -> tipo, valor, elemento, usos, energia
        print(f"Estado: {getattr(card, 'state', 'N/A')}")
        print(f"Efeito de status: {getattr(card, 'status_effect', 'N/A')}")
        print(f"Args do efeito: {getattr(card, 'status_kwargs', 'N/A')}")
        print("===============================\n")

    def disable_debug(self):
        """Desativa mensagens de debug."""
        self._debug_enabled = False

    def enable_debug(self):
        """Ativa mensagens de debug."""
        self._debug_enabled = True
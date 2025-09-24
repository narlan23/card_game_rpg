import pygame
from .battle_state import BattleState
from .animation import DamageAnimation
from .enemy import Enemy
from characters.hand_renderer import HandRenderer, draw_card
from batalha.ui import draw_player_status, END_TURN_BUTTON, draw_end_turn_button


class BattleManager:
    def __init__(self, game):
        self.game = game
        self.font = game.assets.get_font("default")
        self.state = BattleState.PLAYER_TURN
        self.animations = []
        self.enemies = pygame.sprite.Group()

        # Controle de turno inimigo
        self.enemy_actions_queue = []
        self.enemy_attack_timer = 0
        self.enemy_attack_interval = 600  # ms
        self.enemy_turn_started = False

        # Configura dimensões mínimas
        game.screen_width = getattr(game, "screen_width", 800)
        game.screen_height = getattr(game, "screen_height", 600)

        # Renderizador da mão
        self.hand_renderer = HandRenderer(
            game.player,
            screen_width=game.screen_width,
            hand_y=game.screen_height - 150,
            align="center"
        )

        self.last_card_clicked = None
        self.last_click_time = 0
        self.double_click_threshold = 300  # ms para considerar duplo clique

    # =====================================
    # Setup
    # =====================================
    def setup_battle(self, enemies_data):
        """Inicializa os inimigos e reseta estado do jogador."""
        positions = self._enemy_positions()

        for i, data in enumerate(enemies_data[:len(positions)]):
            enemy = Enemy(
                data["name"], data["health"], data["attack"],
                data["image"], positions[i]
            )
            self.enemies.add(enemy)

        self._reset_player()
        self.enemy_turn_started = False

    def _enemy_positions(self):
        """Retorna posições pré-definidas para até 3 inimigos."""
        return [
            (self.game.screen_width * (i + 1) // 4, self.game.screen_height // 4)
            for i in range(3)
        ]

    def _reset_player(self):
        """Restaura energia e seleção do jogador."""
        self.game.player.reset_energy()
        self.game.player.reset_selection()
        self.hand_renderer.set_alignment("center", self.game.screen_height - 150)

    # =====================================
    # Turno do Jogador
    # =====================================
    def end_player_turn(self):
        if self.state == BattleState.PLAYER_TURN:
            self.state = BattleState.ENEMY_TURN
            self.enemy_turn_started = False

    def handle_click(self, pos):
        """Gerencia cliques durante o turno do jogador."""
        if self.state != BattleState.PLAYER_TURN:
            return
        if self._has_active_animations():
            return

        if END_TURN_BUTTON.collidepoint(pos):
            return self.end_player_turn()

        if self._handle_card_click(pos):
            return

        if self._handle_enemy_click(pos):
            return

    def _handle_card_click(self, pos):
        """Verifica se clicou em carta e trata ataque/defesa."""
        for i, card_pos in enumerate(self.hand_renderer.card_positions):
            rect = pygame.Rect(card_pos, (self.hand_renderer.CARD_WIDTH, self.hand_renderer.CARD_HEIGHT))
            if rect.collidepoint(pos):
                card = self.game.player.hand[i]
                
                # Se for carta de ataque -> comportamento normal (selecionar para usar em inimigo)
                if card.card_type == "Ataque":
                    self.game.player.select_card_by_index(i)
                    return True

                # Se for carta de defesa -> verificar se é duplo clique
                elif card.card_type == "Defesa":
                    now = pygame.time.get_ticks()
                    if self.last_card_clicked == i and (now - self.last_click_time) < self.double_click_threshold:
                        # Duplo clique -> aplicar direto no jogador
                        self.resolve_defense_card(card)
                        return True
                    else:
                        # Primeiro clique -> apenas marcar tempo
                        self.last_card_clicked = i
                        self.last_click_time = now
                        return True
        return False


    def _handle_enemy_click(self, pos):
        """Verifica se clicou em inimigo com carta selecionada."""
        if not self.game.player.get_selected_cards():
            return False
        for enemy in self.enemies:
            if enemy.rect.collidepoint(pos) and enemy.health > 0:
                self.resolve_card_effects(enemy)
                return True
        return False
    
    def resolve_defense_card(self, card):
        """Aplica carta de defesa diretamente no jogador."""
        self.game.player.shield += card.value
        print(f"{self.game.player.name} ganhou {card.value} de escudo! Escudo total: {self.game.player.shield}")

        card.use()
        self.hand_renderer.update_card_positions()


    def resolve_card_effects(self, target):
        """Aplica efeitos das cartas selecionadas no alvo (somente ataques)."""
        if target.health <= 0:
            return

        for card in self.game.player.get_selected_cards():
            if card.card_type == "Ataque":
                target.take_damage(card.value)
                self._spawn_damage_animation(target, card.value)
            # Cartas de defesa não são tratadas aqui (são usadas via duplo clique)

            card.use()

        self.game.player.use_selected_cards()
        self.hand_renderer.update_card_positions()
        self.check_battle_end_conditions()


    def _spawn_damage_animation(self, target, damage, is_player=False):
        """Cria animação de dano."""
        self.animations.append(DamageAnimation(
            target, damage,
            is_player=is_player,
            screen_width=self.game.screen_width,
            hand_y=self.hand_renderer.hand_y
        ))

    # =====================================
    # Turno dos Inimigos
    # =====================================
    def start_enemy_turn(self):
        """Coleta ações dos inimigos vivos."""
        if self.enemy_turn_started:
            return
        self.enemy_turn_started = True

        self.enemy_actions_queue = [
            (enemy, enemy.attack_value)
            for enemy in self.enemies if enemy.health > 0 and enemy.choose_action() == "attack"
        ]

        if not self.enemy_actions_queue:
            self.end_enemy_turn()
        else:
            self.enemy_attack_timer = self.enemy_attack_interval

    def end_enemy_turn(self):
        self.state = BattleState.PLAYER_TURN
        self._reset_player()
        self.enemy_turn_started = False

    # =====================================
    # Atualização
    # =====================================
    def update(self, dt=16):
        self._update_animations()

        if self.state in [BattleState.VICTORY, BattleState.DEFEAT]:
            return

        if self.state == BattleState.ENEMY_TURN:
            if not self.enemy_turn_started:
                self.start_enemy_turn()
            self._process_enemy_actions(dt)

    def _update_animations(self):
        for anim in self.animations[:]:
            anim.update()
            if anim.is_finished:
                self.animations.remove(anim)

    def _process_enemy_actions(self, dt):
        if not self.enemy_actions_queue:
            return

        self.enemy_attack_timer -= dt
        if self.enemy_attack_timer <= 0:
            enemy, damage = self.enemy_actions_queue.pop(0)
            self.game.player.take_damage(damage)
            self._spawn_damage_animation(self.game.player, damage, is_player=True)

            if self.check_battle_end_conditions():
                return

            self.enemy_attack_timer = self.enemy_attack_interval if self.enemy_actions_queue else 0
            if not self.enemy_actions_queue:
                self.end_enemy_turn()

    # =====================================
    # Condições de fim
    # =====================================
    def check_battle_end_conditions(self):
        if all(enemy.health <= 0 for enemy in self.enemies):
            self.state = BattleState.VICTORY
            return True
        if self.game.player.health <= 0:
            self.state = BattleState.DEFEAT
            return True
        return False

    def _has_active_animations(self):
        return any(not anim.is_finished for anim in self.animations)

    # =====================================
    # Renderização
    # =====================================
    def draw(self, surface):
        surface.fill((50, 50, 80))
        self._draw_enemies(surface)
        if self.state == BattleState.PLAYER_TURN:
            self.hand_renderer.draw_hand(surface, draw_card)
        draw_player_status(surface, self.game.player, 50, 340)

        for anim in self.animations:
            anim.draw(surface)

        if self.state == BattleState.PLAYER_TURN and not self._has_active_animations():
            draw_end_turn_button(surface, self.font, self)

        self._draw_battle_state(surface)

    def _draw_enemies(self, surface):
        self.enemies.draw(surface)
        for enemy in self.enemies:
            if enemy.health > 0:
                self._draw_health_bar(surface, enemy)

    def _draw_health_bar(self, surface, enemy):
        ratio = enemy.health / enemy.max_health
        pygame.draw.rect(surface, (255, 0, 0), (enemy.rect.x, enemy.rect.y - 20, enemy.rect.width, 10))
        pygame.draw.rect(surface, (0, 255, 0), (enemy.rect.x, enemy.rect.y - 20, enemy.rect.width * ratio, 10))

    def _draw_battle_state(self, surface):
        if self.state in [BattleState.VICTORY, BattleState.DEFEAT]:
            self._draw_overlay_message(
                "VITÓRIA! Pressione ESC para voltar." if self.state == BattleState.VICTORY else "DERROTA! Pressione ESC para voltar.",
                (255, 215, 0) if self.state == BattleState.VICTORY else (255, 0, 0)
            )
        else:
            text = "Seu turno! Selecione cartas e ataque os inimigos." if self.state == BattleState.PLAYER_TURN else "Turno do inimigo! Aguarde..."
            self._draw_text_center(surface, text, (255, 255, 255), y=10)

    def _draw_overlay_message(self, text, color):
        overlay = pygame.Surface((self.game.screen_width, self.game.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.game.SCREEN.blit(overlay, (0, 0))
        self._draw_text_center(self.game.SCREEN, text, color)

    def _draw_text_center(self, surface, text, color, y=None):
        rendered = self.font.render(text, True, color)
        x = self.game.screen_width // 2 - rendered.get_width() // 2
        y = y if y is not None else self.game.screen_height // 2 - rendered.get_height() // 2
        surface.blit(rendered, (x, y))

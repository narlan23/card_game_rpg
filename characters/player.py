import pygame
import random
from characters.cards import Card, CardState
from config import PLAYER_HEALTH


class Player(pygame.sprite.Sprite):
    """Representa o jogador com sprites reais e animações."""

    def __init__(self, name="Jogador", max_energy=3, max_health=PLAYER_HEALTH, x=0, y=0):
        super().__init__()
        
        # 🎯 ATRIBUTOS BÁSICOS DO JOGADOR
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.max_energy = max_energy
        self.energy = max_energy

        # 🛡️ DEFESA E STATUS
        self.shield = 0
        self.status_effects = {}

        # 🃏 DECK, MÃO E DESCARTE
        self.deck = []
        self.hand = []
        self.discard_pile = []
        self.selected_cards = []

        # 🔥 SISTEMA DE SPRITES E ANIMAÇÕES
        self._load_sprites()
        self.current_animation = "idle"
        self.animation_frame = 0
        self.animation_speed = 0.2  # Velocidade da animação
        self.last_update = pygame.time.get_ticks()
        
        # 🎯 ATRIBUTOS VISUAIS OBRIGATÓRIOS DO PYGAME
        self.image = self.animations["idle"][0]  # Imagem inicial
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # 🎮 ESTADO DE MOVIMENTO
        self.is_moving = False
        self.facing_right = True

    def _load_sprites(self):
        """Carrega todos os sprites e animações do jogador."""
        self.animations = {
            "idle": self._load_animation_frames("assets/", "player_idle_", 1),
            "walk": self._load_animation_frames("assets/player/walk/", "player_walk_", 6),
            "attack": self._load_animation_frames("assets/player/attack/", "player_attack_", 4),
        }
        
        # Fallback: criar sprites coloridos se os arquivos não existirem
        if not self.animations["idle"]:
            print("AVISO: Sprites não encontrados. Criando sprites coloridos de fallback.")
            self._create_fallback_sprites()

    def _load_animation_frames(self, folder, prefix, frame_count):
        """Carrega os frames de animação de uma pasta."""
        frames = []
        try:
            for i in range(1, frame_count + 1):
                filename = f"{folder}{prefix}{i}.png"
                image = pygame.image.load(filename).convert_alpha()
                # Redimensiona se necessário (opcional)
                image = pygame.transform.scale(image, (50, 80))
                frames.append(image)
            print(f"✅ Carregados {len(frames)} frames de {folder}")
        except (pygame.error, FileNotFoundError) as e:
            print(f"❌ Erro ao carregar sprites de {folder}: {e}")
            return []
        return frames

    def _create_fallback_sprites(self):
        """Cria sprites coloridos como fallback."""
        self.animations = {
            "idle": [self._create_colored_surface((50, 80), (0, 120, 255))],
            "walk": [
                self._create_colored_surface((50, 80), (0, 100, 230)),
                self._create_colored_surface((50, 80), (0, 120, 255)),
                self._create_colored_surface((50, 80), (0, 140, 230)),  # ✅ CORRIGIDO: 280 → 230
            ],
            "attack": [self._create_colored_surface((50, 80), (255, 100, 100))],
        }

    def _create_colored_surface(self, size, color):
        """Cria uma surface colorida com bordas."""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surface, color, (0, 0, size[0], size[1]))
        pygame.draw.rect(surface, (255, 255, 255), (0, 0, size[0], size[1]), 2)
        return surface

    def update(self):
        """Atualiza a animação do sprite."""
        now = pygame.time.get_ticks()
        
        # Verifica se é hora de atualizar o frame de animação
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.animation_frame = (self.animation_frame + 1) % len(self.animations[self.current_animation])
            
            # Atualiza a imagem atual
            self.image = self.animations[self.current_animation][self.animation_frame]
            
            # Espelha a imagem se estiver virado para esquerda
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

    def set_animation(self, animation_name):
        """Muda para uma animação específica."""
        if animation_name in self.animations and animation_name != self.current_animation:
            self.current_animation = animation_name
            self.animation_frame = 0

    def set_moving(self, is_moving, direction_x=0):
        """Define se o jogador está se movendo e a direção."""
        self.is_moving = is_moving
        
        # Atualiza direção
        if direction_x > 0:
            self.facing_right = True
        elif direction_x < 0:
            self.facing_right = False
            
        # Muda animação baseado no movimento
        if is_moving:
            self.set_animation("walk")
        else:
            self.set_animation("idle")

    # =========================================================================
    # ❤️ VIDA, ESCUDO E ENERGIA
    # =========================================================================

    def take_damage(self, amount: int):
        """Recebe dano levando em conta escudo e status."""
        if self.has_status("esquiva"):
            if random.random() < 0.5:
                print(f"{self.name} esquivou do ataque!")
                self.remove_status("esquiva")
                return False

        if self.shield > 0:
            absorbed = min(amount, self.shield)
            self.shield -= absorbed
            amount -= absorbed
            print(f"{self.name} bloqueou {absorbed} de dano com escudo!")

        if self.has_status("vulnerabilidade") or self.has_status("vulneravel"):
            multiplier = self.status_effects.get(
                "vulnerabilidade",
                self.status_effects.get("vulneravel", {})
            ).get("multiplier", 1.5)
            amount = int(amount * multiplier)
            print(f"O dano foi aumentado para {amount} devido à vulnerabilidade!")

        if amount > 0:
            self.health = max(0, self.health - amount)
            print(f"{self.name} recebeu {amount} de dano! Vida atual: {self.health}")

        return self.health <= 0

    def heal(self, amount: int):
        """Recupera vida até o máximo permitido."""
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        healed = self.health - old_health
        if healed > 0:
            print(f"{self.name} curou {healed} de vida.")
        return healed

    def is_alive(self):
        return self.health > 0

    def is_full_health(self):
        return self.health == self.max_health

    # ⚡ ENERGIA
    def reset_energy(self):
        self.energy = self.max_energy

    def regenerate_energy(self, amount=1):
        self.energy = min(self.max_energy, self.energy + amount)

    def gain_energy(self, amount=1):
        self.energy = min(self.max_energy, self.energy + amount)

    def lose_energy(self, amount=1):
        self.energy = max(0, self.energy - amount)

    # 🛡️ ESCUDO
    def add_shield(self, amount=1):
        self.shield += amount
        print(f"{self.name} ganhou {amount} de escudo (total: {self.shield})")

    # =========================================================================
    # 📊 STATUS EFFECTS
    # =========================================================================

    def add_status(self, status: str, **kwargs):
        self.status_effects[status] = kwargs.copy()
        print(f"{self.name} ganhou status: {status} {kwargs}")

    def has_status(self, status: str):
        return status in self.status_effects

    def remove_status(self, status: str):
        if status in self.status_effects:
            del self.status_effects[status]
            print(f"{self.name} perdeu o status {status}")

    def tick_status(self):
        expired = []
        for status, data in list(self.status_effects.items()):
            if status == "veneno":
                dmg = data.get("power", 1)
                self.take_damage(dmg)
                print(f"{self.name} sofreu {dmg} de dano por veneno!")
            if status == "regeneracao":
                heal = data.get("power", 1)
                self.heal(heal)
                print(f"{self.name} regenerou {heal} de vida!")

            if "duration" in data:
                data["duration"] -= 1
                if data["duration"] <= 0:
                    expired.append(status)
        for s in expired:
            self.remove_status(s)

    # =========================================================================
    # 🎮 MÉTODOS VISUAIS E DE POSIÇÃO
    # =========================================================================
    
    def set_position(self, x, y):
        self.rect.topleft = (x, y)

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def get_position(self):
        return self.rect.topleft

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    # =========================================================================
    # 🃏 DECK E CARTAS (métodos principais mantidos)
    # =========================================================================

    def set_deck(self, deck):
        self.deck = [card.clone() for card in deck]
        random.shuffle(self.deck)
        self.hand.clear()
        self.discard_pile.clear()

    def draw_card(self, amount=1):
        for _ in range(amount):
            if not self.deck:
                self.reshuffle_discard_into_deck()
            if self.deck:
                self.hand.append(self.deck.pop())

    def discard_card(self, card):
        if card in self.hand:
            self.hand.remove(card)
        card.state = CardState.EXHAUSTED
        self.discard_pile.append(card)

    def discard_hand(self):
        while self.hand:
            self.discard_card(self.hand[0])

    def reshuffle_discard_into_deck(self):
        if not self.discard_pile:
            return
        self.deck = [card.clone() for card in self.discard_pile]
        random.shuffle(self.deck)
        self.discard_pile.clear()

    def can_play_card(self, card: Card):
        return self.energy >= card.energy_cost and card.is_active()

    def select_card(self, card):
        if card not in self.hand or not self.can_play_card(card):
            return False
        if card.state == CardState.SELECTED:
            return False
        card.state = CardState.SELECTED
        self.selected_cards.append(card)
        self.lose_energy(card.energy_cost)
        return True

    def deselect_card(self, card):
        if card in self.selected_cards:
            card.state = CardState.IDLE
            self.selected_cards.remove(card)
            self.gain_energy(card.energy_cost)
            return True
        return False

    def select_card_by_index(self, index):
        if 0 <= index < len(self.hand):
            return self.select_card(self.hand[index])
        return False

    def deselect_card_by_index(self, index):
        if 0 <= index < len(self.hand):
            return self.deselect_card(self.hand[index])
        return False

    def use_selected_cards(self, target=None):
        for card in list(self.selected_cards):
            card.use(self, target)
            self.discard_card(card)
        self.selected_cards.clear()

    def get_selected_cards(self):
        return list(self.selected_cards)

    def reset_selection(self):
        for card in self.selected_cards:
            card.state = CardState.IDLE
        self.selected_cards.clear()

    def play_card(self, card, target=None):
        if not self.select_card(card):
            return False
        card.use(self, target)
        self.discard_card(card)
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        return True
    
    def reshuffle_hand(self, energy_cost=3):
        if self.energy < energy_cost:
            print(f"[AVISO] {self.name} não tem energia suficiente para reembaralhar (precisa de {energy_cost}).")
            return False

        old_hand_size = len(self.hand)
        if old_hand_size == 0:
            print(f"{self.name} não tem cartas na mão para reembaralhar.")
            return False

        self.lose_energy(energy_cost)
        print(f"{self.name} gastou {energy_cost} de energia para reembaralhar a mão.")

        self.discard_hand()

        if not self.deck:
            self.reshuffle_discard_into_deck()

        self.draw_card(old_hand_size)

        print(f"{self.name} reembaralhou a mão ({old_hand_size} cartas). Energia restante: {self.energy}/{self.max_energy}")
        return True

    # =========================================================================
    # 🔄 CONTROLE DE TURNO
    # =========================================================================

    def start_turn(self, draw_amount=1):
        self.tick_status()
        self.reset_selection()
        self.reset_energy()

    def end_turn(self):
        self.discard_hand()

    # =========================================================================
    # 📊 DEBUG TEXTUAL
    # =========================================================================

    def show_hand(self):
        return [str(card) for card in self.hand]

    def show_deck(self):
        return [str(card) for card in self.deck]

    def show_discard(self):
        return [str(card) for card in self.discard_pile]

    def __str__(self):
        return (f"{self.name} | HP: {self.health}/{self.max_health} | "
                f"Energy: {self.energy}/{self.max_energy} | "
                f"Shield: {self.shield} | "
                f"Status: {list(self.status_effects.keys())} | "
                f"Hand: {len(self.hand)} cards | "
                f"Position: {self.rect.topleft}")
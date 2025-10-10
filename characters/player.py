import pygame
import random
from characters.cards import Card, CardState
from config import PLAYER_HEALTH


class Player(pygame.sprite.Sprite):
    """Representa o jogador: vida, energia, deck, mão, escudo e efeitos de batalha."""

    def __init__(self, name="Jogador", max_energy=3, max_health=PLAYER_HEALTH, x=0, y=0):
        # 🔥 HERANÇA PYGAME.SPRITE - CONSTRUTOR OBRIGATÓRIO
        super().__init__()
        
        # 🔥 ATRIBUTOS VISUAIS OBRIGATÓRIOS DO PYGAME
        self.image = pygame.Surface((60, 80))  # Tamanho do sprite do jogador
        self.image.fill((0, 120, 255))  # Cor azul para representar o jogador
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)  # Posição inicial
        
        # 🎯 ATRIBUTOS BÁSICOS DO JOGADOR
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.max_energy = max_energy
        self.energy = max_energy

        # 🛡️ DEFESA E STATUS
        self.shield = 0  # escudo que absorve dano
        self.status_effects = {}  # Ex: {"força": {"power": 2, "duration": 3}}

        # 🃏 DECK, MÃO E DESCARTE
        self.deck = []
        self.hand = []
        self.discard_pile = []

        # 🎯 CARTAS SELECIONADAS
        self.selected_cards = []

    # =========================================================================
    # 🎮 MÉTODOS VISUAIS E DE POSIÇÃO (NOVOS - INTEGRAÇÃO PYGAME)
    # =========================================================================
    
    def update(self):
        """
        Método chamado automaticamente pelo grupo de sprites.
        Atualiza aspectos visuais do jogador.
        """
        # Efeito visual quando com pouca vida
        if self.health < self.max_health * 0.3:
            # Piscar para indicar perigo
            alpha = 128 + 127 * (pygame.time.get_ticks() % 1000) // 1000
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)
            
        # Mudar cor baseado na energia
        if self.energy <= 1:
            self.image.fill((255, 100, 100))  # Vermelho quando pouca energia
        else:
            self.image.fill((0, 120, 255))   # Azul normal

    def set_position(self, x, y):
        """Define a posição do jogador na tela."""
        self.rect.topleft = (x, y)

    def move(self, dx, dy):
        """Move o jogador por uma quantidade dx, dy."""
        self.rect.x += dx
        self.rect.y += dy

    def get_position(self):
        """Retorna a posição atual do jogador."""
        return self.rect.topleft

    def draw(self, surface):
        """Desenha o jogador em uma surface (alternativa ao grupo de sprites)."""
        surface.blit(self.image, self.rect)

    # =========================================================================
    # ❤️ VIDA, ESCUDO E ENERGIA
    # =========================================================================

    def take_damage(self, amount: int):
        """Recebe dano levando em conta escudo e status."""
        # Verifica se esquiva o ataque
        if self.has_status("esquiva"):
            if random.random() < 0.5:  # 50% chance de esquivar
                print(f"{self.name} esquivou do ataque!")
                self.remove_status("esquiva")
                return False  # Não morreu

        if self.shield > 0:
            absorbed = min(amount, self.shield)
            self.shield -= absorbed
            amount -= absorbed
            print(f"{self.name} bloqueou {absorbed} de dano com escudo!")

        # Aplica vulnerabilidade
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

        return self.health <= 0  # retorna True se morreu

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
        """Adiciona ou atualiza efeitos de status (buffs/debuffs)."""
        self.status_effects[status] = kwargs.copy()  # Usa copy para evitar referências
        print(f"{self.name} ganhou status: {status} {kwargs}")

    def has_status(self, status: str):
        return status in self.status_effects

    def remove_status(self, status: str):
        if status in self.status_effects:
            del self.status_effects[status]
            print(f"{self.name} perdeu o status {status}")

    def tick_status(self):
        """Reduz duração dos status e aplica efeitos recorrentes por turno."""
        expired = []
        for status, data in list(self.status_effects.items()):
            # Exemplo de status recorrentes
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
    # 🃏 DECK E CARTAS
    # =========================================================================

    def set_deck(self, deck):
        """Configura um novo deck embaralhado."""
        self.deck = [card.clone() for card in deck]
        random.shuffle(self.deck)
        self.hand.clear()
        self.discard_pile.clear()

    def draw_card(self, amount=1):
        """Compra cartas do deck, reembaralhando o descarte se necessário."""
        for _ in range(amount):
            if not self.deck:
                self.reshuffle_discard_into_deck()
            if self.deck:
                self.hand.append(self.deck.pop())

    def discard_card(self, card):
        """Descarta carta da mão para a pilha de descarte."""
        if card in self.hand:
            self.hand.remove(card)
        card.state = CardState.EXHAUSTED
        self.discard_pile.append(card)

    def discard_hand(self):
        """Descarta todas as cartas da mão."""
        while self.hand:
            self.discard_card(self.hand[0])

    def reshuffle_discard_into_deck(self):
        """Reembaralha o descarte de volta para o deck."""
        if not self.discard_pile:
            return
        self.deck = [card.clone() for card in self.discard_pile]
        random.shuffle(self.deck)
        self.discard_pile.clear()

    # =========================================================================
    # 🎯 SELEÇÃO E USO DE CARTAS
    # =========================================================================

    def can_play_card(self, card: Card):
        """Verifica se o jogador pode jogar uma carta."""
        return self.energy >= card.energy_cost and card.is_active()

    def select_card(self, card):
        """Seleciona uma carta se possível."""
        if card not in self.hand or not self.can_play_card(card):
            return False
        if card.state == CardState.SELECTED:
            return False
        card.state = CardState.SELECTED
        self.selected_cards.append(card)
        self.lose_energy(card.energy_cost)
        return True

    def deselect_card(self, card):
        """Deseleciona carta e devolve energia."""
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
        """Consome cartas selecionadas e descarta elas."""
        for card in list(self.selected_cards):
            card.use(self, target)
            self.discard_card(card)
        self.selected_cards.clear()

    def get_selected_cards(self):
        return list(self.selected_cards)

    def reset_selection(self):
        """Reseta seleção de cartas sem consumir energia."""
        for card in self.selected_cards:
            card.state = CardState.IDLE
        self.selected_cards.clear()

    def play_card(self, card, target=None):
        """Atalho para jogar uma carta imediatamente."""
        if not self.select_card(card):
            return False
        card.use(self, target)
        self.discard_card(card)
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        return True
    
    def reshuffle_hand(self, energy_cost=3):
        """
        Descarte todas as cartas atuais da mão e compre novas do deck.
        Possui um custo de energia (padrão = 1).
        Se o deck acabar, o descarte é reembaralhado automaticamente.
        """
        # ⚡ Verifica energia suficiente
        if self.energy < energy_cost:
            print(f"[AVISO] {self.name} não tem energia suficiente para reembaralhar (precisa de {energy_cost}).")
            return False

        old_hand_size = len(self.hand)
        if old_hand_size == 0:
            print(f"{self.name} não tem cartas na mão para reembaralhar.")
            return False

        # ⚡ Consome energia
        self.lose_energy(energy_cost)
        print(f"{self.name} gastou {energy_cost} de energia para reembaralhar a mão.")

        # 1️⃣ Descarta a mão atual
        self.discard_hand()

        # 2️⃣ Reembaralha descarte no deck, se necessário
        if not self.deck:
            self.reshuffle_discard_into_deck()

        # 3️⃣ Compra o mesmo número de cartas
        self.draw_card(old_hand_size)

        print(f"{self.name} reembaralhou a mão ({old_hand_size} cartas). Energia restante: {self.energy}/{self.max_energy}")
        return True

    # =========================================================================
    # 🔄 CONTROLE DE TURNO
    # =========================================================================

    def start_turn(self, draw_amount=1):
        """Inicia turno: atualiza status, reseta energia e compra cartas."""
        self.tick_status()
        self.reset_selection()
        self.reset_energy()
        #self.draw_card(draw_amount)

    def end_turn(self):
        """Descarta a mão no fim do turno."""
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
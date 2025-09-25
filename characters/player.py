import random
from characters.cards import Card
from config import PLAYER_HEALTH


class Player:
    """Representa o jogador: vida, energia, deck, mão, escudo e efeitos de batalha."""

    def __init__(self, name="Jogador", max_energy=3, max_health=PLAYER_HEALTH):
        # Atributos básicos
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.max_energy = max_energy
        self.energy = max_energy

        # Defesa e status
        self.shield = 0  # escudo que absorve dano
        self.status_effects = {}  # Ex: {"vulneravel": {"duration": 2}}

        # Deck, mão e descarte
        self.deck = []
        self.hand = []
        self.discard_pile = []

        # Cartas selecionadas
        self.selected_cards = []

    # -------------------------------
    # Vida, escudo e energia
    # -------------------------------
    def take_damage(self, amount: int):
        """Recebe dano levando em conta escudo e status."""
        if self.shield > 0:
            absorbed = min(amount, self.shield)
            self.shield -= absorbed
            amount -= absorbed
            print(f"{self.name} bloqueou {absorbed} de dano com escudo!")

        if self.has_status("vulneravel"):
            amount = int(amount * 1.5)  # arredonda para inteiro
            print(f"O dano foi aumentado para {amount} devido à vulnerabilidade!")

        if amount > 0:
            self.health = max(0, self.health - amount)
            print(f"{self.name} recebeu {amount} de dano! Vida atual: {self.health}")

        return self.health <= 0  # retorna True se morreu

    def heal(self, amount: int):
        """Recupera vida até o máximo permitido."""
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        print(f"{self.name} curou {self.health - old_health} de vida.")

    def is_alive(self):
        return self.health > 0

    def is_full_health(self):
        return self.health == self.max_health

    # Energia
    def reset_energy(self):
        self.energy = self.max_energy

    def regenerate_energy(self, amount=1):
        self.energy = min(self.max_energy, self.energy + amount)

    def gain_energy(self, amount=1):
        self.energy = min(self.max_energy, self.energy + amount)

    def lose_energy(self, amount=1):
        self.energy = max(0, self.energy - amount)

    # Escudo
    def add_shield(self, amount=1):
        self.shield += amount
        print(f"{self.name} ganhou {amount} de escudo (total: {self.shield})")

    # -------------------------------
    # Status
    # -------------------------------
    def add_status(self, status: str, **kwargs):
        """Adiciona ou atualiza efeitos de status (buffs/debuffs)."""
        self.status_effects[status] = kwargs
        print(f"{self.name} ganhou status: {status} {kwargs}")

    def has_status(self, status: str):
        return status in self.status_effects

    def remove_status(self, status: str):
        if status in self.status_effects:
            del self.status_effects[status]
            print(f"{self.name} perdeu o status {status}")

    def tick_status(self):
        """Reduz duração dos status a cada turno."""
        expired = []
        for status, data in list(self.status_effects.items()):
            if "duration" in data:
                data["duration"] -= 1
                if data["duration"] <= 0:
                    expired.append(status)
        for s in expired:
            self.remove_status(s)

    # -------------------------------
    # Deck e cartas
    # -------------------------------
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
            card.state = "exhausted"
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

    # -------------------------------
    # Seleção e uso de cartas
    # -------------------------------
    def can_play_card(self, card: Card):
        """Verifica se o jogador pode jogar uma carta."""
        return self.energy >= card.energy_cost and card.is_active()

    def select_card(self, card):
        """Seleciona uma carta se possível."""
        if card not in self.hand or not self.can_play_card(card):
            return False
        if card.state == "selected":
            return False
        card.state = "selected"
        self.selected_cards.append(card)
        self.lose_energy(card.energy_cost)
        return True

    def deselect_card(self, card):
        """Deseleciona carta e devolve energia."""
        if card in self.selected_cards:
            card.state = "idle"
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

    def use_selected_cards(self):
        """Consome cartas selecionadas."""
        for card in self.selected_cards:
            card.use()
            # opcional: self.discard_card(card)
        self.selected_cards.clear()

    def get_selected_cards(self):
        return list(self.selected_cards)

    def reset_selection(self):
        """Reseta seleção de cartas sem consumir energia."""
        for card in self.selected_cards:
            card.state = "idle"
        self.selected_cards.clear()

    def play_card(self, card, target=None):
        """Atalho para jogar uma carta imediatamente."""
        if not self.select_card(card):
            return False
        card.use(target)
        self.discard_card(card)
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        return True

    # -------------------------------
    # Controle de turno
    # -------------------------------
    def start_turn(self, draw_amount=1):
        """Inicia turno: atualiza status, reseta energia e compra cartas."""
        self.tick_status()
        self.reset_selection()
        self.reset_energy()
        self.draw_card(draw_amount)

    def end_turn(self):
        """Descarta a mão no fim do turno."""
        self.discard_hand()

    # -------------------------------
    # Debug textual
    # -------------------------------
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
                f"Hand: {[c.card_type for c in self.hand]}")

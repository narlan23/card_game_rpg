import random
from characters.cards import Card
from config import PLAYER_HEALTH


class Player:
    """Representa o jogador: vida, energia, deck e efeitos de batalha."""

    def __init__(self, name="Jogador", max_energy=3, max_health=PLAYER_HEALTH):
        # Atributos básicos
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.max_energy = max_energy
        self.energy = max_energy
        self.block = 0   # armadura temporária

        # Defesa e status
        self.shield = 0  # escudo que absorve dano
        self.status_effects = {}  # {"buff": {"power": 2, "duration": 2}}

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
        """Recebe dano levando em conta o escudo."""
        if self.shield > 0:
            absorbed = min(amount, self.shield)
            self.shield -= absorbed
            amount -= absorbed
            print(f"{self.name} bloqueou {absorbed} de dano com escudo!")

        if amount > 0:
            self.health = max(0, self.health - amount)
            print(f"{self.name} recebeu {amount} de dano! Vida atual: {self.health}")

        return self.health <= 0  # retorna True se morreu

    def heal(self, amount: int):
        """Recupera vida até o máximo permitido."""
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self):
        return self.health > 0

    def reset_energy(self):
        self.energy = self.max_energy

    def regenerate_energy(self, amount=1):
        self.energy = min(self.max_energy, self.energy + amount)

    # -------------------------------
    # Status
    # -------------------------------
    def add_status(self, status: str, **kwargs):
        """Adiciona ou atualiza efeitos de status (buffs/debuffs)."""
        self.status_effects[status] = kwargs
        print(f"{self.name} ganhou status: {status} {kwargs}")

    def has_status(self, status: str):
        return status in self.status_effects

    def tick_status(self):
        """Reduz duração dos status a cada turno."""
        expired = []
        for status, data in list(self.status_effects.items()):
            if "duration" in data:
                data["duration"] -= 1
                if data["duration"] <= 0:
                    expired.append(status)
        for s in expired:
            print(f"{self.name} perdeu o status {s}")
            del self.status_effects[s]

    # -------------------------------
    # Deck e cartas
    # -------------------------------
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
            card.state = "exhausted"
            self.discard_pile.append(card)

    def reshuffle_discard_into_deck(self):
        self.deck = [card.clone() for card in self.discard_pile]
        random.shuffle(self.deck)
        self.discard_pile.clear()

    # -------------------------------
    # Seleção e uso de cartas
    # -------------------------------
    def can_play_card(self, card: Card):
        return self.energy >= card.energy_cost and card.is_active()

    def select_card(self, card):
        if card not in self.hand or not self.can_play_card(card):
            return False
        if card.state == "selected":
            return False
        card.state = "selected"
        self.selected_cards.append(card)
        self.energy -= card.energy_cost
        return True

    def deselect_card(self, card):
        if card in self.selected_cards:
            card.state = "idle"
            self.selected_cards.remove(card)
            self.energy = min(self.max_energy, self.energy + card.energy_cost)
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
        self.selected_cards.clear()

    def get_selected_cards(self):
        return list(self.selected_cards)

    def reset_selection(self):
        for card in self.selected_cards:
            card.state = "idle"
        self.selected_cards.clear()

    # -------------------------------
    # Controle de turno
    # -------------------------------
    def start_turn(self, draw_amount=1):
        self.tick_status()
        self.reset_selection()
        self.reset_energy()
        self.draw_card(draw_amount)

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

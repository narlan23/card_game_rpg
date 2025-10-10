import random
from enum import Enum
from config import ELEMENTS


class CardState(Enum):
    IDLE = "idle"
    SELECTED = "selected"
    EXHAUSTED = "exhausted"


class CardType(Enum):
    ATAQUE = "Ataque"
    DEFESA = "Defesa"
    ESQUIVA = "Esquiva"
    BUFF = "Buff"
    DEBUFF = "Debuff"
    ESPECIAL = "Especial"


# -----------------------------
# Biblioteca de Cartas baseada no Player
# -----------------------------
CARD_LIBRARY = {
    # ATAQUES
    "ataque_fraco": {"type": CardType.ATAQUE, "value": 2, "element": "Fogo"},
    "ataque_medio": {"type": CardType.ATAQUE, "value": 4, "element": "Água"},
    "ataque_forte": {"type": CardType.ATAQUE, "value": 6, "element": "Terra"},

    # DEFESAS
    "defesa_basica": {"type": CardType.DEFESA, "value": 4, "element": "Terra"},
    "defesa_forte": {"type": CardType.DEFESA, "value": 8, "element": "Água"},

}


class Card:
    DEFAULT_MAX_USES = 3
    DEFAULT_ENERGY_COST = 1

    def __init__(self, card_type: CardType, value: int, element: str,
                 max_uses=None, energy_cost=None, status_effect=None, status_kwargs=None):
        if not isinstance(card_type, CardType):
            raise ValueError(f"Tipo de carta inválido: {card_type}")

        if element not in ELEMENTS:
            raise ValueError(f"Elemento inválido: {element}")

        self.card_type = card_type
        self.value = value
        self.element = element
        self.status_effect = status_effect
        self.status_kwargs = status_kwargs or {}

        self.state = None
        self.max_uses = max_uses or self.DEFAULT_MAX_USES
        self.uses_left = self.max_uses
        self.energy_cost = energy_cost if energy_cost is not None else self.DEFAULT_ENERGY_COST

    def __str__(self):
        return f"[{self.card_type.value}] {self.element} {self.value} | Usos {self.uses_left}/{self.max_uses} | Energia {self.energy_cost}"

    def clone(self, keep_state=False):
        new_card = Card(self.card_type, self.value, self.element,
                        self.max_uses, self.energy_cost, self.status_effect, self.status_kwargs)
        if keep_state:
            new_card.uses_left = self.uses_left
            new_card.state = self.state
        return new_card

    def use(self, user=None, target=None, apply_effect=True):
        if not self.is_active():
            return False

        self.uses_left -= 1
        self.state = CardState.EXHAUSTED if self.uses_left <= 0 else CardState.IDLE

        if apply_effect:
            self.apply_effect(user, target)

        return True

    def reset(self):
        self.uses_left = self.max_uses
        self.state = CardState.IDLE

    def reset_uses(self):
        self.uses_left = self.max_uses

    def is_active(self):
        return self.uses_left > 0

    def is_exhausted(self):
        return self.state == CardState.EXHAUSTED or self.uses_left == 0

    def requires_energy(self, current_energy: int) -> bool:
        return current_energy >= self.energy_cost

    def apply_effect(self, user, target):
        if not user:
            return

        if self.card_type == CardType.ATAQUE:
            if target:
                target.take_damage(self.value)
                print(f"{user.name} atacou {target.name} causando {self.value} de dano!")
        elif self.card_type == CardType.DEFESA:
            user.add_shield(self.value)
            print(f"{user.name} ganhou {self.value} de escudo!")
        elif self.card_type == CardType.ESQUIVA:
            user.add_status("esquiva", duration=1)
            print(f"{user.name} se preparou para esquivar!")
        elif self.card_type == CardType.BUFF:
            nome = self.status_effect or "fortalecido"
            user.add_status(nome, power=self.value, **self.status_kwargs)
            print(f"{user.name} recebeu buff: {nome}!")
        elif self.card_type == CardType.DEBUFF and target:
            nome = self.status_effect or "vulneravel"
            target.add_status(nome, power=self.value, **self.status_kwargs)
            print(f"{target.name} recebeu debuff: {nome}!")
        elif self.card_type == CardType.ESPECIAL and target:
            target.take_damage(self.value)
            if hasattr(user, "heal"):
                user.heal(self.value // 2)
            print(f"{user.name} usou um especial e drenou {self.value // 2} de vida!")

    def _apply_attack(self, user, target):
        if target and hasattr(target, "take_damage"):
            target.take_damage(self.value)
            print(f"{user.name} atacou {target.name} causando {self.value} de dano!")

    def _apply_defense(self, user):
        if hasattr(user, "add_shield"):
            user.add_shield(self.value)
            print(f"{user.name} ganhou {self.value} de escudo!")

    def _apply_dodge(self, user):
        if hasattr(user, "add_status"):
            user.add_status("esquiva", duration=1)
            print(f"{user.name} se preparou para esquivar!")

    def _apply_buff(self, user):
        if hasattr(user, "add_status"):
            status_name = self.status_effect if self.status_effect else "buff"
            user.add_status(status_name, power=self.value, **self.status_kwargs)
            print(f"{user.name} recebeu buff: {status_name}!")

    def _apply_debuff(self, target):
        if hasattr(target, "add_status"):
            status_name = self.status_effect if self.status_effect else "debuff"
            target.add_status(status_name, power=self.value, **self.status_kwargs)
            print(f"{target.name} recebeu debuff: {status_name}!")

    def _apply_special(self, user, target):
        if target and hasattr(target, "take_damage"):
            target.take_damage(self.value)
            if hasattr(user, "heal"):
                user.heal(self.value // 2)
            print(f"{user.name} usou especial causando {self.value} de dano!")


def generate_deck(size=12):
    deck = []
    card_ids = list(CARD_LIBRARY.keys())
    for _ in range(size):
        card_id = random.choice(card_ids)
        data = CARD_LIBRARY[card_id]
        deck.append(Card(
            card_type=data["type"],
            value=data["value"],
            element=data["element"],
            max_uses=data.get("max_uses"),
            energy_cost=data.get("energy_cost"),
            status_effect=data.get("status_effect"),
            status_kwargs=data.get("status_kwargs"),
        ))
    return deck

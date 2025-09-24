import random
from config import ELEMENTS


class Card:
    DEFAULT_MAX_USES = 5
    DEFAULT_ENERGY_COST = 1
    STATES = ("idle", "selected", "exhausted")
    TYPES = ("Ataque", "Defesa", "Esquiva", "Buff", "Debuff", "Especial")

    def __init__(self, card_type, value, element, max_uses=None, energy_cost=None):
        if card_type not in self.TYPES:
            raise ValueError(f"Tipo de carta inválido: {card_type}")

        self.card_type = card_type
        self.value = value
        self.element = str(element)

        self.state = "idle"
        self.selected = False

        self.max_uses = max_uses or self.DEFAULT_MAX_USES
        self.uses_left = self.max_uses

        self.energy_cost = energy_cost if energy_cost is not None else self.DEFAULT_ENERGY_COST

    # -----------------------------
    # Representação
    # -----------------------------
    def __str__(self):
        return f"[{self.card_type}] {self.element} {self.value} | Usos {self.uses_left}/{self.max_uses} | Energia {self.energy_cost}"

    def clone(self):
        return Card(self.card_type, self.value, self.element, self.max_uses, self.energy_cost)

    # -----------------------------
    # Controle de usos
    # -----------------------------
    def use(self):
        """Consome 1 uso da carta."""
        if not self.is_active():
            return False

        self.uses_left -= 1
        self.state = "exhausted" if self.uses_left == 0 else "idle"
        self.selected = False
        return True

    def reset(self):
        """Restaura os usos e estado da carta."""
        self.uses_left = self.max_uses
        self.state = "idle"
        self.selected = False

    # -----------------------------
    # Verificações
    # -----------------------------
    def is_active(self):
        """Pode ser usada?"""
        return self.uses_left > 0

    def requires_energy(self, current_energy: int) -> bool:
        """Verifica se há energia suficiente para jogar a carta."""
        return current_energy >= self.energy_cost

    # -----------------------------
    # Efeito da carta
    # -----------------------------
    def apply_effect(self, user, target):
        """
        Executa o efeito da carta.
        Aqui você pode expandir com lógica de buff/debuff/ataque/defesa/etc.
        """
        if self.card_type == "Ataque":
            target.health -= self.value

        elif self.card_type == "Defesa":
            user.shield += self.value

        elif self.card_type == "Esquiva":
            user.add_status("esquiva", duration=1)

        elif self.card_type == "Buff":
            user.add_status("buff", power=self.value, duration=2)

        elif self.card_type == "Debuff":
            target.add_status("debuff", power=self.value, duration=2)

        elif self.card_type == "Especial":
            # Exemplo: roubar vida
            target.health -= self.value
            user.health += self.value // 2

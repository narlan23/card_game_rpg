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


class Card:
    DEFAULT_MAX_USES = 5
    DEFAULT_ENERGY_COST = 1

    def __init__(self, card_type, value, element, max_uses=None, energy_cost=None):
        if card_type not in [t.value for t in CardType]:
            raise ValueError(f"Tipo de carta inválido: {card_type}")

        if element not in ELEMENTS:
            raise ValueError(f"Elemento inválido: {element}")

        self.card_type = card_type
        self.value = value
        self.element = element

        self.state = CardState.IDLE
        self.selected = False

        self.max_uses = max_uses or self.DEFAULT_MAX_USES
        self.uses_left = self.max_uses

        self.energy_cost = energy_cost if energy_cost is not None else self.DEFAULT_ENERGY_COST

    # -----------------------------
    # Representação
    # -----------------------------
    def __str__(self):
        return (
            f"[{self.card_type}] {self.element} {self.value} "
            f"| Usos {self.uses_left}/{self.max_uses} "
            f"| Energia {self.energy_cost}"
        )

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
        self.state = CardState.EXHAUSTED if self.uses_left == 0 else CardState.IDLE
        self.selected = False
        return True

    def reset(self):
        """Restaura os usos e estado da carta."""
        self.uses_left = self.max_uses
        self.state = CardState.IDLE
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
        """Executa o efeito da carta."""
        if self.card_type == CardType.ATAQUE.value:
            self._apply_attack(user, target)

        elif self.card_type == CardType.DEFESA.value:
            self._apply_defense(user)

        elif self.card_type == CardType.ESQUIVA.value:
            self._apply_dodge(user)

        elif self.card_type == CardType.BUFF.value:
            self._apply_buff(user)

        elif self.card_type == CardType.DEBUFF.value:
            self._apply_debuff(target)

        elif self.card_type == CardType.ESPECIAL.value:
            self._apply_special(user, target)

    # ---- Métodos privados para modularizar efeitos ----
    def _apply_attack(self, user, target):
        target.health -= self.value
        print(f"{user.name} atacou {target.name} causando {self.value} de dano!")

    def _apply_defense(self, user):
        user.shield += self.value
        print(f"{user.name} ganhou {self.value} de escudo!")

    def _apply_dodge(self, user):
        user.add_status("esquiva", duration=1)
        print(f"{user.name} se preparou para esquivar o próximo ataque!")

    def _apply_buff(self, user):
        user.add_status("buff", power=self.value, duration=2)
        print(f"{user.name} recebeu um buff de {self.value}!")

    def _apply_debuff(self, target):
        target.add_status("debuff", power=self.value, duration=2)
        print(f"{target.name} recebeu um debuff de {self.value}!")

    def _apply_special(self, user, target):
        target.health -= self.value
        user.health += self.value // 2
        print(f"{user.name} drenou {self.value} de vida de {target.name}!")

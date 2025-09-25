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

        self.state = CardState.IDLE
        self.max_uses = max_uses or self.DEFAULT_MAX_USES
        self.uses_left = self.max_uses
        self.energy_cost = energy_cost if energy_cost is not None else self.DEFAULT_ENERGY_COST

    # -----------------------------
    # Representação
    # -----------------------------
    def __str__(self):
        return (
            f"[{self.card_type.value}] {self.element} {self.value} "
            f"| Usos {self.uses_left}/{self.max_uses} "
            f"| Energia {self.energy_cost}"
        )

    def clone(self, keep_state=False):
        """Cria cópia da carta. Se keep_state=True, mantém usos e estado."""
        new_card = Card(self.card_type, self.value, self.element,
                        self.max_uses, self.energy_cost, self.status_effect, self.status_kwargs)
        if keep_state:
            new_card.uses_left = self.uses_left
            new_card.state = self.state
        return new_card

    # -----------------------------
    # Controle de usos
    # -----------------------------
    def use(self, user=None, target=None, apply_effect=True):
        """Consome 1 uso da carta e opcionalmente aplica o efeito."""
        if not self.is_active():
            return False

        self.uses_left -= 1
        if self.uses_left <= 0:
            self.state = CardState.EXHAUSTED
        else:
            self.state = CardState.IDLE

        if apply_effect:
            self.apply_effect(user, target)

        return True

    def reset(self):
        """Restaura os usos e estado da carta."""
        self.uses_left = self.max_uses
        self.state = CardState.IDLE

    def reset_uses(self):
        """Só reseta usos (sem mexer no estado)."""
        self.uses_left = self.max_uses

    # -----------------------------
    # Verificações
    # -----------------------------
    def is_active(self):
        """Pode ser usada?"""
        return self.uses_left > 0

    def is_exhausted(self):
        return self.state == CardState.EXHAUSTED or self.uses_left == 0

    def requires_energy(self, current_energy: int) -> bool:
        """Verifica se há energia suficiente para jogar a carta."""
        return current_energy >= self.energy_cost

    # -----------------------------
    # Efeito da carta
    # -----------------------------
    def apply_effect(self, user, target):
        """Executa o efeito da carta."""
        if not user:
            return  # segurança: não aplica se não tiver contexto

        if self.card_type == CardType.ATAQUE:
            self._apply_attack(user, target)

        elif self.card_type == CardType.DEFESA:
            self._apply_defense(user)

        elif self.card_type == CardType.ESQUIVA:
            self._apply_dodge(user)

        elif self.card_type == CardType.BUFF:
            self._apply_buff(user)

        elif self.card_type == CardType.DEBUFF:
            if target:
                self._apply_debuff(target)

        elif self.card_type == CardType.ESPECIAL:
            if target:
                self._apply_special(user, target)

    # ---- Métodos privados para modularizar efeitos ----
    def _apply_attack(self, user, target):
        if not target or not hasattr(target, "take_damage"):
            return
        
        # Usa o StatusManager para cálculo consistente de dano
        if hasattr(user, "battle_manager") and hasattr(user.battle_manager, "status_manager"):
            base_damage = self.value
            final_damage = user.battle_manager.status_manager.calculate_player_damage(base_damage, self)
            target.take_damage(final_damage)
            print(f"{user.name} atacou {target.name} causando {final_damage} de dano!")
        else:
            # Fallback: cálculo básico se não houver StatusManager
            target.take_damage(self.value)
            print(f"{user.name} atacou {target.name} causando {self.value} de dano!")

    def _apply_defense(self, user):
        if hasattr(user, "add_shield"):
            user.add_shield(self.value)
            print(f"{user.name} ganhou {self.value} de escudo!")

    def _apply_dodge(self, user):
        if hasattr(user, "add_status"):
            user.add_status("esquiva", duration=1)
            print(f"{user.name} se preparou para esquivar o próximo ataque!")

    def _apply_buff(self, user):
        if hasattr(user, "add_status"):
            # Usa status_effect específico se definido, senão usa "força" como padrão
            status_name = self.status_effect if self.status_effect else "força"
            user.add_status(status_name, power=self.value, duration=2, **self.status_kwargs)
            print(f"{user.name} recebeu um buff de {self.value}!")

    def _apply_debuff(self, target):
        if hasattr(target, "add_status"):
            # Usa status_effect específico se definido, senão usa "fraqueza" como padrão
            status_name = self.status_effect if self.status_effect else "fraqueza"
            target.add_status(status_name, power=self.value, duration=2, **self.status_kwargs)
            print(f"{target.name} recebeu um debuff de {self.value}!")

    def _apply_special(self, user, target):
        if not target or not hasattr(target, "take_damage"):
            return
            
        if hasattr(user, "heal"):
            # Drena vida: causa dano no alvo e cura o usuário
            target.take_damage(self.value)
            user.heal(self.value // 2)
            print(f"{user.name} drenou {self.value} de vida de {target.name}!")


def generate_deck(size=10):
    """
    Gera um deck com o número especificado de cartas aleatórias.
    
    Args:
        size (int): Número de cartas no deck (padrão: 10)
    
    Returns:
        list: Lista de objetos Card aleatórios
    """
    deck = []
    
    # Valores possíveis para as cartas (ajuste conforme necessário)
    possible_values = list(range(1, 11))
    
    # Distribuição balanceada de tipos de carta
    card_types = list(CardType)
    
    for _ in range(size):
        # Escolhe tipo, valor e elemento aleatoriamente
        card_type = random.choice(card_types)
        value = random.choice(possible_values)
        element = random.choice(ELEMENTS)
        
        # Para cartas de ataque e defesa, valores mais altos
        if card_type in [CardType.ATAQUE, CardType.DEFESA]:
            value = random.randint(5, 15)
        
        # Para cartas especiais, valores moderados
        elif card_type == CardType.ESPECIAL:
            value = random.randint(3, 8)
        
        # Cria a carta e adiciona ao deck
        new_card = Card(card_type, value, element)
        deck.append(new_card)
    
    return deck
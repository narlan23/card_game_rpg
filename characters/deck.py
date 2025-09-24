import random
from config import ELEMENTS
from characters.cards import Card


# -------------------------
# Configurações do baralho
# -------------------------
DECK_COMPOSITION = {
    "Ataque": 3,
    "Defesa": 1,
    "Esquiva": 1,
    "Buff": 2,
    "Debuff": 2,
    # Total = 8 cartas
}

CARD_VALUE_RANGES = {
    "Ataque": (5, 12),
    "Defesa": (3, 8),
    "Esquiva": (0, 0),
    "Buff": (1, 3),
    "Debuff": (1, 2),
    "Especial": (6, 10),  # opcional para futuro
}


def generate_deck(thematic_element=None):
    """
    Gera um baralho de 8 cartas com tipos variados.
    Buffs e Debuffs já recebem status_effect configurado.
    """
    card_types = []
    for card_type, count in DECK_COMPOSITION.items():
        card_types.extend([card_type] * count)
    random.shuffle(card_types)

    deck = []
    for idx, card_type in enumerate(card_types):
        min_val, max_val = CARD_VALUE_RANGES.get(card_type, (1, 5))
        value = random.randint(min_val, max_val)

        # Escolha de elemento
        if card_type == "Esquiva":
            element = "Ar"
        else:
            element = thematic_element or random.choice(ELEMENTS)

        # Criar carta
        card = Card(card_type, value, element)

        # Adicionar efeitos extras se necessário
        if card_type == "Buff":
            card.status_effect = "força"
            card.status_kwargs = {"power": value, "duration": 2}

        elif card_type == "Debuff":
            card.status_effect = "fraqueza"
            card.status_kwargs = {"multiplier": 0.75, "duration": 2}

        # Log detalhado
        print(f"[{idx+1}] Carta gerada -> "
              f"Tipo: {card.card_type}, Valor: {card.value}, "
              f"Elemento: {card.element}, Estado: {card.state}, "
              f"Status: {getattr(card, 'status_effect', None)}")

        deck.append(card)

    print(f"Total de cartas no deck: {len(deck)}")
    return deck

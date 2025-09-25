import random
from config import ELEMENTS, CARD_TYPES
from characters.cards import Card, CardType


# -------------------------
# Configurações do baralho
# -------------------------
DECK_COMPOSITION = {
    CardType.ATAQUE.value: 1,
    CardType.DEFESA.value: 0,
    CardType.ESQUIVA.value: 0,
    CardType.BUFF.value: 2,
    CardType.DEBUFF.value: 2,
}

CARD_VALUE_RANGES = {
    CardType.ATAQUE.value: (5, 12),
    CardType.DEFESA.value: (3, 8),
    CardType.ESQUIVA.value: (0, 0),
    CardType.BUFF.value: (1, 3),
    CardType.DEBUFF.value: (1, 2),
    CardType.ESPECIAL.value: (6, 10),
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
        if card_type == CardType.BUFF.value:
            card.status_effect = "força"
            card.status_kwargs = {"power": value, "duration": 2}

        elif card_type == CardType.DEBUFF.value:
            card.status_effect = "fraqueza"
            card.status_kwargs = {"multiplier": 0.75, "duration": 2}

        deck.append(card)

    print(f"Total de cartas no deck: {len(deck)}")
    return deck

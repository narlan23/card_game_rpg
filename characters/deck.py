import pygame
import random
from characters.cards import Card
from config import ELEMENTS,ELEMENT_COLORS ,CARD_TYPES, DECK_COMPOSITION,CARD_VALUE_RANGES, BLACK, RED, FONT, CARD_WIDTH, CARD_HEIGHT

# -------------------------------
# Geração de deck
# -------------------------------
def generate_deck(thematic_element=None):
    """
    Gera um baralho de 8 cartas com tipos variados.
    Args:
        thematic_element (str, opcional): Elemento temático das cartas. Se None, escolhe aleatoriamente.
    Returns:
        list[Card]: Lista de cartas.
    """
    card_types = []
    for card_type, count in DECK_COMPOSITION.items():
        card_types.extend([card_type] * count)
    random.shuffle(card_types)

    deck = []
    for idx, card_type in enumerate(card_types):
        min_val, max_val = CARD_VALUE_RANGES[card_type]
        value = random.randint(min_val, max_val)

        if card_type == CARD_TYPES['DODGE']:
            element = 'Ar'
        else:
            element = thematic_element or random.choice(ELEMENTS)

        card = Card(card_type, value, element)
        deck.append(card)

        # Log detalhado
        print(f"[{idx+1}] Carta gerada -> Tipo: {card.card_type}, Valor: {card.value}, Elemento: {card.element}, Estado: {card.state}")
        
    print(f"Total de cartas no deck: {len(deck)}")
    return deck

# -------------------------------
# Desenho de cartas     
    
# -------------------------------
def draw_card(screen, card, x, y, selected=False, width=None, height=None):
    # Usa largura/altura padrão caso não seja passado
    width = width or CARD_WIDTH
    height = height or CARD_HEIGHT

    bg_color = ELEMENT_COLORS.get(card.element, (200, 200, 200)) # Cores de texto

    # Retângulo da carta
    card_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, bg_color, card_rect, border_radius=8)

    # Borda
    if card.state == "selected":
        pygame.draw.rect(screen, RED, card_rect, 3, border_radius=8)
    else:
        pygame.draw.rect(screen, BLACK, card_rect, 2, border_radius=8)

    text_color = BLACK if card.state != "exhausted" else (80, 80, 80)

    # Renderiza textos centralizados
    type_text = FONT.render(card.card_type, True, text_color)
    value_text = FONT.render(f"Valor: {card.value}", True, text_color)
    element_text = FONT.render(str(card.element), True, text_color)

    type_x = x + (width - type_text.get_width()) // 2
    value_x = x + (width - value_text.get_width()) // 2
    element_x = x + (width - element_text.get_width()) // 2

    screen.blit(type_text, (type_x, y + 15))
    screen.blit(value_text, (value_x, y + 45))
    screen.blit(element_text, (element_x, y + 75))

    return card_rect


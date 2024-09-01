import random
import json

with open('card_deck.json', 'r', encoding='utf-8') as f:
    card_deck = json.load(f)


def make_layout() -> list[dict]:
    layout = []

    while len(layout) < 3:
        card = random.choice(card_deck)

        names = [x['name'] for x in layout] if layout else []
        if card['name'] not in names:
            layout.append(card)

    return layout

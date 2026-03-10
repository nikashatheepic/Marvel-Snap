import copy
import random
import locations
import decks

def main():
   game_locations = create_locations(locations.locations_dict)
   player1_shuffled_deck = create_deck(decks.player1_deck)
   player2_shuffled_deck = create_deck(decks.player2_deck)

   return game_locations, player1_shuffled_deck, player2_shuffled_deck

class Location:
    def __init__(self, name, position, ability=None, ability_type=None):
        self.name = name
        self.position = position    #0, 1, or 2
        self.base_power1 = 0
        self.base_power2 = 0
        self.card_list_1 = []
        self.card_list_2 = []
        self.ability = ability
        self.ability_type = ability_type
        self.revealed = False
        self.ongoing_power1 = 0
        self.ongoing_power2 = 0
        self.total_power1 = 0
        self.total_power2 = 0

def create_locations(locations_list):
    location_0 = Location("unknown",0)
    location_1 = Location("unknown",1)
    location_2 = Location("unknown",2)

    chosen_items = random.sample(list(locations_list.items()), 3)

    location_0.name,(location_0.ability, location_0.ability_type) = chosen_items[0]
    location_1.name,(location_1.ability, location_1.ability_type) = chosen_items[1]
    location_2.name,(location_2.ability, location_2.ability_type) = chosen_items[2]

    return [location_0, location_1, location_2]

def create_deck(deck_list):
    deck = []
    for card in deck_list:
        deck.append(copy.deepcopy(card))
    random.shuffle(deck)
    return deck

if __name__ == '__main__':
    main()

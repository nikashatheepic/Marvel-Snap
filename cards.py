from engine import draw_card
import random

class Card:
    def __init__(self, name, cost, base_power, type, ability, priority):
        self.name = name
        self.cost = cost
        self.base_power = base_power
        self.type = type
        self.ability = ability
        self.priority = priority
        self.ongoing_power = 0
        self.owner = None
        self.order = None

def iron_man_ability(player, location):
    if player.number == 1:
        location.ongoing_power1 += location.base_power1 + location.ongoing_power1
    else:
        location.ongoing_power2 += location.base_power2 + location.ongoing_power2

def forge_ability(player, game_locations, location_index, player1, player2, card):
    player.pending_buffs += 2

def adam_warlock_ability(card, player, game_locations, location_index):
    if player.number == 1:
        winning = game_locations[location_index].total_power1 > game_locations[location_index].total_power2
    else:
        winning = game_locations[location_index].total_power2 > game_locations[location_index].total_power1

    if winning:
        draw_card(player)
    else:
        card.base_power += 1

def silver_sable_ability(player, game_locations, location_index, player1, player2, card):
    if player.number == 1:
        if len(player2.deck) > 0:
            player2.deck[0].base_power -= 2
            card.base_power += 2
    else:
        if len(player1.deck) > 0:
            player1.deck[0].base_power -= 2
            card.base_power += 2

def iceman_ability(player, game_locations, location_index, player1, player2, card):
    if player.number == 1:
        if len(player2.hand) > 0:
            target = random.randint(0,len(player2.hand)-1)
            player2.hand[target].cost += 1
    else:
        if len(player1.hand) > 0:
            target = random.randint(0,len(player1.hand)-1)
            player1.hand[target].cost += 1

def gambit_ability(player, game_locations, location_index, player1, player2, card):
    pass


iron_man = Card('iron man', 5, 0, "ongoing", iron_man_ability, 1)
forge = Card('forge', 2, 2, "on_reveal", forge_ability, 0)
adam_warlock = Card('adam warlock', 2, 0, "end_of_turn", adam_warlock_ability, 0)
silver_sable = Card('silver sable', 1, 0, "on_reveal", silver_sable_ability, 0)
iceman = Card('iceman', 1, 2, "on_reveal", iceman_ability, 0)
gambit = Card('gambit',3,3,'on_reveal',gambit_ability,0)

card_lookup = {
    "iron man" : iron_man,
    "forge" : forge,
    "adam warlock" : adam_warlock,
    "silver sable" : silver_sable,
    "iceman" : iceman,
    "gambit" : gambit
}

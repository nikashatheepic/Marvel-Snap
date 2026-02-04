from engine import draw_card


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

def iron_man_ability(player, location):
    if player.number == 1:
        location.ongoing_power1 += location.base_power1
    else:
        location.ongoing_power2 += location.base_power2

def forge_ability(player, game_locations, location_index):
    player.pending_buffs += 2

def adam_warlock_ability(card, player, game_locations, location_index):
    if player.number == 1:
        winning = game_locations[location_index].total_power1 > game_locations[location_index].total_power2
    else:
        winning = game_locations[location_index].total_power2 > game_locations[location_index].total_power1

    if winning:
        draw_card(player)
        print ("BORN AGAIN!")
    else:
        card.base_power += 1
        if player.number == 1:
            game_locations[location_index].base_power1 += 1
        else:
            game_locations[location_index].base_power2 += 1
        print ("BORN AGAIN!")


iron_man = Card('iron man', 5, 0, "ongoing", iron_man_ability, 1)
forge = Card('forge', 2, 2, "on_reveal", forge_ability, 0)
adam_warlock = Card('adam warlock', 2, 0, "end_of_turn", adam_warlock_ability, 0)

card_lookup = {
    "iron man" : iron_man,
    "forge" : forge,
    "adam warlock" : adam_warlock
}

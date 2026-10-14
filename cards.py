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

def draw_card(player):
    if len(player.deck) > 0 and len(player.hand) < 7:
        player.hand.append(player.deck[0])
        del player.deck[0]

def iron_man_ability(player, opponent, location):
    location.add_ongoing(player, location.base_power_of(player) + location.ongoing_power_of(player))

def forge_ability(player, opponent, game_locations, location_index, card):
    player.pending_buffs += 2

def adam_warlock_ability(card, player, opponent, game_locations, location_index):
    location = game_locations[location_index]
    if location.total_power_of(player) > location.total_power_of(opponent):
        draw_card(player)
    else:
        card.base_power += 1

def silver_sable_ability(player, opponent, game_locations, location_index, card):
    if len(opponent.deck) > 0:
        opponent.deck[0].base_power -= 2
        card.base_power += 2

def iceman_ability(player, opponent, game_locations, location_index, card):
    if len(opponent.hand) > 0:
        random.choice(opponent.hand).cost += 1

def medusa_ability(player, opponent, game_locations, location_index, card):
    if location_index == 1:
        card.base_power += 3

def wolfsbane_ability(player, opponent, game_locations, location_index, card):
    my_cards = game_locations[location_index].cards_of(player)
    card.base_power += 2 * (len(my_cards) - 1)

def elektra_ability(player, opponent, game_locations, location_index, card):
    enemy_cards = game_locations[location_index].cards_of(opponent)
    targets = [enemy for enemy in enemy_cards if enemy.cost == 1]
    if len(targets) > 0:
        target = random.choice(targets)
        enemy_cards.remove(target)
        opponent.destroy_pool.append(target)

def punisher_ability(player, opponent, location):
    location.add_ongoing(player, len(location.cards_of(opponent)))

def ant_man_ability(player, opponent, location):
    if len(location.cards_of(player)) == 4:
        location.add_ongoing(player, 3)

def lizard_ability(player, opponent, location):
    if len(location.cards_of(opponent)) == 4:
        location.add_ongoing(player, -4)

iron_man = Card('iron man', 5, 0, "ongoing", iron_man_ability, 1)
forge = Card('forge', 2, 2, "on_reveal", forge_ability, 0)
adam_warlock = Card('adam warlock', 2, 0, "end_of_turn", adam_warlock_ability, 0)
silver_sable = Card('silver sable', 1, 0, "on_reveal", silver_sable_ability, 0)
iceman = Card('iceman', 1, 2, "on_reveal", iceman_ability, 0)
medusa = Card('medusa', 2, 2, "on_reveal", medusa_ability, 0)
wolfsbane = Card('wolfsbane', 3, 1, "on_reveal", wolfsbane_ability, 0)
elektra = Card('elektra', 1, 1, "on_reveal", elektra_ability, 0)
punisher = Card('punisher', 3, 3, "ongoing", punisher_ability, 0)
ant_man = Card('ant man', 1, 1, "ongoing", ant_man_ability, 0)
lizard = Card('lizard', 2, 5, "ongoing", lizard_ability, 0)

misty_knight = Card('misty knight', 1, 2, "vanilla", None, 0)
cyclops = Card('cyclops', 3, 4, "vanilla", None, 0)
the_thing = Card('the thing', 4, 6, "vanilla", None, 0)
hulk = Card('hulk', 6, 12, "vanilla", None, 0)

card_lookup = {
    "iron man" : iron_man,
    "forge" : forge,
    "adam warlock" : adam_warlock,
    "silver sable" : silver_sable,
    "iceman" : iceman,
    "medusa" : medusa,
    "wolfsbane" : wolfsbane,
    "elektra" : elektra,
    "punisher" : punisher,
    "ant man" : ant_man,
    "lizard" : lizard,
    "misty knight" : misty_knight,
    "cyclops" : cyclops,
    "the thing" : the_thing,
    "hulk" : hulk
}

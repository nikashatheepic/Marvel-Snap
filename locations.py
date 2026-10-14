import random
from cards import draw_card


def deaths_domain_ability(game_locations, location_index, player):
    my_cards = game_locations[location_index].cards_of(player)
    if len(my_cards) > 0:
        player.destroy_pool.append(my_cards.pop())

def hala_ability(game_locations, location_index, turn_number, player1, player2):
    if turn_number == 4:
        location = game_locations[location_index]
        for player in (player1, player2):
            if location.total_power_of(player) < location.total_power_of(player.opponent):
                player.destroy_pool.extend(location.cards_of(player))
                location.cards_of(player).clear()

def jotunheim_ability(game_locations, location_index, turn_number, player1, player2):
    for card in game_locations[location_index].all_cards():
        card.base_power -= 1

def muir_island_ability(game_locations, location_index, turn_number, player1, player2):
    for card in game_locations[location_index].all_cards():
        card.base_power += 1

def murderworld_ability(game_locations, location_index, turn_number, player1, player2):
    if turn_number == 3:
        location = game_locations[location_index]
        for player in (player1, player2):
            player.destroy_pool.extend(location.cards_of(player))
            location.cards_of(player).clear()

def asgard_ability(game_locations, location_index, turn_number, player1, player2):
    if turn_number == 4:
        location = game_locations[location_index]
        for player in (player1, player2):
            if location.total_power_of(player) > location.total_power_of(player.opponent):
                draw_card(player)
                draw_card(player)

def stark_tower_ability(game_locations, location_index, turn_number, player1, player2):
    if turn_number == 5:
        for card in game_locations[location_index].all_cards():
            card.base_power += 2

def danger_room_ability(game_locations, location_index, player):
    if random.random() < 0.25:
        deaths_domain_ability(game_locations, location_index, player)

locations_dict = {
    "death's_domain": (deaths_domain_ability, "on_play"),
    "hala": (hala_ability, "end_of_turn"),
    "jotunheim": (jotunheim_ability, "end_of_turn"),
    "muir_island": (muir_island_ability, "end_of_turn"),
    "murderworld": (murderworld_ability, "end_of_turn"),
    "asgard": (asgard_ability, "end_of_turn"),
    "stark_tower": (stark_tower_ability, "end_of_turn"),
    "danger_room": (danger_room_ability, "on_play")
}
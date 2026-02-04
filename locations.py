
def deaths_domain_ability(game_locations, location_index, player):
    if player.number == 1:
        if len(game_locations[location_index].card_list_1) > 0:
            card_removed = game_locations[location_index].card_list_1[-1]
            del game_locations[location_index].card_list_1[-1]
            game_locations[location_index].base_power1 -= card_removed.base_power

            player.destroy_pool.append(card_removed)

    else:
        if len(game_locations[location_index].card_list_2) > 0:
            card_removed = game_locations[location_index].card_list_2[-1]
            del game_locations[location_index].card_list_2[-1]
            game_locations[location_index].base_power2 -= card_removed.base_power

            player.destroy_pool.append(card_removed)

def hala_ability(game_locations, location_index):
    print("Hala Ability Triggered")

def jotunheim_ability(game_locations, location_index):
    print("Jotunheim Ability Triggered")

locations_dict = {
    "death's_domain": (deaths_domain_ability, "on_play"),
    "hala": (hala_ability, "end_of_turn"),
    "jotunheim": (jotunheim_ability, "end_of_turn")
}
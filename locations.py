
def deaths_domain_ability(game_locations, location_index, player):
    if player.number == 1:
        if len(game_locations[location_index].card_list_1) > 0:
            card_removed = game_locations[location_index].card_list_1[-1]
            del game_locations[location_index].card_list_1[-1]
            player.destroy_pool.append(card_removed)

    else:
        if len(game_locations[location_index].card_list_2) > 0:
            card_removed = game_locations[location_index].card_list_2[-1]
            del game_locations[location_index].card_list_2[-1]
            player.destroy_pool.append(card_removed)

def hala_ability(game_locations, location_index, turn_number, player1, player2):
    if turn_number == 4:
        if game_locations[location_index].total_power1 > game_locations[location_index].total_power2:
            for i in range(len(game_locations[location_index].card_list_2)):
                card_removed = game_locations[location_index].card_list_2[i]
                del game_locations[location_index].card_list_2[i]
                player2.destroy_pool.append(card_removed)

        elif game_locations[location_index].total_power1 < game_locations[location_index].total_power2:
            for i in range(len(game_locations[location_index].card_list_1)):
                card_removed = game_locations[location_index].card_list_1[i]
                del game_locations[location_index].card_list_1[i]
                player1.destroy_pool.append(card_removed)

        elif game_locations[location_index].total_power1 == game_locations[location_index].total_power2:
            return

def jotunheim_ability(game_locations, location_index, turn_number, player1, player2):
    for i in range(len(game_locations[location_index].card_list_1)):
        game_locations[location_index].card_list_1[i].base_power -= 1
    for i in range(len(game_locations[location_index].card_list_2)):
        game_locations[location_index].card_list_2[i].base_power -= 1


locations_dict = {
    "death's_domain": (deaths_domain_ability, "on_play"),
    "hala": (hala_ability, "end_of_turn"),
    "jotunheim": (jotunheim_ability, "end_of_turn")
}

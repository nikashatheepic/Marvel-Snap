import initialize_game
import cards
import random

class Player:
    def __init__(self, deck, number):
        self.deck = deck
        self.hand = []
        self.energy = 0
        self.number = number
        self.priority = False
        self.scheduled_abilities = None
        self.pending_buffs = 0
        self.destroy_pool = []
        self.discard_pool = []
        self.banished_pool = []

def create_player_data(player1_shuffled_deck, player2_shuffled_deck):
    player1, player2 = Player(player1_shuffled_deck, 1), Player(player2_shuffled_deck, 2)

    player1.hand = player1.deck[:3]
    del player1.deck[:3]
    player2.hand = player2.deck[:3]
    del player2.deck[:3]

    return player1, player2

def create_turn(game_locations,turn_number, player1, player2):
    index_to_reveal = turn_number - 1
    if index_to_reveal < len(game_locations):
        game_locations[index_to_reveal].revealed = True

    draw_card(player1)
    draw_card(player2)

    player1.energy, player2.energy = turn_number, turn_number

    choice_dict1 = receive_player_input(player1, game_locations)
    choice_dict2 = receive_player_input(player2, game_locations)

    check_priority(game_locations, player1, player2)

    return choice_dict1, choice_dict2

def check_priority(game_locations, player1, player2):

    location_winners, player1_total_power, player2_total_power = check_winner(game_locations, player1, player2)

    if location_winners.count(player1) > location_winners.count(player2):
        player1.priority = True
        player2.priority = False

    elif location_winners.count(player2) > location_winners.count(player1):
        player2.priority = True
        player1.priority = False

    elif location_winners.count(player1) == location_winners.count(player2):
        if player1_total_power > player2_total_power:
            player1.priority = True
            player2.priority = False
        elif player2_total_power > player1_total_power:
            player2.priority = True
            player1.priority = False

        else:
            prio_roll = random.randint(1, 2)
            if prio_roll == 1:
                player1.priority = True
                player2.priority = False
            else:
                player2.priority = True
                player1.priority = False

def check_winner(game_locations, player1, player2):
    player1_total_power = sum(loc.total_power1 for loc in game_locations)
    player2_total_power = sum(loc.total_power2 for loc in game_locations)

    location_winners = []
    for loc in game_locations:
        if loc.total_power1 > loc.total_power2:
            location_winners.append(player1)
        elif loc.total_power2 > loc.total_power1:
            location_winners.append(player2)
        else:
            location_winners.append(None)
    return location_winners, player1_total_power, player2_total_power

def execute_turn(choice_dict1, choice_dict2, game_locations, player1, player2):
    if player1.priority:
        for card in choice_dict1:
            play_card(card, choice_dict1, game_locations, player1)

        for card in choice_dict2:
            play_card(card, choice_dict2, game_locations, player2)

    elif player2.priority:
        for card in choice_dict2:
            play_card(card, choice_dict2, game_locations, player2)

        for card in choice_dict1:
            play_card(card, choice_dict1, game_locations, player1)

def play_card(card, choice_dict, game_locations, player):
    location_index = choice_dict[card]
    import copy
    card_obj = copy.deepcopy(cards.card_lookup[card])
    card_obj.owner = player

    if player.pending_buffs > 0:
        card_obj.base_power += player.pending_buffs
        player.pending_buffs = 0

    location = game_locations[location_index]
    if player.number == 1:
        location.card_list_1.append(card_obj)
        location.base_power1 += card_obj.base_power
    else:
        location.card_list_2.append(card_obj)
        location.base_power2 += card_obj.base_power

    if cards.card_lookup[card].type == "on_reveal":
        cards.card_lookup[card].ability(player, game_locations, location_index)

    update_ongoing(game_locations)

    check_on_play_locations(game_locations, location_index, player)

def update_ongoing(game_locations):

    for location in game_locations:
        location.ongoing_power1 = 0
        location.ongoing_power2 = 0

        p1_ongoing = [card for card in location.card_list_1 if card.type == "ongoing"]
        p1_ongoing.sort(key=lambda c: getattr(c, "priority", 0))
        for card in p1_ongoing:
            card.ability(card.owner, location)

        p2_ongoing = [card for card in location.card_list_2 if card.type == "ongoing"]
        p2_ongoing.sort(key=lambda c: getattr(c, "priority", 0))
        for card in p2_ongoing:
            card.ability(card.owner, location)

        location.total_power1 = location.base_power1 + location.ongoing_power1
        location.total_power2 = location.base_power2 + location.ongoing_power2

def draw_card(player):
    if len(player.deck) > 0 and len(player.hand) < 7:
        player.hand.append(player.deck[0])
        del player.deck[0]

def receive_player_input(player, game_locations):
    choice_dict = {}
    location_dict = {"left":0, "middle":1, "right":2}

    print(player.hand)

    while True:
        card_choice = input("Which card would you like to play? ").strip().lower()
        if card_choice == "skip":
            break

        location_choice = input("Which location would you like to play in? ").strip().lower()
        if location_choice not in location_dict:
            print("Invalid location. Please enter left, middle, or right.")
            continue

        location_capacity1 = len(game_locations[location_dict[location_choice]].card_list_1)
        location_capacity2 = len(game_locations[location_dict[location_choice]].card_list_2)

        if card_choice in cards.card_lookup and card_choice in player.hand:
            if player.energy >= cards.card_lookup[card_choice].cost:
                player.energy -= cards.card_lookup[card_choice].cost
                if player.number == 1:
                    if location_capacity1 < 4:
                        choice_dict[card_choice] = game_locations[location_dict[location_choice]].position

                        player.hand.remove(card_choice)
                        location_capacity1 += 1

                if player.number == 2:
                    if location_capacity2 < 4:
                        choice_dict[card_choice] = game_locations[location_dict[location_choice]].position

                        player.hand.remove(card_choice)
                        location_capacity2 += 1

    return choice_dict

def print_location_powers(game_locations):
    for idx, location in enumerate(game_locations):
        print(f"Location: {location.name}")
        print(f"  Player 1 base power   : {location.base_power1}")
        print(f"  Player 1 ongoing power: {location.ongoing_power1}")
        print(f"  Player 1 total power  : {location.total_power1}")
        print(f"  Player 2 base power   : {location.base_power2}")
        print(f"  Player 2 ongoing power: {location.ongoing_power2}")
        print(f"  Player 2 total power  : {location.total_power2}")
        print("-" * 40)

def main():
    game_locations, player1_shuffled_deck, player2_shuffled_deck = initialize_game.main()
    player1, player2 = create_player_data(player1_shuffled_deck,player2_shuffled_deck)

    turn_number = 1
    for turn_number in range(1, 7):  # 1, 2, 3, 4, 5, 6
        run_turn(game_locations, player1, player2, turn_number)

    game_winner = end_game(game_locations, player1, player2)
    if game_winner != None:
        print(f'The winner is: player {game_winner.number}!')
    else:
        print(f'Tie!')

def run_turn(game_locations, player1, player2, turn_number):

    for i in range(len(game_locations)):
        print(game_locations[i].name)

    choice_dict1, choice_dict2 = create_turn(game_locations, turn_number, player1, player2)
    execute_turn(choice_dict1, choice_dict2, game_locations, player1, player2)
    check_end_of_turn(game_locations, player1, player2)
    update_ongoing(game_locations)

    print_location_powers(game_locations)

def check_end_of_turn(game_locations, player1, player2):
    check_end_of_turn_cards(game_locations, player1, player2)
    check_end_of_turn_locations(game_locations)

def check_end_of_turn_cards(game_locations, player1, player2):
    if player1.priority:
        players = [player1, player2]
    elif player2.priority:
        players = [player2, player1]

    for player in players:
        for location in game_locations:
            card_list = (location.card_list_1 if player.number == 1 else location.card_list_2)

            for card in card_list:
                if card.type == "end_of_turn":
                    card.ability(card, player, game_locations, location.position)

def check_end_of_turn_locations(game_locations):
    for i in range(len(game_locations)):
        if game_locations[i].ability_type == "end_of_turn" and game_locations[i].revealed:
            game_locations[i].ability(game_locations, game_locations[i])

def check_on_play_locations(game_locations, location_index, player):
    if game_locations[location_index].revealed and game_locations[location_index].ability_type == "on_play":
        game_locations[location_index].ability(game_locations, location_index, player)

    update_ongoing(game_locations)

def end_game(game_locations, player1, player2):
    location_winners, player1_total_power, player2_total_power = check_winner(game_locations, player1, player2)

    if location_winners.count(player1) > location_winners.count(player2):
        game_winner = player1
    elif location_winners.count(player2) > location_winners.count(player1):
        game_winner = player2

    elif location_winners.count(player1) == location_winners.count(player2):
        if player1_total_power > player2_total_power:
            game_winner = player1
        elif player2_total_power > player1_total_power:
            game_winner = player2

        elif player1_total_power == player2_total_power:
            game_winner = None

    return game_winner

if __name__ == '__main__':
    main()
import initialize_game
import cards
import random

class Game:
    def __init__(self, card_order):
        self.card_order = card_order

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

def execute_turn(choice_dict1, choice_dict2, game_locations, player1, player2, game):
    if player1.priority:
        for card_obj in choice_dict1:
            play_card(card_obj, choice_dict1, game_locations, player1, game, player1, player2)
        for card_obj in choice_dict2:
            play_card(card_obj, choice_dict2, game_locations, player2, game, player1, player2)
    else:
        for card_obj in choice_dict2:
            play_card(card_obj, choice_dict2, game_locations, player2, game, player1, player2)
        for card_obj in choice_dict1:
            play_card(card_obj, choice_dict1, game_locations, player1, game, player1, player2)

def play_card(card_obj, choice_dict, game_locations, player, game, player1, player2):
    location_index = choice_dict[card_obj]
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

    card_obj.order = game.card_order + 1
    game.card_order += 1

    if card_obj.type == "on_reveal":
        card_obj.ability(player, game_locations, location_index, player1, player2, card_obj)

    update_power(game_locations)
    check_on_play_locations(game_locations, location_index, player)

def update_power(game_locations):

    for location in game_locations:
        location.base_power1 = 0
        location.base_power2 = 0
        location.ongoing_power1 = 0
        location.ongoing_power2 = 0

        for card in location.card_list_1:
            location.base_power1 += card.base_power
        for card in location.card_list_2:
            location.base_power2 += card.base_power

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
    location_dict = {"left": 0, "middle": 1, "right": 2}

    # Display hand (show card names)
    print([card.name for card in player.hand])

    while True:
        card_choice = input("Which card would you like to play? ").strip().lower()
        if card_choice == "skip":
            break

        location_choice = input("Which location would you like to play in? ").strip().lower()
        if location_choice not in location_dict:
            print("Invalid location. Please enter left, middle, or right.")
            continue

        # Find the card object in hand by name
        card_obj = next((c for c in player.hand if c.name == card_choice), None)

        if card_obj and player.energy >= card_obj.cost:
            loc_idx = location_dict[location_choice]
            location = game_locations[loc_idx]
            card_list = location.card_list_1 if player.number == 1 else location.card_list_2

            if len(card_list) < 4:
                player.energy -= card_obj.cost
                choice_dict[card_obj] = loc_idx  # Store object, not string
                player.hand.remove(card_obj)

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
    game = Game(0)

    turn_number = 1
    for turn_number in range(1, 7):  # 1, 2, 3, 4, 5, 6
        run_turn(game_locations, player1, player2, turn_number, game)

    game_winner = end_game(game_locations, player1, player2)
    if game_winner != None:
        print(f'The winner is: player {game_winner.number}!')
    else:
        print(f'Tie!')

def run_turn(game_locations, player1, player2, turn_number, game):

    for i in range(len(game_locations)):
        print(game_locations[i].name)
    print(f"Turn number: {turn_number}")

    choice_dict1, choice_dict2 = create_turn(game_locations, turn_number, player1, player2)
    execute_turn(choice_dict1, choice_dict2, game_locations, player1, player2, game)
    check_end_of_turn(game_locations, player1, player2, turn_number)
    update_power(game_locations)

    print_location_powers(game_locations)

    discard1=[]
    discard2=[]
    destroy1=[]
    destroy2=[]

    for i in range(len(player1.discard_pool)):
        discard1.append(player1.discard_pool[i].name)
    for i in range(len(player2.discard_pool)):
        discard2.append(player2.discard_pool[i].name)

    for i in range(len(player1.destroy_pool)):
        destroy1.append(player1.destroy_pool[i].name)
    for i in range(len(player2.destroy_pool)):
        destroy2.append(player2.destroy_pool[i].name)

    print(discard1,discard2,destroy1,destroy2)



def check_end_of_turn(game_locations, player1, player2, turn_number):
    check_end_of_turn_cards(game_locations, player1, player2)
    check_end_of_turn_locations(game_locations, turn_number, player1, player2)

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

def check_end_of_turn_locations(game_locations, turn_number, player1, player2):
    for i in range(len(game_locations)):
        if game_locations[i].ability_type == "end_of_turn" and game_locations[i].revealed:
            game_locations[i].ability(game_locations, i, turn_number, player1, player2)

def check_on_play_locations(game_locations, location_index, player):
    if game_locations[location_index].revealed and game_locations[location_index].ability_type == "on_play":
        game_locations[location_index].ability(game_locations, location_index, player)

    update_power(game_locations)

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

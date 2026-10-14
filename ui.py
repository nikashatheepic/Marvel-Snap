import math
import os
import arcade
from PIL import Image
import initialize_game
import engine

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
TOTAL_TURNS = 6

LOCATION_CENTERS = [260, 640, 1020]  # x position of the left, middle and right columns
POSITION_NAMES = ["left", "middle", "right"]
COLUMN_WIDTH = 350

HAND_CARD_W, HAND_CARD_H = 110, 150
HAND_BOTTOM = 30
BOARD_CARD_W, BOARD_CARD_H = 80, 110

P1_ROW_BOTTOM = 240
LOCATION_BOTTOM, LOCATION_TOP = 370, 510
P2_ROW_BOTTOM = 530

END_TURN_BUTTON = (1110, 1250, 60, 120)  # left, right, bottom, top
HELP_BUTTON = (930, 1060, 748, 788)

# Animation timings, in seconds
SLIDE_TIME = 0.45   # a card flying onto the board
STEP_TIME = 1.5     # how long each reveal step stays on screen
FIRST_STEP_TIME = 1.8
FLIP_TIME = 0.8     # a location flipping over

CARD_TEXT = {
    "iron man": "Ongoing: Your total Power is doubled here.",
    "forge": "On Reveal: The next card you play gets +2 Power.",
    "adam warlock": "End of Turn: If you're winning here, draw a card. Otherwise +1 Power.",
    "silver sable": "On Reveal: Steal 2 Power from the top card of your opponent's deck.",
    "iceman": "On Reveal: Give a random card in your opponent's hand +1 Cost.",
    "medusa": "On Reveal: If this is at the middle location, +3 Power.",
    "wolfsbane": "On Reveal: +2 Power for each other card you have here.",
    "elektra": "On Reveal: Destroy a random enemy 1-Cost card here.",
    "punisher": "Ongoing: +1 Power for each enemy card here.",
    "ant man": "Ongoing: If you have 4 cards here, +3 Power.",
    "lizard": "Ongoing: -4 Power if your opponent has 4 cards here.",
    "misty knight": "No ability. Cheap and reliable.",
    "cyclops": "No ability. Solid Power for 3 Energy.",
    "the thing": "No ability. Solid Power for 4 Energy.",
    "hulk": "No ability. Just a huge amount of Power.",
}

LOCATION_TEXT = {
    "death's_domain": "When you play a card here, destroy it.",
    "hala": "At the end of turn 4, destroy all cards at this location from the player who is losing here.",
    "jotunheim": "At the end of each turn, cards here get -1 Power.",
    "muir_island": "At the end of each turn, cards here get +1 Power.",
    "murderworld": "At the end of turn 3, destroy all cards here.",
    "asgard": "At the end of turn 4, whoever is winning here draws 2 cards.",
    "stark_tower": "At the end of turn 5, cards here get +2 Power.",
    "danger_room": "When you play a card here, there's a 25% chance it's destroyed.",
}

# End-of-turn locations that only trigger on one turn (the rest trigger every turn)
LOCATION_TRIGGER_TURN = {"hala": 4, "murderworld": 3, "asgard": 4, "stark_tower": 5}

HELP_LINES = [
    "The game lasts 6 turns. Win 2 of the 3 locations to win the game.",
    "(If that's tied, whoever has more total Power wins.)",
    "",
    "Each turn you get Energy equal to the turn number: 1 on turn 1, 2 on turn 2, and so on.",
    "Cards cost Energy (blue number) and add Power (orange number) to the location you play them at.",
    "To play a card, click it in your hand, then click a location. Each side of a location fits 4 cards.",
    "",
    "Both players choose their cards in secret, then everything is revealed at once.",
    "Whoever is winning more locations reveals their cards first.",
    "",
    "One location is revealed each turn, and each has its own special rule.",
    "Hover over any card to read what it does.",
]

BG_COLOR = (18, 20, 32)
PANEL_COLOR = (30, 34, 52, 230)
P1_COLOR = (80, 160, 255)
P2_COLOR = (255, 110, 90)
COST_COLOR = (40, 110, 230)
POWER_COLOR = (230, 140, 30)
HIGHLIGHT_COLOR = (255, 220, 80)
GAIN_COLOR = (110, 255, 140)
LOSS_COLOR = (255, 90, 90)


def pretty_name(name):
    # "death's_domain" -> "Death's Domain", "iron man" -> "Iron Man"
    return " ".join(word.capitalize() for word in name.replace("_", " ").split())


def with_alpha(color, alpha):
    return color[0], color[1], color[2], int(alpha)


def ease_out(t):
    # Starts fast and slows down at the end, which makes movement look natural
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def load_texture_if_exists(path, aspect=None):
    # aspect (width / height) crops the image to fit its box instead of stretching it
    if not os.path.exists(path):
        return None
    if aspect is None:
        return arcade.load_texture(path)

    image = Image.open(path).convert("RGBA")
    width, height = image.size
    if width / height > aspect:
        new_width = int(height * aspect)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / aspect)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))
    return arcade.Texture(image)


def card_texture_path(card_name):
    # "iron man" -> assets/cards/iron_man.png
    return os.path.join("assets", "cards", card_name.replace(" ", "_") + ".png")


def location_texture_path(location_name):
    # "death's_domain" -> assets/locations/DeathsDomain.png
    file_name = "".join(part.capitalize() for part in location_name.replace("'", "").split("_"))
    return os.path.join("assets", "locations", file_name + ".png")


text_cache = {}

def draw_text(text, x, y, color, font_size, **kwargs):
    # Building an arcade.Text is slow, so build one per text and style, then just move and recolor it
    key = (text, font_size, tuple(sorted(kwargs.items())))
    if key not in text_cache:
        text_cache[key] = arcade.Text(text, x, y, color, font_size, **kwargs)
    label = text_cache[key]
    label.position = (x, y)
    label.color = color
    label.draw()


def point_in_box(x, y, left, right, bottom, top):
    return left <= x <= right and bottom <= y <= top


def slot_box(loc_idx, slot, row_bottom):
    # Where card number `slot` (0-3) sits in a row at a location
    gap = 6
    row_width = 4 * BOARD_CARD_W + 3 * gap
    left = LOCATION_CENTERS[loc_idx] - row_width / 2 + slot * (BOARD_CARD_W + gap)
    return left, left + BOARD_CARD_W, row_bottom, row_bottom + BOARD_CARD_H


def take_snapshot(game_locations):
    # A frozen copy of the board, so the reveal can be replayed one step at a time
    return [{
        "cards1": [(card, card.base_power) for card in loc.card_list_1],
        "cards2": [(card, card.base_power) for card in loc.card_list_2],
        "power1": loc.total_power1,
        "power2": loc.total_power2,
    } for loc in game_locations]


def find_card(entries, card):
    # entries is a list of (card, power) pairs; returns that card's power, or None if it isn't there
    for entry_card, power in entries:
        if entry_card is card:
            return power
    return None


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.textures = {}
        tile_aspect = COLUMN_WIDTH / (LOCATION_TOP - LOCATION_BOTTOM)
        self.background = load_texture_if_exists(os.path.join("assets", "background.png"), WINDOW_WIDTH / WINDOW_HEIGHT)
        self.unrevealed = load_texture_if_exists(os.path.join("assets", "locations", "Unrevealed.png"), tile_aspect)
        self.mouse_x, self.mouse_y = 0, 0
        self.time = 0.0
        self.show_help = True
        self.new_game()

    # ---------- game flow ----------

    def new_game(self):
        self.game_locations, deck1, deck2 = initialize_game.main()
        self.player1, self.player2 = engine.create_player_data(deck1, deck2)
        self.game = engine.Game(0)
        self.turn_number = 1
        self.winner = None
        self.start_turn()

    def start_turn(self):
        players = (self.player1, self.player2)
        hands_before = {player.number: list(player.hand) for player in players}
        revealed_before = [loc.revealed for loc in self.game_locations]

        engine.start_turn(self.game_locations, self.turn_number, self.player1, self.player2)

        # Remember what just changed so it can be animated
        self.new_cards = {player.number: [card for card in player.hand
                                          if not any(card is old for old in hands_before[player.number])]
                          for player in players}
        self.newly_revealed = next((i for i, loc in enumerate(self.game_locations)
                                    if loc.revealed and not revealed_before[i]), None)

        self.choice_dict1 = {}
        self.choice_dict2 = {}
        self.current_player = self.player1
        self.selected_card = None
        self.message = ""
        self.state = "handoff"  # handoff -> choosing -> handoff -> choosing -> revealing -> results

    def begin_choosing(self):
        self.state = "choosing"
        self.choosing_started = self.time
        if self.newly_revealed is not None:
            name = pretty_name(self.game_locations[self.newly_revealed].name)
            self.message = f"New location revealed: {name}"
        else:
            self.message = ""

    def current_choices(self):
        return self.choice_dict1 if self.current_player.number == 1 else self.choice_dict2

    def end_player_turn(self):
        self.selected_card = None
        self.message = ""
        if self.current_player.number == 1:
            self.current_player = self.player2
            self.state = "handoff"
        else:
            self.resolve_turn()

    def resolve_turn(self):
        p1, p2 = self.player1, self.player2
        location_winners, power1, power2 = engine.check_winner(self.game_locations, p1, p2)
        before = take_snapshot(self.game_locations)
        steps = []

        def on_step(event, card=None, player=None, loc_idx=None):
            # Called by the engine after each card is played, and once after end-of-turn effects
            snapshot = take_snapshot(self.game_locations)
            if event == "play":
                location = self.game_locations[loc_idx]
                if location.revealed:
                    where = f"at {pretty_name(location.name)}"
                else:
                    where = f"at the {POSITION_NAMES[loc_idx]} location"
                side = "cards1" if player.number == 1 else "cards2"
                if find_card(snapshot[loc_idx][side], card) is None:
                    detail = f"{pretty_name(location.name)} destroyed it!"
                else:
                    detail = CARD_TEXT.get(card.name, "")
                steps.append({"snapshot": snapshot, "duration": STEP_TIME, "played": (card, player.number, loc_idx),
                              "caption": f"Player {player.number} plays {pretty_name(card.name)} {where}",
                              "detail": detail})
            elif event == "end_of_turn":
                triggers = self.end_of_turn_triggers()
                if triggers:
                    steps.append({"snapshot": snapshot, "duration": STEP_TIME, "played": None,
                                  "caption": "End of turn", "detail": "Triggered: " + ", ".join(triggers)})

        destroyed_before = len(p1.destroy_pool) + len(p2.destroy_pool)
        engine.resolve_turn(self.choice_dict1, self.choice_dict2, self.game_locations,
                            p1, p2, self.turn_number, self.game, on_step)
        destroyed = (p1.destroy_pool + p2.destroy_pool)[destroyed_before:]

        # Explain who revealed first, using the board as it was before this turn's cards
        first = p1 if p1.priority else p2
        if location_winners.count(p1) != location_winners.count(p2):
            reason = "They're winning more locations, so their cards are revealed first."
        elif power1 != power2:
            reason = "Locations are tied, but they have more total Power, so they go first."
        else:
            reason = "The board is tied, so a coin flip decided who goes first."
        if not self.choice_dict1 and not self.choice_dict2:
            first_caption, reason = "Nobody played a card this turn", ""
        else:
            first_caption = f"Revealing cards: Player {first.number} goes first"
        steps.insert(0, {"snapshot": before, "duration": FIRST_STEP_TIME, "played": None,
                         "caption": first_caption, "detail": reason})

        self.steps = steps
        self.step_index = 0
        self.step_started = self.time
        self.state = "revealing"
        self.destroyed_message = ""
        if destroyed:
            self.destroyed_message = "Destroyed this turn: " + ", ".join(pretty_name(card.name) for card in destroyed)

    def end_of_turn_triggers(self):
        names = []
        for location in self.game_locations:
            if location.revealed and location.ability_type == "end_of_turn":
                if LOCATION_TRIGGER_TURN.get(location.name, self.turn_number) == self.turn_number:
                    names.append(pretty_name(location.name))
            for card in location.card_list_1 + location.card_list_2:
                if card.type == "end_of_turn":
                    names.append(f"{pretty_name(card.name)} (Player {card.owner.number})")
        return names

    def next_step(self):
        self.step_index += 1
        self.step_started = self.time
        if self.step_index >= len(self.steps):
            self.finish_reveal()

    def finish_reveal(self):
        self.message = self.destroyed_message
        if self.turn_number == TOTAL_TURNS:
            self.winner = engine.end_game(self.game_locations, self.player1, self.player2)
            self.state = "game_over"
        else:
            self.state = "results"

    def queue_card(self, card, loc_idx):
        player = self.current_player
        choices = self.current_choices()

        if card.cost > player.energy:
            self.message = f"Not enough energy to play {pretty_name(card.name)}."
            return
        if not engine.location_has_room(self.game_locations, loc_idx, player, choices):
            self.message = "That location is full."
            return

        player.energy -= card.cost
        choices[card] = loc_idx
        player.hand.remove(card)
        self.selected_card = None
        self.message = ""

    def unqueue_card(self, card):
        # Take back a card you queued this turn
        choices = self.current_choices()
        del choices[card]
        self.current_player.energy += card.cost
        self.current_player.hand.append(card)
        self.message = ""

    def on_update(self, delta_time):
        self.time += delta_time
        if self.state == "revealing" and self.time - self.step_started >= self.steps[self.step_index]["duration"]:
            self.next_step()

    # ---------- layout helpers ----------

    def hand_card_boxes(self):
        hand = self.current_player.hand
        gap = 14
        total_width = len(hand) * HAND_CARD_W + (len(hand) - 1) * gap
        left = (WINDOW_WIDTH - total_width) / 2 - 60
        boxes = []
        for i, card in enumerate(hand):
            card_left = left + i * (HAND_CARD_W + gap)
            boxes.append((card, card_left, card_left + HAND_CARD_W, HAND_BOTTOM, HAND_BOTTOM + HAND_CARD_H))
        return boxes

    def own_row_bottom(self):
        return P1_ROW_BOTTOM if self.current_player.number == 1 else P2_ROW_BOTTOM

    def own_cards_at(self, loc_idx):
        return self.game_locations[loc_idx].cards_of(self.current_player)

    def queued_card_boxes(self, loc_idx):
        # Queued cards sit after the cards already played on your side
        queued = [card for card, idx in self.current_choices().items() if idx == loc_idx]
        first_slot = len(self.own_cards_at(loc_idx))
        return [(card, *slot_box(loc_idx, first_slot + i, self.own_row_bottom())) for i, card in enumerate(queued)]

    def board_card_boxes(self):
        boxes = []
        for loc_idx, location in enumerate(self.game_locations):
            for cards, row_bottom in ((location.card_list_1, P1_ROW_BOTTOM), (location.card_list_2, P2_ROW_BOTTOM)):
                for slot, card in enumerate(cards):
                    boxes.append((card, *slot_box(loc_idx, slot, row_bottom)))
        return boxes

    def column_box(self, loc_idx):
        center = LOCATION_CENTERS[loc_idx]
        return center - COLUMN_WIDTH / 2, center + COLUMN_WIDTH / 2, P1_ROW_BOTTOM, P2_ROW_BOTTOM + BOARD_CARD_H

    def get_texture(self, path, aspect=None):
        if path not in self.textures:
            self.textures[path] = load_texture_if_exists(path, aspect)
        return self.textures[path]

    # ---------- drawing ----------

    def on_draw(self):
        self.clear(color=BG_COLOR)
        if self.background:
            arcade.draw_texture_rect(self.background, arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), alpha=70)

        # While revealing, draw the board as it was at the current step instead of how it ends up
        if self.state == "revealing":
            step = self.steps[self.step_index]
            board = step["snapshot"]
            previous = self.steps[self.step_index - 1]["snapshot"] if self.step_index > 0 else None
            elapsed = self.time - self.step_started
        else:
            step, board, previous, elapsed = None, take_snapshot(self.game_locations), None, 0

        self.draw_top_bar()
        for loc_idx in range(len(self.game_locations)):
            self.draw_location_column(loc_idx, board, previous, step, elapsed)

        if self.state == "choosing":
            self.draw_hand()
            self.draw_button(END_TURN_BUTTON, "End Turn")
        elif self.state == "revealing":
            self.draw_caption(step)
        elif self.state == "results":
            self.draw_button(END_TURN_BUTTON, "Next Turn")
        elif self.state == "game_over":
            self.draw_game_over()
        elif self.state == "handoff":
            self.draw_handoff()

        if self.message and self.state != "revealing":
            draw_text(self.message, WINDOW_WIDTH / 2, 700, HIGHLIGHT_COLOR, 15, anchor_x="center", bold=True)

        if self.state in ("choosing", "results", "game_over") and not self.show_help:
            self.draw_tooltip()
        if self.show_help:
            self.draw_help()

    def draw_top_bar(self):
        arcade.draw_lrbt_rectangle_filled(0, WINDOW_WIDTH, 735, WINDOW_HEIGHT, PANEL_COLOR)
        draw_text(f"Turn {self.turn_number} / {TOTAL_TURNS}", 24, 760, arcade.color.WHITE, 20, bold=True)

        if self.state == "choosing":
            player = self.current_player
            color = P1_COLOR if player.number == 1 else P2_COLOR
            draw_text(f"Player {player.number} is choosing  -  Energy: {player.energy}",
                      WINDOW_WIDTH / 2 - 60, 760, color, 18, anchor_x="center", bold=True)
        elif self.state == "revealing":
            draw_text("Revealing cards...", WINDOW_WIDTH / 2 - 60, 760, arcade.color.WHITE, 18,
                      anchor_x="center", bold=True)
        elif self.state == "results":
            draw_text("Turn over", WINDOW_WIDTH / 2 - 60, 760, arcade.color.WHITE, 18, anchor_x="center", bold=True)

        self.draw_button(HELP_BUTTON, "How to play", font_size=13)
        draw_text("Player 2 (top)", WINDOW_WIDTH - 24, 770, P2_COLOR, 13, anchor_x="right", bold=True)
        draw_text("Player 1 (bottom)", WINDOW_WIDTH - 24, 748, P1_COLOR, 13, anchor_x="right", bold=True)

    def draw_location_column(self, loc_idx, board, previous, step, elapsed):
        here = board[loc_idx]
        before = previous[loc_idx] if previous else None
        progress = elapsed / SLIDE_TIME

        # Highlight columns you can drop the selected card into
        if self.state == "choosing" and self.selected_card is not None:
            col_left, col_right, col_bottom, col_top = self.column_box(loc_idx)
            if engine.location_has_room(self.game_locations, loc_idx, self.current_player, self.current_choices()):
                arcade.draw_lrbt_rectangle_outline(col_left, col_right, col_bottom - 6, col_top + 6,
                                                   HIGHLIGHT_COLOR, 3)

        tile_finished = self.draw_location_tile(loc_idx)
        if tile_finished:
            self.draw_lead_label(loc_idx, here)

        # Power totals: Player 2 at the top of the tile, Player 1 at the bottom
        left = LOCATION_CENTERS[loc_idx] - COLUMN_WIDTH / 2
        for key, y, color in (("power2", LOCATION_TOP - 24, P2_COLOR), ("power1", LOCATION_BOTTOM + 24, P1_COLOR)):
            changed = before is not None and before[key] != here[key]
            pulse = math.sin(math.pi * min(1.0, progress)) if changed else 0
            self.draw_power_badge(left + 26, y, here[key], color, pulse)
            if changed:
                self.draw_floating_number(here[key] - before[key], left + 64, y - 8, elapsed)

        for side, number, row_bottom in (("cards2", 2, P2_ROW_BOTTOM), ("cards1", 1, P1_ROW_BOTTOM)):
            self.draw_card_row(loc_idx, side, number, row_bottom, here, before, step, elapsed)

        # Cards the current player has queued this turn (only they can see these)
        if self.state == "choosing":
            for card, c_left, c_right, c_bottom, c_top in self.queued_card_boxes(loc_idx):
                self.draw_card_face(card, c_left, c_right, c_bottom, c_top, small=True, queued=True)

    def draw_card_row(self, loc_idx, side, number, row_bottom, here, before, step, elapsed):
        cards = here[side]
        old_cards = before[side] if before else None
        progress = elapsed / SLIDE_TIME
        # Cards fly in from their owner's side of the screen
        start_y = -BOARD_CARD_H - 20 if number == 1 else WINDOW_HEIGHT + 20

        for slot, (card, power) in enumerate(cards):
            left, right, bottom, top = slot_box(loc_idx, slot, row_bottom)
            old_power = find_card(old_cards, card) if old_cards is not None else power
            if old_cards is not None and old_power is None:
                offset = (start_y - bottom) * (1 - ease_out(progress))
                bottom, top = bottom + offset, top + offset
            self.draw_card_face(card, left, right, bottom, top, small=True, power=power)
            if old_power is not None and old_power != power:
                self.draw_floating_number(power - old_power, (left + right) / 2, (bottom + top) / 2 - 20, elapsed)

        # Cards that were here last step but are gone now were destroyed
        if old_cards is not None:
            for slot, (card, power) in enumerate(old_cards):
                if find_card(cards, card) is None:
                    self.draw_destroyed_card(card, power, slot_box(loc_idx, slot, row_bottom), progress)

        # A card destroyed the moment it was played (Death's Domain): fly it in, then destroy it
        if step and step["played"]:
            card, played_by, played_loc = step["played"]
            if played_loc == loc_idx and played_by == number and find_card(cards, card) is None:
                left, right, bottom, top = slot_box(loc_idx, len(cards), row_bottom)
                if progress < 1.3:
                    offset = (start_y - bottom) * (1 - ease_out(progress))
                    self.draw_card_face(card, left, right, bottom + offset, top + offset, small=True)
                else:
                    destroy_progress = (elapsed - 1.3 * SLIDE_TIME) / SLIDE_TIME
                    self.draw_destroyed_card(card, card.base_power, (left, right, bottom, top), destroy_progress)

    def draw_location_tile(self, loc_idx):
        # Returns True once the tile is fully drawn (not partway through flipping)
        location = self.game_locations[loc_idx]
        center = LOCATION_CENTERS[loc_idx]
        tile_aspect = COLUMN_WIDTH / (LOCATION_TOP - LOCATION_BOTTOM)

        # A newly revealed location flips over: it shrinks to a sliver, swaps faces, then grows back
        flip_t = 1.0
        if loc_idx == self.newly_revealed and self.state == "choosing":
            flip_t = (self.time - self.choosing_started) / FLIP_TIME
        flipping = flip_t < 1
        shows_front = location.revealed and flip_t >= 0.5
        width_scale = max(abs(math.cos(math.pi * flip_t)), 0.03) if flipping else 1

        half = COLUMN_WIDTH / 2 * width_scale
        left, right = center - half, center + half
        arcade.draw_lrbt_rectangle_filled(left, right, LOCATION_BOTTOM, LOCATION_TOP, PANEL_COLOR)
        if shows_front:
            texture = self.get_texture(location_texture_path(location.name), tile_aspect)
        else:
            texture = self.unrevealed
        if texture:
            arcade.draw_texture_rect(texture, arcade.LRBT(left, right, LOCATION_BOTTOM, LOCATION_TOP),
                                     alpha=90 if shows_front else 50)

        # Glow around a location for a moment after it's revealed
        glow = loc_idx == self.newly_revealed and self.state == "choosing" and 1 <= flip_t < 3
        border_color = HIGHLIGHT_COLOR if glow else arcade.color.GRAY
        arcade.draw_lrbt_rectangle_outline(left, right, LOCATION_BOTTOM, LOCATION_TOP, border_color, 4 if glow else 2)

        if flipping:
            return False

        if location.revealed:
            draw_text(pretty_name(location.name), center, LOCATION_TOP - 32, arcade.color.WHITE, 17,
                      anchor_x="center", bold=True)
            draw_text(LOCATION_TEXT.get(location.name, ""), center, LOCATION_TOP - 48,
                      arcade.color.LIGHT_GRAY, 11, anchor_x="center", anchor_y="top",
                      width=COLUMN_WIDTH - 70, align="center", multiline=True)
        else:
            draw_text("Unrevealed", center, (LOCATION_BOTTOM + LOCATION_TOP) / 2 + 8, arcade.color.WHITE, 16,
                      anchor_x="center", anchor_y="center", bold=True)
            draw_text(f"Reveals on turn {loc_idx + 1}", center, LOCATION_BOTTOM + 38, arcade.color.LIGHT_GRAY,
                      11, anchor_x="center")
        return True

    def draw_lead_label(self, loc_idx, here):
        if here["power1"] > here["power2"]:
            text, color = "Player 1 leads", P1_COLOR
        elif here["power2"] > here["power1"]:
            text, color = "Player 2 leads", P2_COLOR
        elif here["cards1"] or here["cards2"]:
            text, color = "Tied", arcade.color.LIGHT_GRAY
        else:
            return
        draw_text(text, LOCATION_CENTERS[loc_idx], LOCATION_BOTTOM + 12, color, 12, anchor_x="center", bold=True)

    def draw_power_badge(self, x, y, power, color, pulse=0):
        radius = 18 + 7 * pulse
        if pulse > 0:
            arcade.draw_circle_filled(x, y, radius + 8, with_alpha(HIGHLIGHT_COLOR, 120 * pulse))
        arcade.draw_circle_filled(x, y, radius, color)
        draw_text(str(power), x, y, arcade.color.WHITE, 14, anchor_x="center", anchor_y="center", bold=True)

    def draw_floating_number(self, change, x, y, elapsed):
        # "+2" or "-1" that drifts upward and fades out
        t = min(1.0, elapsed / STEP_TIME)
        alpha = 255 if t < 0.6 else 255 * (1 - t) / 0.4
        color = GAIN_COLOR if change > 0 else LOSS_COLOR
        text = f"+{change}" if change > 0 else str(change)
        y += 25 * ease_out(t)
        draw_text(text, x + 2, y - 2, with_alpha(arcade.color.BLACK, alpha), 20, anchor_x="center", bold=True)
        draw_text(text, x, y, with_alpha(color, alpha), 20, anchor_x="center", bold=True)

    def draw_destroyed_card(self, card, power, box, progress):
        # Flash red, sink a little and fade away
        t = max(0.0, min(1.0, progress))
        left, right, bottom, top = box
        sink = 25 * t
        alpha = 255 * (1 - t)
        self.draw_card_face(card, left, right, bottom - sink, top - sink, small=True, power=power, alpha=alpha)
        arcade.draw_lrbt_rectangle_filled(left, right, bottom - sink, top - sink, with_alpha(LOSS_COLOR, 170 * (1 - t)))
        if t < 0.9:
            draw_text("DESTROYED", (left + right) / 2, (bottom + top) / 2 - sink, with_alpha(arcade.color.WHITE, alpha),
                      9, anchor_x="center", anchor_y="center", bold=True)

    def draw_card_face(self, card, left, right, bottom, top, small=False, selected=False, queued=False,
                       power=None, alpha=255):
        if power is None:
            power = card.base_power
        if queued:
            alpha = min(alpha, 150)
        width = right - left
        white = with_alpha(arcade.color.WHITE, alpha)
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (45, 48, 70, alpha))

        texture = self.get_texture(card_texture_path(card.name))
        if texture:
            arcade.draw_texture_rect(texture, arcade.LRBT(left + 3, right - 3, top - width + 3, top - 3), alpha=alpha)
        else:
            draw_text(pretty_name(card.type), (left + right) / 2, top - width / 2, with_alpha(arcade.color.GRAY, alpha),
                      8 if small else 10, anchor_x="center", anchor_y="center", italic=True)

        draw_text(pretty_name(card.name), (left + right) / 2, bottom + (5 if small else 10), white,
                  8 if small else 11, anchor_x="center", anchor_y="bottom", bold=True,
                  width=int(width) - 4, align="center", multiline=True)

        radius = 10 if small else 15
        badge_size = 10 if small else 14
        arcade.draw_circle_filled(left + radius, top - radius, radius, with_alpha(COST_COLOR, alpha))
        draw_text(str(card.cost), left + radius, top - radius, white, badge_size,
                  anchor_x="center", anchor_y="center", bold=True)
        arcade.draw_circle_filled(right - radius, top - radius, radius, with_alpha(POWER_COLOR, alpha))
        draw_text(str(power), right - radius, top - radius, white, badge_size,
                  anchor_x="center", anchor_y="center", bold=True)

        if selected:
            border_color, border_width = HIGHLIGHT_COLOR, 4
        elif queued:
            border_color, border_width = HIGHLIGHT_COLOR, 1
        else:
            border_color, border_width = arcade.color.GRAY, 1
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, with_alpha(border_color, alpha), border_width)

        if queued:
            draw_text("click to undo", (left + right) / 2, bottom - 12, HIGHLIGHT_COLOR, 8, anchor_x="center")

    def draw_hand(self):
        player = self.current_player
        color = P1_COLOR if player.number == 1 else P2_COLOR
        draw_text(f"Player {player.number}'s hand", 24, 205, color, 14, bold=True)
        draw_text(f"Cards left in deck: {len(player.deck)}", 24, 186, arcade.color.LIGHT_GRAY, 11)

        if not player.hand:
            draw_text("(no cards in hand)", WINDOW_WIDTH / 2 - 60, 100, arcade.color.GRAY, 14, anchor_x="center")

        slide = ease_out((self.time - self.choosing_started) / SLIDE_TIME)
        for card, left, right, bottom, top in self.hand_card_boxes():
            is_new = any(card is new for new in self.new_cards[player.number])
            if is_new:
                # Newly drawn cards slide in from the right edge
                offset = (WINDOW_WIDTH + 20 - left) * (1 - slide)
                left, right = left + offset, right + offset
            if point_in_box(self.mouse_x, self.mouse_y, left, right, bottom, top) or card is self.selected_card:
                bottom, top = bottom + 12, top + 12  # lift the card you're pointing at

            self.draw_card_face(card, left, right, bottom, top, selected=(card is self.selected_card))
            if card.cost > player.energy:
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (0, 0, 0, 140))
            if is_new:
                arcade.draw_lrbt_rectangle_filled(left + 30, right - 30, top + 4, top + 22, HIGHLIGHT_COLOR)
                draw_text("NEW", (left + right) / 2, top + 13, arcade.color.BLACK, 10,
                          anchor_x="center", anchor_y="center", bold=True)

        if self.selected_card is None:
            hint = "Click a card, then click a location to play it."
        else:
            hint = f"Click a location to play {pretty_name(self.selected_card.name)}."
        draw_text(hint, 24, 10, arcade.color.LIGHT_GRAY, 11)

    def draw_caption(self, step):
        arcade.draw_lrbt_rectangle_filled(190, 1090, 652, 728, (10, 12, 24, 220))
        arcade.draw_lrbt_rectangle_outline(190, 1090, 652, 728, HIGHLIGHT_COLOR, 1)
        draw_text(step["caption"], WINDOW_WIDTH / 2, 700, HIGHLIGHT_COLOR, 17, anchor_x="center", bold=True)
        if step["detail"]:
            draw_text(step["detail"], WINDOW_WIDTH / 2, 670, arcade.color.WHITE, 13, anchor_x="center")
        draw_text(f"step {self.step_index + 1} of {len(self.steps)}  -  click to skip ahead", 1080, 657,
                  arcade.color.GRAY, 9, anchor_x="right")

    def draw_tooltip(self):
        boxes = self.board_card_boxes()
        if self.state == "choosing":
            boxes = self.hand_card_boxes() + boxes
        for card, left, right, bottom, top in boxes:
            if point_in_box(self.mouse_x, self.mouse_y, left, right, bottom, top):
                tip_left = min(left, WINDOW_WIDTH - 280)
                tip_bottom = top + 16
                arcade.draw_lrbt_rectangle_filled(tip_left, tip_left + 260, tip_bottom, tip_bottom + 64, (10, 10, 20, 240))
                arcade.draw_lrbt_rectangle_outline(tip_left, tip_left + 260, tip_bottom, tip_bottom + 64,
                                                   arcade.color.GRAY, 1)
                draw_text(pretty_name(card.name), tip_left + 8, tip_bottom + 56, HIGHLIGHT_COLOR, 11,
                          anchor_y="top", bold=True)
                draw_text(CARD_TEXT.get(card.name, ""), tip_left + 8, tip_bottom + 38, arcade.color.WHITE, 10,
                          anchor_y="top", width=244, multiline=True)
                return

    def draw_button(self, box, label, font_size=16):
        left, right, bottom, top = box
        hovered = point_in_box(self.mouse_x, self.mouse_y, left, right, bottom, top)
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (230, 180, 40) if hovered else (200, 150, 30))
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.WHITE, 2)
        draw_text(label, (left + right) / 2, (bottom + top) / 2, arcade.color.BLACK, font_size,
                  anchor_x="center", anchor_y="center", bold=True)

    def draw_overlay(self, title, subtitle, color):
        arcade.draw_lrbt_rectangle_filled(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, (0, 0, 0, 220))
        draw_text(title, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 30, color, 34, anchor_x="center", bold=True)
        draw_text(subtitle, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 25, arcade.color.LIGHT_GRAY, 16, anchor_x="center")

    def draw_handoff(self):
        # Covers the screen so the next player can't see the other player's hand
        number = self.current_player.number
        color = P1_COLOR if number == 1 else P2_COLOR
        self.draw_overlay(f"Player {number}'s turn", "Hand the screen over, then click anywhere to continue.", color)

    def draw_help(self):
        arcade.draw_lrbt_rectangle_filled(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, (0, 0, 0, 200))
        arcade.draw_lrbt_rectangle_filled(160, 1120, 120, 690, (24, 28, 46, 250))
        arcade.draw_lrbt_rectangle_outline(160, 1120, 120, 690, HIGHLIGHT_COLOR, 2)
        draw_text("How to play", WINDOW_WIDTH / 2, 640, HIGHLIGHT_COLOR, 28, anchor_x="center", bold=True)
        y = 590
        for line in HELP_LINES:
            draw_text(line, 210, y, arcade.color.WHITE, 14)
            y -= 32 if line else 16
        draw_text("Click anywhere to start", WINDOW_WIDTH / 2, 150, arcade.color.LIGHT_GRAY, 14,
                  anchor_x="center", bold=True)

    def draw_game_over(self):
        if self.winner is None:
            title, color = "It's a tie!", arcade.color.WHITE
        else:
            title = f"Player {self.winner.number} wins!"
            color = P1_COLOR if self.winner.number == 1 else P2_COLOR
        arcade.draw_lrbt_rectangle_filled(340, 940, 40, 190, (0, 0, 0, 220))
        draw_text(title, WINDOW_WIDTH / 2, 130, color, 32, anchor_x="center", bold=True)
        draw_text("Click anywhere to play again.", WINDOW_WIDTH / 2, 75, arcade.color.LIGHT_GRAY, 14,
                  anchor_x="center")

    # ---------- input ----------

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x, self.mouse_y = x, y

    def on_mouse_press(self, x, y, button, modifiers):
        if self.show_help:
            self.show_help = False
            return
        if point_in_box(x, y, *HELP_BUTTON):
            self.show_help = True
            return

        if self.state == "handoff":
            self.begin_choosing()
            return

        if self.state == "revealing":
            self.next_step()
            return

        if self.state == "game_over":
            self.new_game()
            return

        if self.state == "results":
            if point_in_box(x, y, *END_TURN_BUTTON):
                self.turn_number += 1
                self.start_turn()
            return

        # state == "choosing"
        if point_in_box(x, y, *END_TURN_BUTTON):
            self.end_player_turn()
            return

        for card, left, right, bottom, top in self.hand_card_boxes():
            if point_in_box(x, y, left, right, bottom, top):
                self.selected_card = None if card is self.selected_card else card
                self.message = ""
                return

        for loc_idx in range(len(self.game_locations)):
            for card, left, right, bottom, top in self.queued_card_boxes(loc_idx):
                if point_in_box(x, y, left, right, bottom, top):
                    self.unqueue_card(card)
                    return

        if self.selected_card is not None:
            for loc_idx in range(len(self.game_locations)):
                if point_in_box(x, y, *self.column_box(loc_idx)):
                    self.queue_card(self.selected_card, loc_idx)
                    return


def main():
    # Image paths are relative, so run from the project folder no matter where this is launched from
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Marvel Snap")
    window.show_view(GameView())
    arcade.run()


if __name__ == "__main__":
    main()

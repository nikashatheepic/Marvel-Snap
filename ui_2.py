import engine
from engine import *
from cards import *
from decks import *
from locations import *
import pygame
import sys

def main():
    pygame.init()
    WIDTH, HEIGHT = 1000, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Marvel Snap")

    clock = pygame.time.Clock()
    running = True

    background = pygame.image.load("assets/background.png").convert()
    background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))

    location_image = pygame.image.load("assets/locations/unrevealed.png").convert_alpha()
    LOCATION_WIDTH = 125
    LOCATION_HEIGHT = 125

    location_image = pygame.transform.smoothscale(
        location_image,
        (LOCATION_WIDTH, LOCATION_HEIGHT)
    )

    location_y = (HEIGHT - LOCATION_HEIGHT) // 2

    location_positions = [
        (200, location_y),  # left
        ((WIDTH - LOCATION_WIDTH) // 2, location_y),  # middle
        (WIDTH - LOCATION_WIDTH - 200, location_y)  # right
    ]

    font = pygame.font.SysFont(None, 28)

    PANEL_HEIGHT = 200
    panel_y = HEIGHT - PANEL_HEIGHT

    CARD_WIDTH = 90
    CARD_HEIGHT = 130

    card_images = {}

    player_hand = [iron_man, forge]

    for card in player_hand:
        filename = card.name.lower().replace(" ", "_") + ".png"
        path = f"assets/cards/{filename}"

        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.smoothscale(image, (CARD_WIDTH, CARD_HEIGHT))

        card_images[card] = image


    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.blit(background, (0, 0))

            for pos in location_positions:
                screen.blit(location_image, pos)

            card_surfaces = [card_images[card] for card in player_hand]

            CARD_GAP = 20
            total_width = sum(card.get_width() for card in card_surfaces)
            total_width += CARD_GAP * (len(card_surfaces) - 1)

            start_x = (WIDTH - total_width) // 2
            card_y = panel_y + (PANEL_HEIGHT - CARD_HEIGHT) // 2

            x = start_x
            for card_image in card_surfaces:
                screen.blit(card_image, (x, card_y))
                x += card_image.get_width() + CARD_GAP

            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
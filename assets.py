import pygame

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)

def load_image_with_opacity(path, size=None, alpha=180):
    image = pygame.image.load(path)
    if size:
        image = pygame.transform.scale(image, size)
    image.set_alpha(alpha)
    return image

# Level 1 and Level 2 shared assets
background_image = load_image_with_opacity("assets/backview3.png")
new_background_image = load_image_with_opacity("assets/backview2.jpg")
pin_image = pygame.image.load("assets/pin.png")
hero_image = pygame.image.load("assets/dethero.png")
suspect_image = pygame.image.load("assets/suspect.jpg")
suspect_large_image = pygame.image.load("assets/suspect.jpg")
level_image = pygame.image.load("assets/inspectorStart.png")
intro_background = load_image_with_opacity("assets/story.png")
detective_bg1 = load_image_with_opacity("assets/detective.png")
detective_bg2 = load_image_with_opacity("assets/detective2.png")
detective_bg3 = load_image_with_opacity("assets/detective3.png")
won_bg = load_image_with_opacity("assets/won.jpg")
lost_bg = load_image_with_opacity("assets/lost.png")
menu_bg = load_image_with_opacity("assets/inspectorStart.png") 
hallway_image = pygame.image.load("assets/hallway.png")

# Level 1 clue assets
logbook = pygame.Surface((60, 80), pygame.SRCALPHA)
logbook.fill((139, 69, 19))
pygame.draw.rect(logbook, BLACK, (0, 0, 60, 80), 2)
pygame.draw.line(logbook, WHITE, (10, 20), (50, 20), 2)
pygame.draw.line(logbook, WHITE, (10, 40), (50, 40), 2)

glass = pygame.Surface((50, 70), pygame.SRCALPHA)
pygame.draw.polygon(glass, (173, 216, 230), [(25, 0), (50, 20), (40, 70), (10, 70), (0, 20)])

note = pygame.Surface((70, 50), pygame.SRCALPHA)
note.fill((245, 245, 220))
pygame.draw.rect(note, BLACK, (0, 0, 70, 50), 2)
pygame.draw.line(note, BLACK, (10, 25), (60, 25), 1)

# Level 2 clue assets
cloth = pygame.Surface((70, 60), pygame.SRCALPHA)
cloth.fill((220, 220, 220))  # Off-white cloth
pygame.draw.rect(cloth, BLACK, (0, 0, 70, 60), 2)
pygame.draw.circle(cloth, RED, (35, 30), 15)  # Blood stain

key = pygame.Surface((60, 30), pygame.SRCALPHA)
pygame.draw.rect(key, (169, 169, 169), (0, 0, 40, 20))  # Key shaft
pygame.draw.circle(key, (169, 169, 169), (50, 15), 10)  # Key head
pygame.draw.line(key, BLACK, (20, 15), (30, 15), 2)  # Break in shaft

letter = pygame.Surface((80, 50), pygame.SRCALPHA)
letter.fill((230, 230, 230))  # Parchment-like paper
pygame.draw.rect(letter, BLACK, (0, 0, 80, 50), 2)
pygame.draw.line(letter, BLACK, (15, 20), (65, 20), 1)  # Code line
pygame.draw.line(letter, BLACK, (15, 30), (65, 30), 1)  # Code line
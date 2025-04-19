import pygame

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def load_image_with_opacity(path, size=None, alpha=180):
    image = pygame.image.load(path)
    if size:
        image = pygame.transform.scale(image, size)
    image.set_alpha(alpha)
    return image

background_image = load_image_with_opacity("assets/backview3.png")
new_background_image = load_image_with_opacity("assets/backview2.jpg")
pin_image = pygame.image.load("assets/pin.png")
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

# Clue assets
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
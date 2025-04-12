import pygame

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
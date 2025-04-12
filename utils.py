import pygame

def draw_button(screen, rect, color, hover_color, text, font, mouse_pos, pulse=False):
    hover = rect.collidepoint(mouse_pos)
    if pulse and not hover:
        scale = 1.0 + 0.05 * abs(pygame.time.get_ticks() % 1000 - 500) / 500
        new_width = int(rect.width * scale)
        new_height = int(rect.height * scale)
        button_rect = pygame.Rect(0, 0, new_width, new_height)
        button_rect.center = rect.center
    else:
        button_rect = rect

    pygame.draw.rect(screen, hover_color if hover else color, button_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, 2, border_radius=10)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
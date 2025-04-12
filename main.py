import pygame
import sys
import time
from views import main_menu
from speech import text_to_speech, speech_engine
from config import WHITE, BLACK

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Start in fullscreen
pygame.display.set_caption("Deep Veil")

def initial_welcome(screen):
    font = pygame.font.Font(None, 60)
    welcome_text_en = "Welcome to Deep Veil, an AI detective game"
    welcome_text_ar = "مرحبًا بك في ديب فيل، لعبة محقق ذكاء اصطناعي"
    language = "English"  # Default, updated by menu later
    text_to_speech(welcome_text_en, language)  # Voice plays immediately
    alpha = 0
    fade_in = True
    start_time = time.time()
    
    while time.time() - start_time < 5:  # Changed to 5 seconds
        speech_engine.iterate()  # Process voice
        screen.fill(BLACK)
        welcome_surface = font.render(welcome_text_en if language == "English" else welcome_text_ar, True, WHITE)
        welcome_surface.set_alpha(alpha)
        screen.blit(welcome_surface, welcome_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
        pygame.display.flip()
        
        if fade_in:
            alpha += 10
            if alpha >= 255:
                fade_in = False
                time.sleep(1)  # Reduced from 2 to 1 to fit 5-second total
        else:
            alpha -= 10
        time.sleep(0.03)

if __name__ == "__main__":
    try:
        initial_welcome(screen)  # Show welcome before anything else
        main_menu(screen)
    finally:
        pygame.quit()
        sys.exit()
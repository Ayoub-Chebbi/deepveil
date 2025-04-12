import pygame
import time
from config import WIDTH, HEIGHT, translations, WHITE, BLACK, BLUE, BLUE_HOVER, RED, RED_HOVER, GREEN, GREEN_HOVER, LIGHT_GRAY, DARK_GRAY, INTERROGATE_BG, INTERROGATE_TEXT
from assets import intro_background, suspect_large_image, won_bg, lost_bg, menu_bg
from speech import text_to_speech, stop_speech, speech_engine
from utils import draw_button

def main_menu(screen):
    from game import run_game
    font = pygame.font.Font(None, 36)
    button_width, button_height = 250, 60
    start_button = pygame.Rect(0, 0, button_width, button_height)
    start_button.center = (screen.get_width() // 2, screen.get_height() // 2 - 120)
    language_button = pygame.Rect(0, 0, button_width, button_height)
    language_button.center = (screen.get_width() // 2, screen.get_height() // 2 - 20)
    sound_button = pygame.Rect(0, 0, button_width, button_height)
    sound_button.center = (screen.get_width() // 2, screen.get_height() // 2 + 80)
    languages = ["English", "Arabic"]
    language_selected = languages[0]
    dropdown_open = False
    sound_open = False
    master_volume = 1.0
    voice_enabled = True

    running = True
    while running:
        speech_engine.iterate()
        screen.blit(pygame.transform.scale(menu_bg, screen.get_size()), (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        draw_button(screen, start_button, BLUE, BLUE_HOVER, translations[language_selected]["Start"], font, mouse_pos)
        draw_button(screen, language_button, BLUE, BLUE_HOVER, f"{translations[language_selected]['Language']}: {language_selected}", font, mouse_pos)
        draw_button(screen, sound_button, BLUE, BLUE_HOVER, "Sound Settings", font, mouse_pos)

        if dropdown_open:
            dropdown_rect = pygame.Rect(0, 0, button_width, 100)
            dropdown_rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 40)
            pygame.draw.rect(screen, DARK_GRAY, dropdown_rect, border_radius=10)
            for i, lang in enumerate(languages):
                lang_option = font.render(lang, True, WHITE)
                lang_rect = lang_option.get_rect(center=(dropdown_rect.centerx, dropdown_rect.y + 20 + i * 30))
                screen.blit(lang_option, lang_rect)

        if sound_open:
            sound_rect = pygame.Rect(0, 0, button_width + 50, 150)
            sound_rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 150)
            pygame.draw.rect(screen, DARK_GRAY, sound_rect, border_radius=10)
            vol_up = pygame.Rect(sound_rect.x + 10, sound_rect.y + 20, 40, 40)
            vol_down = pygame.Rect(sound_rect.x + 60, sound_rect.y + 20, 40, 40)
            voice_toggle = pygame.Rect(sound_rect.x + 10, sound_rect.y + 80, 100, 40)
            draw_button(screen, vol_up, GREEN, GREEN_HOVER, "+", font, mouse_pos)
            draw_button(screen, vol_down, RED, RED_HOVER, "-", font, mouse_pos)
            draw_button(screen, voice_toggle, BLUE, BLUE_HOVER, f"Voice: {'On' if voice_enabled else 'Off'}", font, mouse_pos)
            vol_text = font.render(f"Volume: {int(master_volume * 100)}%", True, WHITE)
            screen.blit(vol_text, vol_text.get_rect(center=(sound_rect.centerx, sound_rect.y + 60)))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_speech()
                speech_engine.endLoop()
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    run_game(screen, language_selected)
                elif language_button.collidepoint(event.pos):
                    dropdown_open = not dropdown_open
                    sound_open = False
                elif sound_button.collidepoint(event.pos):
                    sound_open = not sound_open
                    dropdown_open = False
                elif dropdown_open:
                    for i, lang in enumerate(languages):
                        option_rect = pygame.Rect(0, 0, button_width, 30)
                        option_rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 20 + i * 30)
                        if option_rect.collidepoint(event.pos):
                            language_selected = lang
                            dropdown_open = False
                elif sound_open:
                    if vol_up.collidepoint(event.pos):
                        master_volume = min(1.0, master_volume + 0.1)
                        speech_engine.setProperty('volume', master_volume)
                    elif vol_down.collidepoint(event.pos):
                        master_volume = max(0.0, master_volume - 0.1)
                        speech_engine.setProperty('volume', master_volume)
                    elif voice_toggle.collidepoint(event.pos):
                        voice_enabled = not voice_enabled

def intro_view(screen, language):
    font = pygame.font.Font(None, 36)
    case_text = translations[language]["Case Text"]
    words = case_text.split()
    lines = []
    current_line = []
    max_width = screen.get_width() - 100
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(current_line)
            current_line = [word]
    lines.append(current_line)

    text_to_speech(case_text, language)
    running = True
    current_word_index = 0
    displayed_lines = []
    start_time = time.time()
    total_words = len(words)
    audio_duration = len(case_text) / 10
    word_interval = audio_duration / total_words if total_words > 0 else 0.1
    next_button = pygame.Rect(0, 0, 200, 50)
    next_button.center = (screen.get_width() // 2, screen.get_height() // 2 + 100)
    clock = pygame.time.Clock()

    while running:
        speech_engine.iterate()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_speech()
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if next_button.collidepoint(event.pos):
                    stop_speech()
                    return

        screen.fill((0, 0, 0))
        screen.blit(pygame.transform.scale(intro_background, screen.get_size()), (0, 0))
        elapsed_time = time.time() - start_time
        target_word_count = int(elapsed_time / word_interval)
        if current_word_index < total_words and target_word_count > current_word_index:
            current_word_index += 1
            displayed_lines = []
            word_count = 0
            for line in lines:
                line_words = line[:max(0, min(len(line), current_word_index - word_count))]
                if line_words:
                    displayed_lines.append(line_words)
                word_count += len(line)

        text_y_start = screen.get_height() // 2 - (len(lines) * 40) // 2
        for i, line_words in enumerate(displayed_lines):
            text_surface = font.render(' '.join(line_words), True, WHITE)
            screen.blit(text_surface, text_surface.get_rect(center=(screen.get_width() // 2, text_y_start + i * 40)))

        mouse_pos = pygame.mouse.get_pos()
        draw_button(screen, next_button, BLUE, BLUE_HOVER, translations[language]["Next"], font, mouse_pos)
        pygame.display.flip()
        clock.tick(60)

def suspect_background_view(screen, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 28)
    interrogate_font = pygame.font.Font(None, 26)
    suspect_positions = [(WIDTH // 6, HEIGHT // 4), (WIDTH // 2 - 60, HEIGHT // 4), (WIDTH - WIDTH // 4, HEIGHT // 4)]
    suspect_rects = [pygame.Rect(x, y, 120, 160) for x, y in suspect_positions]
    back_button = pygame.Rect(0, 0, 150, 50)
    back_button.center = (WIDTH // 2, HEIGHT - 50)
    interrogate_button = pygame.Rect(0, 0, 200, 60)
    interrogate_button.center = (WIDTH // 2, HEIGHT - 120)
    selected_suspect = None
    hint_text = None
    interrogation_alpha = 0
    has_interrogated = False
    interrogate_panel = pygame.Rect(WIDTH // 10, HEIGHT // 10, WIDTH - WIDTH // 5, HEIGHT // 2)
    running = True
    clock = pygame.time.Clock()

    while running:
        speech_engine.iterate()
        screen.blit(pygame.transform.scale(intro_background, (WIDTH, HEIGHT)), (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        for i, pos in enumerate(suspect_positions):
            hover = suspect_rects[i].collidepoint(mouse_pos)
            pygame.draw.rect(screen, BLUE_HOVER if hover else LIGHT_GRAY, (pos[0] - 5, pos[1] - 5, 130, 170), border_radius=8)
            if selected_suspect == i:
                pygame.draw.rect(screen, GREEN, (pos[0] - 5, pos[1] - 5, 130, 170), 3, border_radius=8)
            screen.blit(pygame.transform.scale(suspect_large_image, (120, 160)), pos)
            name_text = font.render(translations[language][f"Suspect{i+1}"], True, WHITE)
            screen.blit(name_text, name_text.get_rect(center=(pos[0] + 60, pos[1] + 175)))

        if selected_suspect is not None:
            pygame.draw.rect(screen, BLACK, interrogate_panel.inflate(10, 10), border_radius=12)
            pygame.draw.rect(screen, LIGHT_GRAY, interrogate_panel, border_radius=12)
            background_text = translations[language][f"Suspect{selected_suspect+1}_Background"]
            lines = []
            current_line = []
            words = background_text.split()
            for word in words:
                test_line = ' '.join(current_line + [word])
                if font.size(test_line)[0] <= interrogate_panel.width - 40:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            lines.append(' '.join(current_line))

            text_y = interrogate_panel.y + 20
            for line in lines:
                text_surface = font.render(line, True, BLACK)
                screen.blit(text_surface, (interrogate_panel.x + 20, text_y))
                text_y += 35

            if hint_text:
                sub_panel = pygame.Rect(interrogate_panel.x + 10, interrogate_panel.y + 150, interrogate_panel.width - 20, 240)
                pygame.draw.rect(screen, INTERROGATE_BG, sub_panel, border_radius=10)
                interrogation_alpha = min(interrogation_alpha + 10, 255)
                hint_lines = []
                current_line = []
                words = hint_text.split()
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    if interrogate_font.size(test_line)[0] <= sub_panel.width - 20:
                        current_line.append(word)
                    else:
                        hint_lines.append(' '.join(current_line))
                        current_line = [word]
                hint_lines.append(' '.join(current_line))

                hint_y = sub_panel.y + 10
                for line in hint_lines:
                    text_surface = interrogate_font.render(line, True, INTERROGATE_TEXT)
                    text_surface.set_alpha(interrogation_alpha)
                    screen.blit(text_surface, (sub_panel.x + 10, hint_y))
                    hint_y += 30

            if not has_interrogated:
                draw_button(screen, interrogate_button, BLUE, BLUE_HOVER, translations[language]["Interrogate"], font, mouse_pos, pulse=True)

        draw_button(screen, back_button, RED, RED_HOVER, translations[language]["Back"], font, mouse_pos)
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    stop_speech()
                    return
                if interrogate_button.collidepoint(event.pos) and selected_suspect is not None and not has_interrogated:
                    suspect_name = ["Leila", "Sami", "Karim"][selected_suspect]
                    gender = "female" if suspect_name == "Leila" else "male"
                    hint_text = translations[language][f"Suspect{selected_suspect+1}_Hint"]
                    text_to_speech(hint_text, language, gender)
                    has_interrogated = True
                for i, rect in enumerate(suspect_rects):
                    if rect.collidepoint(event.pos):
                        selected_suspect = i
                        hint_text = None
                        has_interrogated = False
                        gender = "female" if i == 0 else "male"
                        text_to_speech(translations[language][f"Suspect{i+1}_Background"], language, gender)

    stop_speech()

def win_view(screen, language):
    font = pygame.font.Font(None, 50)
    back_button = pygame.Rect(0, 0, 250, 60)
    back_button.center = (screen.get_width() // 2, screen.get_height() // 2 + 100)
    running = True
    while running:
        speech_engine.iterate()
        screen.blit(pygame.transform.scale(won_bg, screen.get_size()), (0, 0))
        win_text = font.render(translations[language]["You've Won! Congratulations!"], True, WHITE)
        screen.blit(win_text, win_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50)))
        mouse_pos = pygame.mouse.get_pos()
        draw_button(screen, back_button, GREEN, GREEN_HOVER, translations[language]["Continue"], font, mouse_pos)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos)):
                running = False

def lose_view(screen, language):
    font = pygame.font.Font(None, 50)
    back_button = pygame.Rect(0, 0, 250, 60)
    back_button.center = (screen.get_width() // 2, screen.get_height() // 2 + 100)
    running = True
    while running:
        speech_engine.iterate()
        screen.blit(pygame.transform.scale(lost_bg, screen.get_size()), (0, 0))
        lose_text = font.render(translations[language]["You've Lost! Try Again!"], True, WHITE)
        screen.blit(lose_text, lose_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50)))
        mouse_pos = pygame.mouse.get_pos()
        draw_button(screen, back_button, RED, RED_HOVER, translations[language]["Continue"], font, mouse_pos)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos)):
                running = False
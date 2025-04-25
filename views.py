import pygame
import time
import os
from config import WIDTH, HEIGHT, translations, WHITE, BLACK, BLUE, BLUE_HOVER, RED, RED_HOVER, GREEN, GREEN_HOVER, LIGHT_GRAY, DARK_GRAY, INTERROGATE_BG, INTERROGATE_TEXT
from assets import intro_background, suspect_large_image, won_bg, lost_bg, menu_bg
from speech import text_to_speech, stop_speech, speech_engine
from utils import draw_button

def save_settings(master_volume, voice_enabled, selected_voice):
    with open("settings.txt", "w") as f:
        f.write(f"master_volume={master_volume}\n")
        f.write(f"voice_enabled={voice_enabled}\n")
        f.write(f"selected_voice={selected_voice}\n")

def load_settings():
    settings = {"master_volume": 1.0, "voice_enabled": True, "selected_voice": "David"}
    if os.path.exists("settings.txt"):
        with open("settings.txt", "r") as f:
            for line in f:
                key, value = line.strip().split("=")
                if key == "master_volume":
                    settings["master_volume"] = float(value)
                elif key == "voice_enabled":
                    settings["voice_enabled"] = value.lower() == "true"
                elif key == "selected_voice":
                    settings["selected_voice"] = value
    return settings

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
    settings = load_settings()
    master_volume = settings["master_volume"]
    voice_enabled = settings["voice_enabled"]
    selected_voice = settings["selected_voice"]
    voices = ["David", "Zira", "Arabic"]
    voice_dropdown_open = False

    speech_engine.setProperty('volume', master_volume)
    if not voice_enabled:
        stop_speech()

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
            sound_rect = pygame.Rect(0, 0, button_width + 50, 200)
            sound_rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 150)
            pygame.draw.rect(screen, DARK_GRAY, sound_rect, border_radius=10)
            vol_up = pygame.Rect(sound_rect.x + 10, sound_rect.y + 20, 40, 40)
            vol_down = pygame.Rect(sound_rect.x + 60, sound_rect.y + 20, 40, 40)
            voice_toggle = pygame.Rect(sound_rect.x + 10, sound_rect.y + 80, 100, 40)
            voice_select_button = pygame.Rect(sound_rect.x + 10, sound_rect.y + 130, 150, 40)
            draw_button(screen, vol_up, GREEN, GREEN_HOVER, "+", font, mouse_pos)
            draw_button(screen, vol_down, RED, RED_HOVER, "-", font, mouse_pos)
            draw_button(screen, voice_toggle, BLUE, BLUE_HOVER, f"Voice: {'On' if voice_enabled else 'Off'}", font, mouse_pos)
            draw_button(screen, voice_select_button, BLUE, BLUE_HOVER, f"Voice: {selected_voice}", font, mouse_pos)
            vol_text = font.render(f"Volume: {int(master_volume * 100)}%", True, WHITE)
            screen.blit(vol_text, vol_text.get_rect(center=(sound_rect.centerx, sound_rect.y + 60)))

            if voice_dropdown_open:
                voice_dropdown_rect = pygame.Rect(0, 0, button_width, 120)
                voice_dropdown_rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 210)
                pygame.draw.rect(screen, DARK_GRAY, voice_dropdown_rect, border_radius=10)
                for i, voice in enumerate(voices):
                    voice_option = font.render(voice, True, WHITE)
                    voice_rect = voice_option.get_rect(center=(voice_dropdown_rect.centerx, voice_dropdown_rect.y + 20 + i * 30))
                    screen.blit(voice_option, voice_rect)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_speech()
                speech_engine.endLoop()
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    save_settings(master_volume, voice_enabled, selected_voice)
                    run_game(screen, language_selected)
                elif language_button.collidepoint(event.pos):
                    dropdown_open = not dropdown_open
                    sound_open = False
                    voice_dropdown_open = False
                elif sound_button.collidepoint(event.pos):
                    sound_open = not sound_open
                    dropdown_open = False
                    voice_dropdown_open = False
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
                        if voice_enabled:
                            speech_engine.startLoop(False)
                        else:
                            stop_speech()
                    elif voice_select_button.collidepoint(event.pos):
                        voice_dropdown_open = not voice_dropdown_open
                    elif voice_dropdown_open:
                        for i, voice in enumerate(voices):
                            option_rect = pygame.Rect(0, 0, button_width, 30)
                            option_rect.center = (screen.get_width() // 2, voice_dropdown_rect.y + 20 + i * 30)
                            if option_rect.collidepoint(event.pos):
                                selected_voice = voice
                                voice_dropdown_open = False

    save_settings(master_volume, voice_enabled, selected_voice)
    stop_speech()
    speech_engine.endLoop()

def intro_view(screen, language, level=1):
    try:
        font = pygame.font.Font(None, 36)
        case_text = translations[language][f"Case Text_Level{level}"]
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
            try:
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

                y = screen.get_height() // 4
                for line in displayed_lines:
                    text = font.render(' '.join(line), True, (255, 255, 255))
                    text_rect = text.get_rect(center=(screen.get_width() // 2, y))
                    screen.blit(text, text_rect)
                    y += 30

                draw_button(screen, next_button, BLUE, BLUE_HOVER, translations[language]["Next"], font, pygame.mouse.get_pos())
                pygame.display.flip()
                clock.tick(60)
            except Exception as e:
                print(f"Error in intro_view loop: {str(e)}")
                running = False
    except Exception as e:
        print(f"Error in intro_view: {str(e)}")
        stop_speech()
        return

def suspect_background_view(screen, language, level=1):
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
    intro_text = None
    question_text = None
    response_text = None
    interrogation_alpha = 0
    question_index = 0
    interrogate_panel = pygame.Rect(WIDTH // 10, HEIGHT // 10, WIDTH - WIDTH // 5, HEIGHT // 2)
    running = True
    clock = pygame.time.Clock()

    # Questions for each suspect based on level
    questions = {
        0: [
            translations[language][f"Question1_Suspect1_Level{level}" if level == 2 else "Question1_Suspect1"],
            translations[language][f"Question2_Suspect1_Level{level}" if level == 2 else "Question2_Suspect1"],
            translations[language][f"Question3_Suspect1_Level{level}" if level == 2 else "Question3_Suspect1"]
        ],
        1: [
            translations[language][f"Question1_Suspect2_Level{level}" if level == 2 else "Question1_Suspect2"],
            translations[language][f"Question2_Suspect2_Level{level}" if level == 2 else "Question2_Suspect2"],
            translations[language][f"Question3_Suspect2_Level{level}" if level == 2 else "Question3_Suspect2"]
        ],
        2: [
            translations[language][f"Question1_Suspect3_Level{level}" if level == 2 else "Question1_Suspect3"],
            translations[language][f"Question2_Suspect3_Level{level}" if level == 2 else "Question2_Suspect3"],
            translations[language][f"Question3_Suspect3_Level{level}" if level == 2 else "Question3_Suspect3"]
        ]
    }
    
    # Answers for each suspect based on level
    answers = {
        0: [
            translations[language][f"Answer1_Suspect1_Level{level}" if level == 2 else "Answer1_Suspect1"],
            translations[language][f"Answer2_Suspect1_Level{level}" if level == 2 else "Answer2_Suspect1"],
            translations[language][f"Answer3_Suspect1_Level{level}" if level == 2 else "Answer3_Suspect1"]
        ],
        1: [
            translations[language][f"Answer1_Suspect2_Level{level}" if level == 2 else "Answer1_Suspect2"],
            translations[language][f"Answer2_Suspect2_Level{level}" if level == 2 else "Answer2_Suspect2"],
            translations[language][f"Answer3_Suspect2_Level{level}" if level == 2 else "Answer3_Suspect2"]
        ],
        2: [
            translations[language][f"Answer1_Suspect3_Level{level}" if level == 2 else "Answer1_Suspect3"],
            translations[language][f"Answer2_Suspect3_Level{level}" if level == 2 else "Answer2_Suspect3"],
            translations[language][f"Answer3_Suspect3_Level{level}" if level == 2 else "Answer3_Suspect3"]
        ]
    }

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
            # Use the correct suspect name based on level
            suspect_key = f"Suspect{i+1}_Level{level}" if level == 2 else f"Suspect{i+1}"
            name_text = font.render(translations[language][suspect_key], True, WHITE)
            screen.blit(name_text, name_text.get_rect(center=(pos[0] + 60, pos[1] + 175)))

        if selected_suspect is not None:
            pygame.draw.rect(screen, BLACK, interrogate_panel.inflate(10, 10), border_radius=12)
            pygame.draw.rect(screen, LIGHT_GRAY, interrogate_panel, border_radius=12)
            
            if intro_text:
                intro_surface = interrogate_font.render(intro_text, True, BLACK)
                screen.blit(intro_surface, (interrogate_panel.x + 20, interrogate_panel.y + 20))

            # Use the correct background text based on level
            background_key = f"Suspect{selected_suspect+1}_Background_Level{level}" if level == 2 else f"Suspect{selected_suspect+1}_Background"
            background_text = translations[language][background_key]
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

            text_y = interrogate_panel.y + 50
            for line in lines:
                text_surface = font.render(line, True, BLACK)
                screen.blit(text_surface, (interrogate_panel.x + 20, text_y))
                text_y += 35

            if question_text or response_text:
                sub_panel = pygame.Rect(interrogate_panel.x + 10, interrogate_panel.y + 150, interrogate_panel.width - 20, 240)
                pygame.draw.rect(screen, INTERROGATE_BG, sub_panel, border_radius=10)
                interrogation_alpha = min(interrogation_alpha + 10, 255)
                text_y = sub_panel.y + 10
                if question_text:
                    q_lines = []
                    current_line = []
                    words = question_text.split()
                    for word in words:
                        test_line = ' '.join(current_line + [word])
                        if interrogate_font.size(test_line)[0] <= sub_panel.width - 20:
                            current_line.append(word)
                        else:
                            q_lines.append(' '.join(current_line))
                            current_line = [word]
                    q_lines.append(' '.join(current_line))
                    for line in q_lines:
                        text_surface = interrogate_font.render(line, True, INTERROGATE_TEXT)
                        text_surface.set_alpha(interrogation_alpha)
                        screen.blit(text_surface, (sub_panel.x + 10, text_y))
                        text_y += 30
                if response_text:
                    r_lines = []
                    current_line = []
                    words = response_text.split()
                    for word in words:
                        test_line = ' '.join(current_line + [word])
                        if interrogate_font.size(test_line)[0] <= sub_panel.width - 20:
                            current_line.append(word)
                        else:
                            r_lines.append(' '.join(current_line))
                            current_line = [word]
                    r_lines.append(' '.join(current_line))
                    for line in r_lines:
                        text_surface = interrogate_font.render(line, True, INTERROGATE_TEXT)
                        text_surface.set_alpha(interrogation_alpha)
                        screen.blit(text_surface, (sub_panel.x + 10, text_y))
                        text_y += 30

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
                if interrogate_button.collidepoint(event.pos) and selected_suspect is not None:
                    # Use the correct suspect name based on level
                    suspect_key = f"Suspect{selected_suspect+1}_Level{level}" if level == 2 else f"Suspect{selected_suspect+1}"
                    suspect_name = translations[language][suspect_key]
                    gender = "female" if selected_suspect == 0 or (level == 2 and selected_suspect == 2) else "male"
                    question_text = questions[selected_suspect][question_index]
                    response_text = answers[selected_suspect][question_index]
                    question_index = (question_index + 1) % len(questions[selected_suspect])
                    interrogation_alpha = 0
                    text_to_speech(f"Question: {question_text}", language, "male")
                    text_to_speech(response_text, language, gender)
                for i, rect in enumerate(suspect_rects):
                    if rect.collidepoint(event.pos):
                        selected_suspect = i
                        # Use the correct intro text based on level
                        intro_key = f"Suspect{i+1}_Intro_Level{level}" if level == 2 else f"Suspect{i+1}_Intro"
                        intro_text = translations[language][intro_key]
                        question_text = None
                        response_text = None
                        question_index = 0
                        interrogation_alpha = 0
                        gender = "female" if i == 0 or (level == 2 and i == 2) else "male"
                        text_to_speech(intro_text, language, gender)
                        # Use the correct background text based on level
                        background_key = f"Suspect{i+1}_Background_Level{level}" if level == 2 else f"Suspect{i+1}_Background"
                        text_to_speech(translations[language][background_key], language, gender)

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

def evidence_board_view(screen, language, found_clues, level):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 48)
    back_button = pygame.Rect(0, 0, 150, 50)
    back_button.center = (WIDTH // 2, HEIGHT - 50)
    
    # Create a semi-transparent overlay for the board
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    
    # Create the main board surface with a modern style
    board_width = WIDTH - 200
    board_height = HEIGHT - 200
    board = pygame.Surface((board_width, board_height), pygame.SRCALPHA)
    board.fill((30, 30, 30, 220))
    
    # Add a border to the board
    pygame.draw.rect(board, (100, 100, 100), (0, 0, board_width, board_height), 3, border_radius=15)
    
    # Calculate clue positions relative to the board with more spacing
    clue_positions = [
        (board_width // 4, board_height // 3),
        (board_width // 2, board_height // 3),
        (3 * board_width // 4, board_height // 3)
    ]
    clue_rects = [pygame.Rect(x - 50, y - 50, 100, 100) for x, y in clue_positions]
    
    # Create clue images with improved visuals
    clue_images = {
        "clue1": pygame.Surface((60, 80), pygame.SRCALPHA),
        "clue2": pygame.Surface((50, 70), pygame.SRCALPHA),
        "clue3": pygame.Surface((70, 50), pygame.SRCALPHA)
    }
    
    # Style clue1 (document)
    clue_images["clue1"].fill((200, 180, 150, 255))
    pygame.draw.rect(clue_images["clue1"], (100, 80, 50), (0, 0, 60, 80), 2)
    pygame.draw.line(clue_images["clue1"], (100, 80, 50), (10, 20), (50, 20), 2)
    pygame.draw.line(clue_images["clue1"], (100, 80, 50), (10, 40), (50, 40), 2)
    
    # Style clue2 (glass)
    pygame.draw.polygon(clue_images["clue2"], (200, 230, 255, 200), [(25, 0), (50, 20), (40, 70), (10, 70), (0, 20)])
    pygame.draw.polygon(clue_images["clue2"], (150, 200, 255), [(25, 0), (50, 20), (40, 70), (10, 70), (0, 20)], 2)
    
    # Style clue3 (note)
    clue_images["clue3"].fill((255, 255, 240, 255))
    pygame.draw.rect(clue_images["clue3"], (100, 80, 50), (0, 0, 70, 50), 2)
    pygame.draw.line(clue_images["clue3"], (100, 80, 50), (10, 25), (60, 25), 1)
    
    running = True
    clock = pygame.time.Clock()

    text_to_speech("Review the collected clues on the evidence board.", language)

    while running:
        speech_engine.iterate()
        screen.fill((20, 20, 20))  # Dark background
        screen.blit(overlay, (0, 0))
        
        # Position the board in the center
        board_rect = board.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(board, board_rect)
        
        # Draw the title - handle missing translation gracefully
        try:
            title_text = title_font.render(translations[language]["Evidence Board"], True, (0, 200, 255))
        except KeyError:
            # Default title if translation is missing
            title_text = title_font.render("Evidence Board", True, (0, 200, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, board_rect.y + 50))
        screen.blit(title_text, title_rect)
        
        mouse_pos = pygame.mouse.get_pos()

        # Draw clues and connecting lines
        for i in range(3):
            clue_key = f"clue{i+1}_level{level}"
            if clue_key in found_clues:
                # Calculate position relative to the board
                pos_x = board_rect.x + clue_positions[i][0]
                pos_y = board_rect.y + clue_positions[i][1]
                
                # Draw the clue image
                screen.blit(clue_images[f"clue{i+1}"], (pos_x - 30, pos_y - 40))
                
                # Draw the clue text with better spacing and color
                translation_key = f"Clue{i+1}_Level{level}"
                try:
                    clue_text = font.render(translations[language][translation_key], True, (0, 200, 255))
                    text_rect = clue_text.get_rect(center=(pos_x, pos_y + 80))  # Increased spacing
                    screen.blit(clue_text, text_rect)
                except KeyError:
                    print(f"Missing translation for key: {translation_key}")
                    clue_text = font.render(f"Clue {i+1}", True, (0, 200, 255))
                    text_rect = clue_text.get_rect(center=(pos_x, pos_y + 80))  # Increased spacing
                    screen.blit(clue_text, text_rect)

        # Draw the back button with improved color
        draw_button(screen, back_button, (0, 100, 200), (0, 150, 255), translations[language]["Back"], font, mouse_pos)
        
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    stop_speech()
                    return
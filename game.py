import pygame
import sys
import math
import random
from config import WIDTH, HEIGHT, translations, GREEN, WHITE, DARK_GRAY, LIGHT_GRAY, BLUE, BLUE_HOVER, RED, YELLOW, BLACK
from assets import background_image, new_background_image, pin_image, suspect_image, level_image, hallway_image, detective_bg1,detective_bg2,detective_bg3
from ai import suspect_ai, get_smart_hint
from speech import text_to_speech
from utils import draw_button

def run_game(screen, language):
    from views import intro_view
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_size()
    level_positions = [(WIDTH // 10, HEIGHT // 4), (WIDTH // 2 - 100, HEIGHT // 4), (WIDTH - WIDTH // 4, HEIGHT // 4)]
    level_rects = [pygame.Rect(x, y, 200, 300) for x, y in level_positions]
    locked = [False, True, True]
    running = True
    while running:
        screen.blit(pygame.transform.scale(background_image, (WIDTH, HEIGHT)), (0, 0))
        for i, pos in enumerate(level_positions):
            if locked[i]:
                level = pygame.Surface((200, 300))
                level.fill((100, 100, 100))
                screen.blit(level, pos)
            else:
                screen.blit(pygame.transform.scale(level_image, (200, 300)), pos)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(level_rects):
                    if rect.collidepoint(event.pos) and not locked[i]:
                        if i == 0:
                            intro_view(screen, language)
                            screen.fill(BLACK)
                            pygame.display.flip()
                            points, found_clues, level2_unlocked = new_view(screen, 0, [], language)
                            if level2_unlocked:
                                locked[1] = False
    pygame.quit()
    sys.exit()

def new_view(screen, points, found_clues, language):
    from views import win_view, lose_view, evidence_board_view, suspect_background_view
    WIDTH, HEIGHT = screen.get_size()
    # Deduplicate found_clues to ensure correct length
    found_clues = list(dict.fromkeys(found_clues))
    pin_positions = [(WIDTH // 5, HEIGHT // 3), (WIDTH // 2, HEIGHT // 2), (WIDTH // 5, HEIGHT - HEIGHT // 4)]
    pin_rects = [pygame.Rect(x, y, 40, 40) for x, y in pin_positions]
    suspect_positions = [(WIDTH - WIDTH // 3, HEIGHT // 2), (WIDTH - WIDTH // 4, HEIGHT // 2), (WIDTH - WIDTH // 6, HEIGHT // 2)]
    suspect_rects = [pygame.Rect(x, y, 70, 100) for x, y in suspect_positions]
    suspect_visibility = [False, False, False]
    correct_suspect = 0
    font = pygame.font.Font(None, 28)
    mission_font = pygame.font.Font(None, 48)
    explore_button = pygame.Rect(0, 0, 300, 70)
    explore_button.center = (WIDTH - 350, HEIGHT - 120)
    select_box = pygame.Rect(0, 0, 350, 60)
    select_box.center = (WIDTH - 350, HEIGHT - 50)
    evidence_button = pygame.Rect(0, 0, 200, 60)
    evidence_button.center = (WIDTH - 350, HEIGHT - 190)
    current_pin_index = 0
    objectives = [translations[language][f"Objective{i+1}"] for i in range(3)]
    completed_objectives = [False, False, False]
    unlocked_pin1 = False
    unlocked_pin2 = False
    unlocked_pin3 = False
    select_mode = False  # Flag for suspect selection mode
    running = True
    clock = pygame.time.Clock()

    # Initialize states based on found_clues
    if "clue1" in found_clues:
        suspect_visibility[0] = True
        completed_objectives[0] = True
        current_pin_index = 1
        unlocked_pin1 = True
    if "clue2" in found_clues:
        suspect_visibility[1] = True
        completed_objectives[1] = True
        current_pin_index = 2
        unlocked_pin2 = True
    if "clue3" in found_clues:
        suspect_visibility[2] = True
        completed_objectives[2] = True
        unlocked_pin3 = True

    print(f"new_view: found_clues = {found_clues}, current_pin_index = {current_pin_index}")

    while running:
        try:
            screen.blit(pygame.transform.scale(new_background_image, (WIDTH, HEIGHT)), (0, 0))
            mission_text = mission_font.render(translations[language]["Mission"], True, (0, 255, 255))
            screen.blit(mission_text, mission_text.get_rect(center=(WIDTH // 2, 50)))

            for i, pos in enumerate(pin_positions):
                pin_color = (255, 215, 0) if i == current_pin_index else (150, 150, 150)
                scaled_pin = pygame.transform.scale(pin_image, (40, 40))
                scaled_pin.fill(pin_color, special_flags=pygame.BLEND_MULT)
                if i == current_pin_index:
                    glow_alpha = 128 + int(127 * math.sin(pygame.time.get_ticks() / 500))
                    glow = pygame.Surface((60, 60), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (255, 215, 0, glow_alpha), (30, 30), 30)
                    screen.blit(glow, (pos[0] - 10, pos[1] - 10))
                screen.blit(scaled_pin, pos)
                if i == current_pin_index and i < len(pin_positions) - 1:
                    pygame.draw.line(screen, RED, (pos[0] + 20, pos[1] + 20), (pin_positions[i + 1][0] + 20, pin_positions[i + 1][1] + 20), 3)

            points_box = pygame.Rect(0, 0, 150, 40)
            points_box.center = (WIDTH - 100, 100)
            pygame.draw.rect(screen, LIGHT_GRAY, points_box, border_radius=5)
            points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
            screen.blit(points_text, points_text.get_rect(center=points_box.center))

            obj_x, obj_y = WIDTH - WIDTH // 4, 150
            for i, obj in enumerate(objectives):
                icon_rect = pygame.Rect(obj_x - 30, obj_y + i * 40, 20, 20)
                icon_color = GREEN if completed_objectives[i] else WHITE
                pygame.draw.rect(screen, icon_color, icon_rect, border_radius=5)
                obj_text = font.render(obj, True, WHITE)
                screen.blit(obj_text, (obj_x, obj_y + i * 40))

            for i, (pos, visible) in enumerate(zip(suspect_positions, suspect_visibility)):
                if visible:
                    suspect_rect = suspect_rects[i]
                    hover = suspect_rect.collidepoint(pygame.mouse.get_pos()) and len(found_clues) == 3 and select_mode
                    if hover or (select_mode and visible):
                        glow_alpha = 128 + int(127 * math.sin(pygame.time.get_ticks() / 500))
                        glow = pygame.Surface((80, 110), pygame.SRCALPHA)
                        pygame.draw.rect(glow, (0, 255, 255, glow_alpha), (0, 0, 80, 110), border_radius=5)
                        screen.blit(glow, (pos[0] - 5, pos[1] - 5))
                    screen.blit(pygame.transform.scale(suspect_image, (70, 100)), pos)
                    suspect_text = font.render(translations[language][f"Suspect{i+1}"], True, WHITE)
                    screen.blit(suspect_text, suspect_text.get_rect(center=(pos[0] + 35, pos[1] + 115)))

            if len(found_clues) > 0:
                draw_button(screen, evidence_button, BLUE, BLUE_HOVER, "Evidence Board", font, pygame.mouse.get_pos())
            if len(found_clues) == 3:
                draw_button(screen, explore_button, BLUE, BLUE_HOVER, translations[language]["Explore Suspect Background"], font, pygame.mouse.get_pos())
                draw_button(screen, select_box, BLUE, BLUE_HOVER, translations[language]["Select a suspect!"], font, pygame.mouse.get_pos())

            pygame.display.flip()
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print(f"Mouse click at {event.pos}")
                    if len(found_clues) == 3 and explore_button.collidepoint(event.pos):
                        print("Calling suspect_background_view")
                        try:
                            suspect_background_view(screen, language)
                            print("Returned from suspect_background_view")
                        except Exception as e:
                            print(f"Error in suspect_background_view: {e}")
                            import traceback
                            traceback.print_exc()
                    if len(found_clues) == 3 and select_box.collidepoint(event.pos):
                        print("Toggled select_mode")
                        select_mode = not select_mode
                        text_to_speech("Select a suspect now.", language)
                    if evidence_button.collidepoint(event.pos):
                        print("Clicked evidence_button")
                        evidence_board_view(screen, language, found_clues)
                    for i, rect in enumerate(suspect_rects):
                        if rect.collidepoint(event.pos) and suspect_visibility[i] and len(found_clues) == 3 and select_mode:
                            print(f"Selected suspect {i}")
                            select_mode = False
                            if i == correct_suspect:
                                win_view(screen, language)
                                return points, found_clues, True
                            else:
                                lose_view(screen, language)
                                return points, found_clues, False
                    for i, pin_rect in enumerate(pin_rects):
                        if pin_rect.collidepoint(event.pos) and i == current_pin_index:
                            print(f"Pin {i} clicked, current_pin_index = {current_pin_index}")
                            if i == 0:
                                if unlocked_pin1:
                                    pin_view_index = hall_view(screen, points, language, 0)
                                    print(f"hall_view returned pin_view_index: {pin_view_index}")
                                    if pin_view_index == 0:
                                        points, found_clues = pin_view_1(screen, points, found_clues, language)
                                        print(f"pin_view_1: found_clues = {found_clues}")
                                else:
                                    points, unlocked_pin1 = puzzle_view_1(screen, points, language)
                                    print(f"puzzle_view_1: unlocked_pin1 = {unlocked_pin1}")
                            elif i == 1:
                                if unlocked_pin2:
                                    pin_view_index = hall_view(screen, points, language, 1)
                                    print(f"hall_view returned pin_view_index: {pin_view_index}")
                                    if pin_view_index == 1:
                                        points, found_clues = pin_view_2(screen, points, found_clues, language)
                                        print(f"pin_view_2: found_clues = {found_clues}")
                                else:
                                    try:
                                        points, unlocked_pin2 = puzzle_view_2(screen, points, language)
                                        print(f"puzzle_view_2: unlocked_pin2 = {unlocked_pin2}")
                                        if unlocked_pin2:
                                            pin_view_index = hall_view(screen, points, language, 1)
                                            print(f"hall_view returned pin_view_index: {pin_view_index}")
                                            if pin_view_index == 1:
                                                points, found_clues = pin_view_2(screen, points, found_clues, language)
                                                print(f"pin_view_2: found_clues = {found_clues}")
                                                if "clue2" in found_clues and not suspect_visibility[1]:
                                                    suspect_visibility[1] = True
                                                    completed_objectives[1] = True
                                                    current_pin_index = 2
                                                    print(f"Clue2 found, current_pin_index = 2")
                                    except Exception as e:
                                        print(f"Error in puzzle_view_2 transition: {e}")
                                        import traceback
                                        traceback.print_exc()
                                        unlocked_pin2 = False
                            elif i == 2:
                                if unlocked_pin3:
                                    pin_view_index = hall_view(screen, points, language, 2)
                                    print(f"hall_view returned pin_view_index: {pin_view_index}")
                                    if pin_view_index == 2:
                                        points, found_clues = pin_view_3(screen, points, found_clues, language)
                                        print(f"pin_view_3: found_clues = {found_clues}")
                                else:
                                    points, unlocked_pin3 = puzzle_view_3(screen, points, language)
                                    print(f"puzzle_view_3: unlocked_pin3 = {unlocked_pin3}")
                            if "clue1" in found_clues and not suspect_visibility[0]:
                                suspect_visibility[0] = True
                                completed_objectives[0] = True
                                current_pin_index = 1
                                print(f"Clue1 found, current_pin_index = 1")
                            elif "clue2" in found_clues and not suspect_visibility[1]:
                                suspect_visibility[1] = True
                                completed_objectives[1] = True
                                current_pin_index = 2
                                print(f"Clue2 found, current_pin_index = 2")
                            elif "clue3" in found_clues and not suspect_visibility[2]:
                                suspect_visibility[2] = True
                                completed_objectives[2] = True
                                print(f"Clue3 found, suspect_visibility = {suspect_visibility}")
                            try:
                                suspect_visibility = suspect_ai(found_clues, suspect_visibility, language, points)
                            except Exception as e:
                                print(f"Error in suspect_ai: {e}")
                                import traceback
                                traceback.print_exc()
        except Exception as e:
            print(f"Error in new_view main loop: {e}")
            import traceback
            traceback.print_exc()
            return points, found_clues, False

    return points, found_clues, False

def evidence_board_view(screen, language, found_clues):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 48)
    content_font = pygame.font.Font(None, 32)  # Slightly smaller font for content
    
    # Create semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
    
    # Create evidence board background
    board_bg = pygame.Surface((WIDTH - 200, HEIGHT - 200), pygame.SRCALPHA)
    board_bg.fill((30, 30, 30, 200))  # Dark gray with 80% opacity
    board_rect = board_bg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Evidence card properties
    card_width = 400  # Increased width for better text spacing
    card_height = 300  # Increased height for better text spacing
    card_spacing = 60  # Increased spacing between cards
    cards_per_row = 2
    start_x = board_rect.x + (board_rect.width - (cards_per_row * card_width + (cards_per_row - 1) * card_spacing)) // 2
    start_y = board_rect.y + 120  # Increased top margin
    
    # Create evidence cards
    evidence_cards = []
    for i, clue in enumerate(found_clues):
        row = i // cards_per_row
        col = i % cards_per_row
        x = start_x + col * (card_width + card_spacing)
        y = start_y + row * (card_height + card_spacing)
        
        # Create card surface with opacity
        card = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        card.fill((50, 50, 50, 200))  # Semi-transparent dark gray
        
        # Add subtle border
        pygame.draw.rect(card, (100, 100, 100, 150), (0, 0, card_width, card_height), 2, border_radius=10)
        
        # Add evidence text with proper spacing
        title = font.render(translations[language][f"Clue{i+1}_Title"], True, (255, 255, 255))
        content = content_font.render(translations[language][f"Clue{i+1}"], True, (200, 200, 200))
        
        # Center text on card with increased vertical spacing
        title_rect = title.get_rect(center=(card_width // 2, 50))  # Moved title up
        content_rect = content.get_rect(center=(card_width // 2, card_height // 2 + 50))  # Moved content down
        
        # Add text with padding
        card.blit(title, title_rect)
        card.blit(content, content_rect)
        
        # Add a subtle separator line between title and content
        separator_y = title_rect.bottom + 30  # Increased spacing
        pygame.draw.line(card, (100, 100, 100, 100), 
                        (card_width // 4, separator_y),
                        (3 * card_width // 4, separator_y), 1)
        
        evidence_cards.append({
            'surface': card,
            'rect': pygame.Rect(x, y, card_width, card_height)
        })
    
    back_button = pygame.Rect(0, 0, 200, 60)
    back_button.center = (WIDTH // 2, HEIGHT - 120)  # Moved button down
    
    running = True
    clock = pygame.time.Clock()

    while running:
        # Draw background and overlay
        screen.blit(pygame.transform.scale(detective_bg1, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(board_bg, board_rect)
        
        # Draw title with increased spacing
        title_text = title_font.render(translations[language]["Evidence Board"], True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, board_rect.y + 70)))  # Moved title down
        
        # Draw evidence cards
        for card in evidence_cards:
            screen.blit(card['surface'], card['rect'])
            
            # Add hover effect
            if card['rect'].collidepoint(pygame.mouse.get_pos()):
                hover_glow = pygame.Surface((card_width + 20, card_height + 20), pygame.SRCALPHA)
                hover_glow.fill((255, 255, 255, 30))
                screen.blit(hover_glow, (card['rect'].x - 10, card['rect'].y - 10))
        
        # Draw back button
        draw_button(screen, back_button, BLUE, BLUE_HOVER, translations[language]["Return to Map"], font, pygame.mouse.get_pos())
        
        pygame.display.flip()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return

def suspect_background_view(screen, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 28)
    title_font = pygame.font.Font(None, 48)
    suspect_positions = [(WIDTH - WIDTH // 3 - 50, HEIGHT // 2), (WIDTH - WIDTH // 4 - 50, HEIGHT // 2), (WIDTH - WIDTH // 6 - 50, HEIGHT // 2)]
    suspect_rects = [pygame.Rect(x, y, 70, 100) for x, y in suspect_positions]
    back_button = pygame.Rect(0, 0, 200, 60)
    back_button.center = (WIDTH // 2, HEIGHT - 100)
    
    # Add interrogation buttons
    question_buttons = [
        pygame.Rect(WIDTH // 4, HEIGHT // 3, 300, 50),
        pygame.Rect(WIDTH // 4, HEIGHT // 3 + 70, 300, 50),
        pygame.Rect(WIDTH // 4, HEIGHT // 3 + 140, 300, 50)
    ]
    
    # Questions for each suspect
    questions = {
        0: [
            translations[language]["Question1_Suspect1"],
            translations[language]["Question2_Suspect1"],
            translations[language]["Question3_Suspect1"]
        ],
        1: [
            translations[language]["Question1_Suspect2"],
            translations[language]["Question2_Suspect2"],
            translations[language]["Question3_Suspect2"]
        ],
        2: [
            translations[language]["Question1_Suspect3"],
            translations[language]["Question2_Suspect3"],
            translations[language]["Question3_Suspect3"]
        ]
    }
    
    # Answers for each suspect
    answers = {
        0: [
            translations[language]["Answer1_Suspect1"],
            translations[language]["Answer2_Suspect1"],
            translations[language]["Answer3_Suspect1"]
        ],
        1: [
            translations[language]["Answer1_Suspect2"],
            translations[language]["Answer2_Suspect2"],
            translations[language]["Answer3_Suspect2"]
        ],
        2: [
            translations[language]["Answer1_Suspect3"],
            translations[language]["Answer2_Suspect3"],
            translations[language]["Answer3_Suspect3"]
        ]
    }
    
    selected_suspect = None
    current_question = None
    answer_text = None
    answer_timer = 0
    answer_alpha = 255
    running = True
    clock = pygame.time.Clock()

    print("Entered suspect_background_view")
    text_to_speech("Explore the suspect backgrounds and interrogate them.", language)
    pygame.event.clear()  # Clear stale events

    while running:
        screen.blit(pygame.transform.scale(detective_bg1, (WIDTH, HEIGHT)), (0, 0))
        title_text = title_font.render(translations[language]["Explore Suspect Background"], True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 50)))

        # Draw suspects
        for i, pos in enumerate(suspect_positions):
            screen.blit(pygame.transform.scale(suspect_image, (70, 100)), pos)
            suspect_text = font.render(translations[language][f"Suspect{i+1}"], True, WHITE)
            screen.blit(suspect_text, suspect_text.get_rect(center=(pos[0] + 35, pos[1] + 115)))
            background_text = font.render(translations[language][f"Suspect{i+1}_Background"], True, YELLOW)
            screen.blit(background_text, background_text.get_rect(center=(pos[0] + 35, pos[1] + 150)))

        # Draw question buttons if suspect is selected
        if selected_suspect is not None:
            for i, button in enumerate(question_buttons):
                hover = button.collidepoint(pygame.mouse.get_pos())
                color = BLUE_HOVER if hover else BLUE
                pygame.draw.rect(screen, color, button, border_radius=5)
                question_text = font.render(questions[selected_suspect][i], True, WHITE)
                screen.blit(question_text, question_text.get_rect(center=button.center))

        # Draw answer if there is one
        if answer_text and answer_timer > 0:
            answer_surface = font.render(answer_text, True, WHITE)
            answer_surface.set_alpha(answer_alpha)
            answer_rect = answer_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, answer_rect.inflate(20, 20), border_radius=10)
            screen.blit(answer_surface, answer_rect)
            answer_alpha = max(answer_alpha - 2, 0)
            answer_timer -= 1

        draw_button(screen, back_button, BLUE, BLUE_HOVER, translations[language]["Return to Map"], font, pygame.mouse.get_pos())

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("QUIT event in suspect_background_view")
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                print("ESC in suspect_background_view, returning to new_view")
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    print("Returning to new_view from back_button")
                    return
                
                # Check if a suspect was clicked
                for i, rect in enumerate(suspect_rects):
                    if rect.collidepoint(event.pos):
                        selected_suspect = i
                        print(f"Selected suspect {i+1}")
                        text_to_speech(f"Selected suspect {i+1}. What would you like to ask?", language)
                        break
                
                # Check if a question was clicked
                if selected_suspect is not None:
                    for i, button in enumerate(question_buttons):
                        if button.collidepoint(event.pos):
                            current_question = i
                            answer_text = answers[selected_suspect][i]
                            answer_timer = 120
                            answer_alpha = 255
                            print(f"Asked question {i+1} to suspect {selected_suspect+1}")
                            text_to_speech(answer_text, language)
                            break

def hall_view(screen, points, language, pin_index):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    background = hallway_image
    avatar = pygame.transform.scale(pin_image, (40, 40))
    avatar_rect = pygame.Rect(WIDTH // 2 - 20, 50, 40, 40)  # Start at top center
    
    # Different light positions for each pin
    light_positions = [
        (WIDTH // 2, HEIGHT // 3),  # Pin 1: upper third
        (WIDTH // 2, HEIGHT // 2),  # Pin 2: middle
        (WIDTH // 2, 2 * HEIGHT // 3)  # Pin 3: lower third
    ]
    
    light_rect = pygame.Rect(light_positions[pin_index][0] - 50, light_positions[pin_index][1] - 50, 100, 100)
    light_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
    avatar_speed = 5
    instruction = font.render("Move to the yellow light", True, WHITE)
    running = True
    clock = pygame.time.Clock()

    print(f"Entered hall_view with pin_index: {pin_index}")
    text_to_speech("Move the avatar to the yellow light to find the clue.", language)

    while running:
        screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))
        glow_alpha = 128 + int(127 * math.sin(pygame.time.get_ticks() / 500))
        light_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(light_surface, (255, 255, 0, glow_alpha), (0, 0, 100, 100), border_radius=10)
        screen.blit(light_surface, light_rect)
        screen.blit(avatar, avatar_rect)
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return -1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            avatar_rect.y -= avatar_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            avatar_rect.y += avatar_speed
        # Keep avatar within screen bounds
        avatar_rect.y = max(50, min(HEIGHT - 50 - avatar_rect.height, avatar_rect.y))

        if avatar_rect.colliderect(light_rect):
            print(f"Collision detected, returning pin_index: {pin_index}")
            return pin_index

    return -1

def puzzle_view_1(screen, points, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
    
    # Create puzzle background
    puzzle_bg = pygame.Surface((300, 300), pygame.SRCALPHA)
    puzzle_bg.fill((30, 30, 30, 200))  # Dark gray with 80% opacity
    puzzle_bg_rect = puzzle_bg.get_rect(center=(WIDTH//2, HEIGHT//2))
    
    grid = [[None for _ in range(3)] for _ in range(3)]
    cell_rects = [pygame.Rect(WIDTH // 2 - 90 + x * 60, HEIGHT // 2 - 90 + y * 60, 50, 50) for y in range(3) for x in range(3)]
    message_text = None
    message_timer = 0
    message_alpha = 255
    puzzle_solved = False
    hint = get_smart_hint([], points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, YELLOW)
    instruction = font.render("Get 3 X's in a row", True, WHITE)
    running = True
    clock = pygame.time.Clock()

    def check_win(board, player):
        for i in range(3):
            if all(board[i][j] == player for j in range(3)) or all(board[j][i] == player for j in range(3)):
                return True
        if all(board[i][i] == player for i in range(3)) or all(board[i][2-i] == player for i in range(3)):
            return True
        return False

    def ai_move(board):
        for i in range(3):
            for j in range(3):
                if board[i][j] is None:
                    return i, j
        return None

    text_to_speech("Get three X's in a row to unlock the clue.", language)

    while running:
        # Draw background and overlay
        screen.blit(pygame.transform.scale(new_background_image, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(puzzle_bg, puzzle_bg_rect)
        
        # Draw grid lines
        for i in range(4):
            # Vertical lines
            pygame.draw.line(screen, (100, 100, 100), 
                           (WIDTH//2 - 90 + i*60, HEIGHT//2 - 90),
                           (WIDTH//2 - 90 + i*60, HEIGHT//2 + 90), 2)
            # Horizontal lines
            pygame.draw.line(screen, (100, 100, 100),
                           (WIDTH//2 - 90, HEIGHT//2 - 90 + i*60),
                           (WIDTH//2 + 90, HEIGHT//2 - 90 + i*60), 2)
        
        for i, rect in enumerate(cell_rects):
            x, y = i % 3, i // 3
            # Draw cell background
            cell_bg = pygame.Surface((50, 50), pygame.SRCALPHA)
            cell_bg.fill((50, 50, 50, 200))  # Dark gray with 80% opacity
            screen.blit(cell_bg, rect)
            
            if grid[y][x] == 'X':
                text = font.render('X', True, BLUE)
                screen.blit(text, text.get_rect(center=rect.center))
            elif grid[y][x] == 'O':
                text = font.render('O', True, RED)
                screen.blit(text, text.get_rect(center=rect.center))
        
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, WHITE)
            message_surface.set_alpha(message_alpha)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
            screen.blit(message_surface, message_rect)
            message_alpha = max(message_alpha - 5, 0)
            message_timer -= 1
            if message_timer <= 0 and puzzle_solved:
                return points, True

        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return points, False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(cell_rects):
                    if rect.collidepoint(event.pos):
                        x, y = i % 3, i // 3
                        if grid[y][x] is None:
                            grid[y][x] = 'X'
                            if check_win(grid, 'X'):
                                points += 10
                                message_text = "Access Granted"
                                message_timer = 120
                                puzzle_solved = True
                                text_to_speech("Access granted. Entering the room.", language)
                            else:
                                move = ai_move(grid)
                                if move:
                                    grid[move[0]][move[1]] = 'O'
                                    if check_win(grid, 'O'):
                                        points = max(0, points - 5)
                                        message_text = "You Lost. Try Again."
                                        message_timer = 60
                                        text_to_speech("You lost. Try again.", language)
                                        grid = [[None for _ in range(3)] for _ in range(3)]
    return points, False

def puzzle_view_2(screen, points, language):
    try:
        WIDTH, HEIGHT = screen.get_size()
        if not isinstance(new_background_image, pygame.Surface):
            print("Error: new_background_image is not a valid surface")
            return points, False
        if not isinstance(pin_image, pygame.Surface):
            print("Error: pin_image is not a valid surface")
            return points, False
        scaled_background = pygame.transform.scale(new_background_image, (WIDTH, HEIGHT))
        scaled_pin = pygame.transform.scale(pin_image, (50, 50))
        font = pygame.font.Font(None, 36)
        clue_font = pygame.font.Font(None, 48)
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        
        # Create puzzle background
        puzzle_bg = pygame.Surface((300, 300), pygame.SRCALPHA)
        puzzle_bg.fill((30, 30, 30, 200))  # Dark gray with 80% opacity
        puzzle_bg_rect = puzzle_bg.get_rect(center=(WIDTH//2, HEIGHT//2))
        
        grid = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12],
            [13, 14, 15, None]
        ]
        tile_rects = [pygame.Rect(WIDTH // 2 - 120 + x * 60, HEIGHT // 2 - 120 + y * 60, 50, 50) for y in range(4) for x in range(4)]
        target_piece = 15
        message_text = None
        message_timer = 0
        message_alpha = 255
        puzzle_solved = False
        hint = get_smart_hint([], points, language)
        hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, YELLOW)
        instruction = font.render("Slide to move piece 15 to center", True, WHITE)
        running = True
        clock = pygame.time.Clock()

        def find_empty():
            for y in range(4):
                for x in range(4):
                    if grid[y][x] is None:
                        return x, y
            return None

        def is_solved():
            return grid[1][1] == 15 or grid[1][2] == 15 or grid[2][1] == 15 or grid[2][2] == 15

        try:
            text_to_speech("Slide the blocks to move piece fifteen to the center to unlock the clue.", language)
        except Exception as e:
            print(f"TTS error at start: {e}")

        while running:
            try:
                # Draw background and overlay
                screen.blit(scaled_background, (0, 0))
                screen.blit(overlay, (0, 0))
                screen.blit(puzzle_bg, puzzle_bg_rect)
                
                # Draw grid lines
                for i in range(5):
                    # Vertical lines
                    pygame.draw.line(screen, (100, 100, 100), 
                                   (WIDTH//2 - 120 + i*60, HEIGHT//2 - 120),
                                   (WIDTH//2 - 120 + i*60, HEIGHT//2 + 120), 2)
                    # Horizontal lines
                    pygame.draw.line(screen, (100, 100, 100),
                                   (WIDTH//2 - 120, HEIGHT//2 - 120 + i*60),
                                   (WIDTH//2 + 120, HEIGHT//2 - 120 + i*60), 2)
                
                # Draw tiles
                for i, rect in enumerate(tile_rects):
                    x, y = i % 4, i // 4
                    if grid[y][x] is not None:
                        # Draw tile background
                        tile_bg = pygame.Surface((50, 50), pygame.SRCALPHA)
                        tile_bg.fill((50, 50, 50, 200))  # Dark gray with 80% opacity
                        screen.blit(tile_bg, rect)
                        
                        if grid[y][x] == 15:
                            screen.blit(scaled_pin, rect)
                        else:
                            text = font.render(str(grid[y][x]), True, WHITE)
                            screen.blit(text, text.get_rect(center=rect.center))
                
                # Draw instruction and hint
                screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 180)))
                screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))
                points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
                screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))

                if message_text and message_timer > 0:
                    message_surface = clue_font.render(message_text, True, WHITE)
                    message_surface.set_alpha(message_alpha)
                    message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
                    screen.blit(message_surface, message_rect)
                    message_alpha = max(message_alpha - 5, 0)
                    message_timer -= 1
                    if message_timer <= 0 and puzzle_solved:
                        print("Returning from puzzle_view_2 with points =", points)
                        return points, True

                pygame.display.flip()
                clock.tick(60)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return points, False
                    elif event.type == pygame.MOUSEBUTTONDOWN and not puzzle_solved:
                        empty_pos = find_empty()
                        if empty_pos is None:
                            continue
                        empty_x, empty_y = empty_pos
                        for i, rect in enumerate(tile_rects):
                            if rect.collidepoint(event.pos):
                                x, y = i % 4, i // 4
                                if (abs(x - empty_x) == 1 and y == empty_y) or (abs(y - empty_y) == 1 and x == empty_x):
                                    grid[empty_y][empty_x], grid[y][x] = grid[y][x], grid[empty_y][empty_x]
                                    if is_solved():
                                        print(f"Grid state when solved: {grid}")
                                        points += 10
                                        message_text = "Access Granted"
                                        message_timer = 120
                                        puzzle_solved = True
                                        try:
                                            text_to_speech("Access granted. Entering the room.", language)
                                        except Exception as e:
                                            print(f"TTS error in puzzle_view_2: {e}")
            except Exception as e:
                print(f"Error in puzzle_view_2 main loop: {e}")
                import traceback
                traceback.print_exc()
                return points, False

        return points, False
    except Exception as e:
        print(f"Crash in puzzle_view_2: {e}")
        import traceback
        traceback.print_exc()
        return points, False

def puzzle_view_3(screen, points, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
    
    # Create puzzle background
    puzzle_bg = pygame.Surface((400, 400), pygame.SRCALPHA)
    puzzle_bg.fill((30, 30, 30, 200))  # Dark gray with 80% opacity
    puzzle_bg_rect = puzzle_bg.get_rect(center=(WIDTH//2, HEIGHT//2))
    
    # Memory game setup
    symbols = ['!', '@', '#', '$', '%', '&', '*', '+']
    pairs = symbols * 2  # Create pairs
    random.shuffle(pairs)
    
    # Create 4x4 grid of cards
    cards = []
    card_size = 80
    card_spacing = 20
    start_x = WIDTH // 2 - (4 * (card_size + card_spacing)) // 2
    start_y = HEIGHT // 2 - (4 * (card_size + card_spacing)) // 2
    
    for i in range(16):
        row = i // 4
        col = i % 4
        x = start_x + col * (card_size + card_spacing)
        y = start_y + row * (card_size + card_spacing)
        cards.append({
            'rect': pygame.Rect(x, y, card_size, card_size),
            'symbol': pairs[i],
            'flipped': False,
            'matched': False
        })
    
    # Game state
    first_card = None
    second_card = None
    can_flip = True
    matched_pairs = 0
    message_text = None
    message_timer = 0
    message_alpha = 255
    puzzle_solved = False
    hint = get_smart_hint([], points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, YELLOW)
    instruction = font.render("Match all pairs to unlock the clue", True, WHITE)
    running = True
    clock = pygame.time.Clock()

    text_to_speech("Match all pairs of symbols to unlock the clue.", language)

    while running:
        # Draw background and overlay
        screen.blit(pygame.transform.scale(new_background_image, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(puzzle_bg, puzzle_bg_rect)
        
        # Draw instruction and hint
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))

        # Draw cards
        for card in cards:
            if not card['matched']:
                if card['flipped']:
                    # Draw flipped card with symbol
                    pygame.draw.rect(screen, WHITE, card['rect'], border_radius=10)
                    symbol_text = font.render(card['symbol'], True, BLACK)
                    screen.blit(symbol_text, symbol_text.get_rect(center=card['rect'].center))
                else:
                    # Draw face-down card
                    pygame.draw.rect(screen, BLUE, card['rect'], border_radius=10)
                    pygame.draw.rect(screen, BLUE_HOVER, card['rect'].inflate(-10, -10), border_radius=10)

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, WHITE)
            message_surface.set_alpha(message_alpha)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
            screen.blit(message_surface, message_rect)
            message_alpha = max(message_alpha - 5, 0)
            message_timer -= 1
            if message_timer <= 0 and puzzle_solved:
                return points, True

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return points, False
            elif event.type == pygame.MOUSEBUTTONDOWN and can_flip and not puzzle_solved:
                for card in cards:
                    if not card['matched'] and not card['flipped'] and card['rect'].collidepoint(event.pos):
                        card['flipped'] = True
                        
                        if first_card is None:
                            first_card = card
                        else:
                            second_card = card
                            can_flip = False
                            
                            # Check for match
                            if first_card['symbol'] == second_card['symbol']:
                                first_card['matched'] = True
                                second_card['matched'] = True
                                matched_pairs += 1
                                
                                if matched_pairs == 8:  # All pairs matched
                                    points += 10
                                    message_text = "Access Granted"
                                    message_timer = 120
                                    puzzle_solved = True
                                    text_to_speech("Access granted. Entering the room.", language)
                            else:
                                # No match, flip cards back after delay
                                pygame.time.delay(1000)
                                first_card['flipped'] = False
                                second_card['flipped'] = False
                            
                            first_card = None
                            second_card = None
                            can_flip = True
                        break

    return points, False

def pin_view_1(screen, points, found_clues, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    
    # Create logbook surface
    logbook = pygame.Surface((60, 80), pygame.SRCALPHA)
    logbook.fill((139, 69, 19))
    pygame.draw.rect(logbook, BLACK, (0, 0, 60, 80), 2)
    pygame.draw.line(logbook, WHITE, (10, 20), (50, 20), 2)
    pygame.draw.line(logbook, WHITE, (10, 40), (50, 40), 2)
    
    # Logbook properties - random position in top right quadrant
    logbook_rect = logbook.get_rect(center=(
        random.randint(WIDTH // 2 + 100, WIDTH - 100),
        random.randint(100, HEIGHT // 2 - 100)
    ))
    pulse_speed = 0.05
    pulse_phase = 0
    glow_radius = 0
    max_glow = 30
    glow_speed = 0.5
    glow_alpha = 0
    fade_in_time = 0
    max_fade_in = 300  # 5 seconds at 60 FPS
    search_time = 0
    hint_alpha = 0
    
    message_text = None
    message_timer = 0
    message_alpha = 255
    clue_found = False
    hint = get_smart_hint(found_clues, points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, YELLOW)
    instruction = font.render("Search for the hidden logbook...", True, WHITE)
    running = True
    clock = pygame.time.Clock()

    text_to_speech("Search for the hidden logbook to find the clue.", language)

    while running:
        screen.blit(pygame.transform.scale(detective_bg1, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))

        if not clue_found:
            # Update fade in and search time
            search_time += 1
            if search_time > 180:  # 3 seconds before starting to fade in
                fade_in_time = min(fade_in_time + 1, max_fade_in)
                fade_ratio = fade_in_time / max_fade_in
                
                # Update pulse and glow effects
                pulse_phase += pulse_speed
                glow_radius = int((math.sin(pulse_phase) + 1) * max_glow / 2 * fade_ratio)
                glow_alpha = int((math.sin(pulse_phase) + 1) * 127.5 * fade_ratio)
                
                # Create glow effect
                glow_surface = pygame.Surface((60 + glow_radius * 2, 80 + glow_radius * 2), pygame.SRCALPHA)
                glow_surface.fill((0, 0, 0, 0))
                pygame.draw.rect(glow_surface, (255, 255, 0, glow_alpha), 
                               (glow_radius, glow_radius, 60, 80), 
                               border_radius=5)
                
                # Draw glow
                screen.blit(glow_surface, (logbook_rect.x - glow_radius, logbook_rect.y - glow_radius))
                
                # Draw logbook with pulsing scale
                scale = 1 + math.sin(pulse_phase) * 0.1
                scaled_logbook = pygame.transform.scale(logbook, 
                    (int(60 * scale), int(80 * scale)))
                scaled_rect = scaled_logbook.get_rect(center=logbook_rect.center)
                scaled_logbook.set_alpha(int(255 * fade_ratio))
                screen.blit(scaled_logbook, scaled_rect)

            # Show subtle hint after some time
            if search_time > 360 and not clue_found:  # 6 seconds
                hint_alpha = min(hint_alpha + 1, 100)
                hint_surface = font.render("Look around the center of the screen...", True, (255, 255, 255, hint_alpha))
                screen.blit(hint_surface, hint_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150)))

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, WHITE)
            message_surface.set_alpha(message_alpha)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
            screen.blit(message_surface, message_rect)
            if clue_found:
                screen.blit(logbook, (WIDTH // 2 - 30, HEIGHT // 2 + 100))
                message_alpha = max(message_alpha - 5, 0)
            message_timer -= 1
            if message_timer <= 0 and clue_found:
                print(f"pin_view_1: found_clues = {found_clues}")
                return points, found_clues

        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return points, found_clues
            elif event.type == pygame.MOUSEBUTTONDOWN and not clue_found:
                if logbook_rect.collidepoint(event.pos) and fade_in_time > 0:
                    points += 10
                    found_clues.append("clue1")
                    message_text = translations[language]["Clue1"]
                    message_timer = 120
                    clue_found = True
                    text_to_speech(message_text, language)
    return points, found_clues

def pin_view_2(screen, points, found_clues, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    
    # Create glass shard surface
    glass = pygame.Surface((50, 70), pygame.SRCALPHA)
    pygame.draw.polygon(glass, (173, 216, 230), [(25, 0), (50, 20), (40, 70), (10, 70), (0, 20)])
    
    # Glass properties - random position in left side
    glass_rect = glass.get_rect(center=(
        random.randint(100, WIDTH // 2 - 100),
        random.randint(HEIGHT // 4, 3 * HEIGHT // 4)
    ))
    pulse_speed = 0.05
    pulse_phase = 0
    glow_radius = 0
    max_glow = 40
    glow_speed = 0.5
    glow_alpha = 0
    rotation_angle = 0
    fade_in_time = 0
    max_fade_in = 300  # 5 seconds at 60 FPS
    search_time = 0
    hint_alpha = 0
    
    message_text = None
    message_timer = 0
    message_alpha = 255
    clue_found = False
    hint = get_smart_hint(found_clues, points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, YELLOW)
    instruction = font.render("Search for the hidden glass shard...", True, WHITE)
    running = True
    clock = pygame.time.Clock()

    text_to_speech("Search for the hidden glass shard to find the clue.", language)

    while running:
        screen.blit(pygame.transform.scale(detective_bg2, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))

        if not clue_found:
            # Update fade in and search time
            search_time += 1
            if search_time > 180:  # 3 seconds before starting to fade in
                fade_in_time = min(fade_in_time + 1, max_fade_in)
                fade_ratio = fade_in_time / max_fade_in
                
                # Update pulse and glow effects
                pulse_phase += pulse_speed
                glow_radius = int((math.sin(pulse_phase) + 1) * max_glow / 2 * fade_ratio)
                glow_alpha = int((math.sin(pulse_phase) + 1) * 127.5 * fade_ratio)
                rotation_angle = math.sin(pulse_phase * 2) * 15 * fade_ratio
                
                # Create glow effect
                glow_surface = pygame.Surface((50 + glow_radius * 2, 70 + glow_radius * 2), pygame.SRCALPHA)
                glow_surface.fill((0, 0, 0, 0))
                pygame.draw.polygon(glow_surface, (173, 216, 230, glow_alpha), 
                                  [(25 + glow_radius, glow_radius), 
                                   (50 + glow_radius, 20 + glow_radius),
                                   (40 + glow_radius, 70 + glow_radius),
                                   (10 + glow_radius, 70 + glow_radius),
                                   (glow_radius, 20 + glow_radius)])
                
                # Draw glow
                screen.blit(glow_surface, (glass_rect.x - glow_radius, glass_rect.y - glow_radius))
                
                # Draw glass with rotation and scaling
                scale = 1 + math.sin(pulse_phase) * 0.1
                rotated_glass = pygame.transform.rotate(glass, rotation_angle)
                scaled_glass = pygame.transform.scale(rotated_glass, 
                    (int(50 * scale), int(70 * scale)))
                scaled_rect = scaled_glass.get_rect(center=glass_rect.center)
                scaled_glass.set_alpha(int(255 * fade_ratio))
                screen.blit(scaled_glass, scaled_rect)

            # Show subtle hint after some time
            if search_time > 360 and not clue_found:  # 6 seconds
                hint_alpha = min(hint_alpha + 1, 100)
                hint_surface = font.render("Look for something sparkling in the center...", True, (255, 255, 255, hint_alpha))
                screen.blit(hint_surface, hint_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150)))

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, WHITE)
            message_surface.set_alpha(message_alpha)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
            screen.blit(message_surface, message_rect)
            if clue_found:
                screen.blit(glass, (WIDTH // 2 - 25, HEIGHT // 2 + 100))
                message_alpha = max(message_alpha - 5, 0)
            message_timer -= 1
            if message_timer <= 0 and clue_found:
                print(f"pin_view_2: found_clues = {found_clues}")
                return points, found_clues

        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return points, found_clues
            elif event.type == pygame.MOUSEBUTTONDOWN and not clue_found:
                if glass_rect.collidepoint(event.pos) and fade_in_time > 0:
                    points += 10
                    found_clues.append("clue2")
                    message_text = translations[language]["Clue2"]
                    message_timer = 120
                    clue_found = True
                    text_to_speech(message_text, language)
    return points, found_clues

def pin_view_3(screen, points, found_clues, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    
    # Create note surface
    note = pygame.Surface((70, 50), pygame.SRCALPHA)
    note.fill((245, 245, 220))
    pygame.draw.rect(note, BLACK, (0, 0, 70, 50), 2)
    pygame.draw.line(note, BLACK, (10, 25), (60, 25), 1)
    
    # Note properties - random position in bottom area
    note_rect = note.get_rect(center=(
        random.randint(WIDTH // 4, 3 * WIDTH // 4),
        random.randint(HEIGHT // 2 + 100, HEIGHT - 100)
    ))
    pulse_speed = 0.05
    pulse_phase = 0
    glow_radius = 0
    max_glow = 35
    glow_speed = 0.5
    glow_alpha = 0
    wave_offset = 0
    fade_in_time = 0
    max_fade_in = 300  # 5 seconds at 60 FPS
    search_time = 0
    hint_alpha = 0
    
    message_text = None
    message_timer = 0
    message_alpha = 255
    clue_found = False
    hint = get_smart_hint(found_clues, points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, YELLOW)
    instruction = font.render("Search for the hidden note...", True, WHITE)
    running = True
    clock = pygame.time.Clock()

    text_to_speech("Search for the hidden note to find the clue.", language)

    while running:
        screen.blit(pygame.transform.scale(detective_bg3, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))

        if not clue_found:
            # Update fade in and search time
            search_time += 1
            if search_time > 180:  # 3 seconds before starting to fade in
                fade_in_time = min(fade_in_time + 1, max_fade_in)
                fade_ratio = fade_in_time / max_fade_in
                
                # Update pulse and glow effects
                pulse_phase += pulse_speed
                glow_radius = int((math.sin(pulse_phase) + 1) * max_glow / 2 * fade_ratio)
                glow_alpha = int((math.sin(pulse_phase) + 1) * 127.5 * fade_ratio)
                wave_offset = math.sin(pulse_phase * 1.5) * 20 * fade_ratio
                
                # Create glow effect
                glow_surface = pygame.Surface((70 + glow_radius * 2, 50 + glow_radius * 2), pygame.SRCALPHA)
                glow_surface.fill((0, 0, 0, 0))
                pygame.draw.rect(glow_surface, (255, 255, 255, glow_alpha), 
                               (glow_radius, glow_radius, 70, 50), 
                               border_radius=5)
                
                # Draw glow
                screen.blit(glow_surface, (note_rect.x - glow_radius, note_rect.y - glow_radius))
                
                # Draw note with floating effect
                scale = 1 + math.sin(pulse_phase) * 0.1
                scaled_note = pygame.transform.scale(note, 
                    (int(70 * scale), int(50 * scale)))
                scaled_rect = scaled_note.get_rect(center=(note_rect.centerx, note_rect.centery + wave_offset))
                scaled_note.set_alpha(int(255 * fade_ratio))
                screen.blit(scaled_note, scaled_rect)

            # Show subtle hint after some time
            if search_time > 360 and not clue_found:  # 6 seconds
                hint_alpha = min(hint_alpha + 1, 100)
                hint_surface = font.render("Look for something floating in the center...", True, (255, 255, 255, hint_alpha))
                screen.blit(hint_surface, hint_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150)))

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, WHITE)
            message_surface.set_alpha(message_alpha)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
            screen.blit(message_surface, message_rect)
            if clue_found:
                screen.blit(note, (WIDTH // 2 - 35, HEIGHT // 2 + 100))
                message_alpha = max(message_alpha - 5, 0)
            message_timer -= 1
            if message_timer <= 0 and clue_found:
                print(f"pin_view_3: found_clues = {found_clues}")
                return points, found_clues

        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return points, found_clues
            elif event.type == pygame.MOUSEBUTTONDOWN and not clue_found:
                if note_rect.collidepoint(event.pos) and fade_in_time > 0:
                    points += 10
                    found_clues.append("clue3")
                    message_text = translations[language]["Clue3"]
                    message_timer = 120
                    clue_found = True
                    text_to_speech(message_text, language)
    return points, found_clues
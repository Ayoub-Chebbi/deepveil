import pygame
import sys
import math
import random
from config import WIDTH, HEIGHT, translations, GREEN, WHITE, DARK_GRAY, LIGHT_GRAY, BLUE, BLUE_HOVER, RED, YELLOW, BLACK
from assets import background_image, new_background_image, pin_image, suspect_image, level_image, hallway_image, detective_bg1, detective_bg2, detective_bg3, hero_image, logbook, glass, note, cloth, key, letter, room1, room2, room3
from ai import suspect_ai, get_smart_hint
from speech import text_to_speech
from utils import draw_button

def run_game(screen, language):
    try:
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
                            try:
                                if i == 0:
                                    intro_view(screen, language, level=1)
                                    screen.fill(BLACK)
                                    pygame.display.flip()
                                    points, found_clues, level2_unlocked = new_view(screen, 0, [], language, level=1)
                                    if level2_unlocked:
                                        locked[1] = False
                                elif i == 1:
                                    intro_view(screen, language, level=2)
                                    screen.fill(BLACK)
                                    pygame.display.flip()
                                    points, found_clues, level3_unlocked = new_view(screen, 0, [], language, level=2)
                                    if level3_unlocked:
                                        locked[2] = False
                            except Exception as e:
                                print(f"Error when selecting level {i+1}: {str(e)}")
                                running = False
        pygame.quit()
        sys.exit()
    except Exception as e:
        print(f"Error in run_game: {str(e)}")
        pygame.quit()
        sys.exit(1)

def new_view(screen, points, found_clues, language, level):
    try:
        from views import win_view, lose_view, evidence_board_view, suspect_background_view
        WIDTH, HEIGHT = screen.get_size()
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
        
        # Safely get translations with fallbacks
        def get_translation(key, default=""):
            try:
                return translations[language][key]
            except (KeyError, TypeError):
                print(f"Missing translation for key: {key}")
                return default
                
        objectives = [get_translation(f"Objective{i+1}_Level{level}", f"Objective {i+1}") for i in range(3)]
        completed_objectives = [False, False, False]
        unlocked_pin1 = False
        unlocked_pin2 = False
        unlocked_pin3 = False
        select_mode = False
        running = True
        clock = pygame.time.Clock()

        # Initialize states based on found_clues
        clue_keys = [f"clue{i+1}_level{level}" for i in range(3)]
        if clue_keys[0] in found_clues:
            suspect_visibility[0] = True
            completed_objectives[0] = True
            current_pin_index = 1
            unlocked_pin1 = True
        if clue_keys[1] in found_clues:
            suspect_visibility[1] = True
            completed_objectives[1] = True
            current_pin_index = 2
            unlocked_pin2 = True
        if clue_keys[2] in found_clues:
            suspect_visibility[2] = True
            completed_objectives[2] = True
            unlocked_pin3 = True

        while running:
            try:
                screen.blit(pygame.transform.scale(new_background_image, (WIDTH, HEIGHT)), (0, 0))
                mission_text = mission_font.render(get_translation("Mission", "Mission"), True, (0, 255, 255))
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
                        suspect_text = font.render(translations[language][f"Suspect{i+1}_Level{level}" if level == 2 else f"Suspect{i+1}"], True, WHITE)
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
                        if len(found_clues) == 3 and explore_button.collidepoint(event.pos):
                            suspect_background_view(screen, language, level)
                        if len(found_clues) == 3 and select_box.collidepoint(event.pos):
                            select_mode = not select_mode
                            text_to_speech("Select a suspect now.", language)
                        if evidence_button.collidepoint(event.pos):
                            evidence_board_view(screen, language, found_clues, level)
                        for i, rect in enumerate(suspect_rects):
                            if rect.collidepoint(event.pos) and suspect_visibility[i] and len(found_clues) == 3 and select_mode:
                                select_mode = False
                                if i == correct_suspect:
                                    win_view(screen, language)
                                    return points, found_clues, True
                                else:
                                    lose_view(screen, language)
                                    return points, found_clues, False
                        for i, pin_rect in enumerate(pin_rects):
                            if pin_rect.collidepoint(event.pos) and i == current_pin_index:
                                if i == 0:
                                    if unlocked_pin1:
                                        pin_view_index = hall_view(screen, points, language, 0)
                                        if pin_view_index == 0:
                                            points, found_clues = pin_view_1(screen, points, found_clues, language, level)
                                    else:
                                        points, unlocked_pin1 = puzzle_view_1(screen, points, language, level)
                                elif i == 1:
                                    if unlocked_pin2:
                                        pin_view_index = hall_view(screen, points, language, 1)
                                        if pin_view_index == 1:
                                            points, found_clues = pin_view_2(screen, points, found_clues, language, level)
                                    else:
                                        points, unlocked_pin2 = puzzle_view_2(screen, points, language, level)
                                elif i == 2:
                                    if unlocked_pin3:
                                        pin_view_index = hall_view(screen, points, language, 2)
                                        if pin_view_index == 2:
                                            points, found_clues = pin_view_3(screen, points, found_clues, language, level)
                                    else:
                                        points, unlocked_pin3 = puzzle_view_3(screen, points, language, level)
                                if f"clue1_level{level}" in found_clues and not suspect_visibility[0]:
                                    suspect_visibility[0] = True
                                    completed_objectives[0] = True
                                    current_pin_index = 1
                                elif f"clue2_level{level}" in found_clues and not suspect_visibility[1]:
                                    suspect_visibility[1] = True
                                    completed_objectives[1] = True
                                    current_pin_index = 2
                                elif f"clue3_level{level}" in found_clues and not suspect_visibility[2]:
                                    suspect_visibility[2] = True
                                    completed_objectives[2] = True
                                    suspect_visibility = suspect_ai(found_clues, suspect_visibility, language, points)
            except Exception as e:
                print(f"Error in new_view: {e}")
                import traceback
                traceback.print_exc()
        return points, found_clues, False
    except Exception as e:
        print(f"Error in new_view: {e}")
        pygame.quit()
        sys.exit(1)

def suspect_background_view(screen, language, level):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 28)
    title_font = pygame.font.Font(None, 48)
    suspect_positions = [(WIDTH - WIDTH // 3 - 50, HEIGHT // 2), (WIDTH - WIDTH // 4 - 50, HEIGHT // 2), (WIDTH - WIDTH // 6 - 50, HEIGHT // 2)]
    suspect_rects = [pygame.Rect(x, y, 70, 100) for x, y in suspect_positions]
    back_button = pygame.Rect(0, 0, 200, 60)
    back_button.center = (WIDTH // 2, HEIGHT - 100)
    
    question_buttons = [
        pygame.Rect(WIDTH // 4, HEIGHT // 3, 300, 50),
        pygame.Rect(WIDTH // 4, HEIGHT // 3 + 70, 300, 50),
        pygame.Rect(WIDTH // 4, HEIGHT // 3 + 140, 300, 50)
    ]
    
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

    text_to_speech("Explore the suspect backgrounds and interrogate them.", language)

    while running:
        screen.blit(pygame.transform.scale(detective_bg1, (WIDTH, HEIGHT)), (0, 0))
        title_text = title_font.render(translations[language]["Explore Suspect Background"], True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 50)))

        for i, pos in enumerate(suspect_positions):
            screen.blit(pygame.transform.scale(suspect_image, (70, 100)), pos)
            suspect_text = font.render(translations[language][f"Suspect{i+1}_Level{level}" if level == 2 else f"Suspect{i+1}"], True, WHITE)
            screen.blit(suspect_text, suspect_text.get_rect(center=(pos[0] + 35, pos[1] + 115)))
            background_text = font.render(translations[language][f"Suspect{i+1}_Background"], True, YELLOW)
            screen.blit(background_text, background_text.get_rect(center=(pos[0] + 35, pos[1] + 150)))

        if selected_suspect is not None:
            for i, button in enumerate(question_buttons):
                hover = button.collidepoint(pygame.mouse.get_pos())
                color = BLUE_HOVER if hover else BLUE
                pygame.draw.rect(screen, color, button, border_radius=5)
                question_text = font.render(questions[selected_suspect][i], True, WHITE)
                screen.blit(question_text, question_text.get_rect(center=button.center))

        if answer_text and answer_timer > 0:
            answer_surface = font.render(answer_text, True, WHITE)
            answer_surface.set_alpha(answer_alpha)
            answer_rect = answer_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, answer_rect.inflate(20, 20), border_radius=10)
            screen.blit(answer_surface, answer_rect)
            answer_alpha = max(answer_alpha - 2, 0)
            answer_timer -= 1

        draw_button(screen, back_button, BLUE, BLUE_HOVER, translations[language]["Back"], font, pygame.mouse.get_pos())

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
                
                for i, rect in enumerate(suspect_rects):
                    if rect.collidepoint(event.pos):
                        selected_suspect = i
                        text_to_speech(f"Selected suspect {i+1}. What would you like to ask?", language)
                        break
                
                if selected_suspect is not None:
                    for i, button in enumerate(question_buttons):
                        if button.collidepoint(event.pos):
                            current_question = i
                            answer_text = answers[selected_suspect][i]
                            answer_timer = 120
                            answer_alpha = 255
                            text_to_speech(answer_text, language)

def hall_view(screen, points, language, pin_index):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    background = hallway_image
    
    avatar = pygame.transform.scale(hero_image, (280, 280))
    avatar_rect = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 180, 280, 280)
    
    light_positions = [
        (WIDTH // 2, HEIGHT // 2 + 180),
        (3 * WIDTH // 4, HEIGHT // 2 + 180),
        (100, HEIGHT // 2 + 180)
    ]
    
    light_rect = pygame.Rect(light_positions[pin_index][0] - 25, light_positions[pin_index][1] - 25, 50, 50)
    light_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
    avatar_speed = 5
    
    instruction_texts = [
        translations[language]["Move to the yellow light"],
        translations[language]["Move to the yellow light"],
        translations[language]["Move to the yellow light"]
    ]
    instruction = font.render(instruction_texts[pin_index], True, (0, 255, 255))
    
    running = True
    clock = pygame.time.Clock()

    text_to_speech(f"Move to the yellow light for door {pin_index + 1}", language)

    while running:
        screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))
        glow_alpha = 128 + int(127 * math.sin(pygame.time.get_ticks() / 500))
        light_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(light_surface, (255, 255, 0, glow_alpha), (0, 0, 50, 50), border_radius=5)
        screen.blit(light_surface, light_rect)
        screen.blit(avatar, avatar_rect)
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, (0, 255, 255))
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return -1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            avatar_rect.x -= avatar_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            avatar_rect.x += avatar_speed
        
        avatar_rect.x = max(0, min(WIDTH - avatar_rect.width, avatar_rect.x))

        if avatar_rect.colliderect(light_rect):
            return pin_index

    return -1

def puzzle_view_1(screen, points, language, level):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    
    puzzle_bg = pygame.Surface((300, 300), pygame.SRCALPHA)
    puzzle_bg.fill((30, 30, 30, 200))
    puzzle_bg_rect = puzzle_bg.get_rect(center=(WIDTH//2, HEIGHT//2))
    
    if level == 1:
        # Level 1: Regular tic-tac-toe
        grid = [[None for _ in range(3)] for _ in range(3)]
        cell_rects = [pygame.Rect(WIDTH // 2 - 90 + x * 60, HEIGHT // 2 - 90 + y * 60, 50, 50) for y in range(3) for x in range(3)]
        instruction = font.render("Get 3 X's in a row", True, (0, 255, 255))
        player_char = 'X'
        ai_char = 'O'
    else:
        # Level 2: 4x4 tic-tac-toe with diagonal win
        grid = [[None for _ in range(4)] for _ in range(4)]
        cell_rects = [pygame.Rect(WIDTH // 2 - 120 + x * 60, HEIGHT // 2 - 120 + y * 60, 50, 50) for y in range(4) for x in range(4)]
        instruction = font.render("Get 3 O's in a diagonal", True, (0, 255, 255))
        player_char = 'O'
        ai_char = 'X'
    
    message_text = None
    message_timer = 0
    message_alpha = 255
    puzzle_solved = False
    hint = get_smart_hint([], points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, (0, 255, 255))
    running = True
    clock = pygame.time.Clock()
    
    ai_move_delay = 0
    ai_move_pending = False
    ai_move_position = None

    def check_win(board, player):
        if level == 1:
            # Regular tic-tac-toe win conditions
            for i in range(3):
                if all(board[i][j] == player for j in range(3)) or all(board[j][i] == player for j in range(3)):
                    return True
            if all(board[i][i] == player for i in range(3)) or all(board[i][2-i] == player for i in range(3)):
                return True
        else:
            # Level 2: Check diagonals in 4x4 grid
            # Main diagonals
            if all(board[i][i] == player for i in range(4)) or all(board[i][3-i] == player for i in range(4)):
                return True
            # Check all possible 3-in-a-row diagonals
            for i in range(2):
                for j in range(2):
                    if all(board[i+k][j+k] == player for k in range(3)):
                        return True
                    if all(board[i+k][3-(j+k)] == player for k in range(3)):
                        return True
        return False

    def ai_move(board, player, opponent):
        if level == 1:
            # Level 1: Easy AI with mostly random moves
            if random.random() < 0.8:
                available = [(i, j) for i in range(3) for j in range(3) if board[i][j] is None]
                if available:
                    return random.choice(available)
                return None
        else:
            # Level 2: Slightly smarter AI for 4x4
            if random.random() < 0.6:  # 60% random moves
                available = [(i, j) for i in range(4) for j in range(4) if board[i][j] is None]
                if available:
                    return random.choice(available)
                return None
            
        # Try to win
        for i in range(4 if level == 2 else 3):
            for j in range(4 if level == 2 else 3):
                if board[i][j] is None:
                    board[i][j] = player
                    if check_win(board, player):
                        board[i][j] = None
                        return i, j
                    board[i][j] = None
                    
        # Block opponent's win
        for i in range(4 if level == 2 else 3):
            for j in range(4 if level == 2 else 3):
                if board[i][j] is None:
                    board[i][j] = opponent
                    if check_win(board, opponent):
                        board[i][j] = None
                        return i, j
                    board[i][j] = None
                    
        # Center if available
        center = 2 if level == 1 else 1
        if board[center][center] is None:
            return center, center
            
        # Random corner or edge
        corners = [(0, 0), (0, 3 if level == 2 else 2), (3 if level == 2 else 2, 0), (3 if level == 2 else 2, 3 if level == 2 else 2)]
        edges = [(0, 1), (1, 0), (1, 3 if level == 2 else 2), (3 if level == 2 else 2, 1)]
        available_corners = [pos for pos in corners if board[pos[0]][pos[1]] is None]
        available_edges = [pos for pos in edges if board[pos[0]][pos[1]] is None]
        
        if available_corners:
            return random.choice(available_corners)
        if available_edges:
            return random.choice(available_edges)
            
        # Any available spot
        available = [(i, j) for i in range(4 if level == 2 else 3) for j in range(4 if level == 2 else 3) if board[i][j] is None]
        return random.choice(available) if available else None

    text_to_speech(f"Get three {player_char}'s in a {'diagonal' if level == 2 else 'row'} to unlock the clue.", language)

    while running:
        screen.blit(pygame.transform.scale(new_background_image, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(puzzle_bg, puzzle_bg_rect)
        
        grid_size = 4 if level == 2 else 3
        for i in range(grid_size + 1):
            pygame.draw.line(screen, (100, 100, 100), 
                           (WIDTH//2 - (90 if level == 1 else 120) + i*60, HEIGHT//2 - (90 if level == 1 else 120)),
                           (WIDTH//2 - (90 if level == 1 else 120) + i*60, HEIGHT//2 + (90 if level == 1 else 120)), 2)
            pygame.draw.line(screen, (100, 100, 100),
                           (WIDTH//2 - (90 if level == 1 else 120), HEIGHT//2 - (90 if level == 1 else 120) + i*60),
                           (WIDTH//2 + (90 if level == 1 else 120), HEIGHT//2 - (90 if level == 1 else 120) + i*60), 2)
        
        for i, rect in enumerate(cell_rects):
            x, y = i % grid_size, i // grid_size
            cell_bg = pygame.Surface((50, 50), pygame.SRCALPHA)
            cell_bg.fill((50, 50, 50, 200))
            screen.blit(cell_bg, rect)
            
            if grid[y][x] == 'X':
                text = font.render('X', True, BLUE)
                screen.blit(text, text.get_rect(center=rect.center))
            elif grid[y][x] == 'O':
                text = font.render('O', True, RED)
                screen.blit(text, text.get_rect(center=rect.center))
        
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, (0, 255, 255))
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, (0, 255, 255))
            message_surface.set_alpha(message_alpha)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
            screen.blit(message_surface, message_rect)
            message_alpha = max(message_alpha - 5, 0)
            message_timer -= 1
            if message_timer <= 0 and puzzle_solved:
                return points, True
                
        if ai_move_pending:
            ai_move_delay += 1
            if ai_move_delay > 30:
                if ai_move_position:
                    y, x = ai_move_position
                    grid[y][x] = ai_char
                    if check_win(grid, ai_char):
                        points = max(0, points - 5)
                        message_text = "You Lost. Try Again."
                        message_timer = 60
                        text_to_speech("You lost. Try again.", language)
                        grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
                ai_move_pending = False
                ai_move_delay = 0
                ai_move_position = None

        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return points, False
            elif event.type == pygame.MOUSEBUTTONDOWN and not ai_move_pending:
                for i, rect in enumerate(cell_rects):
                    if rect.collidepoint(event.pos):
                        x, y = i % grid_size, i // grid_size
                        if grid[y][x] is None:
                            grid[y][x] = player_char
                            if check_win(grid, player_char):
                                points += 10
                                message_text = "Access Granted"
                                message_timer = 120
                                puzzle_solved = True
                                text_to_speech("Access granted. Entering the room.", language)
                            else:
                                ai_move_position = ai_move(grid, ai_char, player_char)
                                ai_move_pending = True
                                ai_move_delay = 0
    return points, False

def puzzle_view_2(screen, points, language, level):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    
    puzzle_bg = pygame.Surface((300, 300), pygame.SRCALPHA)
    puzzle_bg.fill((30, 30, 30, 200))
    puzzle_bg_rect = puzzle_bg.get_rect(center=(WIDTH//2, HEIGHT//2))
    
    if level == 1:
        # Level 1: Regular sliding puzzle
        grid = [
            [1, 2, 3, 4],
            [5, 6, 7, 8], 
            [9, 10, 11, 12],
            [13, 14, 15, None]
        ]
        target_piece = 15
        instruction = font.render(f"Slide to move piece {target_piece} to center", True, (0, 255, 255))
    else:
        # Level 2: 5x5 sliding puzzle with multiple targets
        grid = [
            [1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10],
            [11, 12, 13, 14, 15],
            [16, 17, 18, 19, 20],
            [21, 22, 23, 24, None]
        ]
        target_pieces = [13, 14, 15]  # Need to get any of these to center
        instruction = font.render("Slide to move any target piece to center", True, (0, 255, 255))
    
    tile_size = 50 if level == 1 else 40
    spacing = 10 if level == 1 else 5
    grid_size = 4 if level == 1 else 5
    
    tile_rects = [pygame.Rect(WIDTH // 2 - (grid_size * (tile_size + spacing)) // 2 + x * (tile_size + spacing),
                            HEIGHT // 2 - (grid_size * (tile_size + spacing)) // 2 + y * (tile_size + spacing),
                            tile_size, tile_size) for y in range(grid_size) for x in range(grid_size)]
    
    message_text = None
    message_timer = 0
    message_alpha = 255
    puzzle_solved = False
    hint = get_smart_hint([], points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, (0, 255, 255))
    running = True
    clock = pygame.time.Clock()

    def find_empty():
        for y in range(grid_size):
            for x in range(grid_size):
                if grid[y][x] is None:
                    return x, y
        return None

    def is_solved():
        if level == 1:
            return grid[1][1] == target_piece or grid[1][2] == target_piece or grid[2][1] == target_piece or grid[2][2] == target_piece
        else:
            center_y, center_x = grid_size // 2, grid_size // 2
            return grid[center_y][center_x] in target_pieces

    text_to_speech(f"Slide the blocks to move {'any target piece' if level == 2 else f'piece {target_piece}'} to the center to unlock the clue.", language)

    while running:
        screen.blit(pygame.transform.scale(new_background_image, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(puzzle_bg, puzzle_bg_rect)
        
        for i in range(grid_size + 1):
            pygame.draw.line(screen, (100, 100, 100), 
                           (WIDTH//2 - (grid_size * (tile_size + spacing)) // 2 + i*(tile_size + spacing), HEIGHT//2 - (grid_size * (tile_size + spacing)) // 2),
                           (WIDTH//2 - (grid_size * (tile_size + spacing)) // 2 + i*(tile_size + spacing), HEIGHT//2 + (grid_size * (tile_size + spacing)) // 2), 2)
            pygame.draw.line(screen, (100, 100, 100),
                           (WIDTH//2 - (grid_size * (tile_size + spacing)) // 2, HEIGHT//2 - (grid_size * (tile_size + spacing)) // 2 + i*(tile_size + spacing)),
                           (WIDTH//2 + (grid_size * (tile_size + spacing)) // 2, HEIGHT//2 - (grid_size * (tile_size + spacing)) // 2 + i*(tile_size + spacing)), 2)
        
        for i, rect in enumerate(tile_rects):
            x, y = i % grid_size, i // grid_size
            if grid[y][x] is not None:
                tile_bg = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                tile_bg.fill((50, 50, 50, 200))
                screen.blit(tile_bg, rect)
                
                if level == 1:
                    is_target = grid[y][x] == target_piece
                else:
                    is_target = grid[y][x] in target_pieces
                
                if is_target:
                    scaled_pin = pygame.transform.scale(pin_image, (tile_size, tile_size))
                    screen.blit(scaled_pin, rect)
                else:
                    text = font.render(str(grid[y][x]), True, WHITE)
                    screen.blit(text, text.get_rect(center=rect.center))
        
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 180)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, (0, 255, 255))
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, (0, 255, 255))
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
            elif event.type == pygame.MOUSEBUTTONDOWN and not puzzle_solved:
                empty_pos = find_empty()
                if empty_pos is None:
                    continue
                empty_x, empty_y = empty_pos
                for i, rect in enumerate(tile_rects):
                    if rect.collidepoint(event.pos):
                        x, y = i % grid_size, i // grid_size
                        if (abs(x - empty_x) == 1 and y == empty_y) or (abs(y - empty_y) == 1 and x == empty_x):
                            grid[empty_y][empty_x], grid[y][x] = grid[y][x], grid[empty_y][empty_x]
                            if is_solved():
                                points += 10
                                message_text = "Access Granted"
                                message_timer = 120
                                puzzle_solved = True
                                text_to_speech("Access granted. Entering the room.", language)
                            break
    return points, False

def puzzle_view_3(screen, points, language, level):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    
    puzzle_bg = pygame.Surface((400, 400), pygame.SRCALPHA)
    puzzle_bg.fill((30, 30, 30, 200))
    puzzle_bg_rect = puzzle_bg.get_rect(center=(WIDTH//2, HEIGHT//2))
    
    if level == 1:
        # Level 1: Regular memory matching with symbols
        symbols = ['!', '@', '#', '$', '%', '&', '*', '+']
        grid_size = 4
        card_size = 80
        card_spacing = 20
    else:
        # Level 2: Memory matching with words and time limit
        symbols = ['CAT', 'DOG', 'BIRD', 'FISH', 'BEAR', 'LION', 'WOLF', 'DEER']
        grid_size = 4
        card_size = 100
        card_spacing = 10
    
    pairs = symbols * 2
    random.shuffle(pairs)
    
    cards = []
    start_x = WIDTH // 2 - (grid_size * (card_size + card_spacing)) // 2
    start_y = HEIGHT // 2 - (grid_size * (card_size + card_spacing)) // 2
    
    for i in range(grid_size * grid_size):
        row = i // grid_size
        col = i % grid_size
        x = start_x + col * (card_size + card_spacing)
        y = start_y + row * (card_size + card_spacing)
        cards.append({
            'rect': pygame.Rect(x, y, card_size, card_size),
            'symbol': pairs[i],
            'flipped': False,
            'matched': False,
            'flip_angle': 0,
            'flip_direction': 1,
            'flip_speed': 5
        })
    
    first_card = None
    second_card = None
    matched_pairs = 0
    message_text = None
    message_timer = 0
    message_alpha = 255
    puzzle_solved = False
    hint = get_smart_hint([], points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, (0, 255, 255))
    instruction = font.render("Match all pairs" + (" (with time limit)" if level == 2 else ""), True, (0, 255, 255))
    running = True
    clock = pygame.time.Clock()
    
    # Level 2 specific variables
    time_limit = 60 if level == 2 else None  # 60 seconds time limit
    start_time = pygame.time.get_ticks() if level == 2 else None
    time_remaining = time_limit

    text_to_speech("Match all pairs" + (" within the time limit" if level == 2 else "") + " to unlock the clue.", language)

    while running:
        screen.blit(pygame.transform.scale(new_background_image, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(puzzle_bg, puzzle_bg_rect)
        
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, (0, 255, 255))
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))
        
        if level == 2:
            # Update time remaining
            current_time = pygame.time.get_ticks()
            time_remaining = max(0, time_limit - (current_time - start_time) // 1000)
            if time_remaining == 0 and not puzzle_solved:
                message_text = "Time's Up! Try Again."
                message_timer = 60
                text_to_speech("Time's up. Try again.", language)
                # Reset the puzzle
                random.shuffle(pairs)
                for i, card in enumerate(cards):
                    card['symbol'] = pairs[i]
                    card['flipped'] = False
                    card['matched'] = False
                first_card = None
                second_card = None
                matched_pairs = 0
                start_time = pygame.time.get_ticks()
            
            # Display time remaining
            time_text = font.render(f"Time: {time_remaining}s", True, (255, 0, 0) if time_remaining < 10 else (0, 255, 255))
            screen.blit(time_text, time_text.get_rect(center=(WIDTH // 2, 20)))

        for card in cards:
            if not card['matched']:
                card_surface = pygame.Surface((card_size, card_size), pygame.SRCALPHA)
                shadow = pygame.Surface((card_size + 10, card_size + 10), pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 100))
                pygame.draw.rect(shadow, (0, 0, 0, 100), (0, 0, card_size + 10, card_size + 10), border_radius=10)
                
                if card['flipped']:
                    pygame.draw.rect(card_surface, (255, 255, 255), (0, 0, card_size, card_size), border_radius=10)
                    symbol_text = font.render(card['symbol'], True, (0, 0, 0))
                    screen.blit(shadow, (card['rect'].x - 5, card['rect'].y - 5))
                    screen.blit(card_surface, card['rect'])
                    screen.blit(symbol_text, symbol_text.get_rect(center=card['rect'].center))
                else:
                    pygame.draw.rect(card_surface, (0, 100, 200), (0, 0, card_size, card_size), border_radius=10)
                    pygame.draw.rect(card_surface, (0, 150, 255), (5, 5, card_size - 10, card_size - 10), border_radius=10)
                    screen.blit(shadow, (card['rect'].x - 5, card['rect'].y - 5))
                    screen.blit(card_surface, card['rect'])

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, (0, 255, 255))
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
            elif event.type == pygame.MOUSEBUTTONDOWN and not puzzle_solved:
                for card in cards:
                    if not card['matched'] and not card['flipped'] and card['rect'].collidepoint(event.pos):
                        card['flipped'] = True
                        
                        if first_card is None:
                            first_card = card
                        else:
                            second_card = card
                            
                            if first_card['symbol'] == second_card['symbol']:
                                first_card['matched'] = True
                                second_card['matched'] = True
                                matched_pairs += 1
                                
                                if matched_pairs == len(symbols):
                                    points += 10
                                    message_text = "Access Granted"
                                    message_timer = 120
                                    puzzle_solved = True
                                    text_to_speech("Access granted. Entering the room.", language)
                            else:
                                first_card['flipped'] = False
                                second_card['flipped'] = False
                            
                            first_card = None
                            second_card = None
                        break
    return points, False

def pin_view_1(screen, points, found_clues, language, level):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    
    clue_surface = logbook if level == 1 else cloth
    clue_rect = clue_surface.get_rect(center=(
        random.randint(WIDTH // 2 + 100, WIDTH - 100),
        random.randint(100, HEIGHT - 100)
    ))
    pulse_speed = 0.05
    pulse_phase = 0
    glow_radius = 0
    max_glow = 30
    glow_speed = 0.5
    glow_alpha = 0
    fade_in_time = 0
    max_fade_in = 300
    search_time = 0
    hint_alpha = 0
    
    message_text = None
    message_timer = 0
    message_alpha = 255
    clue_found = False
    hint = get_smart_hint(found_clues, points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, (0, 255, 255))
    instruction = font.render(translations[language]["Objective1_Level" + str(level)], True, (0, 255, 255))
    running = True
    clock = pygame.time.Clock()

    text_to_speech(translations[language]["Objective1_Level" + str(level)], language)

    while running:
        # Use room1 for level 2, detective_bg1 for level 1
        background = room1 if level == 2 else detective_bg1
        screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))
        pulse_phase += pulse_speed
        glow_alpha = 128 + int(127 * math.sin(pulse_phase))
        
        if not clue_found:
            glow_surface = pygame.Surface((clue_rect.width + 2 * max_glow, clue_rect.height + 2 * max_glow), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 215, 0, glow_alpha // 2), 
                           (max_glow - glow_radius, max_glow - glow_radius, 
                            clue_rect.width + 2 * glow_radius, clue_rect.height + 2 * glow_radius))
            screen.blit(glow_surface, (clue_rect.x - max_glow + glow_radius, clue_rect.y - max_glow + glow_radius))
            screen.blit(clue_surface, clue_rect)
        
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, (0, 255, 255))
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))
        hint_surface = hint_text
        hint_surface.set_alpha(hint_alpha)
        screen.blit(hint_surface, hint_surface.get_rect(center=(WIDTH // 2, HEIGHT - 50)))

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, (0, 255, 255))
            message_surface.set_alpha(message_alpha)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
            screen.blit(message_surface, message_rect)
            message_alpha = max(message_alpha - 5, 0)
            message_timer -= 1
            if message_timer <= 0 and clue_found:
                return points, found_clues

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return points, found_clues
            elif event.type == pygame.MOUSEBUTTONDOWN and not clue_found:
                if clue_rect.collidepoint(event.pos):
                    clue_found = True
                    found_clues.append(f"clue1_level{level}")
                    points += 5
                    message_text = "Clue Found!"
                    message_timer = 120
                    text_to_speech("Clue found!", language)

        fade_in_time += 1
        if fade_in_time < max_fade_in:
            clue_surface.set_alpha(int(255 * (fade_in_time / max_fade_in)))
        search_time += 1
        if search_time > 300:
            hint_alpha = min(hint_alpha + 5, 255)
    return points, found_clues

def pin_view_2(screen, points, found_clues, language, level):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    
    clue_surface = glass if level == 1 else key
    clue_rect = clue_surface.get_rect(center=(
        random.randint(WIDTH // 2 + 100, WIDTH - 100),
        random.randint(100, HEIGHT - 100)
    ))
    pulse_speed = 0.05
    pulse_phase = 0
    glow_radius = 0
    max_glow = 30
    glow_speed = 0.5
    glow_alpha = 0
    fade_in_time = 0
    max_fade_in = 300
    search_time = 0
    hint_alpha = 0
    
    message_text = None
    message_timer = 0
    message_alpha = 255
    clue_found = False
    hint = get_smart_hint(found_clues, points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, (0, 255, 255))
    instruction = font.render(translations[language]["Objective2_Level" + str(level)], True, (0, 255, 255))
    running = True
    clock = pygame.time.Clock()

    text_to_speech(translations[language]["Objective2_Level" + str(level)], language)

    while running:
        # Use room2 for level 2, detective_bg2 for level 1
        background = room2 if level == 2 else detective_bg2
        screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))
        pulse_phase += pulse_speed
        glow_alpha = 128 + int(127 * math.sin(pulse_phase))
        
        if not clue_found:
            glow_surface = pygame.Surface((clue_rect.width + 2 * max_glow, clue_rect.height + 2 * max_glow), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 215, 0, glow_alpha // 2), 
                           (max_glow - glow_radius, max_glow - glow_radius, 
                            clue_rect.width + 2 * glow_radius, clue_rect.height + 2 * glow_radius))
            screen.blit(glow_surface, (clue_rect.x - max_glow + glow_radius, clue_rect.y - max_glow + glow_radius))
            screen.blit(clue_surface, clue_rect)
        
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, (0, 255, 255))
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))
        hint_surface = hint_text
        hint_surface.set_alpha(hint_alpha)
        screen.blit(hint_surface, hint_surface.get_rect(center=(WIDTH // 2, HEIGHT - 50)))

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, (0, 255, 255))
            message_surface.set_alpha(message_alpha)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
            screen.blit(message_surface, message_rect)
            message_alpha = max(message_alpha - 5, 0)
            message_timer -= 1
            if message_timer <= 0 and clue_found:
                return points, found_clues

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return points, found_clues
            elif event.type == pygame.MOUSEBUTTONDOWN and not clue_found:
                if clue_rect.collidepoint(event.pos):
                    clue_found = True
                    found_clues.append(f"clue2_level{level}")
                    points += 5
                    message_text = "Clue Found!"
                    message_timer = 120
                    text_to_speech("Clue found!", language)

        fade_in_time += 1
        if fade_in_time < max_fade_in:
            clue_surface.set_alpha(int(255 * (fade_in_time / max_fade_in)))
        search_time += 1
        if search_time > 300:
            hint_alpha = min(hint_alpha + 5, 255)
    return points, found_clues

def pin_view_3(screen, points, found_clues, language, level):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    
    clue_surface = note if level == 1 else letter
    clue_rect = clue_surface.get_rect(center=(
        random.randint(WIDTH // 2 + 100, WIDTH - 100),
        random.randint(100, HEIGHT - 100)
    ))
    pulse_speed = 0.05
    pulse_phase = 0
    glow_radius = 0
    max_glow = 30
    glow_speed = 0.5
    glow_alpha = 0
    fade_in_time = 0
    max_fade_in = 300
    search_time = 0
    hint_alpha = 0
    
    message_text = None
    message_timer = 0
    message_alpha = 255
    clue_found = False
    hint = get_smart_hint(found_clues, points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, (0, 255, 255))
    instruction = font.render(translations[language]["Objective3_Level" + str(level)], True, (0, 255, 255))
    running = True
    clock = pygame.time.Clock()

    text_to_speech(translations[language]["Objective3_Level" + str(level)], language)

    while running:
        # Use room3 for level 2, detective_bg3 for level 1
        background = room3 if level == 2 else detective_bg3
        screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))
        pulse_phase += pulse_speed
        glow_alpha = 128 + int(127 * math.sin(pulse_phase))
        
        if not clue_found:
            glow_surface = pygame.Surface((clue_rect.width + 2 * max_glow, clue_rect.height + 2 * max_glow), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 215, 0, glow_alpha // 2), 
                           (max_glow - glow_radius, max_glow - glow_radius, 
                            clue_rect.width + 2 * glow_radius, clue_rect.height + 2 * glow_radius))
            screen.blit(glow_surface, (clue_rect.x - max_glow + glow_radius, clue_rect.y - max_glow + glow_radius))
            screen.blit(clue_surface, clue_rect)
        
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, (0, 255, 255))
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))
        hint_surface = hint_text
        hint_surface.set_alpha(hint_alpha)
        screen.blit(hint_surface, hint_surface.get_rect(center=(WIDTH // 2, HEIGHT - 50)))

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, (0, 255, 255))
            message_surface.set_alpha(message_alpha)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
            screen.blit(message_surface, message_rect)
            message_alpha = max(message_alpha - 5, 0)
            message_timer -= 1
            if message_timer <= 0 and clue_found:
                return points, found_clues

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return points, found_clues
            elif event.type == pygame.MOUSEBUTTONDOWN and not clue_found:
                if clue_rect.collidepoint(event.pos):
                    clue_found = True
                    found_clues.append(f"clue3_level{level}")
                    points += 5
                    message_text = "Clue Found!"
                    message_timer = 120
                    text_to_speech("Clue found!", language)

        fade_in_time += 1
        if fade_in_time < max_fade_in:
            clue_surface.set_alpha(int(255 * (fade_in_time / max_fade_in)))
        search_time += 1
        if search_time > 300:
            hint_alpha = min(hint_alpha + 5, 255)
    return points, found_clues
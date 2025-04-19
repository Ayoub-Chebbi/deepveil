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

def suspect_background_view(screen, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 28)
    title_font = pygame.font.Font(None, 48)
    suspect_positions = [(WIDTH - WIDTH // 3 - 50, HEIGHT // 2), (WIDTH - WIDTH // 4 - 50, HEIGHT // 2), (WIDTH - WIDTH // 6 - 50, HEIGHT // 2)]
    suspect_rects = [pygame.Rect(x, y, 70, 100) for x, y in suspect_positions]
    back_button = pygame.Rect(0, 0, 200, 60)
    back_button.center = (WIDTH // 2, HEIGHT - 100)
    running = True
    clock = pygame.time.Clock()

    print("Entered suspect_background_view")
    text_to_speech("Explore the suspect backgrounds.", language)
    pygame.event.clear()  # Clear stale events

    while running:
        screen.blit(pygame.transform.scale(detective_bg1, (WIDTH, HEIGHT)), (0, 0))
        title_text = title_font.render(translations[language]["Explore Suspect Background"], True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 50)))

        for i, pos in enumerate(suspect_positions):
            screen.blit(pygame.transform.scale(suspect_image, (70, 100)), pos)
            suspect_text = font.render(translations[language][f"Suspect{i+1}"], True, WHITE)
            screen.blit(suspect_text, suspect_text.get_rect(center=(pos[0] + 35, pos[1] + 115)))
            background_text = font.render(translations[language][f"Suspect{i+1}_Background"], True, YELLOW)
            screen.blit(background_text, background_text.get_rect(center=(pos[0] + 35, pos[1] + 150)))

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
        screen.blit(pygame.transform.scale(new_background_image, (WIDTH, HEIGHT)), (0, 0))
        for i, rect in enumerate(cell_rects):
            x, y = i % 3, i // 3
            pygame.draw.rect(screen, WHITE, rect, border_radius=5)
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
                screen.blit(scaled_background, (0, 0))
                for i, rect in enumerate(tile_rects):
                    x, y = i % 4, i // 4
                    if grid[y][x] is not None:
                        if grid[y][x] == 15:
                            screen.blit(scaled_pin, rect)
                        else:
                            pygame.draw.rect(screen, BLUE, rect, border_radius=5)
                            text = font.render(str(grid[y][x]), True, WHITE)
                            screen.blit(text, text.get_rect(center=rect.center))
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
    pieces = [
        {'rect': pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 50, 50), 'pos': (0, 0)},
        {'rect': pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 - 100, 50, 50), 'pos': (1, 0)},
        {'rect': pygame.Rect(WIDTH // 2 + 50, HEIGHT // 2 - 100, 50, 50), 'pos': (2, 0)},
        {'rect': pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 50, 50), 'pos': (1, 1)},
        {'rect': pygame.Rect(WIDTH // 2, HEIGHT // 2, 50, 50), 'pos': (2, 1)}
    ]
    target_positions = [(x, y) for y in range(2) for x in range(3) if not (y == 1 and x == 0)]
    correct_positions = [(0, 0), (1, 0), (2, 0), (1, 1), (2, 1)]
    selected_piece = None
    message_text = None
    message_timer = 0
    message_alpha = 255
    puzzle_solved = False
    hint = get_smart_hint([], points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, YELLOW)
    instruction = font.render("Arrange pieces to form image", True, WHITE)
    running = True
    clock = pygame.time.Clock()

    def is_solved():
        return all(piece['pos'] == correct_positions[i] for i, piece in enumerate(pieces))

    text_to_speech("Arrange the pieces to form a complete image to unlock the clue.", language)

    while running:
        screen.blit(pygame.transform.scale(new_background_image, (WIDTH, HEIGHT)), (0, 0))
        target_rects = [pygame.Rect(WIDTH // 2 - 90 + x * 60, HEIGHT // 2 - 60 + y * 60, 50, 50) for y in range(2) for x in range(3) if not (y == 1 and x == 0)]
        for rect in target_rects:
            pygame.draw.rect(screen, LIGHT_GRAY, rect, 2, border_radius=5)
        for i, piece in enumerate(pieces):
            x, y = piece['pos']
            src_rect = pygame.Rect(x * 35, y * 50, 35, 50)
            screen.blit(pygame.transform.scale(suspect_image, (105, 100)), piece['rect'], src_rect)
            pygame.draw.rect(screen, BLUE, piece['rect'], 2, border_radius=5)
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
                for i, piece in enumerate(pieces):
                    if piece['rect'].collidepoint(event.pos):
                        selected_piece = i
                        break
            elif event.type == pygame.MOUSEBUTTONUP and selected_piece is not None:
                for i, target in enumerate(target_rects):
                    if target.collidepoint(event.pos):
                        target_pos = target_positions[i]
                        for other_piece in pieces:
                            if other_piece['pos'] == target_pos and other_piece != pieces[selected_piece]:
                                other_piece['pos'], pieces[selected_piece]['pos'] = pieces[selected_piece]['pos'], other_piece['pos']
                                other_piece['rect'].center = target.center
                                pieces[selected_piece]['rect'].center = target.center
                                break
                        else:
                            pieces[selected_piece]['pos'] = target_pos
                            pieces[selected_piece]['rect'].center = target.center
                        if is_solved():
                            points += 10
                            message_text = "Access Granted"
                            message_timer = 120
                            puzzle_solved = True
                            text_to_speech("Access granted. Entering the room.", language)
                        break
                selected_piece = None
            elif event.type == pygame.MOUSEMOTION and selected_piece is not None:
                pieces[selected_piece]['rect'].move_ip(event.rel)

    return points, False

def pin_view_1(screen, points, found_clues, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    click_count = 0
    max_clicks = 3
    message_text = None
    message_timer = 0
    message_alpha = 255
    clue_found = False
    logbook = pygame.Surface((60, 80), pygame.SRCALPHA)
    logbook.fill((139, 69, 19))
    pygame.draw.rect(logbook, BLACK, (0, 0, 60, 80), 2)
    pygame.draw.line(logbook, WHITE, (10, 20), (50, 20), 2)
    pygame.draw.line(logbook, WHITE, (10, 40), (50, 40), 2)
    hint = get_smart_hint(found_clues, points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, YELLOW)
    instruction = font.render("Click 3 times to find the clue", True, WHITE)
    running = True
    clock = pygame.time.Clock()

    text_to_speech("Click three times to find the clue.", language)

    while running:
        screen.blit(pygame.transform.scale(detective_bg1, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))

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
                click_count += 1
                print(f"pin_view_1: click_count = {click_count}")
                if click_count >= max_clicks and "clue1" not in found_clues:
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
    glass = pygame.Surface((50, 70), pygame.SRCALPHA)
    pygame.draw.polygon(glass, (173, 216, 230), [(25, 0), (50, 20), (40, 70), (10, 70), (0, 20)])
    glass_rect = pygame.Rect(WIDTH // 2 - 25, HEIGHT // 2 - 100, 50, 70)
    target_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 50, 100, 100)
    message_text = None
    message_timer = 0
    message_alpha = 255
    clue_found = False
    drag_offset = None
    hint = get_smart_hint(found_clues, points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, YELLOW)
    instruction = font.render("Drag the shard to the target", True, WHITE)
    running = True
    clock = pygame.time.Clock()

    text_to_speech("Drag the shard to the target to find the clue.", language)

    while running:
        screen.blit(pygame.transform.scale(detective_bg2, (WIDTH, HEIGHT)), (0, 0))
        pygame.draw.rect(screen, LIGHT_GRAY, target_rect, border_radius=10)
        screen.blit(glass, glass_rect)
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if glass_rect.collidepoint(event.pos):
                    drag_offset = (event.pos[0] - glass_rect.x, event.pos[1] - glass_rect.y)
            elif event.type == pygame.MOUSEBUTTONUP:
                if drag_offset and glass_rect.colliderect(target_rect) and "clue2" not in found_clues:
                    points += 10
                    found_clues.append("clue2")
                    message_text = translations[language]["Clue2"]
                    message_timer = 120
                    clue_found = True
                    text_to_speech(message_text, language)
                drag_offset = None
                glass_rect.center = (WIDTH // 2, HEIGHT // 2 - 65)
            elif event.type == pygame.MOUSEMOTION and drag_offset:
                glass_rect.x = event.pos[0] - drag_offset[0]
                glass_rect.y = event.pos[1] - drag_offset[1]
    return points, found_clues

def pin_view_3(screen, points, found_clues, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    click_count = 0
    max_clicks = 2
    message_text = None
    message_timer = 0
    message_alpha = 255
    clue_found = False
    note = pygame.Surface((70, 50), pygame.SRCALPHA)
    note.fill((245, 245, 220))
    pygame.draw.rect(note, BLACK, (0, 0, 70, 50), 2)
    pygame.draw.line(note, BLACK, (10, 25), (60, 25), 1)
    hint = get_smart_hint(found_clues, points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, YELLOW)
    instruction = font.render("Click 2 times to find the clue", True, WHITE)
    running = True
    clock = pygame.time.Clock()

    text_to_speech("Click two times to find the clue.", language)

    while running:
        screen.blit(pygame.transform.scale(detective_bg3, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(instruction, instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))
        points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))

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
                click_count += 1
                print(f"pin_view_3: click_count = {click_count}")
                if click_count >= max_clicks and "clue3" not in found_clues:
                    points += 10
                    found_clues.append("clue3")
                    message_text = translations[language]["Clue3"]
                    message_timer = 120
                    clue_found = True
                    text_to_speech(message_text, language)
    return points, found_clues
import pygame
import sys
import math
from config import WIDTH, HEIGHT, translations, GREEN, WHITE, DARK_GRAY, LIGHT_GRAY, BLUE, BLUE_HOVER, RED, YELLOW, BLACK
from assets import background_image, new_background_image, pin_image, suspect_image, level_image, detective_bg1, detective_bg2, detective_bg3
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
    from views import suspect_background_view, win_view, lose_view
    WIDTH, HEIGHT = screen.get_size()
    pin_positions = [(WIDTH // 5, HEIGHT // 3), (WIDTH // 2, HEIGHT // 2), (WIDTH // 5, HEIGHT - HEIGHT // 4)]
    pin_rects = [pygame.Rect(x, y, 40, 40) for x, y in pin_positions]
    suspect_positions = [(WIDTH - WIDTH // 3, HEIGHT // 2), (WIDTH - WIDTH // 4, HEIGHT // 2), (WIDTH - WIDTH // 6, HEIGHT // 2)]
    suspect_rects = [pygame.Rect(x, y, 70, 100) for x, y in suspect_positions]
    suspect_visibility = [False, False, False]
    correct_suspect = 0
    font = pygame.font.Font(None, 28)
    mission_font = pygame.font.Font(None, 48)
    explore_button = pygame.Rect(0, 0, 250, 50)
    explore_button.center = (WIDTH // 2, HEIGHT - 100)
    select_box = pygame.Rect(0, 0, 350, 60)
    select_box.center = (WIDTH // 2, HEIGHT - 50)
    current_pin_index = 0
    objectives = [translations[language][f"Objective{i+1}"] for i in range(3)]
    completed_objectives = [False, False, False]
    running = True
    clock = pygame.time.Clock()

    while running:
        screen.blit(pygame.transform.scale(new_background_image, (WIDTH, HEIGHT)), (0, 0))
        mission_text = mission_font.render(translations[language]["Mission"], True, (0, 255, 255))
        screen.blit(mission_text, mission_text.get_rect(center=(WIDTH // 2, 50)))

        for i, pos in enumerate(pin_positions):
            pin_color = (255, 215, 0) if i == current_pin_index else (150, 150, 150)
            scaled_pin = pygame.transform.scale(pin_image, (40, 40))
            scaled_pin.fill(pin_color, special_flags=pygame.BLEND_MULT)
            if i == current_pin_index and i == 0:  # Highlight first pin
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
                hover = suspect_rect.collidepoint(pygame.mouse.get_pos()) and len(found_clues) == 3
                if hover:
                    pygame.draw.rect(screen, BLUE_HOVER, (pos[0] - 5, pos[1] - 5, 80, 110), border_radius=5)
                screen.blit(pygame.transform.scale(suspect_image, (70, 100)), pos)
                suspect_text = font.render(translations[language][f"Suspect{i+1}"], True, WHITE)
                screen.blit(suspect_text, suspect_text.get_rect(center=(pos[0] + 35, pos[1] + 115)))

        if len(found_clues) == 3:
            draw_button(screen, explore_button, BLUE, BLUE_HOVER, translations[language]["Explore Suspect Background"], font, pygame.mouse.get_pos())
            pygame.draw.rect(screen, DARK_GRAY, select_box, border_radius=10)
            select_text = font.render(translations[language]["Select a suspect!"], True, WHITE)
            screen.blit(select_text, select_text.get_rect(center=select_box.center))

        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if len(found_clues) == 3 and explore_button.collidepoint(event.pos):
                    suspect_background_view(screen, language)
                for i, rect in enumerate(suspect_rects):
                    if rect.collidepoint(event.pos) and suspect_visibility[i] and len(found_clues) == 3:
                        if i == correct_suspect:
                            win_view(screen, language)
                            return points, found_clues, True
                        else:
                            lose_view(screen, language)
                            return points, found_clues, False
                for i, pin_rect in enumerate(pin_rects):
                    if pin_rect.collidepoint(event.pos) and i == current_pin_index:
                        if i == 0:
                            points, found_clues = pin_view_1(screen, points, found_clues, language)
                            if "clue1" in found_clues and not suspect_visibility[0]:
                                suspect_visibility[0] = True
                                completed_objectives[0] = True
                                current_pin_index = 1
                            suspect_visibility = suspect_ai(found_clues, suspect_visibility, language, points)
                        elif i == 1:
                            points, found_clues = pin_view_2(screen, points, found_clues, language)
                            if "clue2" in found_clues and not suspect_visibility[1]:
                                suspect_visibility[1] = True
                                completed_objectives[1] = True
                                current_pin_index = 2
                            suspect_visibility = suspect_ai(found_clues, suspect_visibility, language, points)
                        elif i == 2:
                            points, found_clues = pin_view_3(screen, points, found_clues, language)
                            if "clue3" in found_clues and not suspect_visibility[2]:
                                suspect_visibility[2] = True
                                completed_objectives[2] = True
                            suspect_visibility = suspect_ai(found_clues, suspect_visibility, language, points)
    return points, found_clues, False

def pin_view_1(screen, points, found_clues, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    logbook = pygame.Surface((60, 80), pygame.SRCALPHA)
    logbook.fill((139, 69, 19))
    pygame.draw.rect(logbook, BLACK, (0, 0, 60, 80), 2)
    pygame.draw.line(logbook, WHITE, (10, 20), (50, 20), 2)
    pygame.draw.line(logbook, WHITE, (10, 40), (50, 40), 2)
    logbook_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, 60, 80)
    clue = {"rect": logbook_rect, "image": logbook, "found": False, "id": "clue1", "clicks_needed": 3, "clicks": 0, "visible": False}
    hint = get_smart_hint(found_clues, points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, (255, 165, 0) if hint == "Processing..." else YELLOW)
    message_text = None
    message_timer = 0
    message_alpha = 0
    running = True
    clock = pygame.time.Clock()
    shine_alpha = 255

    while running:
        screen.blit(pygame.transform.scale(detective_bg1, (WIDTH, HEIGHT)), (0, 0))
        if not clue["found"]:
            if not clue["visible"]:
                shine_alpha = 128 + int(127 * math.sin(pygame.time.get_ticks() / 500))
                clue["image"].set_alpha(shine_alpha)
                if logbook_rect.collidepoint(pygame.mouse.get_pos()):
                    clue["visible"] = True
            else:
                clue["image"].set_alpha(255)
            screen.blit(clue["image"], clue["rect"])
        elif message_timer > 0:
            scale = 1.0 + 0.1 * abs(math.sin(pygame.time.get_ticks() / 200))
            scaled_logbook = pygame.transform.scale(logbook, (int(60 * scale), int(80 * scale)))
            screen.blit(scaled_logbook, (clue["rect"].x - (scaled_logbook.get_width() - 60) // 2, clue["rect"].y - (scaled_logbook.get_height() - 80) // 2))

        points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, WHITE)
            message_surface.set_alpha(message_alpha)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
            screen.blit(message_surface, message_rect)
            if message_timer > 180:
                message_alpha = min(message_alpha + 5, 255)
            elif message_timer < 60:
                message_alpha = max(message_alpha - 5, 0)
            message_timer -= 1
            if message_timer <= 0:
                return points, found_clues

        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return points, found_clues
            elif event.type == pygame.MOUSEBUTTONDOWN and clue["visible"]:
                if clue["rect"].collidepoint(event.pos) and not clue["found"]:
                    clue["clicks"] += 1
                    if clue["clicks"] >= clue["clicks_needed"]:
                        clue["found"] = True
                        points += 10
                        found_clues.append(clue["id"])
                        message_text = translations[language]["Clue1"]
                        message_timer = 240
                        text_to_speech(message_text, language)
    return points, found_clues

def pin_view_2(screen, points, found_clues, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    glass = pygame.Surface((50, 70), pygame.SRCALPHA)
    pygame.draw.polygon(glass, (173, 216, 230), [(25, 0), (50, 20), (40, 70), (10, 70), (0, 20)])
    glass_rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 50, 70)
    shine = pygame.Surface((60, 80), pygame.SRCALPHA)
    shine.fill((255, 255, 255, 50))
    clue = {"rect": glass_rect, "image": glass, "found": False, "id": "clue2", "drag_offset": None, "visible": False}
    hint = get_smart_hint(found_clues, points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, (255, 165, 0) if hint == "Processing..." else YELLOW)
    message_text = None
    message_timer = 0
    message_alpha = 0
    trail = []
    running = True
    clock = pygame.time.Clock()
    shine_alpha = 255

    while running:
        screen.blit(pygame.transform.scale(detective_bg2, (WIDTH, HEIGHT)), (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        if not clue["found"]:
            if not clue["visible"]:
                shine_alpha = 128 + int(127 * math.sin(pygame.time.get_ticks() / 500))
                shine.set_alpha(shine_alpha)
                shine_pos = (glass_rect.x - 5, glass_rect.y - 5)
                screen.blit(shine, shine_pos)
                if math.hypot(mouse_pos[0] - glass_rect.centerx, mouse_pos[1] - glass_rect.centery) < 100:
                    clue["visible"] = True
            else:
                screen.blit(clue["image"], clue["rect"])
                for pos in trail[-10:]:
                    pygame.draw.circle(screen, (173, 216, 230, 100), pos, 5)
        elif message_timer > 0:
            scale = 1.0 + 0.1 * abs(math.sin(pygame.time.get_ticks() / 200))
            scaled_glass = pygame.transform.scale(glass, (int(50 * scale), int(70 * scale)))
            screen.blit(scaled_glass, (clue["rect"].x - (scaled_glass.get_width() - 50) // 2, clue["rect"].y - (scaled_glass.get_height() - 70) // 2))

        points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, WHITE)
            message_surface.set_alpha(message_alpha)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
            screen.blit(message_surface, message_rect)
            if message_timer > 180:
                message_alpha = min(message_alpha + 5, 255)
            elif message_timer < 60:
                message_alpha = max(message_alpha - 5, 0)
            message_timer -= 1
            if message_timer <= 0:
                return points, found_clues

        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return points, found_clues
            elif event.type == pygame.MOUSEBUTTONDOWN and clue["visible"]:
                if clue["rect"].collidepoint(event.pos) and not clue["found"]:
                    clue["drag_offset"] = (event.pos[0] - clue["rect"].x, event.pos[1] - clue["rect"].y)
            elif event.type == pygame.MOUSEBUTTONUP:
                if clue["drag_offset"] and abs(clue["rect"].x - WIDTH // 2) > 50:
                    clue["found"] = True
                    points += 10
                    found_clues.append(clue["id"])
                    message_text = translations[language]["Clue2"]
                    message_timer = 240
                    text_to_speech(message_text, language)
                clue["drag_offset"] = None
            elif event.type == pygame.MOUSEMOTION and clue["drag_offset"]:
                clue["rect"].x = event.pos[0] - clue["drag_offset"][0]
                clue["rect"].y = event.pos[1] - clue["drag_offset"][1]
                trail.append((clue["rect"].x + 25, clue["rect"].y + 35))
    return points, found_clues

def pin_view_3(screen, points, found_clues, language):
    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.Font(None, 36)
    clue_font = pygame.font.Font(None, 48)
    note = pygame.Surface((70, 50), pygame.SRCALPHA)
    note.fill((245, 245, 220))
    pygame.draw.rect(note, BLACK, (0, 0, 70, 50), 2)
    pygame.draw.line(note, BLACK, (10, 25), (60, 25), 1)
    note_rect = pygame.Rect(WIDTH // 3, HEIGHT // 2, 70, 50)
    clue = {"rect": note_rect, "image": note, "found": False, "id": "clue3", "clicks_needed": 2, "clicks": 0, "visible": False}
    hint = get_smart_hint(found_clues, points, language)
    hint_text = font.render(hint if hint != "Processing..." else "Processing...", True, (255, 165, 0) if hint == "Processing..." else YELLOW)
    message_text = None
    message_timer = 0
    message_alpha = 0
    running = True
    clock = pygame.time.Clock()
    shine_alpha = 255

    while running:
        screen.blit(pygame.transform.scale(detective_bg3, (WIDTH, HEIGHT)), (0, 0))
        if not clue["found"]:
            if not clue["visible"]:
                shine_alpha = 128 + int(127 * math.sin(pygame.time.get_ticks() / 500))
                clue["image"].set_alpha(shine_alpha)
                if note_rect.collidepoint(pygame.mouse.get_pos()):
                    clue["visible"] = True
            else:
                clue["image"].set_alpha(255)
            screen.blit(clue["image"], clue["rect"])
        elif message_timer > 0:
            scale = 1.0 + 0.1 * abs(math.sin(pygame.time.get_ticks() / 200))
            scaled_note = pygame.transform.scale(note, (int(70 * scale), int(50 * scale)))
            screen.blit(scaled_note, (clue["rect"].x - (scaled_note.get_width() - 70) // 2, clue["rect"].y - (scaled_note.get_height() - 50) // 2))

        points_text = font.render(f"{translations[language]['Points']}: {points}", True, WHITE)
        screen.blit(points_text, points_text.get_rect(center=(WIDTH - 100, 20)))
        screen.blit(hint_text, hint_text.get_rect(center=(WIDTH // 2, 50)))

        if message_text and message_timer > 0:
            message_surface = clue_font.render(message_text, True, WHITE)
            message_surface.set_alpha(message_alpha)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, DARK_GRAY, message_rect.inflate(20, 20), border_radius=10)
            screen.blit(message_surface, message_rect)
            if message_timer > 180:
                message_alpha = min(message_alpha + 5, 255)
            elif message_timer < 60:
                message_alpha = max(message_alpha - 5, 0)
            message_timer -= 1
            if message_timer <= 0:
                return points, found_clues

        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return points, found_clues
            elif event.type == pygame.MOUSEBUTTONDOWN and clue["visible"]:
                if clue["rect"].collidepoint(event.pos) and not clue["found"]:
                    clue["clicks"] += 1
                    if clue["clicks"] >= clue["clicks_needed"]:
                        clue["found"] = True
                        points += 10
                        found_clues.append(clue["id"])
                        message_text = translations[language]["Clue3"]
                        message_timer = 240
                        text_to_speech(message_text, language)
    return points, found_clues
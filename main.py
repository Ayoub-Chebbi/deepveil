import pygame
import sys
from views import welcome_view, main_menu
from speech import speech_engine, stop_speech
import os

# Try to import moviepy
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    print("Warning: moviepy not installed. Using fallback intro.")
    MOVIEPY_AVAILABLE = False

# Try to import intro_background for fallback
try:
    from assets import intro_background
    INTRO_BACKGROUND_AVAILABLE = True
except ImportError:
    print("Warning: intro_background not available in assets.py.")
    INTRO_BACKGROUND_AVAILABLE = False

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Start in fullscreen
pygame.display.set_caption("Deep Veil")

def play_intro_video(screen, video_path="assets/videos/intro.mp4"):
    # Fallback if moviepy is not available or video is missing
    if not MOVIEPY_AVAILABLE or not os.path.exists(video_path):
        print(f"moviepy available: {MOVIEPY_AVAILABLE}, Video path: {video_path}, Exists: {os.path.exists(video_path)}")
        screen.fill((0, 0, 0))  # Black screen
        font = pygame.font.Font(None, 36)
        
        # Use intro_background if available
        if INTRO_BACKGROUND_AVAILABLE:
            screen.blit(pygame.transform.scale(intro_background, screen.get_size()), (0, 0))
            message = "Video intro unavailable. Continuing in 5 seconds..."
        else:
            message = "Video intro unavailable (no moviepy or video file). Continuing in 5 seconds..."
        
        fallback_text = font.render(message, True, (255, 255, 255))
        text_rect = fallback_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        skip_text = font.render("Click or press any key to skip", True, (255, 255, 255))
        skip_rect = skip_text.get_rect(bottomright=(screen.get_width() - 20, screen.get_height() - 20))
        
        screen.blit(fallback_text, text_rect)
        screen.blit(skip_text, skip_rect)
        pygame.display.flip()
        
        start_time = pygame.time.get_ticks()
        running = True
        while running and pygame.time.get_ticks() - start_time < 5000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False  # Exit game
                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    return True  # Continue to welcome_view
            pygame.time.wait(10)
        return True

    try:
        # Stop TTS to avoid audio overlap
        stop_speech()
        print(f"Playing video: {video_path}")

        # Load video
        video = VideoFileClip(video_path)
        screen_width, screen_height = screen.get_size()
        
        # Scale video to fit screen while preserving aspect ratio
        video_aspect = video.w / video.h
        screen_aspect = screen_width / screen_height
        if video_aspect > screen_aspect:
            new_width = screen_width
            new_height = int(screen_width / video_aspect)
        else:
            new_height = screen_height
            new_width = int(screen_height * video_aspect)
        
        video = video.resize((new_width, new_height))
        
        # Center video
        video_x = (screen_width - new_width) // 2
        video_y = (screen_height - new_height) // 2
        
        clock = pygame.time.Clock()
        running = True
        
        # Display "Click to skip" text
        font = pygame.font.Font(None, 36)
        skip_text = font.render("Click or press any key to skip", True, (255, 255, 255))
        skip_rect = skip_text.get_rect(bottomright=(screen_width - 20, screen_height - 20))
        
        for frame in video.iter_frames(fps=video.fps, dtype="uint8"):
            if not running:
                break
                
            # Convert frame to Pygame surface
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            screen.fill((0, 0, 0))
            screen.blit(frame_surface, (video_x, video_y))
            screen.blit(skip_text, skip_rect)
            pygame.display.flip()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    video.close()
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    video.close()
                    return True
            
            clock.tick(video.fps)
        
        video.close()
        # Fade-out transition
        fade_surface = pygame.Surface(screen.get_size())
        fade_surface.fill((0, 0, 0))
        for alpha in range(0, 256, 10):
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.wait(30)
        return True
    except Exception as e:
        print(f"Error playing video: {str(e)}. Using fallback intro.")
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        message = f"Error playing intro video: {str(e)}. Continuing in 5 seconds..."
        fallback_text = font.render(message, True, (255, 255, 255))
        screen.blit(fallback_text, fallback_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
        pygame.display.flip()
        pygame.time.wait(5000)
        return True

def main():
    initial_language = "English"  # Default, updated by menu later
    
    # Play intro video
    if not play_intro_video(screen):
        pygame.quit()
        sys.exit()
    
    # Show welcome screen
    welcome_view(screen, initial_language)
    
    # Proceed to main menu
    main_menu(screen, initial_language)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    finally:
        speech_engine.endLoop()
        pygame.quit()
        sys.exit()
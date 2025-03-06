import pygame, sys
from button import Button
from PIL import Image  # We need the PIL library to read GIFs

pygame.init()

# Initialize pygame mixer explicitly
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)  # Initialize with more options if needed

info = pygame.display.Info()
height = info.current_h
width = info.current_w

SCREEN = pygame.display.set_mode((width, height), pygame.SCALED | pygame.NOFRAME)
pygame.display.set_caption("Menu")

# Flag to check if the music is already playing
music_playing = False

# Function to extract frames from a GIF and scale them to the screen size
def extract_frames(gif_path, width, height):
    frames = []
    gif = Image.open(gif_path)
    for frame in range(gif.n_frames):
        gif.seek(frame)
        frame_image = gif.convert("RGBA")  # Convert to RGBA
        frame_image = frame_image.resize((width, height))  # Resize to fit the screen
        frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode)
        frames.append(frame_surface)
    return frames

# Load GIF frames and scale them to the screen size
frames = extract_frames("__pycache__/greece.gif", width, height)

def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font(r"C:\Users\mccau\.vscode\__pycache__\font.ttf", size)

def play():
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black")

        PLAY_TEXT = get_font(30).render("It was a cold winter night in the capital of Ancient Sparta", True, "White")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(width // 2, height // 4))  
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        PLAY_BACK = Button(image=None, pos=(width // 2, height // 2), 
                            text_input="BACK", font=get_font(75), base_color="White", hovering_color="Green")

        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def options():
    global music_playing  # Reference the global music_playing flag
    volume = pygame.mixer.music.get_volume()  # Get the current volume (0.0 to 1.0)
    slider_x = width // 2 - 100  # Starting position for the volume slider
    slider_width = 200  # Width of the slider

    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(width // 2, height // 4)) 
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(width // 2, height // 2), 
                            text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        # Volume slider bar
        pygame.draw.rect(SCREEN, (200, 200, 200), (slider_x, height // 2 + 50, slider_width, 10))  # Background bar
        pygame.draw.rect(SCREEN, (0, 255, 0), (slider_x, height // 2 + 50, volume * slider_width, 10))  # Current volume

        # Volume knob
        volume_knob_x = slider_x + (volume * slider_width) - 10  # Position of the knob
        pygame.draw.circle(SCREEN, (255, 0, 0), (volume_knob_x, height // 2 + 55), 15)

        volume_text = get_font(30).render(f"Volume: {int(volume * 100)}%", True, "Black")
        volume_text_rect = volume_text.get_rect(center=(width // 2, height // 2 + 100))
        SCREEN.blit(volume_text, volume_text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

            # Adjust volume when dragging the slider
            if event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:  # Left mouse button is held down
                if slider_x <= OPTIONS_MOUSE_POS[0] <= slider_x + slider_width:
                    volume = (OPTIONS_MOUSE_POS[0] - slider_x) / slider_width
                    pygame.mixer.music.set_volume(volume)  # Adjust the music volume

        pygame.display.update()

def main_menu():
    global music_playing  # Reference the global music_playing flag
    frame_index = 0
    clock = pygame.time.Clock()

    if not music_playing:
        try:
            # Attempt to load and play the background music only if it's not already playing
            pygame.mixer.music.load("__pycache__/Goddess.mp3")  # Replace with your music file path
            pygame.mixer.music.set_volume(1.0)  # Set initial volume to 100%
            pygame.mixer.music.play(-1, 0.0)  # Loop the music indefinitely
            music_playing = True  # Set flag to True once the music is playing
            print("Background music is playing!")  # Debug message to confirm music is playing
        except pygame.error as e:
            print(f"Error loading music: {e}")  # If there's an issue, this will output the error message
            pygame.mixer.music.stop()  # Ensure music is stopped if there’s an issue

    while True:
        # Draw the GIF background frame, which is now scaled to fit the whole screen
        SCREEN.blit(frames[frame_index], (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("Misthios", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(width // 2, 100))  
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        button_height = 5
        total_buttons_height = button_height * 3
        spacing = (height - total_buttons_height) // 4  

        PLAY_BUTTON = Button(image=pygame.image.load("__pycache__/Play Rect.png"), pos=(width // 2, spacing + button_height // 3), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("__pycache__/Options Rect.png"), pos=(width // 2, spacing * 2 + button_height + button_height // 3), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("__pycache__/Quit Rect.png"), pos=(width // 2, spacing * 3 + button_height * 2 + button_height // 3), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        # Update the GIF frame index
        frame_index = (frame_index + 1) % len(frames)

        # Control the frame rate of the GIF (e.g., 10 FPS)
        clock.tick(10)

        pygame.display.update()

# Run the main menu
main_menu()

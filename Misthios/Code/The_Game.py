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
frames = extract_frames("images/greece.gif", width, height)

def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font(r"Code/font.ttf", size)
player_pos = pygame.Vector2(400,400)
flip = False
def play():
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    key = pygame.key.get_pressed()
    if key[pygame.K_BACKSPACE]:
        main_menu()
    
    
    
    
    global flip
    player_image = pygame.image.load("images/spartan.png")
    player_image = pygame.transform.scale(player_image, (200,200))
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()


        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass
            key = pygame.key.get_pressed()
            if key[pygame.K_BACKSPACE]:
                main_menu()
        
        
        
        pygame.event.get()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player_pos.y -= 2 
        if keys[pygame.K_s]:
            player_pos.y += 2 
        if keys[pygame.K_a]:
            player_pos.x -= 2
            if flip!=True:
                player_image = pygame.transform.flip(player_image,1,0)
                flip = True
        if keys[pygame.K_d]:
            if flip!=False:
                player_image = pygame.transform.flip(player_image,1,0)
                flip = False 
            player_pos.x += 2
        SCREEN.fill("black")
    

        SCREEN.blit(player_image, player_pos)
        # PLAY_TEXT = get_font(30).render("It was a cold winter night in the capital of Ancient Sparta", True, "White")
        # PLAY_RECT = PLAY_TEXT.get_rect(center=(width // 2, height // 4))  
        # SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        # PLAY_BACK = Button(image=None, pos=(width // 2, height // 2), 
        #                     text_input="BACK", font=get_font(75), base_color="White", hovering_color="Green")

        # PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        # PLAY_BACK.update(SCREEN)




        pygame.display.update()

def options():
    global music_playing  # Reference the global music_playing flag
    volume = pygame.mixer.music.get_volume()  # Get the current volume (0.0 to 1.0)
    slider_x = width // 2 - 100  # Starting position for the volume slider
    slider_width = 200  # Width of the slider
    slider_y = height // 2 + 50  # Vertical position of the slider
    slider_height = 10  # Height of the slider bar
    dragging = False  # Flag to check if the user is dragging the slider

    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(45).render("OPTIONS", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(width // 2, height // 4)) 
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(width // 2, height - 25), 
                            text_input="BACK", font=get_font(30), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        # Volume slider bar
        pygame.draw.rect(SCREEN, (200, 200, 200), (slider_x, slider_y, slider_width, slider_height))  # Background bar
        pygame.draw.rect(SCREEN, (0, 255, 0), (slider_x, slider_y, volume * slider_width, slider_height))  # Current volume

        # Volume knob
        volume_knob_x = slider_x + (volume * slider_width) - 10  # Position of the knob
        pygame.draw.circle(SCREEN, (255, 0, 0), (volume_knob_x, slider_y + 5), 15)

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

                # Check if the click is inside the slider's bounds (both horizontally and vertically)
                if slider_x <= OPTIONS_MOUSE_POS[0] <= slider_x + slider_width and slider_y <= OPTIONS_MOUSE_POS[1] <= slider_y + slider_height + 10:
                    dragging = True
                    volume = (OPTIONS_MOUSE_POS[0] - slider_x) / slider_width
                    pygame.mixer.music.set_volume(volume)  # Adjust the music volume

            if event.type == pygame.MOUSEBUTTONUP:
                # Stop dragging the slider when the mouse button is released
                dragging = False

            # Adjust volume only when dragging the slider
            if event.type == pygame.MOUSEMOTION and dragging:
                # Track mouse position even outside the slider area
                if slider_x <= OPTIONS_MOUSE_POS[0] <= slider_x + slider_width:
                    volume = (OPTIONS_MOUSE_POS[0] - slider_x) / slider_width
                    volume = max(0.0, min(1.0, volume))  # Clamp the volume value between 0.0 and 1.0
                    pygame.mixer.music.set_volume(volume)  # Adjust the music volume

        pygame.display.update()

def main_menu():
    global music_playing  # Reference the global music_playing flag
    frame_index = 0
    clock = pygame.time.Clock()

    if not music_playing:
        try:
            # Attempt to load and play the background music only if it's not already playing
            pygame.mixer.music.load("sound/Goddess.mp3")  # Replace with your music file path
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

        PLAY_BUTTON = Button(image=pygame.image.load("images/Play Rect.png"), pos=(width // 2, spacing + button_height // 3), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("images/Options Rect.png"), pos=(width // 2, spacing * 2 + button_height + button_height // 3), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("images/Quit Rect.png"), pos=(width // 2, spacing * 3 + button_height * 2 + button_height // 3), 
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

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
frames = extract_frames("Misthios/images/greece.gif", width, height)

def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font(r"Misthios/Code/font.ttf", size)

flip = False
def play():
    global flip
    player_image = pygame.image.load("Misthios/images/spartan.png")
    player_image = pygame.transform.scale(player_image, (200, 200))
    
    # Load enemy image
    enemy_image = pygame.image.load("Misthios/images/snake.png")
    enemy_image = pygame.transform.scale(enemy_image, (200, 200))

    # Initial positions
    player_pos = pygame.Vector2(400, 400)
    enemy_pos = pygame.Vector2(800, 400)  # Start position of the enemy
    
    player_speed = 2
    enemy_speed = player_speed * 0.50  # Enemy moves at 2/4 of the player's speed

    # Health parameters
    max_health = 100
    player_health = max_health

    # Cooldown variables
    last_damage_time = 0  # Last time the player took damage
    damage_cooldown = 1500  # 1.5 seconds cooldown in milliseconds

    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            key = pygame.key.get_pressed()
            if key[pygame.K_BACKSPACE]:
                main_menu()

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player_pos.y -= player_speed
        if keys[pygame.K_s]:
            player_pos.y += player_speed
        if keys[pygame.K_a]:
            player_pos.x -= player_speed
            if not flip:
                player_image = pygame.transform.flip(player_image, 1, 0)
                flip = True
        if keys[pygame.K_d]:
            if flip:
                player_image = pygame.transform.flip(player_image, 1, 0)
                flip = False
            player_pos.x += player_speed

        # Enemy movement: Calculate direction to player and move at 2/4 speed
        direction = player_pos - enemy_pos
        if direction.length() != 0:  # Avoid division by zero
            direction.normalize_ip()  # Normalize the direction vector
            enemy_pos += direction * enemy_speed  # Move the enemy at 2/4 the speed of the player

        # Collision detection: If the player and enemy touch, check cooldown and lose health
        if player_pos.distance_to(enemy_pos) < 50:  # Adjust the threshold as needed
            current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
            if current_time - last_damage_time >= damage_cooldown:  # Check if cooldown is over
                player_health -= 10
                last_damage_time = current_time  # Update the last damage time
                if player_health <= 0:
                    player_health = 0

        # Fill the screen with black
        SCREEN.fill("black")
        
        # Draw player and enemy
        SCREEN.blit(player_image, player_pos)
        SCREEN.blit(enemy_image, enemy_pos)

        # Draw the health bar
        draw_health_bar(SCREEN, player_health, max_health, width, height)

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

        OPTIONS_TEXT = get_font(60).render("OPTIONS", True, "Black")
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

def draw_health_bar(screen, health, max_health, width, height):
    # Health bar parameters
    bar_width = 300
    bar_height = 25
    bar_x = (width - bar_width) // 2
    bar_y = height - bar_height - 20  # Position at the bottom middle of the screen

    # Draw the background of the health bar (gray with no corners)
    pygame.draw.rect(screen, (169, 169, 169), (bar_x, bar_y, bar_width, bar_height), border_radius=8)

    # Calculate the width of the health portion
    health_width = (health / max_health) * bar_width

    # Draw the current health portion (red rectangle)
    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, health_width, bar_height), border_radius=8)

    # Display the health percentage (centered inside the bar)
    health_percentage = f"{int((health / max_health) * 100)}%"
    font = pygame.font.Font(None, 30)  # Choose a font and size
    text = font.render(health_percentage, True, (255, 255, 255))  # White color for the text
    text_rect = text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))  # Center the text
    screen.blit(text, text_rect)

def main_menu():
    global music_playing  # Reference the global music_playing flag
    frame_index = 0
    clock = pygame.time.Clock()

    if not music_playing:
        try:
            # Attempt to load and play the background music only if it's not already playing
            pygame.mixer.music.load("Misthios/sound/Goddess.mp3")  # Replace with your music file path
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

        PLAY_BUTTON = Button(image=pygame.image.load("Misthios/images/Play Rect.png"), pos=(width // 2, spacing + button_height // 3), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("Misthios/images/Options Rect.png"), pos=(width // 2, spacing * 2 + button_height + button_height // 3), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("Misthios/images/Quit Rect.png"), pos=(width // 2, spacing * 3 + button_height * 2 + button_height // 3), 
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

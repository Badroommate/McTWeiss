pygame, sys
from button import Button
from PIL import Image  # We need the PIL library to read GIFs

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

info = pygame.display.Info()
height = info.current_h
width = info.current_w

SCREEN = pygame.display.set_mode((width, height), pygame.SCALED | pygame.NOFRAME)
pygame.display.set_caption("Menu")

music_playing = False

def extract_frames(gif_path, width, height):
    frames = []
    gif = Image.open(gif_path)
    for frame in range(gif.n_frames):
        gif.seek(frame)
        frame_image = gif.convert("RGBA")
        frame_image = frame_image.resize((width, height))
        frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode)
        frames.append(frame_surface)
    return frames

frames = extract_frames("images/greece.gif", width, height)

def get_font(size):
    return pygame.font.Font(r"Code/font.ttf", size)

flip = False

# Define the Enemies class for snake behavior
class Enemies:
    def __init__(self, pos, image, speed, health=100):
        self.pos = pos
        self.image = image
        self.speed = speed
        self.health = health
        self.max_health = health
        self.dropped = False  # Ensures coin drops only once

    def update(self, player_pos):
        if self.health > 0:
            direction = player_pos - self.pos
            if direction.length() != 0:
                direction.normalize_ip()
                self.pos += direction * self.speed

    def draw(self, screen):
        if self.health > 0:
            screen.blit(self.image, self.pos)
            # Draw the health bar further down on the snake image
            bar_width = 100
            bar_height = 10
            bar_x = self.pos.x + (200 - bar_width) // 2
            bar_y = self.pos.y + 80  # Health bar offset (for snake)
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            current_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, current_width, bar_height))

# Define a new Centaur enemy that inherits from Enemies
class Centaur(Enemies):
    def __init__(self, pos, image, speed, health=150):
        super().__init__(pos, image, speed, health)
        # Optionally, you can adjust properties unique to the centaur here.

    # You can override update or draw methods if the centaur behaves differently
    def draw(self, screen):
        if self.health > 0:
            screen.blit(self.image, self.pos)
            # Draw the health bar even further down for the centaur (if needed)
            bar_width = 100
            bar_height = 10
            bar_x = self.pos.x + (200 - bar_width) // 2
            bar_y = self.pos.y + 20  # Adjusted offset for centaur's health bar
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            current_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, current_width, bar_height))

# Define a Coin class for dropped coins
class Coin:
    def __init__(self, pos, image):
        self.pos = pos.copy()  # Drop the coin exactly at the enemy's death location
        self.image = image
        self.rect = self.image.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
    
    def draw(self, screen):
        screen.blit(self.image, self.pos)

# Define a Weapons class with three weapons: spear, sword, and bow
class Weapons:
    def __init__(self):
        self.spear = "spear"
        self.sword = "sword"
        self.bow = "bow"

# New placeholder function for weapons (functionality to be added later)
def weapon_placeholder():
    pass

def pause_game():
    resume_button = Button(
        image=None, 
        pos=(width // 2, height // 2 - 50), 
        text_input="RESUME", 
        font=get_font(50), 
        base_color="Red", 
        hovering_color="Green"
    )
    main_menu_button = Button(
        image=None, 
        pos=(width // 2, height // 2 + 50), 
        text_input="MAIN MENU", 
        font=get_font(50), 
        base_color="Red", 
        hovering_color="Green"
    )
    paused = True
    while paused:
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        SCREEN.blit(overlay, (0, 0))
        pause_text = get_font(80).render("Paused", True, "White")
        pause_rect = pause_text.get_rect(center=(width // 2, height // 2 - 150))
        SCREEN.blit(pause_text, pause_rect)
        mouse_pos = pygame.mouse.get_pos()
        resume_button.changeColor(mouse_pos)
        resume_button.update(SCREEN)
        main_menu_button.changeColor(mouse_pos)
        main_menu_button.update(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.checkForInput(mouse_pos):
                    paused = False
                if main_menu_button.checkForInput(mouse_pos):
                    main_menu()
        pygame.display.update()

def play():
    global flip
    player_image = pygame.image.load("images/spartan.png")
    player_image = pygame.transform.scale(player_image, (200, 200))
    
    snake_image = pygame.image.load("images/snake.png")
    snake_image = pygame.transform.scale(snake_image, (200, 200))
    
    # Load centaur image for the new enemy type
    centaur_image = pygame.image.load("images/centaur.png")
    centaur_image = pygame.transform.scale(centaur_image, (200, 200))
    
    coin_image = pygame.image.load("images/coin.png")
    coin_image = pygame.transform.scale(coin_image, (50, 50))
    
    player_pos = pygame.Vector2(400, 400)
    snake_max_health = 100
    centaur_max_health = 150
    player_speed = 2
    snake_speed = player_speed * 0.50
    centaur_speed = player_speed * 0.75  # Centaur moves a bit faster than snake
    max_health = 100
    player_health = max_health
    last_damage_time = 0
    damage_cooldown = 1500  # milliseconds
    start_ticks = pygame.time.get_ticks()
    
    # Create enemy instances: three snakes and one centaur
    enemies = [
        Enemies(pygame.Vector2(800, 400), snake_image, snake_speed, snake_max_health),
        Enemies(pygame.Vector2(1200, 300), snake_image, snake_speed, snake_max_health),
        Enemies(pygame.Vector2(1000, 600), snake_image, snake_speed, snake_max_health),
        Centaur(pygame.Vector2(1300, 500), centaur_image, centaur_speed, centaur_max_health)
    ]
    
    coins = []         # List to hold dropped coins
    player_coins = 0   # Counter for coins collected

    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_game()
        
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

        # Player attack: reduce enemy health when space is held and enemy is in range
        if keys[pygame.K_SPACE]:
            for enemy in enemies:
                if enemy.health > 0 and player_pos.distance_to(enemy.pos) < 150:
                    enemy.health -= 1
                    if enemy.health < 0:
                        enemy.health = 0

        collision_occurred = False
        for enemy in enemies:
            if enemy.health > 0:
                enemy.update(player_pos)
                if player_pos.distance_to(enemy.pos) < 50:
                    collision_occurred = True

        # For any enemy that died and hasn't dropped a coin, drop a coin at its death location
        for enemy in enemies:
            if enemy.health <= 0 and not enemy.dropped:
                coins.append(Coin(enemy.pos.copy(), coin_image))
                enemy.dropped = True

        # Remove dead enemies so they no longer appear
        enemies = [enemy for enemy in enemies if enemy.health > 0]
        
        # Player picks up coins only if close enough
        pickup_range = 75
        player_center = player_pos + pygame.Vector2(100, 100)  # Center of the player's 200x200 image
        for coin in coins[:]:
            coin_center = coin.pos + pygame.Vector2(25, 25)  # Center of the coin (50x50)
            if player_center.distance_to(coin_center) < pickup_range:
                coins.remove(coin)
                player_coins += 1

        if collision_occurred:
            current_time = pygame.time.get_ticks()
            if current_time - last_damage_time >= damage_cooldown:
                player_health -= 10
                last_damage_time = current_time
                if player_health < 0:
                    player_health = 0

        SCREEN.fill("black")
        SCREEN.blit(player_image, player_pos)
        for enemy in enemies:
            enemy.draw(SCREEN)
        for coin in coins:
            coin.draw(SCREEN)
        draw_health_bar(SCREEN, player_health, max_health, width, height)
        draw_timer(SCREEN, start_ticks)
        
        coin_text = get_font(30).render("Coins: " + str(player_coins), True, "Yellow")
        SCREEN.blit(coin_text, (10, 10))
        
        if player_health <= 0:
            game_over()

        pygame.display.update()

def options():
    global music_playing
    volume = pygame.mixer.music.get_volume()
    slider_x = width // 2 - 100
    slider_width = 200
    slider_y = height // 2 + 50
    slider_height = 10
    dragging = False
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("white")
        OPTIONS_TEXT = get_font(60).render("OPTIONS", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(width // 2, height // 4))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)
        OPTIONS_BACK = Button(
            image=None, 
            pos=(width // 2, height - 25), 
            text_input="BACK", 
            font=get_font(30), 
            base_color="Black", 
            hovering_color="Green"
        )
        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)
        pygame.draw.rect(SCREEN, (200, 200, 200), (slider_x, slider_y, slider_width, slider_height))
        pygame.draw.rect(SCREEN, (0, 255, 0), (slider_x, slider_y, volume * slider_width, slider_height))
        volume_knob_x = slider_x + (volume * slider_width) - 10
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
                if slider_x <= OPTIONS_MOUSE_POS[0] <= slider_x + slider_width and slider_y <= OPTIONS_MOUSE_POS[1] <= slider_y + slider_height + 10:
                    dragging = True
                    volume = (OPTIONS_MOUSE_POS[0] - slider_x) / slider_width
                    pygame.mixer.music.set_volume(volume)
            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                if slider_x <= OPTIONS_MOUSE_POS[0] <= slider_x + slider_width:
                    volume = (OPTIONS_MOUSE_POS[0] - slider_x) / slider_width
                    volume = max(0.0, min(1.0, volume))
                    pygame.mixer.music.set_volume(volume)
        pygame.display.update()

def draw_health_bar(screen, health, max_health, width, height):
    bar_width = 300
    bar_height = 25
    bar_x = (width - bar_width) // 2
    bar_y = height - bar_height - 20
    pygame.draw.rect(screen, (144, 238, 144), (bar_x, bar_y, bar_width, bar_height), border_radius=8)
    health_width = (health / max_health) * bar_width
    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height), border_radius=8)
    if health < max_health:
        lost_health_width = ((max_health - health) / max_health) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (bar_x + health_width, bar_y, lost_health_width, bar_height), border_radius=8)
    health_percentage = f"{int((health / max_health) * 100)}%"
    font = pygame.font.Font(r"Code/font.ttf", 30)
    text = font.render(health_percentage, True, (255, 255, 255))
    text_rect = text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
    screen.blit(text, text_rect)

def draw_timer(screen, start_ticks):
    elapsed_time = pygame.time.get_ticks() - start_ticks
    seconds = elapsed_time // 1000
    minutes = seconds // 60
    seconds %= 60
    timer_text = f"{minutes:02}:{seconds:02}"
    font = pygame.font.Font(r"Code/font.ttf", 36)
    text = font.render(timer_text, True, (255, 255, 255))
    text_rect = text.get_rect(topright=(width - 10, 10))
    screen.blit(text, text_rect)

def game_over():
    retry_button = Button(
        image=None, 
        pos=(width // 2, height // 2 + 50), 
        text_input="RETRY", 
        font=get_font(50), 
        base_color="Red", 
        hovering_color="Green"
    )
    quit_button = Button(
        image=None, 
        pos=(width // 2, height // 2 + 150), 
        text_input="MAIN MENU", 
        font=get_font(50), 
        base_color="Red", 
        hovering_color="Green"
    )
    while True:
        SCREEN.fill("black")
        game_over_text = get_font(80).render("Consumed by Darkness", True, "White")
        game_over_text_rect = game_over_text.get_rect(center=(width // 2, height // 2 - 50))
        SCREEN.blit(game_over_text, game_over_text_rect)
        retry_button.changeColor(pygame.mouse.get_pos())
        quit_button.changeColor(pygame.mouse.get_pos())
        retry_button.update(SCREEN)
        quit_button.update(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.checkForInput(pygame.mouse.get_pos()):
                    play()
                if quit_button.checkForInput(pygame.mouse.get_pos()):
                    main_menu()
        pygame.display.update()

def main_menu():
    global music_playing
    frame_index = 0
    clock = pygame.time.Clock()
    if not music_playing:
        try:
            pygame.mixer.music.load("sound/Goddess.mp3")
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(-1, 0.0)
            music_playing = True
            print("Background music is playing!")
        except pygame.error as e:
            print(f"Error loading music: {e}")
            pygame.mixer.music.stop()
    while True:
        SCREEN.blit(frames[frame_index], (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        MENU_TEXT = get_font(100).render("Misthios", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(width // 2, 100))
        SCREEN.blit(MENU_TEXT, MENU_RECT)
        button_height = 5
        total_buttons_height = button_height * 3
        spacing = (height - total_buttons_height) // 4
        PLAY_BUTTON = Button(
            image=pygame.image.load("images/Play Rect.png"), 
            pos=(width // 2, spacing + button_height // 3), 
            text_input="PLAY", 
            font=get_font(75), 
            base_color="#d7fcd4", 
            hovering_color="White"
        )
        OPTIONS_BUTTON = Button(
            image=pygame.image.load("images/Options Rect.png"), 
            pos=(width // 2, spacing * 2 + button_height + button_height // 3), 
            text_input="OPTIONS", 
            font=get_font(75), 
            base_color="#d7fcd4", 
            hovering_color="White"
        )
        QUIT_BUTTON = Button(
            image=pygame.image.load("images/Quit Rect.png"), 
            pos=(width // 2, spacing * 3 + button_height * 2 + button_height // 3), 
            text_input="QUIT", 
            font=get_font(75), 
            base_color="#d7fcd4", 
            hovering_color="White"
        )
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
        frame_index = (frame_index + 1) % len(frames)
        clock.tick(10)
        pygame.display.update()

main_menu()

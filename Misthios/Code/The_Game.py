import pygame, sys, random
from button import Button
from PIL import Image  # We need the PIL library to read GIFs

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

info = pygame.display.Info()
height = info.current_h
width = info.current_w

SCREEN = pygame.display.set_mode((width, height), pygame.SCALED | pygame.NOFRAME)
pygame.display.set_caption("Menu")

# GLOBAL VARIABLES FOR MUSIC
menu_music_tracks = ["Misthios/sound/Main_menu_1.mp3", "Misthios/sound/Main_menu_2.mp3"]
current_menu_track = None  # Stores the currently loaded main menu track

# GLOBAL SOUND LISTS
hurt_sounds = ["Misthios/sound/Hurt_1.mp3", "Misthios/sound/Hurt_2.mp3"]
death_sounds = ["Misthios/sound/Death_1.mp3", "Misthios/sound/Death_1.mp3"]
death_sound_played = False  # To ensure death sound is played only once

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

frames = extract_frames("Misthios/images/greece.gif", width, height)

def get_font(size):
    return pygame.font.Font(r"Misthios/Code/font.ttf", size)

flip = False

# Base Enemies class (snake)
class Enemies:
    def __init__(self, pos, image, speed, health=100):
        self.pos = pos
        self.image = image
        self.speed = speed
        self.health = health
        self.max_health = health
        self.dropped = False  # Ensures coin drops only once

    def update(self, player_pos, dt):
        if self.health > 0:
            direction = player_pos - self.pos
            if direction.length() != 0:
                direction.normalize_ip()
                self.pos += direction * self.speed * dt
                # Clamp enemy within screen (assuming sprite size 200x200)
                self.pos.x = max(0, min(self.pos.x, width - 200))
                self.pos.y = max(0, min(self.pos.y, height - 200))

    def draw(self, screen):
        if self.health > 0:
            screen.blit(self.image, self.pos)
            # Draw health bar for snake
            bar_width = 100
            bar_height = 10
            bar_x = self.pos.x + (200 - bar_width) // 2
            bar_y = self.pos.y + 80
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            current_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, current_width, bar_height))

# Base Centaur class
class Centaur(Enemies):
    def __init__(self, pos, image, speed, health=150):
        super().__init__(pos, image, speed, health)

    def draw(self, screen):
        if self.health > 0:
            screen.blit(self.image, self.pos)
            # Draw health bar for centaur
            bar_width = 100
            bar_height = 10
            bar_x = self.pos.x + (200 - bar_width) // 2
            bar_y = self.pos.y + 90
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            current_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, current_width, bar_height))

# Centaur with spear
class CentaurSpear(Centaur):
    def __init__(self, pos, speed, health=150):
        image = pygame.image.load("Misthios/images/centaur_spear.png")
        image = pygame.transform.scale(image, (200, 200))
        super().__init__(pos, image, speed, health)

# Centaur with bow
class CentaurBow(Centaur):
    def __init__(self, pos, speed, health=150):
        image = pygame.image.load("Misthios/images/centaur_bow.png")
        image = pygame.transform.scale(image, (200, 200))
        super().__init__(pos, image, speed, health)
        self.shoot_cooldown = 2000  # milliseconds between shots
        self.last_shot = 0

    def try_shoot(self, player_pos, current_time):
        if current_time - self.last_shot >= self.shoot_cooldown:
            self.last_shot = current_time
            direction = player_pos - (self.pos + pygame.Vector2(100, 100))
            if direction.length() != 0:
                direction.normalize_ip()
            # Increase arrow speed to 300 pixels per second for visible motion
            return Arrow(self.pos + pygame.Vector2(100, 100), direction, speed=300)
        return None

# Arrow class for bow-wielding enemies
class Arrow:
    def __init__(self, pos, direction, speed=300):
        self.pos = pygame.Vector2(pos)
        self.direction = direction
        self.speed = speed
        self.image = pygame.image.load("Misthios/images/arrow.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, screen):
        screen.blit(self.image, self.pos)

# Coin class for dropped coins
class Coin:
    def __init__(self, pos, image):
        self.pos = pos.copy()  # Drop coin exactly at enemy's death location
        self.image = image
        self.rect = self.image.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
    
    def draw(self, screen):
        screen.blit(self.image, self.pos)

# Door class that appears when all enemies are defeated
class Door:
    def __init__(self, pos, image):
        self.pos = pos
        self.image = image
        self.rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Weapons class (unused for now)
class Weapons:
    def __init__(self):
        self.spear = "spear"
        self.sword = "sword"
        self.bow = "bow"

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
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.checkForInput(mouse_pos):
                    paused = False
                if main_menu_button.checkForInput(mouse_pos):
                    main_menu(new_song=False)
        pygame.display.update()

def play():
    global flip, death_sound_played
    death_sound_played = False  # Reset flag for new game
    clock = pygame.time.Clock()
    # STOP MAIN MENU MUSIC AND LOAD GAME MUSIC
    pygame.mixer.music.stop()
    pygame.time.delay(100)
    try:
        pygame.mixer.music.load("Misthios/sound/Fight_music_1.mp3")
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1, 0.0)
        print("Game music is playing!")
    except pygame.error as e:
        print(f"Error loading game music: {e}")
    
    background1 = pygame.image.load("Misthios/images/backgroundtest.png")
    background1 = pygame.transform.scale(background1, (width, height))
    background2 = pygame.image.load("Misthios/images/backgroundtest2.png")
    background2 = pygame.transform.scale(background2, (width, height))
    level = 1

    player_image = pygame.image.load("Misthios/images/spartan.png")
    player_image = pygame.transform.scale(player_image, (200, 200))
    
    snake_image = pygame.image.load("Misthios/images/snake.png")
    snake_image = pygame.transform.scale(snake_image, (200, 200))
    
    coin_image = pygame.image.load("Misthios/images/coin.png")
    coin_image = pygame.transform.scale(coin_image, (50, 50))
    
    door_image = pygame.image.load("Misthios/images/door.png")
    door_image = pygame.transform.scale(door_image, (100, 150))
    
    player_pos = pygame.Vector2(400, 400)
    snake_max_health = 100
    centaur_max_health = 150
    player_speed = 250  # Increased player speed (was 200)
    snake_speed = player_speed * 0.50
    centaur_speed = player_speed * 0.75
    max_health = 100
    player_health = max_health
    
    dash_distance = 200
    dash_cooldown = 1000  # milliseconds
    last_dash_time = 0
    last_direction = pygame.Vector2(1, 0)
    
    damage_cooldown = 1500  # milliseconds
    last_damage_time = 0
    
    start_ticks = pygame.time.get_ticks()
    
    enemies = [
        Enemies(pygame.Vector2(800, 400), snake_image, snake_speed, snake_max_health),
        Enemies(pygame.Vector2(1200, 300), snake_image, snake_speed, snake_max_health),
        Enemies(pygame.Vector2(1000, 600), snake_image, snake_speed, snake_max_health),
        CentaurSpear(pygame.Vector2(1300, 500), centaur_speed, centaur_max_health),
        CentaurBow(pygame.Vector2(1400, 550), centaur_speed, centaur_max_health)
    ]
    
    coins = []
    player_coins = 0
    arrows = []
    door = None

    while True:
        dt = clock.tick(60) / 1000.0  # delta time in seconds
        current_time = pygame.time.get_ticks()
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if current_time - last_dash_time >= dash_cooldown:
                    player_pos += last_direction * dash_distance
                    last_dash_time = current_time

        movement = pygame.Vector2(0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            movement.y -= 1
        if keys[pygame.K_s]:
            movement.y += 1
        if keys[pygame.K_a]:
            movement.x -= 1
        if keys[pygame.K_d]:
            movement.x += 1
        
        if movement.length() != 0:
            movement.normalize_ip()
            last_direction = movement.copy()
            if movement.x < 0 and not flip:
                player_image = pygame.transform.flip(player_image, 1, 0)
                flip = True
            elif movement.x > 0 and flip:
                player_image = pygame.transform.flip(player_image, 1, 0)
                flip = False
        
        player_pos += movement * player_speed * dt
        
        # Allow player to attack enemies by left clicking
        if pygame.mouse.get_pressed()[0]:
            for enemy in enemies:
                if enemy.health > 0 and player_pos.distance_to(enemy.pos) < 150:
                    enemy.health -= 2  # Damage doubled from 1 to 2
                    if enemy.health < 0:
                        enemy.health = 0

        player_pos.x = max(0, min(player_pos.x, width - 200))
        player_pos.y = max(0, min(player_pos.y, height - 200))
        
        if level == 1:
            SCREEN.blit(background1, (0, 0))
        elif level == 2:
            SCREEN.blit(background2, (0, 0))
        
        player_rect = pygame.Rect(int(player_pos.x), int(player_pos.y), 200, 200)
        collision_occurred = False
        for enemy in enemies:
            enemy_rect = pygame.Rect(int(enemy.pos.x), int(enemy.pos.y), 200, 200)
            if player_rect.colliderect(enemy_rect):
                collision_occurred = True
                break

        if collision_occurred:
            if current_time - last_damage_time >= damage_cooldown:
                player_health -= 10
                last_damage_time = current_time
                if player_health <= 0:
                    player_health = 0
                    if not death_sound_played:
                        random_death = random.choice(death_sounds)
                        pygame.mixer.Sound(random_death).play()
                        death_sound_played = True
                else:
                    random_hurt = random.choice(hurt_sounds)
                    pygame.mixer.Sound(random_hurt).play()

        for enemy in enemies:
            if enemy.health > 0:
                enemy.update(player_pos, dt)
                if isinstance(enemy, CentaurBow):
                    arrow = enemy.try_shoot(player_pos, current_time)
                    if arrow is not None:
                        arrows.append(arrow)

        for arrow in arrows[:]:
            arrow.update(dt)
            if not SCREEN.get_rect().colliderect(arrow.rect):
                arrows.remove(arrow)
            
        for enemy in enemies:
            if enemy.health <= 0 and not enemy.dropped:
                coins.append(Coin(enemy.pos.copy(), coin_image))
                enemy.dropped = True

        enemies = [enemy for enemy in enemies if enemy.health > 0]

        pickup_range = 75
        player_center = player_pos + pygame.Vector2(100, 100)
        for coin in coins[:]:
            coin_center = coin.pos + pygame.Vector2(25, 25)
            if player_center.distance_to(coin_center) < pickup_range:
                coins.remove(coin)
                player_coins += 1

        if enemies:
            SCREEN.blit(player_image, player_pos)
            for enemy in enemies:
                enemy.draw(SCREEN)
            for coin in coins:
                coin.draw(SCREEN)
            for arrow in arrows:
                arrow.draw(SCREEN)
            draw_health_bar(SCREEN, player_health, max_health, width, height)
            draw_timer(SCREEN, start_ticks)
            coin_text = get_font(30).render("Coins: " + str(player_coins), True, "Yellow")
            SCREEN.blit(coin_text, (10, 10))
        else:
            if door is None:
                door = Door(pygame.Vector2(width // 2, height // 2), door_image)
            door.draw(SCREEN)
            SCREEN.blit(player_image, player_pos)
            for coin in coins:
                coin.draw(SCREEN)
            for arrow in arrows:
                arrow.draw(SCREEN)
            draw_health_bar(SCREEN, player_health, max_health, width, height)
            draw_timer(SCREEN, start_ticks)
            coin_text = get_font(30).render("Coins: " + str(player_coins), True, "Yellow")
            SCREEN.blit(coin_text, (10, 10))
            if player_rect.colliderect(door.rect):
                new_enemies = []
                for i in range(5):
                    enemy_type = random.choice(["snake", "centaur_spear", "centaur_bow"])
                    x = random.randint(0, width - 200)
                    y = random.randint(0, height - 200)
                    pos = pygame.Vector2(x, y)
                    if enemy_type == "snake":
                        new_enemies.append(Enemies(pos, snake_image, snake_speed, snake_max_health))
                    elif enemy_type == "centaur_spear":
                        new_enemies.append(CentaurSpear(pos, centaur_speed, centaur_max_health))
                    else:
                        new_enemies.append(CentaurBow(pos, centaur_speed, centaur_max_health))
                enemies = new_enemies
                door = None
                level = 2

        if player_health <= 0:
            game_over()

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
    font = pygame.font.Font(r"Misthios/Code/font.ttf", 30)
    text = font.render(health_percentage, True, (255, 255, 255))
    text_rect = text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
    screen.blit(text, text_rect)

def draw_timer(screen, start_ticks):
    elapsed_time = pygame.time.get_ticks() - start_ticks
    seconds = elapsed_time // 1000
    minutes = seconds // 60
    seconds %= 60
    timer_text = f"{minutes:02}:{seconds:02}"
    font = pygame.font.Font(r"Misthios/Code/font.ttf", 36)
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
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.checkForInput(pygame.mouse.get_pos()):
                    play()
                if quit_button.checkForInput(pygame.mouse.get_pos()):
                    main_menu(new_song=True)
        pygame.display.update()

def options():
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
        music_vol_text = get_font(30).render(f"Music Volume: {int(volume * 100)}%", True, "Black")
        music_vol_rect = music_vol_text.get_rect(center=(width // 2, height // 2 + 20))
        SCREEN.blit(music_vol_text, music_vol_rect)
        pygame.draw.rect(SCREEN, (200, 200, 200), (slider_x, slider_y, slider_width, slider_height))
        pygame.draw.rect(SCREEN, (0, 255, 0), (slider_x, slider_y, volume * slider_width, slider_height))
        volume_knob_x = slider_x + (volume * slider_width) - 10
        pygame.draw.circle(SCREEN, (255, 0, 0), (int(volume_knob_x), slider_y + 5), 15)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu(new_song=False)
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

def main_menu(new_song=True):
    global current_menu_track
    frame_index = 0
    clock = pygame.time.Clock()
    if new_song or current_menu_track is None:
        current_menu_track = random.choice(menu_music_tracks)
        try:
            pygame.mixer.music.load(current_menu_track)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(-1, 0.0)
            print(f"Main menu music is playing: {current_menu_track}")
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
            image=pygame.image.load("Misthios/images/Play Rect.png"),
            pos=(width // 2, spacing + button_height // 3),
            text_input="PLAY",
            font=get_font(75),
            base_color="#d7fcd4",
            hovering_color="White"
        )
        OPTIONS_BUTTON = Button(
            image=pygame.image.load("Misthios/images/Options Rect.png"),
            pos=(width // 2, spacing * 2 + button_height + button_height // 3),
            text_input="OPTIONS",
            font=get_font(75),
            base_color="#d7fcd4",
            hovering_color="White"
        )
        QUIT_BUTTON = Button(
            image=pygame.image.load("Misthios/images/Quit Rect.png"),
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
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit(); sys.exit()
        frame_index = (frame_index + 1) % len(frames)
        clock.tick(10)
        pygame.display.update()

main_menu()

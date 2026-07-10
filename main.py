import pygame
import os
import random
import math
import audio  # Custom module handling our safe audio loading

# ==========================================
# 1. CORE ENGINE INITIALIZATION
# ==========================================
pygame.init()

# Setup screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AeroStrike: Extreme Skies")

# Setup performance clock (The FPS Governor)
clock = pygame.time.Clock()
FPS = 60  

# Setup paths & Load Audio via our custom module
base_dir = os.getcwd()
sound_dir = os.path.join(base_dir, "assets", "sounds")
launch_sound, explosion_sound = audio.load_game_sounds(sound_dir)

# ==========================================
# 2. GAME VARIABLES & PHYSICS ENTITIES
# ==========================================
# Player Setup
player_width, player_height = 50, 50
player_x = (SCREEN_WIDTH // 2) - (player_width // 2)
player_y = SCREEN_HEIGHT - player_height - 30
player_speed = 5.5

# Laser System
lasers = []
laser_speed = 8.0
laser_cooldown = 0
COOLDOWN_MAX = 15  # Frames between shots

# Enemy System (Dynamic Wave Spawning)
enemies = []
enemy_speed_min = 2.0
enemy_speed_max = 4.5
enemy_spawn_timer = 0
SPAWN_RATE = 40  # Lower = faster spawning

for _ in range(5):
    enemies.append({
        'x': random.randint(0, SCREEN_WIDTH - 40),
        'y': random.randint(-200, -50),
        'speed': random.uniform(enemy_speed_min, enemy_speed_max),
        'angle': 0.0
    })

# Score Tracking
score = 0
font = pygame.font.SysFont("Arial", 24)

# ==========================================
# 3. MAIN GAME LOOP (CORE ENGINE)
# ==========================================
running = True
while running:
    # Calculate Delta Time (Elapsed time per frame in seconds)
    # This guarantees smooth physics across all CPUs!
    dt = clock.tick(FPS) / 1000.0

    # Fill background (Space Black)
    screen.fill((10, 10, 20))

    # --- 3A. EVENT & INPUT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Continuous Keypress Tracking (Smooth Movement)
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_x > 0:
        player_x -= player_speed
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_x < SCREEN_WIDTH - player_width:
        player_x += player_speed
        
    # Laser Shooting Logic (Spacebar)
    if keys[pygame.K_SPACE] and laser_cooldown == 0:
        lasers.append([player_x + (player_width // 2) - 2, player_y])
        laser_cooldown = COOLDOWN_MAX
        if launch_sound:
            launch_sound.play()  # Trigger clean modular audio

    # Decrement shooting cooldown
    if laser_cooldown > 0:
        laser_cooldown -= 1

    # --- 3B. GAME PHYSICS ENGINE ---
    # Update Lasers
    for laser in lasers[:]:
        laser[1] -= laser_speed
        if laser[1] < 0:
            lasers.remove(laser)

    # Update Enemies (Sinusoidal Path Variables for Advanced Movement)
    for enemy in enemies:
        enemy['y'] += enemy['speed']
        enemy['angle'] += 0.05
        # Add a subtle horizontal sway using math.sin
        enemy['x'] += math.sin(enemy['angle']) * 1.5

        # Respawn enemy if it passes the bottom screen
        if enemy['y'] > SCREEN_HEIGHT:
            enemy['x'] = random.randint(0, SCREEN_WIDTH - 40)
            enemy['y'] = random.randint(-150, -50)
            enemy['speed'] = random.uniform(enemy_speed_min, enemy_speed_max)

    # --- 3C. COLLISION DETECTION ENGINE ---
    for laser in lasers[:]:
        for enemy in enemies:
            # Check AABB bounding box overlapping
            if (laser[0] > enemy['x'] and laser[0] < enemy['x'] + 40 and
                laser[1] > enemy['y'] and laser[1] < enemy['y'] + 40):
                
                # Collision detected! Trigger explosion sound
                if explosion_sound:
                    explosion_sound.play()
                
                # Remove laser, reset enemy, update score
                lasers.remove(laser)
                enemy['x'] = random.randint(0, SCREEN_WIDTH - 40)
                enemy['y'] = random.randint(-150, -50)
                enemy['speed'] = random.uniform(enemy_speed_min, enemy_speed_max)
                score += 100
                break

    # --- 3D. GRAPHICS RENDERING ENGINE ---
    # Draw Player (Neon Blue Jet Fighter)
    pygame.draw.rect(screen, (0, 180, 255), (player_x, player_y, player_width, player_height))
    pygame.draw.polygon(screen, (0, 255, 200), [
        (player_x + (player_width // 2), player_y - 12),
        (player_x + 5, player_y),
        (player_x + player_width - 5, player_y)
    ])

    # Draw Lasers (Bright Emerald Green Blasts)
    for laser in lasers:
        pygame.draw.rect(screen, (0, 255, 100), (laser[0], laser[1], 4, 12))

    # Draw Enemies (Vibrant Crimson Alien Invaders)
    for enemy in enemies:
        pygame.draw.rect(screen, (255, 50, 100), (enemy['x'], enemy['y'], 40, 40), border_radius=4)
        # Inside core detail
        pygame.draw.rect(screen, (255, 255, 255), (enemy['x'] + 12, enemy['y'] + 12, 16, 16))

    # Render User Interface HUD (Scoreboard)
    score_text = font.render(f"SCORE: {score}", True, (255, 255, 255))
    screen.blit(score_text, (15, 15))

    # Swap the back buffer to update the display window
    pygame.display.flip()

pygame.quit()
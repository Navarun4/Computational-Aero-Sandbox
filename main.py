import pygame
import os
import random
import math
import time

# ==========================================
# 1. CORE ENGINE INITIALIZATION
# ==========================================

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AeroStrike: Extreme Skies [v2.5 - Nexus State Engine]")

clock = pygame.time.Clock()
FPS = 60  

# Audio Fallback
base_dir = os.getcwd()
sound_dir = os.path.join(base_dir, "assets", "sounds")
try:
    launch_sound = pygame.mixer.Sound(os.path.join(sound_dir, "launch.wav.wav"))
    explosion_sound = pygame.mixer.Sound(os.path.join(sound_dir, "explosion.wav.wav"))
except Exception:
    launch_sound, explosion_sound = None, None

font_small = pygame.font.SysFont("Courier New", 18)
font_large = pygame.font.SysFont("Arial", 32, bold=True)

# ==========================================
# 2. CYBERPUNK LOADING & PROMPT SYSTEM
# ==========================================
def run_loading_screen():
    boot_messages = [
        "INITIALIZING AEROSTRIKE KERNEL...",
        "MOUNTING GRAPHICS BUFFER OVERLAYS...",
        "DECOUPLING DELTA-TIME CORE REGISTERS...",
        "COUCHING AUDIO MODULE INITIALIZATION...",
        "LAUNCHING COMBAT SIMULATION CORE v2.0..."
    ]
    
    progress = 0
    message_idx = 0
    
    # --- PHASE A: Running the Progress Bar ---
    while progress <= 100:
        screen.fill((5, 5, 10))
        
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(screen, (15, 15, 30), (i, 0), (i, SCREEN_HEIGHT))
        for j in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, (15, 15, 30), (0, j), (SCREEN_WIDTH, j))
            
        title_surf = font_large.render("AEROSTRIKE: NEXUS BOOT", True, (0, 255, 200))
        screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 180))
        
        if progress > (message_idx + 1) * 20 and message_idx < len(boot_messages) - 1:
            message_idx += 1
            
        msg_surf = font_small.render(boot_messages[message_idx], True, (0, 180, 255))
        screen.blit(msg_surf, (SCREEN_WIDTH//2 - msg_surf.get_width()//2, 300))
        
        bar_width = 400
        bar_height = 20
        bar_x = SCREEN_WIDTH//2 - bar_width//2
        bar_y = 350
        
        pygame.draw.rect(screen, (0, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=4)
        fill_width = int((progress / 100) * bar_width)
        if fill_width > 0:
            pygame.draw.rect(screen, (0, 255, 150), (bar_x + 2, bar_y + 2, fill_width - 4, bar_height - 4), border_radius=2)
            
        pct_surf = font_small.render(f"{progress}% COMPLETE", True, (255, 255, 255))
        screen.blit(pct_surf, (SCREEN_WIDTH//2 - pct_surf.get_width()//2, 390))
        
        pygame.display.flip()
        progress += random.randint(1, 3)
        time.sleep(0.03)

    # --- PHASE B: Standby Checkpoint (Press Any Key to Start) ---
    waiting_for_input = True
    flash_timer = 0
    
    while waiting_for_input:
        flash_timer += 1
        screen.fill((5, 5, 10))
        
        # Tech Background Grid
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(screen, (15, 15, 30), (i, 0), (i, SCREEN_HEIGHT))
        for j in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, (15, 15, 30), (0, j), (SCREEN_WIDTH, j))
            
        title_surf = font_large.render("SYSTEM INITIALIZED", True, (0, 255, 150))
        screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 180))
        
        # Flashing technical prompt text
        if (flash_timer // 30) % 2 == 0:
            prompt_surf = font_small.render(">> PRESS ANY KEY TO ENGAGE SIMULATION <<", True, (255, 255, 255))
        else:
            prompt_surf = font_small.render(">> PRESS ANY KEY TO ENGAGE SIMULATION <<", True, (0, 100, 100))
            
        screen.blit(prompt_surf, (SCREEN_WIDTH//2 - prompt_surf.get_width()//2, 320))
        
        pygame.display.flip()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting_for_input = False

run_loading_screen()

# ==========================================
# 3. GAME VARIABLES & ADVANCED VISUAL SYSTEMS
# ==========================================
engine_particles = []
explosion_particles = []

def spawn_explosion(x, y):
    for _ in range(25):
        explosion_particles.append([
            x, y, 
            random.uniform(-4, 4), random.uniform(-4, 4), 
            random.randint(3, 6), 1.0, 
            random.choice([(255, 80, 0), (255, 200, 0), (255, 50, 50)])
        ])

class PlayerMock:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.bullet_speed = 600.0

player_width, player_height = 56, 56
player_x = (SCREEN_WIDTH // 2) - (player_width // 2)
player_y = SCREEN_HEIGHT - player_height - 40
player_speed = 360.0  
player_health = 100

# Weapon Assist Configurations
FOV_ANGLE = 0.707
ASSIST_STRENGTH = 5.5

lasers = []
laser_cooldown = 0
COOLDOWN_MAX = 12  

# --- NEW PROGRESSIVE LEVEL MECHANICS ---
current_level = 1
enemies_killed_this_level = 0
enemies_spawned_count = 0

# Dynamic Helper to spawn an enemy scaled exactly to current level limits
def create_level_enemy(level_num):
    # Base speeds scale slightly as the levels advance
    speed_min = 100.0 + (level_num * 15)
    speed_max = 180.0 + (level_num * 25)
    return {
        'x': random.uniform(0, SCREEN_WIDTH - 45),
        'y': random.uniform(-250, -50),
        'base_speed': random.uniform(speed_min, speed_max),
        'vx': 0.0,
        'vy': 0.0,
        'angle': random.uniform(0, 3.14)
    }

# Initialization of Level 1 parameters (Starts with just 2 slow tactical units!)
enemies = []
enemies_required_to_advance = 4  
max_simultaneous_enemies = 2     

for _ in range(max_simultaneous_enemies):
    enemies.append(create_level_enemy(current_level))
    enemies_spawned_count += 1

score = 0
level_banner_timer = 180  # Frame duration to display "LEVEL X" UI alert at startup

# ==========================================
# 4. ENGINE RUNTIME LOOP
# ==========================================
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    if dt > 0.1: 
        dt = 0.1

    screen.fill((8, 8, 16))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_x > 0:
        player_x -= player_speed * dt
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_x < SCREEN_WIDTH - player_width:
        player_x += player_speed * dt
        
    player_wrapper = PlayerMock(player_x + player_width // 2, player_y, 600.0)

    # Laser Array Execution
    if keys[pygame.K_SPACE] and laser_cooldown == 0:
        spawn_offsets = [6, player_width - 10]
        for offset in spawn_offsets:
            lx = player_x + offset
            ly = player_y + 15
            
            best_target = None
            closest_dist_sq = float('inf')
            aim_x, aim_y = 0.0, -1.0

            for enemy in enemies:
                to_enemy_x = enemy['x'] + 20 - lx
                to_enemy_y = enemy['y'] + 20 - ly
                dist_sq = to_enemy_x**2 + to_enemy_y**2
                dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.0
                
                dir_to_enemy_x = to_enemy_x / dist if dist > 0 else 0.0
                dir_to_enemy_y = to_enemy_y / dist if dist > 0 else 0.0
                
                dot_product = (aim_x * dir_to_enemy_x) + (aim_y * dir_to_enemy_y)

                if dot_product > FOV_ANGLE and dist_sq < closest_dist_sq:
                    closest_dist_sq = dist_sq
                    best_target = enemy

            lasers.append({
                'x': lx,
                'y': ly,
                'vx': aim_x * player_wrapper.bullet_speed,
                'vy': aim_y * player_wrapper.bullet_speed,
                'target': best_target
            })
            
        laser_cooldown = COOLDOWN_MAX
        if launch_sound:
            launch_sound.play()

    if laser_cooldown > 0:
        laser_cooldown -= 1

    if random.random() < 0.6:
        engine_particles.append([player_x + 12, player_y + 45, random.uniform(-0.5, 0.5), random.uniform(2, 4), random.randint(2, 4), 1.0])
        engine_particles.append([player_x + player_width - 12, player_y + 45, random.uniform(-0.5, 0.5), random.uniform(2, 4), random.randint(2, 4), 1.0])

    for p in engine_particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[5] -= 0.04
        if p[5] <= 0:
            engine_particles.remove(p)

    for ep in explosion_particles[:]:
        ep[0] += ep[2]
        ep[1] += ep[3]
        ep[5] -= 0.03
        if ep[5] <= 0:
            explosion_particles.remove(ep)

    # --- 4B. AUTO-ASSIST WEAPON UPDATE MECHANICS ---
    for laser in lasers[:]:
        target = laser['target']
        
        if target and target in enemies:
            to_target_x = (target['x'] + 20) - laser['x']
            to_target_y = (target['y'] + 20) - laser['y']
            dist = math.sqrt(to_target_x**2 + to_target_y**2)

            if dist > 5:
                current_speed = math.sqrt(laser['vx']**2 + laser['vy']**2)
                desired_vx = (to_target_x / dist) * current_speed
                desired_vy = (to_target_y / dist) * current_speed

                blend_factor = 1.0 - math.exp(-ASSIST_STRENGTH * dt)
                laser['vx'] += (desired_vx - laser['vx']) * blend_factor
                laser['vy'] += (desired_vy - laser['vy']) * blend_factor

        laser['x'] += laser['vx'] * dt
        laser['y'] += laser['vy'] * dt
        
        if laser['y'] < 0 or laser['x'] < 0 or laser['x'] > SCREEN_WIDTH:
            lasers.remove(laser)

    # --- 4C. DYNAMIC LEVEL STATE MONITOR ---
    if enemies_killed_this_level >= enemies_required_to_advance:
        current_level += 1
        enemies_killed_this_level = 0
        enemies_spawned_count = 0
        # Scale parameters upward incrementally
        max_simultaneous_enemies = min(7, 2 + current_level) 
        enemies_required_to_advance = 4 + (current_level * 2)
        level_banner_timer = 180  # Reset flash banner trigger
        enemies.clear()
        lasers.clear()

    # Fill the sky mapping up to the dynamic level capacity limits
    while len(enemies) < max_simultaneous_enemies and enemies_spawned_count < enemies_required_to_advance:
        enemies.append(create_level_enemy(current_level))
        enemies_spawned_count += 1

    # --- 4D. PROXIMITY SPEED DAMPENING ENEMY MECHANICS ---
    for enemy in enemies:
        dx = (player_x + player_width // 2) - (enemy['x'] + 20)
        dy = (player_y + player_height // 2) - (enemy['y'] + 20)
        distance_sq = dx**2 + dy**2
        
        engagement_radius_sq = 90000  
        current_speed = enemy['base_speed']

        if distance_sq < engagement_radius_sq:
            proximity_ratio = distance_sq / engagement_radius_sq
            current_speed = enemy['base_speed'] * (0.35 + proximity_ratio * 0.65)

        enemy['angle'] += 2.4 * dt
        wave_offset = math.sin(enemy['angle']) * 100.0
        
        enemy['vx'] = wave_offset
        enemy['vy'] = current_speed

        enemy['x'] += enemy['vx'] * dt
        enemy['y'] += enemy['vy'] * dt

        if enemy['y'] > SCREEN_HEIGHT:
            # Recycle standard tracking position
            enemy['x'] = random.randint(0, SCREEN_WIDTH - 45)
            enemy['y'] = random.randint(-150, -50)
            player_health -= 10  

        if (enemy['x'] < player_x + player_width and enemy['x'] + 40 > player_x and
            enemy['y'] < player_y + player_height and enemy['y'] + 40 > player_y):
            spawn_explosion(enemy['x'] + 20, enemy['y'] + 20)
            player_health -= 20
            
            if len(enemies) + enemies_killed_this_level < enemies_required_to_advance:
                enemy['x'] = random.randint(0, SCREEN_WIDTH - 45)
                enemy['y'] = random.randint(-150, -50)
            else:
                enemies.remove(enemy)
                enemies_killed_this_level += 1

    # Intersection matrices
    for laser in lasers[:]:
        for enemy in enemies:
            if (laser['x'] > enemy['x'] and laser['x'] < enemy['x'] + 40 and
                laser['y'] > enemy['y'] and laser['y'] < enemy['y'] + 40):
                
                spawn_explosion(enemy['x'] + 20, enemy['y'] + 20)
                if explosion_sound:
                    explosion_sound.play()
                
                if laser in lasers:
                    lasers.remove(laser)
                
                enemies.remove(enemy)
                enemies_killed_this_level += 1
                score += 150
                break

    # --- 4E. GRAPHICS RENDERING LAYER ---
    for p in engine_particles:
        pygame.draw.circle(screen, (0, 200, 255), (int(p[0]), int(p[1])), int(p[4]))

    for ep in explosion_particles:
        pygame.draw.circle(screen, ep[6], (int(ep[0]), int(ep[1])), int(ep[4]))

    pygame.draw.rect(screen, (30, 50, 90), (player_x + 16, player_y + 10, 24, 38), border_radius=3)
    pygame.draw.polygon(screen, (0, 180, 255), [
        (player_x + player_width // 2, player_y),
        (player_x, player_y + player_height - 10),
        (player_x + player_width, player_y + player_height - 10)
    ])
    pygame.draw.ellipse(screen, (0, 255, 200), (player_x + 23, player_y + 12, 10, 18))

    for laser in lasers:
        pygame.draw.rect(screen, (0, 255, 120), (int(laser['x']), int(laser['y']), 4, 14))

    for enemy in enemies:
        pygame.draw.rect(screen, (220, 40, 70), (int(enemy['x']), int(enemy['y']), 40, 40), border_radius=6)
        pygame.draw.circle(screen, (255, 255, 255), (int(enemy['x'] + 20), int(enemy['y'] + 20)), 8)
        pygame.draw.circle(screen, (0, 0, 0), (int(enemy['x'] + 20), int(enemy['y'] + 20)), 4)

    # UI Dashboard HUD Layers
    score_surf = font_small.render(f"SYSTEM SCORE // {score:06d}", True, (255, 255, 255))
    screen.blit(score_surf, (20, 20))
    
    # Progress towards next level indicator
    lvl_surf = font_small.render(f"SECTOR LEVEL: {current_level} [{enemies_killed_this_level}/{enemies_required_to_advance}]", True, (0, 255, 200))
    screen.blit(lvl_surf, (20, 45))
    
    # Shield HUD Draw Meter
    pygame.draw.rect(screen, (40, 40, 60), (SCREEN_WIDTH - 170, 20, 150, 16), border_radius=4)
    if player_health > 0:
        health_color = (0, 255, 150) if player_health > 40 else (255, 50, 50)
        pygame.draw.rect(screen, health_color, (SCREEN_WIDTH - 168, 22, int(146 * (player_health / 100)), 12), border_radius=2)
    hp_lbl = font_small.render("SHIELDS", True, (255, 255, 255))
    screen.blit(hp_lbl, (SCREEN_WIDTH - 250, 20))

    # Splashing "Level Up" Announcement Text
    if level_banner_timer > 0:
        level_banner_timer -= 1
        banner_surf = font_large.render(f"ENTERING SECTOR {current_level}", True, (255, 215, 0))
        # Draw soft shadow text
        shadow_surf = font_large.render(f"ENTERING SECTOR {current_level}", True, (50, 30, 0))
        screen.blit(shadow_surf, (SCREEN_WIDTH//2 - banner_surf.get_width()//2 + 2, SCREEN_HEIGHT//3 + 2))
        screen.blit(banner_surf, (SCREEN_WIDTH//2 - banner_surf.get_width()//2, SCREEN_HEIGHT//3))

    if player_health <= 0:
        game_over_surf = font_large.render("SYSTEM CRITICAL: GAME OVER", True, (255, 50, 100))
        screen.blit(game_over_surf, (SCREEN_WIDTH//2 - game_over_surf.get_width()//2, SCREEN_HEIGHT//2))
        pygame.display.flip()
        time.sleep(3)
        running = False

    pygame.display.flip()

pygame.quit()

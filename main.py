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
pygame.display.set_caption("AeroStrike: Extreme Skies [v4.0 - Customization & Levels]")

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

font_small = pygame.font.SysFont("Courier New", 16)
font_medium = pygame.font.SysFont("Courier New", 22, bold=True)
font_large = pygame.font.SysFont("Arial", 32, bold=True)

# ==========================================
# 2. PLAYER PROGRESSION & CUSTOMIZATION STATES
# ==========================================
# Leveling Stats
player_level = 1
player_xp = 0
xp_needed_for_next_level = 1000
upgrade_points_available = 0

# Customizable Attributes (Tweakable via level up)
engine_level = 1
shield_level = 1
weapon_level = 1

player_width, player_height = 56, 56
player_x = (SCREEN_WIDTH // 2) - (player_width // 2)
player_y = SCREEN_HEIGHT - player_height - 40

# Stats calculated dynamically from Attribute Levels
def get_player_speed():
    return 360.0 + (engine_level - 1) * 45.0

def get_max_shields():
    return 100 + (shield_level - 1) * 25

def get_weapon_cooldown():
    return max(5, 12 - (weapon_level - 1) * 1)

player_max_health = get_max_shields()
player_health = player_max_health

# ==========================================
# 3. UPGRADE MENU SUBSYSTEM (PAUSE STATE)
# ==========================================
def run_upgrade_menu():
    global upgrade_points_available, engine_level, shield_level, weapon_level, player_health, player_max_health
    
    menu_running = True
    selected_option = 0  # 0: Engine, 1: Shields, 2: Weapons
    
    while menu_running:
        screen.fill((5, 5, 15))
        
        # Cyber grid backdrop
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(screen, (15, 15, 35), (i, 0), (i, SCREEN_HEIGHT))
        for j in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, (15, 15, 35), (0, j), (SCREEN_WIDTH, j))
            
        # Headers
        title_surf = font_large.render("CRITICAL LEVEL UP: CUSTOMIZE FIGHTER", True, (0, 255, 200))
        screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 80))
        
        points_text = f"UPGRADE POINTS AVAILABLE: {upgrade_points_available}"
        points_surf = font_medium.render(points_text, True, (255, 255, 255))
        screen.blit(points_surf, (SCREEN_WIDTH//2 - points_surf.get_width()//2, 140))
        
        # Build options list dynamically
        options = [
            {"name": "🚀 ENGINE THRUST", "lvl": engine_level, "desc": f"Increases speed. Current: {int(get_player_speed())} px/s"},
            {"name": "🔋 SHIELD CAPACITY", "lvl": shield_level, "desc": f"Increases max hull. Current: {get_max_shields()} HP"},
            {"name": "⚡ LASER OVERCLOCK", "lvl": weapon_level, "desc": f"Reduces fire rate delay. Current: {get_weapon_cooldown()} frames"}
        ]
        
        # Render the customization panel items
        for idx, opt in enumerate(options):
            box_y = 220 + (idx * 90)
            box_width = 550
            box_height = 75
            box_x = SCREEN_WIDTH//2 - box_width//2
            
            # Selection Highlight border
            if idx == selected_option:
                pygame.draw.rect(screen, (0, 255, 150), (box_x, box_y, box_width, box_height), 3, border_radius=6)
                bg_color = (10, 40, 30)
            else:
                pygame.draw.rect(screen, (0, 100, 150), (box_x, box_y, box_width, box_height), 1, border_radius=6)
                bg_color = (10, 15, 25)
                
            pygame.draw.rect(screen, bg_color, (box_x + 2, box_y + 2, box_width - 4, box_height - 4), border_radius=4)
            
            # Print Info Inside Box
            name_surf = font_medium.render(f"{opt['name']} [LVL {opt['lvl']}]", True, (255, 255, 255))
            screen.blit(name_surf, (box_x + 20, box_y + 12))
            
            desc_surf = font_small.render(opt['desc'], True, (0, 180, 255))
            screen.blit(desc_surf, (box_x + 20, box_y + 42))
            
        # Controls Notice
        prompt_surf = font_small.render("[W/S or UP/DOWN] Select | [SPACE] Allocate Point | [ENTER] Return to Combat", True, (255, 200, 0))
        screen.blit(prompt_surf, (SCREEN_WIDTH//2 - prompt_surf.get_width()//2, 510))
        
        pygame.display.flip()
        
        # Dedicated Input Listener Loop for Paused Menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    selected_option = (selected_option - 1) % 3
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    selected_option = (selected_option + 1) % 3
                elif event.key == pygame.K_SPACE:
                    if upgrade_points_available > 0:
                        upgrade_points_available -= 1
                        if selected_option == 0:
                            engine_level += 1
                        elif selected_option == 1:
                            shield_level += 1
                            # Instantly scale up max shield and heal player fully
                            player_max_health = get_max_shields()
                            player_health = player_max_health
                        elif selected_option == 2:
                            weapon_level += 1
                elif event.key == pygame.K_RETURN:
                    # Let them exit only if they spent points, or have none left
                    if upgrade_points_available == 0:
                        menu_running = False

def add_xp(amount):
    global player_xp, player_level, xp_needed_for_next_level, upgrade_points_available
    player_xp += amount
    if player_xp >= xp_needed_for_next_level:
        player_xp -= xp_needed_for_next_level
        player_level += 1
        upgrade_points_available += 1
        xp_needed_for_next_level = player_level * 1000
        run_upgrade_menu()

# ==========================================
# 4. GAME VARIABLES & ENTITY LISTS
# ==========================================
engine_particles = []
explosion_particles = []
powerups = []  

screen_shake_intensity = 0.0  
screen_shake_decay = 5.0      
camera_offset_x = 0
camera_offset_y = 0

def trigger_screen_shake(intensity):
    global screen_shake_intensity
    screen_shake_intensity = max(screen_shake_intensity, intensity)

def spawn_explosion(x, y):
    for _ in range(25):
        explosion_particles.append([
            x, y, 
            random.uniform(-4, 4), random.uniform(-4, 4), 
            random.randint(3, 6), 1.0, 
            random.choice([(255, 80, 0), (255, 200, 0), (255, 50, 50)])
        ])

def attempt_powerup_drop(x, y):
    if random.random() < 0.35:
        p_type = random.choice(['REPAIR', 'TRIPLE'])
        color = (0, 255, 255) if p_type == 'TRIPLE' else (0, 255, 100)
        powerups.append({
            'x': x, 'y': y, 'type': p_type, 'speed': 150.0,
            'radius': 12, 'color': color, 'pulse_angle': 0.0
        })

class PlayerMock:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.bullet_speed = 600.0

FOV_ANGLE = 0.707
ASSIST_STRENGTH = 5.5

lasers = []
laser_cooldown = 0
triple_shot_timer = 0.0  

current_level = 1
enemies_killed_this_level = 0
enemies_spawned_count = 0

def create_level_enemy(level_num):
    speed_min = 100.0 + (level_num * 15)
    speed_max = 180.0 + (level_num * 25)
    return {
        'x': random.uniform(0, SCREEN_WIDTH - 45),
        'y': random.uniform(-250, -50),
        'base_speed': random.uniform(speed_min, speed_max),
        'vx': 0.0, 'vy': 0.0, 'angle': random.uniform(0, 3.14)
    }

enemies = []
enemies_required_to_advance = 4  
max_simultaneous_enemies = 2     

for _ in range(max_simultaneous_enemies):
    enemies.append(create_level_enemy(current_level))
    enemies_spawned_count += 1

score = 0
level_banner_timer = 180  

# ==========================================
# 5. MAIN ENGINE RUNTIME LOOP
# ==========================================
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    if dt > 0.1: dt = 0.1

    screen.fill((8, 8, 16))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- CALCULATE SCREEN SHAKE ---
    if screen_shake_intensity > 0.1:
        screen_shake_intensity -= screen_shake_intensity * screen_shake_decay * dt
        shake_angle = random.uniform(0, 2 * math.pi)
        camera_offset_x = int(math.cos(shake_angle) * screen_shake_intensity)
        camera_offset_y = int(math.sin(shake_angle) * screen_shake_intensity)
    else:
        screen_shake_intensity = 0.0
        camera_offset_x, camera_offset_y = 0, 0

    if triple_shot_timer > 0:
        triple_shot_timer -= dt

    # Read speed dynamically from customization matrix
    current_speed = get_player_speed()
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_x > 0:
        player_x -= current_speed * dt
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_x < SCREEN_WIDTH - player_width:
        player_x += current_speed * dt
        
    player_wrapper = PlayerMock(player_x + player_width // 2, player_y, 600.0)

    # --- ENHANCED WEAPON SYSTEM ---
    if keys[pygame.K_SPACE] and laser_cooldown == 0:
        angles = [-0.25, 0.0, 0.25] if triple_shot_timer > 0 else [0.0]
        spawn_offsets = [6, player_width - 10] if triple_shot_timer <= 0 else [player_width // 2]
        
        for offset in spawn_offsets:
            for angle in angles:
                lx, ly = player_x + offset, player_y + 15
                best_target = None
                closest_dist_sq = float('inf')
                aim_x, aim_y = math.sin(angle), -math.cos(angle)

                for enemy in enemies:
                    to_enemy_x = enemy['x'] + 20 - lx
                    to_enemy_y = enemy['y'] + 20 - ly
                    dist_sq = to_enemy_x**2 + to_enemy_y**2
                    dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.0
                    
                    dot_product = (aim_x * (to_enemy_x / dist if dist > 0 else 0.0)) + (aim_y * (to_enemy_y / dist if dist > 0 else 0.0))
                    if dot_product > FOV_ANGLE and dist_sq < closest_dist_sq:
                        closest_dist_sq = dist_sq
                        best_target = enemy

                lasers.append({
                    'x': lx, 'y': ly,
                    'vx': aim_x * player_wrapper.bullet_speed,
                    'vy': aim_y * player_wrapper.bullet_speed,
                    'target': best_target
                })
            
        laser_cooldown = get_weapon_cooldown()  # Pulled dynamically from weapon overclock configs
        if launch_sound: launch_sound.play()

    if laser_cooldown > 0:
        laser_cooldown -= 1

    # --- ITEM DROPS MATRIX ---
    for p in powerups[:]:
        p['y'] += p['speed'] * dt
        p['pulse_angle'] += 5.0 * dt
        
        if (p['x'] + p['radius'] > player_x and p['x'] - p['radius'] < player_x + player_width and
            p['y'] + p['radius'] > player_y and p['y'] - p['radius'] < player_y + player_height):
            
            if p['type'] == 'REPAIR':
                player_health = min(get_max_shields(), player_health + 25)
                trigger_screen_shake(4.0)
            elif p['type'] == 'TRIPLE':
                triple_shot_timer = 7.0
                trigger_screen_shake(6.0)
            powerups.remove(p)
            continue
            
        if p['y'] > SCREEN_HEIGHT + 20:
            powerups.remove(p)

    # Particle Updates
    if random.random() < 0.6:
        engine_particles.append([player_x + 12, player_y + 45, random.uniform(-0.5, 0.5), random.uniform(2, 4), random.randint(2, 4), 1.0])
        engine_particles.append([player_x + player_width - 12, player_y + 45, random.uniform(-0.5, 0.5), random.uniform(2, 4), random.randint(2, 4), 1.0])

    for p in engine_particles[:]:
        p[0] += p[2]; p[1] += p[3]; p[5] -= 0.04
        if p[5] <= 0: engine_particles.remove(p)

    for ep in explosion_particles[:]:
        ep[0] += ep[2]; ep[1] += ep[3]; ep[5] -= 0.03
        if ep[5] <= 0: explosion_particles.remove(ep)

    # Lasers Processing
    for laser in lasers[:]:
        target = laser['target']
        if target and target in enemies:
            to_target_x = (target['x'] + 20) - laser['x']
            to_target_y = (target['y'] + 20) - laser['y']
            dist = math.sqrt(to_target_x**2 + to_target_y**2)
            if dist > 5:
                current_laser_spd = math.sqrt(laser['vx']**2 + laser['vy']**2)
                blend = 1.0 - math.exp(-ASSIST_STRENGTH * dt)
                laser['vx'] += ((to_target_x / dist) * current_laser_spd - laser['vx']) * blend
                laser['vy'] += ((to_target_y / dist) * current_laser_spd - laser['vy']) * blend

        laser['x'] += laser['vx'] * dt
        laser['y'] += laser['vy'] * dt
        if laser['y'] < 0 or laser['x'] < 0 or laser['x'] > SCREEN_WIDTH or laser['y'] > SCREEN_HEIGHT:
            lasers.remove(laser)

    # Level Management
    if enemies_killed_this_level >= enemies_required_to_advance:
        current_level += 1
        enemies_killed_this_level = 0
        enemies_spawned_count = 0
        max_simultaneous_enemies = min(7, 2 + current_level) 
        enemies_required_to_advance = 4 + (current_level * 2)
        level_banner_timer = 180  
        enemies.clear()
        lasers.clear()

    while len(enemies) < max_simultaneous_enemies and enemies_spawned_count < enemies_required_to_advance:
        enemies.append(create_level_enemy(current_level))
        enemies_spawned_count += 1

    # Enemy Loops
    for enemy in enemies[:]:
        dx = (player_x + player_width // 2) - (enemy['x'] + 20)
        dy = (player_y + player_height // 2) - (enemy['y'] + 20)
        distance_sq = dx**2 + dy**2
        
        enemy_speed = enemy['base_speed']
        if distance_sq < 90000:
            enemy_speed = enemy['base_speed'] * (0.35 + (distance_sq / 90000) * 0.65)

        enemy['angle'] += 2.4 * dt
        enemy['vx'] = math.sin(enemy['angle']) * 100.0
        enemy['vy'] = enemy_speed

        enemy['x'] += enemy['vx'] * dt
        enemy['y'] += enemy['vy'] * dt

        if enemy['y'] > SCREEN_HEIGHT:
            enemy['x'] = random.randint(0, SCREEN_WIDTH - 45)
            enemy['y'] = random.randint(-150, -50)
            player_health -= 10  
            trigger_screen_shake(12.0)

        # Hull Smash Collision
        if (enemy['x'] < player_x + player_width and enemy['x'] + 40 > player_x and
            enemy['y'] < player_y + player_height and enemy['y'] + 40 > player_y):
            spawn_explosion(enemy['x'] + 20, enemy['y'] + 20)
            attempt_powerup_drop(enemy['x'] + 20, enemy['y'] + 20)
            player_health -= 20
            trigger_screen_shake(22.0)
            add_xp(100) # Awarding partial combat crash XP
            
            if len(enemies) + enemies_killed_this_level < enemies_required_to_advance:
                enemy['x'] = random.randint(0, SCREEN_WIDTH - 45)
                enemy['y'] = random.randint(-150, -50)
            else:
                enemies.remove(enemy)
                enemies_killed_this_level += 1

    # Laser Impact Check
    for laser in lasers[:]:
        for enemy in enemies[:]:
            if (laser['x'] > enemy['x'] and laser['x'] < enemy['x'] + 40 and
                laser['y'] > enemy['y'] and laser['y'] < enemy['y'] + 40):
                
                spawn_explosion(enemy['x'] + 20, enemy['y'] + 20)
                attempt_powerup_drop(enemy['x'] + 20, enemy['y'] + 20)
                trigger_screen_shake(8.0)
                if explosion_sound: explosion_sound.play()
                
                if laser in lasers: lasers.remove(laser)
                if enemy in enemies: enemies.remove(enemy)
                enemies_killed_this_level += 1
                score += 150
                add_xp(150) # Boost Player Meta XP Register!
                break

    # ==========================================
    # 6. GRAPHICS RENDERING SYSTEM
    # ==========================================
    for i in range(0, SCREEN_WIDTH, 40):
        pygame.draw.line(screen, (15, 15, 30), (i + camera_offset_x, camera_offset_y), (i + camera_offset_x, SCREEN_HEIGHT + camera_offset_y))
    for j in range(0, SCREEN_HEIGHT, 40):
        pygame.draw.line(screen, (15, 15, 30), (camera_offset_x, j + camera_offset_y), (SCREEN_WIDTH + camera_offset_x, j + camera_offset_y))

    for p in engine_particles:
        pygame.draw.circle(screen, (0, 200, 255), (int(p[0]) + camera_offset_x, int(p[1]) + camera_offset_y), int(p[4]))

    for p in powerups:
        pulse = p['radius'] + int(math.sin(p['pulse_angle']) * 3)
        pygame.draw.circle(screen, p['color'], (int(p['x']) + camera_offset_x, int(p['y']) + camera_offset_y), pulse)
        pygame.draw.circle(screen, (255, 255, 255), (int(p['x']) + camera_offset_x, int(p['y']) + camera_offset_y), pulse + 4, 1)

    for ep in explosion_particles:
        pygame.draw.circle(screen, ep[6], (int(ep[0]) + camera_offset_x, int(ep[1]) + camera_offset_y), int(ep[4]))

    # Ship Chassis
    pygame.draw.rect(screen, (30, 50, 90), (player_x + 16 + camera_offset_x, player_y + 10 + camera_offset_y, 24, 38), border_radius=3)
    pygame.draw.polygon(screen, (0, 180, 255), [
        (player_x + player_width // 2 + camera_offset_x, player_y + camera_offset_y),
        (player_x + camera_offset_x, player_y + player_height - 10 + camera_offset_y),
        (player_x + player_width + camera_offset_x, player_y + player_height - 10 + camera_offset_y)
    ])
    pygame.draw.ellipse(screen, (0, 255, 200), (player_x + 23 + camera_offset_x, player_y + 12 + camera_offset_y, 10, 18))

    for laser in lasers:
        pygame.draw.rect(screen, (0, 255, 120), (int(laser['x']) + camera_offset_x, int(laser['y']) + camera_offset_y, 4, 14))

    for enemy in enemies:
        pygame.draw.rect(screen, (220, 40, 70), (int(enemy['x']) + camera_offset_x, int(enemy['y']) + camera_offset_y, 40, 40), border_radius=6)
        pygame.draw.circle(screen, (255, 255, 255), (int(enemy['x'] + 20) + camera_offset_x, int(enemy['y'] + 20) + camera_offset_y), 8)

    # --- HUD OVERLAY LAYER ---
    score_surf = font_small.render(f"SCORE: {score:06d}", True, (255, 255, 255))
    screen.blit(score_surf, (20, 20))
    
    lvl_surf = font_small.render(f"SECTOR: {current_level} [{enemies_killed_this_level}/{enemies_required_to_advance}]", True, (0, 255, 200))
    screen.blit(lvl_surf, (20, 42))
    
    if triple_shot_timer > 0:
        overcharge_surf = font_small.render(f"OVERCHARGE: {triple_shot_timer:.1f}s", True, (0, 255, 255))
        screen.blit(overcharge_surf, (20, 64))

    # Top Right HUD Modules: Shield Status + Pilot Level Profile
    pygame.draw.rect(screen, (40, 40, 60), (SCREEN_WIDTH - 170, 20, 150, 14), border_radius=4)
    if player_health > 0:
        h_ratio = player_health / get_max_shields()
        pygame.draw.rect(screen, (0, 255, 150) if h_ratio > 0.4 else (255, 50, 50), (SCREEN_WIDTH - 168, 22, int(146 * h_ratio), 10), border_radius=2)
    hp_lbl = font_small.render("SHIELD", True, (255, 255, 255))
    screen.blit(hp_lbl, (SCREEN_WIDTH - 235, 18))

    # XP Progression Meter Block
    pygame.draw.rect(screen, (30, 30, 45), (SCREEN_WIDTH - 170, 40, 150, 8), border_radius=2)
    xp_ratio = min(1.0, player_xp / xp_needed_for_next_level)
    pygame.draw.rect(screen, (255, 200, 0), (SCREEN_WIDTH - 168, 41, int(146 * xp_ratio), 6), border_radius=1)
    
    xp_lbl = font_small.render(f"PILOT LVL {player_level}", True, (255, 200, 0))
    screen.blit(xp_lbl, (SCREEN_WIDTH - 300, 36))

    if level_banner_timer > 0:
        level_banner_timer -= 1
        banner_surf = font_large.render(f"ENTERING SECTOR {current_level}", True, (255, 215, 0))
        screen.blit(banner_surf, (SCREEN_WIDTH//2 - banner_surf.get_width()//2, SCREEN_HEIGHT//3))

    if player_health <= 0:
        game_over_surf = font_large.render("SYSTEM CRITICAL: GAME OVER", True, (255, 50, 100))
        screen.blit(game_over_surf, (SCREEN_WIDTH//2 - game_over_surf.get_width()//2, SCREEN_HEIGHT//2))
        pygame.display.flip()
        time.sleep(3)
        running = False

    pygame.display.flip()

pygame.quit()

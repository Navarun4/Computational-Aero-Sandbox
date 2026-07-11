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
pygame.display.set_caption("AeroStrike: Extreme Skies [v2.0 - Mega Engine]")

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
# 2. CYBERPUNK LOADING SCREEN SYSTEM
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
    
    while progress <= 100:
        screen.fill((5, 5, 10))
        
        # Draw tech grid background lines
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(screen, (15, 15, 30), (i, 0), (i, SCREEN_HEIGHT))
        for j in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, (15, 15, 30), (0, j), (SCREEN_WIDTH, j))
            
        # Title text
        title_surf = font_large.render("AEROSTRIKE: NEXUS BOOT", True, (0, 255, 200))
        screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 180))
        
        # Cycling technical boot messages
        if progress > (message_idx + 1) * 20 and message_idx < len(boot_messages) - 1:
            message_idx += 1
            
        msg_surf = font_small.render(boot_messages[message_idx], True, (0, 180, 255))
        screen.blit(msg_surf, (SCREEN_WIDTH//2 - msg_surf.get_width()//2, 300))
        
        # Progress Bar Box
        bar_width = 400
        bar_height = 20
        bar_x = SCREEN_WIDTH//2 - bar_width//2
        bar_y = 350
        
        # Draw outer border box
        pygame.draw.rect(screen, (0, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=4)
        # Fill inner progress bar dynamically
        fill_width = int((progress / 100) * bar_width)
        if fill_width > 0:
            pygame.draw.rect(screen, (0, 255, 150), (bar_x + 2, bar_y + 2, fill_width - 4, bar_height - 4), border_radius=2)
            
        # Percent text
        pct_surf = font_small.render(f"{progress}% COMPLETE", True, (255, 255, 255))
        screen.blit(pct_surf, (SCREEN_WIDTH//2 - pct_surf.get_width()//2, 390))
        
        pygame.display.flip()
        progress += random.randint(1, 3)
        time.sleep(0.04)

# Execute the loading sequence immediately!
run_loading_screen()

# ==========================================
# 3. OPTIMIZED ENGINE SUBSYSTEMS
# ==========================================
class WeaponSystem:
    def __init__(self):
        self.fov_angle = 0.707  # 90-degree forward tracking cone
        self.assist_strength = 4.5  # Auto-aim pull scaling curve strength

    def fire_projectile(self, player_center_x, player_center_y, target_list, base_dir_x, base_dir_y, bullet_speed):
        best_target = None
        closest_dist_sq = float('inf')
        
        input_mag = math.sqrt(base_dir_x ** 2 + base_dir_y ** 2)
        aim_x = base_dir_x / input_mag if input_mag > 0 else 0
        aim_y = base_dir_y / input_mag if input_mag > 0 else -1

        for enemy in target_list:
            to_enemy_x = (enemy['x'] + 20) - player_center_x
            to_enemy_y = (enemy['y'] + 20) - player_center_y
            dist_sq = to_enemy_x ** 2 + to_enemy_y ** 2

            dist = math.sqrt(dist_sq)
            dir_to_enemy_x = to_enemy_x / dist if dist > 0 else 0
            dir_to_enemy_y = to_enemy_y / dist if dist > 0 else 0

            dot_product = (aim_x * dir_to_enemy_x) + (aim_y * dir_to_enemy_y)

            if dot_product > self.fov_angle and dist_sq < closest_dist_sq:
                closest_dist_sq = dist_sq
                best_target = enemy

        return {
            'x': player_center_x,
            'y': player_center_y,
            'vx': aim_x * bullet_speed,
            'vy': aim_y * bullet_speed,
            'target': best_target
        }

    def update_projectile(self, projectile, delta_time):
        target = projectile['target']
        
        # Check if target is missing or was reset back to top of screen
        if not target or target['y'] < 0:
            projectile['x'] += projectile['vx'] * delta_time
            projectile['y'] += projectile['vy'] * delta_time
            return

        to_target_x = (target['x'] + 20) - projectile['x']
        to_target_y = (target['y'] + 20) - projectile['y']
        dist = math.sqrt(to_target_x ** 2 + to_target_y ** 2)

        if dist > 5:
            current_speed = math.sqrt(projectile['vx'] ** 2 + projectile['vy'] ** 2)
            desired_vx = (to_target_x / dist) * current_speed
            desired_vy = (to_target_y / dist) * current_speed

            blend_factor = 1.0 - math.exp(-self.assist_strength * delta_time)
            projectile['vx'] += (desired_vx - projectile['vx']) * blend_factor
            projectile['vy'] += (desired_vy - projectile['vy']) * blend_factor

        projectile['x'] += projectile['vx'] * delta_time
        projectile['y'] += projectile['vy'] * delta_time


def update_enemy(enemy, player_center_x, player_center_y, delta_time):
    # Base pattern tracking logic (Sine wave down screen)
    enemy['angle'] += 0.04
    enemy['x'] += math.sin(enemy['angle']) * 1.8
    
    dx = player_center_x - (enemy['x'] + 20)
    dy = player_center_y - (enemy['y'] + 20)
    distance_sq = dx ** 2 + dy ** 2
    
    engagement_radius_sq = 90000  # 300 pixels squared radius zone
    current_speed = enemy['base_speed']

    # Proximity Matrix Speed Dampening
    if distance_sq < engagement_radius_sq:
        proximity_ratio = distance_sq / engagement_radius_sq
        current_speed = enemy['base_speed'] * (0.4 + proximity_ratio * 0.6)

    # Apply velocity conversion based on speed scaling down standard y tracking
    enemy['y'] += current_speed * delta_time

# Initialize custom component systems
weapons = WeaponSystem()

# ==========================================
# 4. GAME VARIABLES & ADVANCED VISUAL SYSTEMS
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

# Player Setup & Upgraded Tech Costume Coordinates
player_width, player_height = 56, 56
player_x = (SCREEN_WIDTH // 2) - (player_width // 2)
player_y = SCREEN_HEIGHT - player_height - 40
player_speed = 360.0  # Decoupled speed capacity (pixels/sec)
player_health = 100

lasers = []
laser_speed = 600.0  # Decoupled velocity capacity
laser_cooldown = 0
COOLDOWN_MAX = 0.2  # Timing interval in seconds instead of frames

enemies = []
enemy_speed_min = 120.0
enemy_speed_max = 240.0
for _ in range(6):
    enemies.append({
        'x': random.randint(0, SCREEN_WIDTH - 45),
        'y': random.randint(-250, -50),
        'base_speed': random.uniform(enemy_speed_min, enemy_speed_max),
        'angle': random.uniform(0, 3.14)
    })

score = 0

# ==========================================
# 5. ENGINE RUNTIME LOOP
# ==========================================
running = True
while running:
    # 60 FPS Delta Time calculation
    dt = clock.tick(FPS) / 1000.0

    # Draw Cosmic Abyss Space Background
    screen.fill((8, 8, 16))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player_center_x = player_x + player_width // 2
    player_center_y = player_y + player_height // 2

    # Input Matrix Parsing Engine
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_x > 0:
        player_x -= player_speed * dt
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_x < SCREEN_WIDTH - player_width:
        player_x += player_speed * dt
        
    # Laser Array Execution
    if keys[pygame.K_SPACE] and laser_cooldown <= 0:
        # Spawn Dual-Barreled Wing Lasers with soft auto-aim tracking!
        left_laser = weapons.fire_projectile(player_x + 6, player_y + 15, enemies, 0, -1, laser_speed)
        right_laser = weapons.fire_projectile(player_x + player_width - 10, player_y + 15, enemies, 0, -1, laser_speed)
        
        lasers.append(left_laser)
        lasers.append(right_laser)
        
        laser_cooldown = COOLDOWN_MAX
        if launch_sound:
            launch_sound.play()

    if laser_cooldown > 0:
        laser_cooldown -= dt

    # --- 5A. PARTICLE ENGINE PHYSICS ---
    if random.random() < 0.6:
        engine_particles.append([player_x + 12, player_y + 45, random.uniform(-30, 30), random.uniform(120, 240), random.randint(2, 4), 1.0])
        engine_particles.append([player_x + player_width - 12, player_y + 45, random.uniform(-30, 30), random.uniform(120, 240), random.randint(2, 4), 1.0])

    # Update Engine Particles
    for p in engine_particles[:]:
        p[0] += p[2] * dt
        p[1] += p[3] * dt
        p[5] -= 2.4 * dt  
        if p[5] <= 0:
            engine_particles.remove(p)

    # Update Shockwave Explosion Particles
    for ep in explosion_particles[:]:
        ep[0] += ep[2]
        ep[1] += ep[3]
        ep[5] -= 1.8 * dt
        if ep[5] <= 0:
            explosion_particles.remove(ep)

    # --- 5B. ENTITY PHYSICS & COLLISION CALCULATIONS ---
    for laser in lasers[:]:
        weapons.update_projectile(laser, dt)
        if laser['y'] < 0 or laser['x'] < 0 or laser['x'] > SCREEN_WIDTH:
            lasers.remove(laser)

    for enemy in enemies:
        update_enemy(enemy, player_center_x, player_center_y, dt)

        # Respawn if passed screen boundaries
        if enemy['y'] > SCREEN_HEIGHT:
            enemy['x'] = random.randint(0, SCREEN_WIDTH - 45)
            enemy['y'] = random.randint(-150, -50)
            enemy['base_speed'] = random.uniform(enemy_speed_min, enemy_speed_max)
            player_health -= 10  

        # Player-Enemy Collision Matrix Check
        if (enemy['x'] < player_x + player_width and enemy['x'] + 40 > player_x and
            enemy['y'] < player_y + player_height and enemy['y'] + 40 > player_y):
            spawn_explosion(enemy['x'] + 20, enemy['y'] + 20)
            player_health -= 20
            enemy['x'] = random.randint(0, SCREEN_WIDTH - 45)
            enemy['y'] = random.randint(-150, -50)
            enemy['base_speed'] = random.uniform(enemy_speed_min, enemy_speed_max)

    # Laser-Enemy Intersections
    for laser in lasers[:]:
        for enemy in enemies:
            if (laser['x'] > enemy['x'] and laser['x'] < enemy['x'] + 40 and
                laser['y'] > enemy['y'] and laser['y'] < enemy['y'] + 40):
                
                spawn_explosion(enemy['x'] + 20, enemy['y'] + 20)
                if explosion_sound:
                    explosion_sound.play()
                
                if laser in lasers:
                    lasers.remove(laser)
                enemy['x'] = random.randint(0, SCREEN_WIDTH - 45)
                enemy['y'] = random.randint(-150, -50)
                enemy['base_speed'] = random.uniform(enemy_speed_min, enemy_speed_max)
                score += 150
                break

    # --- 5C. ADVANCED GRAPHICS RENDERING LAYER ---
    # Render Tail Plasma Flames
    for p in engine_particles:
        pygame.draw.circle(screen, (0, 200, 255), (int(p[0]), int(p[1])), int(p[4]))

    # Render Active Debris Particles
    for ep in explosion_particles:
        pygame.draw.circle(screen, ep[6], (int(ep[0]), int(ep[1])), int(ep[4]))

    # Draw Player Costume: Cyber-Interceptor Jet Architecture
    pygame.draw.rect(screen, (30, 50, 90), (player_x + 16, player_y + 10, 24, 38), border_radius=3)
    pygame.draw.polygon(screen, (0, 180, 255), [
        (player_x + player_width // 2, player_y),
        (player_x, player_y + player_height - 10),
        (player_x + player_width, player_y + player_height - 10)
    ])
    pygame.draw.ellipse(screen, (0, 255, 200), (player_x + 23, player_y + 12, 10, 18))

    # Render Weapon Lasers Array Lines
    for laser in lasers:
        pygame.draw.rect(screen, (0, 255, 120), (int(laser['x']), int(laser['y']), 4, 14))

    # Render Red Alien Attacker Drones
    for enemy in enemies:
        pygame.draw.rect(screen, (220, 40, 70), (int(enemy['x']), int(enemy['y']), 40, 40), border_radius=6)
        pygame.draw.circle(screen, (255, 255, 255), (int(enemy['x'] + 20), int(enemy['y'] + 20)), 8)
        pygame.draw.circle(screen, (0, 0, 0), (int(enemy['x'] + 20), int(enemy['y'] + 20)), 4)

    # UI Dashboard HUD Layers
    score_surf = font_small.render(f"SYSTEM SCORE // {score:06d}", True, (255, 255, 255))
    screen.blit(score_surf, (20, 20))
    
    # Shield HUD Draw Meter
    pygame.draw.rect(screen, (40, 40, 60), (SCREEN_WIDTH - 170, 20, 150, 16), border_radius=4)
    if player_health > 0:
        health_color = (0, 255, 150) if player_health > 40 else (255, 50, 50)
        pygame.draw.rect(screen, health_color, (SCREEN_WIDTH - 168, 22, int(146 * (player_health / 100)), 12), border_radius=2)
    hp_lbl = font_small.render("SHIELDS", True, (255, 255, 255))
    screen.blit(hp_lbl, (SCREEN_WIDTH - 250, 20))

    # Game Over Conditions check
    if player_health <= 0:
        game_over_surf = font_large.render("SYSTEM CRITICAL: GAME OVER", True, (255, 50, 100))
        screen.blit(game_over_surf, (SCREEN_WIDTH//2 - game_over_surf.get_width()//2, SCREEN_HEIGHT//2))
        pygame.display.flip()
        time.sleep(3)
        running = False

    pygame.display.flip()

pygame.quit()

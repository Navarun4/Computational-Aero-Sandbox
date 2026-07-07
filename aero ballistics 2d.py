import sys
import math
import pygame

# Initialize Pygame
pygame.init()

# --- STREAMLINED WINDOW SETUP ---
WIDTH, HEIGHT = 800, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aerodynamic Sandbox: Free Kick Simulator")
clock = pygame.time.Clock()

# --- PHYSICS CONFIGURATION (Scale: 110 pixels = 1 meter) ---
SCALE = 110
GRAVITY = 9.81 * SCALE
AIR_DENSITY = 1.225
DRAG_COEFF = 0.45      
MAGNUS_COEFF = 0.30    

# --- COLORS ---
BG_COLOR = (10, 15, 30)
PITCH_COLOR = (16, 140, 90)
BALL_BASE = (245, 245, 245)
TRIONDA_RED = (235, 40, 60)
TRIONDA_BLUE = (40, 100, 220)
TRIONDA_GREEN = (30, 180, 100)
TRAIL_COLOR = (0, 200, 255)
GOAL_COLOR = (240, 240, 240)
HUD_BG = (15, 23, 42, 220) 
TEXT_COLOR = (226, 232, 240)
GOAL_TEXT_COLOR = (34, 197, 94)

# --- GOALPOST VECTOR STRUCTURE ---
GOAL_X = 710
GOAL_TOP_Y = 230    # Crossbar height coordinate
GOAL_BOTTOM_Y = 390 # Pitch floor coordinate
GOAL_WIDTH = 60

# --- INITIAL PHYSICS STATE ---
ball_x = 80.0
ball_y = 380.0
ball_radius = 12  
ball_mass = 0.43  

ball_vx = 0.0
ball_vy = 0.0
ball_angular_velocity = 0.0
ball_angle = 0.0  

force_drag = 0.0
force_magnus = 0.0
has_scored = False

trail = []
font = pygame.font.SysFont("monospace", 12, bold=True)
goal_font = pygame.font.SysFont("arial", 42, bold=True)

def launch_ball(speed_ms, launch_angle_deg, spin_rad_s):
    global ball_x, ball_y, ball_vx, ball_vy, ball_angular_velocity, ball_angle, trail, has_scored
    ball_x = 80.0
    ball_y = 380.0
    has_scored = False
    
    angle_rad = math.radians(launch_angle_deg)
    ball_vx = speed_ms * math.cos(angle_rad) * SCALE
    ball_vy = -speed_ms * math.sin(angle_rad) * SCALE 
    
    ball_angular_velocity = spin_rad_s
    ball_angle = 0.0
    trail = []

# TUNED INITIAL LAUNCH: Curving strike straight into the netting matrix
launch_ball(21, 18, -25.0) 

running = True
while running:
    dt = clock.tick(60) / 1000.0
    if dt > 0.1: dt = 0.1

    # --- 1. KEYBOARD INPUT SELECTIONS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                # TUNED KNUCKLEBALL: High velocity, completely flat, pure drag drop
                launch_ball(26, 12, 0.0)    
            elif event.key == pygame.K_2:
                # TUNED INSIDE CURVE: Whipped over the wall, then aggressively dips down
                launch_ball(21, 18, -25.0)  
            elif event.key == pygame.K_3:
                # TUNED OUTSIDE TRIVELA: Lower angle, unique reverse spin dip
                launch_ball(19, 14, 20.0)   

    # --- 2. FORCES & VECTOR MATH ENGINE ---
    speed = math.sqrt(ball_vx**2 + ball_vy**2) / SCALE
    
    if speed > 0.1:
        ux = (ball_vx / SCALE) / speed
        uy = (ball_vy / SCALE) / speed

        # Drag Calculation
        area = math.pi * ((ball_radius / SCALE) ** 2)
        force_drag = 0.5 * AIR_DENSITY * (speed ** 2) * DRAG_COEFF * area * SCALE
        fx_drag = -force_drag * ux
        fy_drag = -force_drag * uy

        # Magnus Effect Vector Mechanics
        force_magnus = MAGNUS_COEFF * AIR_DENSITY * speed * ball_angular_velocity * area * SCALE
        fx_magnus = -force_magnus * uy
        fy_magnus = force_magnus * ux

        # Net Acceleration Calculation (F=ma)
        # FIXED: Inverted Magnus vertical sign (-fy_magnus) to force down-dip
        ax = (fx_drag + fx_magnus) / ball_mass
        ay = (fy_drag - fy_magnus) / ball_mass + GRAVITY

        ball_vx += ax * dt
        ball_vy += ay * dt
        ball_angle += ball_angular_velocity * dt
    else:
        ball_vy += GRAVITY * dt
        force_drag = 0.0
        force_magnus = 0.0

    # Coordinate position updating
    ball_x += ball_vx * dt
    ball_y += ball_vy * dt

    # Capture movement trail positions
    trail.append((int(ball_x), int(ball_y)))
    if len(trail) > 40:
        trail.pop(0)

    # Ground Bounce Engine Mechanics
    if ball_y + ball_radius > 390:
        ball_y = 390 - ball_radius
        ball_vy = -ball_vy * 0.35  
        ball_vx *= 0.75
        ball_angular_velocity *= 0.4

    # --- BOUNDING BOX GOAL DETECTION PLANE ---
    if not has_scored:
        if GOAL_X < ball_x < (GOAL_X + GOAL_WIDTH):
            if GOAL_TOP_Y < ball_y < GOAL_BOTTOM_Y:
                has_scored = True

    # --- 3. RENDERING ENGINE LAYERS ---
    screen.fill(BG_COLOR)

    # Draw Pitch Turf
    pygame.draw.rect(screen, PITCH_COLOR, (0, 390, WIDTH, 60))
    pygame.draw.line(screen, (255, 255, 255), (0, 390), (WIDTH, 390), 2)

    # Goal Net Grid Generation
    net_surf = pygame.Surface((GOAL_WIDTH, GOAL_BOTTOM_Y - GOAL_TOP_Y), pygame.SRCALPHA)
    for ny in range(0, GOAL_BOTTOM_Y - GOAL_TOP_Y, 8):
        pygame.draw.line(net_surf, (71, 85, 105, 120), (0, ny), (GOAL_WIDTH, ny), 1)
    for nx in range(0, GOAL_WIDTH, 8):
        pygame.draw.line(net_surf, (71, 85, 105, 120), (nx, 0), (nx, GOAL_BOTTOM_Y - GOAL_TOP_Y), 1)
    screen.blit(net_surf, (GOAL_X, GOAL_TOP_Y))

    # Goalpost White Boundary Lines
    pygame.draw.line(screen, GOAL_COLOR, (GOAL_X, GOAL_TOP_Y), (GOAL_X, GOAL_BOTTOM_Y), 4) # Goalpost
    pygame.draw.line(screen, GOAL_COLOR, (GOAL_X, GOAL_TOP_Y), (GOAL_X + GOAL_WIDTH, GOAL_TOP_Y), 4) # Crossbar

    # Trajectory Visualization Stream
    if len(trail) > 1:
        for i in range(len(trail) - 1):
            alpha = int(255 * (i / len(trail)))
            color_blend = (max(0, 59-alpha//4), min(255, 130+alpha//2), 255)
            pygame.draw.line(screen, color_blend, trail[i], trail[i+1], max(1, i // 10))

    # Rotational Ball Transformation Matrix
    ball_surf = pygame.Surface((ball_radius * 2, ball_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(ball_surf, BALL_BASE, (ball_radius, ball_radius), ball_radius)
    pygame.draw.arc(ball_surf, TRIONDA_RED, (1, 1, ball_radius*2-2, ball_radius*2-2), 0, math.pi*0.6, 2)
    pygame.draw.arc(ball_surf, TRIONDA_GREEN, (2, 2, ball_radius*2-4, ball_radius*2-4), math.pi*0.7, math.pi*1.4, 2)
    pygame.draw.arc(ball_surf, TRIONDA_BLUE, (1, 1, ball_radius*2-2, ball_radius*2-2), math.pi*1.5, math.pi*1.9, 2)
    
    rotated_ball = pygame.transform.rotate(ball_surf, math.degrees(ball_angle))
    new_rect = rotated_ball.get_rect(center=(int(ball_x), int(ball_y)))
    screen.blit(rotated_ball, new_rect.topleft)

    # Stats Summary Dashboard Panel
    hud_surface = pygame.Surface((290, 130), pygame.SRCALPHA)
    hud_surface.fill(HUD_BG)
    screen.blit(hud_surface, (15, 15))
    pygame.draw.rect(screen, (51, 65, 85), (15, 15, 290, 130), 1)

    metrics = [
        "AERODYNAMICS RADAR HUD",
        "--------------------------------",
        f"Velocity : [{round(ball_vx/SCALE, 1)}, {round(-ball_vy/SCALE, 1)}] m/s",
        f"Air Speed: {round(speed, 1)} m/s ({round(speed * 3.6, 1)} km/h)",
        f"Spin Rate: {round(ball_angular_velocity, 1)} rad/s",
        f"Drag Force: {round(force_drag / SCALE, 3)} N",
        "--------------------------------",
        "Kicks: [1] Knuckle [2] Curve [3] Trivela"
    ]
    
    for idx, text_line in enumerate(metrics):
        rendered_text = font.render(text_line, True, TEXT_COLOR)
        screen.blit(rendered_text, (25, 22 + idx * 13))

    # Trigger UI overlay text check
    if has_scored:
        goal_surface = goal_font.render("GOAL!!!", True, GOAL_TEXT_COLOR)
        screen.blit(goal_surface, (WIDTH // 2 - 60, HEIGHT // 2 - 60))

    pygame.display.flip()

pygame.quit()
sys.exit()
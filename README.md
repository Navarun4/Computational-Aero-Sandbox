


1. 3D Cyberpunk Physics Engine (projectile_sim.py)
A continuous numerical solver for ballistics.

Physics: Computes gravitational pull (g) integrated with aerodynamic drag coefficients (C_d).

Functionality: Real-time telemetry sliders for velocity, pitch, and yaw.

Utility: Scalable to drone path planning and high-resistance trajectory modeling.
![Physics Engine](physics.png)



2. AeroBallistics-2D

A real-time 2D physics engine simulating projectile trajectories under the influence of air resistance, gravity, and spin curve mechanics.

 The Science Behind the Engine

The engine calculates forces frame-by-frame based on real-world fluid dynamics scale where 110 pixels equals 1 meter.

1. Aerodynamic Drag
This accounts for air resistance pushing against the ball as it travels forward. It uses standard air density (1.225 kg/m3) and a realistic sphere drag coefficient (0.45) to slow the ball down naturally over time.

2. Magnus Effect (Spin Curve)
This generates a lift or dipping force perpendicular to the direction of travel based on how fast the ball is spinning. The rotational spin rate drives both the visual roll of the ball and its physics path.

---

 Presets Built into the Code

* Press [1] Knuckleball: High velocity, zero spin, pure drag drop.
* Press [2] Inside Curve: Top and side-spin blend creating an aggressive late dip into the net.
* Press [3] Trivela: Reverse spin mechanics causing an opposite aerodynamic break.

 Tech Stack
* Language: Python 3
* Library: Pygame

![Aero ballistics 2D](ballistics.png)

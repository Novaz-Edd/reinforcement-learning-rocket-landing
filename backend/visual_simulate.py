"""
Advanced rocket landing simulation with particle effects, physics interpolation, and HUD.

Features:
- Smooth animation with frame interpolation
- Thrust flame particle effects
- Particle trail system behind rocket
- Camera follow system
- Real-time HUD overlay (height, velocity, fuel, action status)
- Landing/crash feedback
- Ground interaction effects
- 30 FPS target framerate
"""

import sys
import os
import math
import numpy as np
import torch
import pygame
from collections import deque

# Import from same directory (backend/)
from env import RocketEnv
from agent import PPOAgent


# ─────────────────────────────────────────────────────────────────────────────
# PARTICLE SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

class Particle:
    """Single particle with position, velocity, lifetime."""
    
    def __init__(self, x, y, vx, vy, life_time, size=3, color=(255, 165, 0)):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.max_life = life_time
        self.life = life_time
        self.size = size
        self.color = color
    
    def update(self, dt):
        """Update particle position and lifetime."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        self.vy += 9.8 * dt  # gravity
    
    def is_alive(self):
        """Check if particle should still be rendered."""
        return self.life > 0
    
    def get_alpha(self):
        """Return fade factor (0-1) based on remaining life."""
        return max(0, min(1, self.life / self.max_life))
    
    def draw(self, surface, screen_y_offset=0):
        """Draw particle with fade effect."""
        if not self.is_alive():
            return
        
        alpha = self.get_alpha()
        size = int(self.size * alpha)
        if size > 0:
            # Create temporary surface for alpha blending
            temp_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, int(200 * alpha))
            pygame.draw.circle(temp_surf, color_with_alpha, (size, size), size)
            screen_y = int(self.y - screen_y_offset)
            surface.blit(temp_surf, (int(self.x) - size, screen_y - size))


class ParticleSystem:
    """Manages all active particles."""
    
    def __init__(self, max_particles=500):
        self.particles = deque(maxlen=max_particles)
    
    def emit_flame(self, x, y, count=8, intensity=1.0):
        """Emit particles downward (thrust flame)."""
        for _ in range(count):
            angle = np.random.uniform(-0.4, 0.4)  # spread cone below rocket
            speed = np.random.uniform(20, 50) * intensity
            vx = speed * math.sin(angle)
            vy = speed * math.cos(angle)  # downward
            
            life = np.random.uniform(0.2, 0.5)
            color = (
                np.random.randint(200, 256),
                np.random.randint(100, 200),
                np.random.randint(0, 100)
            )
            self.particles.append(Particle(x, y, vx, vy, life, size=4, color=color))
    
    def emit_trail(self, x, y, count=2, color=(100, 150, 255)):
        """Emit trailing particles behind rocket (velocity-dependent)."""
        for _ in range(count):
            angle = np.random.uniform(-0.5, 0.5)
            speed = np.random.uniform(2, 6)
            vx = speed * math.sin(angle)
            vy = speed * math.cos(angle)
            
            life = np.random.uniform(0.3, 0.6)
            self.particles.append(Particle(x, y, vx, vy, life, size=2, color=color))
    
    def emit_dust(self, x, y, count=15):
        """Emit dust particles on landing."""
        for _ in range(count):
            angle = np.random.uniform(0, 2 * math.pi)
            speed = np.random.uniform(5, 20)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            
            life = np.random.uniform(0.4, 0.8)
            color = (180, 160, 120)
            self.particles.append(Particle(x, y, vx, vy, life, size=3, color=color))
    
    def update(self, dt):
        """Update all particles."""
        dead_count = 0
        for particle in self.particles:
            particle.update(dt)
            if not particle.is_alive():
                dead_count += 1
        
        # Remove dead particles
        for _ in range(dead_count):
            if len(self.particles) > 0:
                self.particles.popleft()
    
    def draw(self, surface, screen_y_offset=0):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface, screen_y_offset)


# ─────────────────────────────────────────────────────────────────────────────
# GRAPHICS & RENDERING
# ─────────────────────────────────────────────────────────────────────────────

class RocketRenderer:
    """Handles all rendering logic."""
    
    # Color scheme
    COLOR_SKY = (135, 206, 235)  # light blue
    COLOR_WATER = (30, 100, 150)  # dark blue
    COLOR_GROUND = (100, 100, 80)  # brown
    COLOR_PLATFORM = (60, 60, 60)  # dark gray
    COLOR_ROCKET = (200, 200, 200)  # silver
    COLOR_ROCKET_LANDED = (100, 200, 100)  # green
    COLOR_ROCKET_CRASH = (255, 100, 100)  # red
    COLOR_FLAME = (255, 150, 50)  # orange
    COLOR_TEXT = (255, 255, 255)  # white
    COLOR_HUD_BG = (0, 0, 0)  # black
    
    def __init__(self, width=1200, height=800, env_y_max=100):
        self.width = width
        self.height = height
        self.env_y_max = env_y_max
        
        pygame.init()
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Rocket Landing Simulator - PPO Agent")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Physics interpolation
        self.prev_y = 50.0
        self.prev_vy = -5.0
        self.frame_time = 0.0
        self.dt = 0.016  # ~60 FPS internal
        
        # Particle system
        self.particles = ParticleSystem()
        self.flame_intensity = 0.0
        
        # Camera
        self.camera_y = self.height // 2
        self.camera_target_y = self.height // 2
        
        # Game state
        self.status = None  # 'landed', 'crashed', None
        self.flash_timer = 0.0
        self.flash_interval = 0.1
    
    def world_to_screen_y(self, world_y):
        """Convert world Y coordinate to screen Y."""
        # World: 0 at bottom (ground), 100 at top
        # Screen: 0 at top
        sky_height = self.height * 0.3
        normalized = (world_y / self.env_y_max)
        return sky_height + (1.0 - normalized) * (self.height - sky_height)
    
    def draw_background(self):
        """Draw sky and water."""
        # Sky gradient
        sky_height = int(self.height * 0.3)
        pygame.draw.rect(self.surface, self.COLOR_SKY, (0, 0, self.width, sky_height))
        
        # Water
        water_height = self.height - sky_height
        pygame.draw.rect(self.surface, self.COLOR_WATER, (0, sky_height, self.width, water_height))
        
        # Horizon line
        pygame.draw.line(self.surface, (100, 100, 100), (0, sky_height), (self.width, sky_height), 2)
    
    def draw_ground_and_platform(self):
        """Draw landing platform and ground."""
        ground_y = self.world_to_screen_y(0)
        
        # Platform (20 units wide = 200 pixels at this scale)
        platform_width = 200
        platform_x = (self.width - platform_width) // 2
        pygame.draw.rect(self.surface, self.COLOR_PLATFORM, 
                        (platform_x, ground_y, platform_width, 15))
        
        # Platform outline
        pygame.draw.rect(self.surface, (150, 150, 150), 
                        (platform_x, ground_y, platform_width, 15), 2)
        
        # Ground beneath
        pygame.draw.rect(self.surface, self.COLOR_GROUND, 
                        (0, ground_y + 15, self.width, self.height - ground_y))
    
    def draw_rocket(self, world_y, flashing=False):
        """Draw rocket sprite."""
        screen_y = self.world_to_screen_y(world_y)
        rocket_x = self.width // 2
        
        # Determine rocket color
        if flashing and self.status == 'crashed':
            # Flash red on crash
            color = self.COLOR_ROCKET_CRASH if int(self.flash_timer / self.flash_interval) % 2 == 0 else self.COLOR_ROCKET
        elif self.status == 'landed':
            color = self.COLOR_ROCKET_LANDED
        else:
            color = self.COLOR_ROCKET
        
        # Rocket body (rectangle with tapered top)
        rocket_width = 20
        rocket_height = 40
        
        # Body
        pygame.draw.rect(self.surface, color, 
                        (rocket_x - rocket_width//2, screen_y - rocket_height//2, 
                         rocket_width, rocket_height))
        
        # Nose cone (triangle)
        nose_points = [
            (rocket_x, screen_y - rocket_height//2 - 10),
            (rocket_x - rocket_width//2, screen_y - rocket_height//2),
            (rocket_x + rocket_width//2, screen_y - rocket_height//2)
        ]
        pygame.draw.polygon(self.surface, (255, 200, 0), nose_points)
        
        # Window
        window_radius = 3
        pygame.draw.circle(self.surface, (100, 150, 255), (rocket_x, screen_y - 5), window_radius)
        
        # Landing legs (small)
        leg_length = 8
        leg_offset = 10
        pygame.draw.line(self.surface, color, 
                        (rocket_x - leg_offset, screen_y + rocket_height//2),
                        (rocket_x - leg_offset - 3, screen_y + rocket_height//2 + leg_length), 2)
        pygame.draw.line(self.surface, color,
                        (rocket_x + leg_offset, screen_y + rocket_height//2),
                        (rocket_x + leg_offset + 3, screen_y + rocket_height//2 + leg_length), 2)
        
        return screen_y, rocket_x
    
    def draw_thrust_flame(self, rocket_x, rocket_y):
        """Draw main thrust flame."""
        if self.flame_intensity < 0.01:
            return
        
        flame_width = int(15 * self.flame_intensity)
        flame_height = int(30 * self.flame_intensity)
        
        # Triangle flame
        flame_points = [
            (rocket_x, rocket_y + 25),  # base center
            (rocket_x - flame_width, rocket_y + 25 + flame_height),  # bottom left
            (rocket_x + flame_width, rocket_y + 25 + flame_height),  # bottom right
        ]
        pygame.draw.polygon(self.surface, self.COLOR_FLAME, flame_points)
        
        # Inner brighter flame
        if self.flame_intensity > 0.3:
            inner_width = int(flame_width * 0.6)
            inner_height = int(flame_height * 0.8)
            inner_flame = [
                (rocket_x, rocket_y + 25 + inner_height * 0.2),
                (rocket_x - inner_width, rocket_y + 25 + inner_height * 0.8),
                (rocket_x + inner_width, rocket_y + 25 + inner_height * 0.8),
            ]
            pygame.draw.polygon(self.surface, (255, 255, 100), inner_flame)
    
    def draw_hud(self, height, velocity, fuel, action, landed, crashed):
        """Draw heads-up display overlay."""
        hud_x = 20
        hud_y = 20
        line_height = 35
        
        # HUD background panel
        panel_width = 280
        panel_height = 170
        panel_rect = pygame.Rect(hud_x, hud_y, panel_width, panel_height)
        pygame.draw.rect(self.surface, self.COLOR_HUD_BG, panel_rect)
        pygame.draw.rect(self.surface, (0, 255, 0), panel_rect, 2)  # green border
        
        text_x = hud_x + 15
        text_y = hud_y + 10
        
        # Height
        height_text = self.font_small.render(f"Height: {height:.1f} m", True, self.COLOR_TEXT)
        self.surface.blit(height_text, (text_x, text_y))
        text_y += line_height
        
        # Velocity
        vel_color = self.COLOR_TEXT
        if abs(velocity) > 5:
            vel_color = (255, 150, 100)  # orange warning
        vel_text = self.font_small.render(f"Velocity: {velocity:.1f} m/s", True, vel_color)
        self.surface.blit(vel_text, (text_x, text_y))
        text_y += line_height
        
        # Fuel
        fuel_color = self.COLOR_TEXT
        if fuel < 20:
            fuel_color = (255, 100, 100)  # red warning
        fuel_text = self.font_small.render(f"Fuel: {fuel:.0f} / 100", True, fuel_color)
        self.surface.blit(fuel_text, (text_x, text_y))
        text_y += line_height
        
        # Action status
        action_text = "THRUST" if action == 1 else "IDLE"
        action_color = (255, 150, 50) if action == 1 else (100, 100, 100)
        action_display = self.font_small.render(f"Action: {action_text}", True, action_color)
        self.surface.blit(action_display, (text_x, text_y))
    
    def draw_status_message(self, message, color, y_offset=None):
        """Draw large status message."""
        if y_offset is None:
            y_offset = self.height // 3
        
        text = self.font_large.render(message, True, color)
        text_rect = text.get_rect(center=(self.width // 2, y_offset))
        
        # Background for readability
        bg_rect = text_rect.inflate(40, 20)
        pygame.draw.rect(self.surface, (0, 0, 0), bg_rect)
        pygame.draw.rect(self.surface, color, bg_rect, 3)
        
        self.surface.blit(text, text_rect)
    
    def update_physics(self, world_y, world_vy, action, dt):
        """Update interpolation variables."""
        self.prev_y = world_y
        self.prev_vy = world_vy
        self.frame_time += dt
        
        # Update thrust flame intensity
        target_intensity = 1.0 if action == 1 else 0.0
        self.flame_intensity += (target_intensity - self.flame_intensity) * 0.2
        
        # Emit particles
        if action == 1:
            self.particles.emit_flame(self.width // 2, self.world_to_screen_y(world_y), 
                                     count=int(6 * self.flame_intensity), intensity=self.flame_intensity)
        
        # Trail particles (always, but fade based on speed)
        trail_intensity = min(1.0, abs(world_vy) / 10.0)
        if trail_intensity > 0.1:
            self.particles.emit_trail(self.width // 2, self.world_to_screen_y(world_y), 
                                     count=max(1, int(3 * trail_intensity)))
    
    def update_particles(self, dt):
        """Update all particles."""
        self.particles.update(dt)
    
    def emit_landing_dust(self, world_y):
        """Emit dust particles on landing."""
        screen_y = self.world_to_screen_y(world_y)
        self.particles.emit_dust(self.width // 2, screen_y)
    
    def update_status(self, landed, crashed, dt):
        """Update game status and flashing effects."""
        if landed:
            self.status = 'landed'
        elif crashed:
            self.status = 'crashed'
            self.flash_timer += dt
        
        return self.status
    
    def render_frame(self, world_y, world_vy, action, height, velocity, fuel, 
                    landed, crashed, done):
        """Render complete frame."""
        dt = 0.016  # 60 FPS
        
        # Update physics and particles
        self.update_physics(world_y, world_vy, action, dt)
        self.update_particles(dt)
        self.update_status(landed, crashed, dt)
        
        # Clear screen
        self.draw_background()
        self.draw_ground_and_platform()
        
        # Draw particles (behind rocket)
        self.particles.draw(self.surface)
        
        # Draw rocket and flame
        screen_y, rocket_x = self.draw_rocket(world_y, flashing=(self.status == 'crashed' and done))
        self.draw_thrust_flame(rocket_x, screen_y)
        
        # Draw HUD
        self.draw_hud(height, velocity, fuel, action, landed, crashed)
        
        # Draw status messages
        if done and landed:
            self.draw_status_message("✅ SUCCESSFUL LANDING", (100, 255, 100))
        elif done and crashed:
            self.draw_status_message("💥 CRASH", (255, 100, 100))
        
        # Update display
        pygame.display.flip()
        self.clock.tick(30)  # 30 FPS target


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

def get_deterministic_action(agent, obs):
    """Get action using deterministic policy (argmax)."""
    obs_t = torch.FloatTensor(obs).unsqueeze(0)
    with torch.no_grad():
        logits, value = agent.net(obs_t)
    action = torch.argmax(logits, dim=1).item()
    
    # Map 4-action model to 2-action environment
    if action >= 2:
        action = 1
    
    return action


def run_visual_simulation(model_path="models/ppo_ep2400.pt"):
    """Run interactive rocket landing simulation."""
    print("=" * 70)
    print("ROCKET LANDING SIMULATOR - Visual Edition")
    print("=" * 70)
    print(f"Loading model from: {model_path}")
    
    # Initialize
    env = RocketEnv()
    agent = PPOAgent(obs_dim=5, action_dim=4, hidden=128)
    agent.load(model_path)
    agent.net.eval()
    
    renderer = RocketRenderer(width=1200, height=800, env_y_max=env.Y_MAX)
    
    print("Starting episode...")
    print("Press ESC to quit\n")
    
    obs = env.reset()
    done = False
    episode_return = 0.0
    step = 0
    
    while not done:
        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
        
        # Get deterministic action
        action = get_deterministic_action(agent, obs)
        
        # Step environment
        obs, reward, done, info = env.step(action)
        episode_return += reward
        step += 1
        
        # Render frame
        renderer.render_frame(
            world_y=info["y"],
            world_vy=info["vy"],
            action=action,
            height=info["y"],
            velocity=info["vy"],
            fuel=info["fuel"],
            landed=info["landed"],
            crashed=info["crashed"],
            done=done
        )
        
        # Emit landing dust if just landed
        if done and (env.landed or env.crashed):
            renderer.emit_landing_dust(info["y"])
            # Show result for a moment
            for _ in range(150):  # Show for ~5 seconds at 30 FPS
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            return
                
                renderer.update_particles(0.016)
                renderer.render_frame(
                    world_y=info["y"],
                    world_vy=0,
                    action=0,
                    height=info["y"],
                    velocity=0,
                    fuel=info["fuel"],
                    landed=env.landed,
                    crashed=env.crashed,
                    done=done
                )
    
    # Print summary
    print("\n" + "=" * 70)
    print("EPISODE COMPLETE")
    print("=" * 70)
    
    if env.landed:
        print(f"Status: ✅ SUCCESSFUL LANDING")
    elif env.crashed:
        print(f"Status: ✗ CRASH")
    else:
        print(f"Status: ⏱ TIMEOUT")
    
    final_vy = abs(env.landing_vy) if env.landing_vy is not None else abs(env.vy)
    print(f"Final landing velocity: {final_vy:.2f} m/s")
    print(f"Total timesteps: {env.step_count}")
    print(f"Fuel remaining: {env.fuel:.1f} / {env.FUEL_MAX:.1f}")
    print(f"Episode return: {episode_return:.2f}")
    print()
    
    pygame.quit()


if __name__ == "__main__":
    run_visual_simulation("models/ppo_ep2400.pt")

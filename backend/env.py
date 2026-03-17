import numpy as np


class RocketEnv:
    """2D Rocket Landing Environment with detailed physics and reward shaping."""
    
    # Physics constants
    GRAVITY = -9.8
    THRUST = 30.0
    FUEL_MAX = 100.0
    FUEL_BURN_RATE = 0.5
    DT = 0.05
    MAX_STEPS = 600
    LAND_VELOCITY = 3.0
    
    # World bounds
    Y_MIN = 0.0
    Y_MAX = 100.0
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset environment and return initial observation."""
        # Spawn rocket between y=60-90, always falling
        self.y = np.random.uniform(60.0, 90.0)
        self.vy = np.random.uniform(-6.0, -1.0)  # Always falling
        self.fuel = self.FUEL_MAX
        self.step_count = 0
        self.landed = False
        self.crashed = False
        self.prev_y = self.y
        
        return self._get_obs()
    
    def _get_obs(self):
        """Get normalized state space [y_norm, vy_norm, fuel_norm, time_to_ground_norm, danger_signal]."""
        # y_norm: normalized height in [-1, 1]
        y_norm = (self.y / self.Y_MAX) * 2 - 1
        
        # vy_norm: velocity normalized and clipped
        vy_norm = np.clip(self.vy / 30.0, -1, 1)
        
        # fuel_norm: fuel normalized in [-1, 1]
        fuel_norm = (self.fuel / self.FUEL_MAX) * 2 - 1
        
        # time_to_ground_norm: estimated time to hit ground
        if abs(self.vy) > 0.1:
            time_to_ground = abs(self.y / self.vy)
        else:
            time_to_ground = 1.0
        time_to_ground_norm = np.clip(time_to_ground / 10.0, 0, 1) * 2 - 1
        
        # danger_signal: proximity-weighted velocity danger
        danger_signal = np.clip(abs(self.vy) / (self.y + 1) / 2.0, 0, 1)
        
        return np.array([y_norm, vy_norm, fuel_norm, time_to_ground_norm, danger_signal], dtype=np.float32)
    
    def step(self, action):
        """
        Execute one step of the environment.
        
        action: 0=nothing, 1=fire engine
        returns: (obs, reward, done, info)
        """
        self.step_count += 1
        self.prev_y = self.y
        
        # Apply thrust if action == 1 and fuel available
        ay = self.GRAVITY
        fuel_used = 0.0
        
        if action == 1 and self.fuel > 0:
            ay += self.THRUST / 1.0  # Assuming mass = 1
            fuel_used = self.FUEL_BURN_RATE
            self.fuel = max(0, self.fuel - fuel_used)
        
        # Physics update
        self.vy += ay * self.DT
        self.y += self.vy * self.DT
        
        # Check if rocket went above Y_MAX, redirect downward
        if self.y > self.Y_MAX:
            self.y = self.Y_MAX
            self.vy = max(self.vy, -1.0)  # Ensure falling
        
        # Check landing or crash conditions
        done = False
        landed = False
        crashed = False
        
        if self.y <= self.Y_MIN:
            # Rocket touched ground
            done = True
            self.y = self.Y_MIN
            
            if abs(self.vy) <= self.LAND_VELOCITY:
                # Successful landing
                landed = True
                self.landed = True
            else:
                # Hard crash
                crashed = True
                self.crashed = True
        
        if self.step_count >= self.MAX_STEPS:
            done = True
            crashed = True
            self.crashed = True
        
        # Compute reward
        reward = self._compute_reward(fuel_used, landed, crashed)
        
        obs = self._get_obs()
        
        info = {
            "landed": landed,
            "crashed": crashed,
            "vy": self.vy,
            "y": self.y,
            "fuel": self.fuel,
        }
        
        return obs, reward, done, info
    
    def _compute_reward(self, fuel_used, landed, crashed):
        """Compute shaped reward."""
        reward = 0.0
        
        if landed:
            # Successful landing: base reward + gentleness bonus
            gentleness = max(0, 1 - abs(self.vy) / self.LAND_VELOCITY)
            reward = 100.0 + gentleness * 100.0
        elif crashed:
            # Crash penalty
            reward = -80.0
        else:
            # Normal step rewards
            
            # Progress reward: descending is good
            progress = (self.prev_y - self.y) * 0.05
            reward += progress
            
            # Height reward: lower is good
            height_reward = (1 - self.y / self.Y_MAX) * 0.1
            reward += height_reward
            
            # Velocity penalty: high speed is bad, especially near ground
            proximity = 1 - self.y / self.Y_MAX
            velocity_penalty = -abs(self.vy) * 0.02 * (1 + proximity * 4)
            reward += velocity_penalty
            
            # Fuel penalty
            fuel_penalty = -fuel_used * 0.003
            reward += fuel_penalty
        
        return reward
    
    def render(self):
        """Render rocket position as text bar."""
        bar_height = 20
        bar_width = 50
        
        # Normalize position for bar
        pos = int((self.y / self.Y_MAX) * bar_height)
        pos = max(0, min(bar_height - 1, pos))
        
        bar = [' '] * bar_height
        bar[bar_height - 1 - pos] = '🚀'
        
        print(f"y={self.y:6.2f} vy={self.vy:+6.2f} fuel={self.fuel:6.1f} | {''.join(bar)}")
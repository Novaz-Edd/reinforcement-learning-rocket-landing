import numpy as np


class RocketEnv:
    """2D Rocket Landing Environment - landing is the ONLY positive reward source."""
    
    # Physics constants
    GRAVITY = -9.8
    THRUST = 20.0  # Just enough to slow descent, not to fly upward
    FUEL_MAX = 100.0
    FUEL_BURN_RATE = 1.0
    DT = 0.05
    MAX_STEPS = 400
    LAND_VELOCITY = 4.0
    
    # World bounds
    Y_MIN = 0.0
    Y_MAX = 100.0
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset environment and return initial observation."""
        # Spawn rocket between y=50-80, always falling downward
        self.y = np.random.uniform(50.0, 80.0)
        self.vy = np.random.uniform(-8.0, -3.0)  # Always falling
        self.fuel = self.FUEL_MAX
        self.step_count = 0
        self.landed = False
        self.crashed = False
        self.landing_vy = None  # Velocity at which we landed (if we do)
        
        return self._get_obs()
    
    def _get_obs(self):
        """Get normalized state space (5 values)."""
        # 1. y_norm: normalized height [0, 1]
        y_norm = self.y / self.Y_MAX
        
        # 2. vy_norm: velocity normalized and clipped [-1, 1]
        vy_norm = np.clip(self.vy / 20.0, -1.0, 1.0)
        
        # 3. fuel_norm: fuel [0, 1]
        fuel_norm = self.fuel / self.FUEL_MAX
        
        # 4. time_to_impact: estimated time to ground [0, 1]
        # How many time units until we hit ground at current velocity?
        time_to_impact = np.clip(abs(self.y / (self.vy - 0.001)) / 5.0, 0.0, 1.0)
        
        # 5. throttle_needed: how much throttle to slow down [0, 1]
        # Direct action hint: what acceleration is needed?
        throttle_needed = np.clip(-self.vy / 10.0, 0.0, 1.0)
        
        return np.array([y_norm, vy_norm, fuel_norm, time_to_impact, throttle_needed], dtype=np.float32)
    
    def step(self, action):
        """
        Execute one step of the environment.
        
        action: 0=nothing, 1=fire engine (ONLY 2 actions)
        returns: (obs, reward, done, info)
        
        Physics: net_accel = GRAVITY + (THRUST if action==1 else 0)
                = -9.8 + (20.0 or 0) = 10.2 or -9.8
        This allows slowing descent but NOT flying upward.
        """
        self.step_count += 1
        
        # Apply thrust if action == 1 and fuel available
        ay = self.GRAVITY
        fuel_used = 0.0
        
        if action == 1 and self.fuel > 0:
            ay += self.THRUST  # net accel = 20 - 9.8 = +10.2 (still downward deceleration)
            fuel_used = self.FUEL_BURN_RATE
            self.fuel = max(0, self.fuel - fuel_used)
        
        # Physics update
        self.vy += ay * self.DT
        self.y += self.vy * self.DT
        
        # Boundary: if above Y_MAX, bounce back down
        if self.y > self.Y_MAX:
            self.y = self.Y_MAX
            self.vy = -abs(self.vy)  # Ensure falling
        
        # Check landing or crash conditions
        done = False
        landed = False
        crashed = False
        
        if self.y <= self.Y_MIN:
            # Rocket touched ground
            done = True
            self.y = self.Y_MIN
            self.landing_vy = abs(self.vy)
            
            if abs(self.vy) <= self.LAND_VELOCITY:
                # Successful landing!
                landed = True
                self.landed = True
            else:
                # Hard crash
                crashed = True
                self.crashed = True
        
        # Timeout: ran out of time steps
        if self.step_count >= self.MAX_STEPS:
            done = True
            crashed = True
            self.crashed = True
        
        # Compute reward (SIMPLE: no shaping that can be gamed)
        reward = self._compute_reward(landed, crashed)
        
        obs = self._get_obs()
        
        info = {
            "landed": landed,
            "crashed": crashed,
            "vy": self.vy,
            "y": self.y,
            "fuel": self.fuel,
        }
        
        return obs, reward, done, info
    
    def _compute_reward(self, landed, crashed):
        """
        Simple reward function - ONLY landing gives positive reward.
        
        No altitude reward (can be gamed by flying up).
        No progress reward (can be gamed by hovering).
        No fuel penalty (too weak to prevent gaming).
        """
        reward = 0.0
        
        # Small time penalty every step (forces efficiency)
        reward -= 0.1
        
        # Gentle velocity penalty (too high and agent learns to fall)
        reward -= abs(self.vy) * 0.01
        
        # LANDING: the ONLY positive reward
        if landed:
            reward += 200.0
        
        # CRASH: significant penalty
        elif crashed:
            reward -= 50.0
        
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
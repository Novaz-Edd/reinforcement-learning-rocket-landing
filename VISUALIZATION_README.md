# Rocket Landing Simulator - Visualization System

A professional-grade rocket landing simulation with PPO reinforcement learning agent, featuring smooth animations, particle effects, HUD overlay, and landing feedback.

## Features

### 1. **Advanced Graphics Rendering**
- 30 FPS smooth animation with frame interpolation
- Professional color palette (sky blue, water, landing platform)
- Detailed rocket sprite with:
  - Silver body with nose cone
  - Window viewport
  - Landing legs
  - Color-coded status (silver→green for success, red for crash)

### 2. **Particle Effects System**
- **Thrust Flames**: Orange/red particles emitted downward when engine fires
  - Dynamic intensity based on acceleration
  - Flickering effect for visual appeal
- **Rocket Trail**: Blue fading particles behind rocket showing velocity
  - Intensity scales with rocket speed
  - Smooth fade-out based on particle lifetime
- **Landing Dust**: Brown particles scattered on landing/crash
  - Spreads in circular pattern
  - 15+ particles with variable lifetime

### 3. **Real-Time HUD Overlay**
Green-bordered information panel displaying:
- **Height**: Current Y position in meters (0-100)
- **Velocity**: Vertical velocity (m/s) with color-coded warnings
  - White: Normal
  - Orange: High velocity (>5 m/s, dangerous)
  - Red: Low fuel (<20)
- **Fuel**: Remaining fuel / Total capacity (0-100)
- **Action**: Current control state (THRUST or IDLE)
  - THRUST shown in orange
  - IDLE shown in gray

### 4. **Landing Feedback**
- **Successful Landing**: 
  - Rocket turns green
  - Large green message "✅ SUCCESSFUL LANDING"
  - 5-second display with particle effects
- **Crash**:
  - Rocket flashes red
  - Large red message "💥 CRASH"
  - Dust particles on impact
  - 5-second display with flashing effect

### 5. **Environment Visualization**
- **Sky**: Gradient blue background
- **Water**: Lower half with darker blue
- **Landing Platform**: 200px wide safe zone with highlighted borders
- **Ground**: Brown area beneath platform
- **Horizon Line**: Visual separation between sky and water

## How to Run

### Option 1: Direct Execution
```bash
cd backend
python visual_simulate.py
```

### Option 2: Using Launcher
```bash
cd backend
python launch_visual.py
```

### Option 3: From Project Root
```bash
python backend/visual_simulate.py
```

## Controls

- **ESC**: Quit simulation at any time
- **Window Close Button**: Quit simulation
- The simulation automatically displays results for 5 seconds after episode completion

## Dependencies

```bash
pip install pygame torch numpy
```

## Configuration

### Model Selection
Edit the model path in `visual_simulate.py`:
```python
run_visual_simulation("models/ppo_ep2400.pt")  # Change to different checkpoint
```

Available models in `models/`:
- `ppo_ep200.pt` - Early training
- `ppo_ep1000.pt` - Mid training
- `ppo_ep2400.pt` - Advanced training (recommended)
- `ppo_ep4500.pt` - Late training

### Display Settings
Modify in `RocketRenderer.__init__()`:
```python
self.width = 1200      # Screen width in pixels
self.height = 800      # Screen height in pixels
self.clock.tick(30)    # Target FPS (30 recommended)
```

### Particle Settings
Adjust particle behavior in `ParticleSystem`:
```python
max_particles=500      # Maximum concurrent particles
count=8               # Thrust flame particles per frame
count=2               # Trail particles per frame
count=15              # Landing dust particles
```

## Technical Details

### Physics Interpolation
The renderer smoothly interpolates rocket position between simulation steps for fluid animation, avoiding visual jittering.

### Particle System
- Uses deque with max capacity for O(1) particle management
- Each particle has position, velocity, lifetime, and opacity
- Gravity applied during particle update for natural motion
- Alpha blending for smooth fade effects

### Performance
- Efficient redraw using pygame display.flip()
- Particle cap prevents performance degradation
- No blocking operations - runs at target FPS consistently
- Suitable for live presentations and video capture

### Rendering Pipeline
1. Draw background (sky/water)
2. Draw ground and platform
3. Draw particles (behind rocket)
4. Draw rocket and flames
5. Draw HUD overlay
6. Display status messages (if episode complete)
7. Update display and maintain framerate

## Agent Configuration

### Deterministic Policy
Uses argmax action selection (no sampling) for reproducible demonstrations:
```python
action = torch.argmax(logits, dim=1).item()
```

### Model Architecture
- Input: 5-dimensional state space (height, velocity, fuel, time-to-impact, throttle-needed)
- Hidden: 128-unit layers with Tanh activation
- Output: 4-action space (mapped to 2 actions in environment)
- Policy: PPO trained agent

### Action Space
- Action 0: No thrust (IDLE)
- Action 1+: Apply maximum thrust (THRUST)

## Output

The simulator produces:
1. **Live Animation**: 30 FPS smooth visualization with all effects
2. **Console Output**: Final statistics after episode
   - Landing status (Success/Crash/Timeout)
   - Final velocity at impact
   - Total timesteps
   - Remaining fuel
   - Episode return

## Example Output
```
======================================================================
ROCKET LANDING SIMULATOR - Visual Edition
======================================================================
Loading model from: models/ppo_ep2400.pt
Model loaded ← models/ppo_ep2400.pt
Model loaded successfully!

Starting episode...

======================================================================
EPISODE COMPLETE
======================================================================
Status: ✅ SUCCESSFUL LANDING
Final landing velocity: 3.45 m/s
Total timesteps: 127
Fuel remaining: 42.5 / 100.0
Episode return: 402.85
```

## Architecture

### File Structure
```
backend/
├── visual_simulate.py      # Main visualization script
├── launch_visual.py        # Launcher with documentation
├── env.py                  # Rocket environment
├── agent.py                # PPO agent
├── model.py                # Actor-Critic network
└── simulate.py             # Non-interactive matplotlib version
```

### Core Classes

#### `Particle`
Represents a single particle with physics
- `update(dt)`: Updates position with gravity
- `is_alive()`: Checks if particle should persist
- `get_alpha()`: Returns current opacity
- `draw(surface)`: Renders with fade effect

#### `ParticleSystem`
Manages all active particles
- `emit_flame()`: Thrust effect particles
- `emit_trail()`: Rocket trail particles
- `emit_dust()`: Landing/crash dust
- `update()`: Update all particles
- `draw()`: Render all particles

#### `RocketRenderer`
Handles all rendering and animation
- `draw_background()`: Sky/water gradient
- `draw_rocket()`: Sprite with status
- `draw_thrust_flame()`: Engine visualization
- `draw_hud()`: Information overlay
- `render_frame()`: Complete frame render

## Customization

### Color Scheme
Modify colors in `RocketRenderer`:
```python
COLOR_SKY = (135, 206, 235)      # Light blue
COLOR_WATER = (30, 100, 150)    # Dark blue
COLOR_ROCKET = (200, 200, 200)  # Silver
COLOR_ROCKET_LANDED = (100, 200, 100)  # Green
COLOR_ROCKET_CRASH = (255, 100, 100)   # Red
COLOR_FLAME = (255, 150, 50)    # Orange
```

### Particle Colors
```python
# Thrust flames - orange to red
color = (np.random.randint(200, 256), np.random.randint(100, 200), np.random.randint(0, 100))

# Rocket trail - blue
color = (100, 150, 255)

# Landing dust - brown
color = (180, 160, 120)
```

## Known Limitations

- Requires display server (not suitable for headless servers without virtual display)
- Windows only tested on Windows 10+
- Model checkpoint must exist before running
- 30 FPS lower bound on slower machines

## Future Enhancements

Potential additions:
- Multiple episode playback with statistics
- Speed controls (slow-motion, pause)
- Camera zoom/pan
- Trajectory prediction visualization
- Sound effects (engine thrust, landing sound, crash sound)
- Multiple model comparison
- Recording to video file
- Headless rendering mode

## Troubleshooting

### pygame.error: cannot connect to X server
You're running on a headless server. Consider:
- Using the matplotlib version (simulate.py)
- Setting up a virtual display (Xvfb on Linux)
- Using WSL2 with X11 forwarding on Windows

### Model loading failed
Ensure:
- Model file exists: `models/ppo_ep2400.pt`
- Model dimensions match (128 hidden, 4 actions)
- File path is correct

### Low FPS / Performance Issues
- Reduce max_particles in ParticleSystem
- Lower resolution in RocketRenderer
- Close other applications
- Check GPU/CPU load

## Credits

Built with:
- PyTorch - Neural network framework
- Pygame - Graphics and rendering
- NumPy - Numerical computations

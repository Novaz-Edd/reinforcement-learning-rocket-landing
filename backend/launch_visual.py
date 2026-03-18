"""
Enhanced rocket landing visualization with particle effects and HUD.

This script provides an interactive, game-quality visualization of the trained PPO agent
landing a rocket. It includes:

1. Smooth Physics Animation
   - Frame interpolation for smooth rocket movement
   - 30 FPS target framerate

2. Particle Effects
   - Thrust flame particles (orange/red) when engine fires
   - Rocket trail particles behind rocket motion
   - Dust particles on landing/crash
   - Particle fading and lifetime management

3. UI Overlay (HUD)
   - Real-time Height display (meters)
   - Vertical Velocity display (m/s)
   - Fuel remaining / Fuel maximum
   - Current action status (THRUST or IDLE)
   - Color-coded warnings (orange for high velocity, red for low fuel)

4. Landing Feedback
   - Green rocket color + "✅ SUCCESSFUL LANDING" message for successful landings
   - Red flashing rocket + "💥 CRASH" message for crashes
   - Dust effect on ground contact

5. Graphics
   - Professional color scheme (sky, water, ground)
   - Detailed rocket sprite with nose cone and windows
   - Landing platform visualization
   - Real-time flame rendering

Usage:
------
python backend/visual_simulate.py

Key Controls:
- ESC: Quit at any time
- Window close: Quit

Requirements:
- pygame
- torch
- numpy

The script will:
1. Load the trained model (models/ppo_ep2400.pt)
2. Initialize the rocket landing environment
3. Run one episode with deterministic policy (argmax action selection)
4. Render smooth animation with all visual effects
5. Display final statistics upon completion

Performance:
- Maintains 30 FPS target for smooth animation
- Efficient particle management with max 500 active particles
- No lag from physics simulation or rendering

This visualization is suitable for:
- Live demonstrations and presentations
- Portfolio/video documentation  
- Debugging agent behavior
- Showcasing RL achievements
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from visual_simulate import run_visual_simulation

if __name__ == "__main__":
    try:
        run_visual_simulation("../models/ppo_ep2400.pt")
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure pygame is installed: pip install pygame")
        print("2. Ensure the model file exists: models/ppo_ep2400.pt")
        print("3. Run from the backend/ directory: python visual_simulate.py")
        sys.exit(1)

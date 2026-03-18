"""
Rocket Landing Simulation - Utility Runner

Provides multiple ways to run the rocket landing simulation:
1. Visual (Pygame) - Full graphics with particle effects
2. Plot (Matplotlib) - Static plots of trajectory
3. Headless - Fast execution without rendering

Usage:
    python sim_runner.py --mode visual|plot|headless [--model ppo_ep2400.pt] [--count 1]
"""

import sys
import argparse
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


def run_visual(model_path):
    """Run visual Pygame simulation."""
    print("\n" + "="*70)
    print("VISUAL SIMULATION - Pygame")
    print("="*70)
    print(f"Model: {model_path}")
    print("Controls: ESC to quit\n")
    
    from backend.visual_simulate import run_visual_simulation
    try:
        run_visual_simulation(model_path)
    except Exception as e:
        print(f"Error running visual simulation: {e}")
        print("\nTroubleshooting:")
        print("- Ensure pygame is installed: pip install pygame")
        print("- Check you have an X display (not running on headless server)")
        print("- Try the 'plot' mode instead: python sim_runner.py --mode plot")
        return False
    return True


def run_plot(model_path):
    """Run plot-based Matplotlib simulation."""
    print("\n" + "="*70)
    print("PLOT SIMULATION - Matplotlib")
    print("="*70)
    print(f"Model: {model_path}")
    print("Generating trajectory plots...\n")
    
    from backend.simulate import run_simulation, plot_trajectory
    try:
        trajectory, landed_success, final_vy, total_steps = run_simulation(model_path)
        plot_trajectory(trajectory, landed_success)
        return True
    except Exception as e:
        print(f"Error running plot simulation: {e}")
        return False


def run_headless(model_path, count=1):
    """Run headless simulation (no rendering, just data)."""
    print("\n" + "="*70)
    print("HEADLESS SIMULATION")
    print("="*70)
    print(f"Model: {model_path}")
    print(f"Episodes: {count}\n")
    
    import torch
    import numpy as np
    from backend.env import RocketEnv
    from backend.agent import PPOAgent
    
    env = RocketEnv()
    agent = PPOAgent(obs_dim=5, action_dim=4, hidden=128)
    agent.load(model_path)
    agent.net.eval()
    
    results = {
        "landings": 0,
        "crashes": 0,
        "timeouts": 0,
        "velocities": [],
        "rewards": [],
        "steps": [],
    }
    
    for episode in range(count):
        obs = env.reset()
        done = False
        ep_reward = 0.0
        ep_steps = 0
        
        while not done:
            obs_t = torch.FloatTensor(obs).unsqueeze(0)
            with torch.no_grad():
                logits, _ = agent.net(obs_t)
            action = torch.argmax(logits, dim=1).item()
            if action >= 2:
                action = 1
            
            obs, reward, done, info = env.step(action)
            ep_reward += reward
            ep_steps += 1
        
        # Collect results
        if env.landed:
            results["landings"] += 1
        elif env.crashed:
            results["crashes"] += 1
        else:
            results["timeouts"] += 1
        
        if env.landing_vy is not None:
            results["velocities"].append(env.landing_vy)
        results["rewards"].append(ep_reward)
        results["steps"].append(ep_steps)
        
        print(f"Episode {episode+1:2d}: ", end="")
        if env.landed:
            print(f"✓ Land @ {env.landing_vy:5.2f} m/s, Steps: {ep_steps:3d}, Reward: {ep_reward:7.2f}")
        elif env.crashed:
            print(f"✗ Crash @ {abs(env.vy):5.2f} m/s, Steps: {ep_steps:3d}, Reward: {ep_reward:7.2f}")
        else:
            print(f"⏱ Timeout, Steps: {ep_steps:3d}, Reward: {ep_reward:7.2f}")
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total episodes: {count}")
    print(f"  Landings: {results['landings']} ({results['landings']*100/count:.1f}%)")
    print(f"  Crashes:  {results['crashes']} ({results['crashes']*100/count:.1f}%)")
    print(f"  Timeouts: {results['timeouts']} ({results['timeouts']*100/count:.1f}%)")
    
    if results["velocities"]:
        avg_vel = np.mean(results["velocities"])
        min_vel = np.min(results["velocities"])
        max_vel = np.max(results["velocities"])
        print(f"\nLanding Velocities (successful landings):")
        print(f"  Average: {avg_vel:.2f} m/s")
        print(f"  Min:     {min_vel:.2f} m/s")
        print(f"  Max:     {max_vel:.2f} m/s")
    
    avg_reward = np.mean(results["rewards"])
    avg_steps = np.mean(results["steps"])
    print(f"\nRewards:")
    print(f"  Average: {avg_reward:.2f}")
    print(f"  Total steps: {sum(results['steps'])}")
    print(f"  Avg per episode: {avg_steps:.1f}")
    print()
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Rocket Landing Simulation Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sim_runner.py --mode visual
  python sim_runner.py --mode plot --model models/ppo_ep1000.pt
  python sim_runner.py --mode headless --count 10
        """
    )
    parser.add_argument(
        "--mode",
        choices=["visual", "plot", "headless"],
        default="visual",
        help="Simulation mode (default: visual)"
    )
    parser.add_argument(
        "--model",
        default="models/ppo_ep2400.pt",
        help="Path to model checkpoint (default: models/ppo_ep2400.pt)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of episodes for headless mode (default: 1)"
    )
    
    args = parser.parse_args()
    
    # Check if model exists
    if not os.path.exists(args.model):
        print(f"Error: Model not found: {args.model}")
        print(f"Available models:")
        models_dir = os.path.dirname(args.model)
        if os.path.exists(models_dir):
            for f in sorted(os.listdir(models_dir)):
                if f.endswith(".pt"):
                    print(f"  - {f}")
        sys.exit(1)
    
    # Run simulation
    if args.mode == "visual":
        success = run_visual(args.model)
    elif args.mode == "plot":
        success = run_plot(args.model)
    elif args.mode == "headless":
        success = run_headless(args.model, args.count)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

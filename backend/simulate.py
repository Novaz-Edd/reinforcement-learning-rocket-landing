"""
Simulation script for trained PPO rocket landing agent.

Loads a trained model, runs one episode in deterministic evaluation mode,
and visualizes the rocket's trajectory.
"""

import sys
import torch
import numpy as np
import matplotlib.pyplot as plt
from env import RocketEnv
from agent import PPOAgent


def get_deterministic_action(agent, obs):
    """
    Get action using deterministic policy (argmax instead of sampling).
    
    Args:
        agent: PPOAgent instance
        obs: observation array
        
    Returns:
        action: deterministic action (0 or 1)
    """
    obs_t = torch.FloatTensor(obs).unsqueeze(0)
    with torch.no_grad():
        logits, value = agent.net(obs_t)
    
    # Use argmax for deterministic action selection
    action = torch.argmax(logits, dim=1).item()
    
    # If agent was trained with 4 actions, map to binary (threshold at 2)
    if action >= 2:
        action = 1
    
    return action


def run_simulation(model_path="models/ppo_ep2400.pt"):
    """
    Run one episode of the trained agent in deterministic mode.
    
    Args:
        model_path: path to trained model checkpoint
        
    Returns:
        dict with episode data and results
    """
    print("=" * 70)
    print("ROCKET LANDING SIMULATION - Deterministic Policy")
    print("=" * 70)
    print(f"Loading model from: {model_path}")
    print()
    
    # Initialize environment and agent
    env = RocketEnv()
    # Create agent with matching trained model dimensions (hidden=128, action_dim=4)
    agent = PPOAgent(obs_dim=5, action_dim=4, hidden=128)
    
    # Load trained weights
    agent.load(model_path)
    agent.net.eval()  # Set to evaluation mode
    print(f"Model loaded successfully!")
    print()
    
    # Storage for trajectory
    trajectory = {
        "timesteps": [],
        "heights": [],
        "velocities": [],
        "actions": [],
    }
    
    # Run one episode
    print("Starting episode...")
    obs = env.reset()
    done = False
    episode_return = 0.0
    
    while not done:
        # Get deterministic action
        action = get_deterministic_action(agent, obs)
        
        # Step environment
        obs, reward, done, info = env.step(action)
        episode_return += reward
        
        # Record trajectory
        trajectory["timesteps"].append(env.step_count)
        trajectory["heights"].append(info["y"])
        trajectory["velocities"].append(info["vy"])
        trajectory["actions"].append(action)
    
    # Extract final results
    final_vy = abs(env.landing_vy) if env.landing_vy is not None else abs(env.vy)
    total_steps = env.step_count
    landed_success = env.landed
    crashed = env.crashed
    
    print()
    print("=" * 70)
    print("EPISODE COMPLETE")
    print("=" * 70)
    
    # Status
    if landed_success:
        status = "✓ SUCCESSFUL LANDING"
        print(f"Status: {status}")
    elif crashed:
        status = "✗ CRASH"
        print(f"Status: {status}")
    else:
        status = "⏱ TIMEOUT"
        print(f"Status: {status}")
    
    print(f"Final landing velocity: {final_vy:.2f} m/s")
    print(f"Total timesteps: {total_steps}")
    print(f"Fuel remaining: {env.fuel:.1f} / {env.FUEL_MAX:.1f}")
    print(f"Episode return: {episode_return:.2f}")
    print()
    
    return trajectory, landed_success, final_vy, total_steps


def plot_trajectory(trajectory, landed_success):
    """
    Create two plots: height vs timestep and velocity vs timestep.
    
    Args:
        trajectory: dict with timesteps, heights, velocities, actions
        landed_success: boolean indicating successful landing
    """
    timesteps = np.array(trajectory["timesteps"])
    heights = np.array(trajectory["heights"])
    velocities = np.array(trajectory["velocities"])
    actions = np.array(trajectory["actions"])
    
    # Determine plot styling
    if landed_success:
        color_height = "#2E7D32"  # Green for success
        color_velocity = "#2E7D32"
        title_suffix = " (Successful Landing)"
    else:
        color_height = "#C62828"  # Red for failure
        color_velocity = "#C62828"
        title_suffix = " (Crashed/Timeout)"
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle(f"PPO Agent Rocket Landing Trajectory{title_suffix}", fontsize=14, fontweight="bold")
    
    # Plot 1: Height vs Timestep
    ax1 = axes[0]
    ax1.plot(timesteps, heights, linewidth=2.5, color=color_height, label="Rocket Height")
    ax1.axhline(y=0, color="gray", linestyle="--", linewidth=1, alpha=0.7, label="Ground Level")
    ax1.fill_between(timesteps, 0, heights, alpha=0.2, color=color_height)
    ax1.set_xlabel("Timestep", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Height (m)", fontsize=11, fontweight="bold")
    ax1.set_title("Height vs Time", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
    ax1.legend(loc="upper right", fontsize=10)
    ax1.set_ylim(bottom=0)
    
    # Plot 2: Velocity vs Timestep
    ax2 = axes[1]
    ax2.plot(timesteps, velocities, linewidth=2.5, color=color_velocity, label="Vertical Velocity")
    ax2.axhline(y=0, color="gray", linestyle="--", linewidth=1, alpha=0.7, label="Zero Velocity")
    ax2.axhline(y=-4.0, color="orange", linestyle=":", linewidth=1.5, alpha=0.7, label="Landing Threshold (4 m/s)")
    
    # Color regions for demonstration
    ax2.fill_between(timesteps, velocities, 0, where=(velocities <= 0), alpha=0.15, color=color_velocity, label="Falling")
    
    # Add thrust markers
    thrust_indices = np.where(actions == 1)[0]
    if len(thrust_indices) > 0:
        ax2.scatter(timesteps[thrust_indices], velocities[thrust_indices], 
                   color="orange", s=30, marker="^", alpha=0.6, label="Thrust Applied", zorder=5)
    
    ax2.set_xlabel("Timestep", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Vertical Velocity (m/s)", fontsize=11, fontweight="bold")
    ax2.set_title("Velocity vs Time", fontsize=12, fontweight="bold")
    ax2.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
    ax2.legend(loc="lower right", fontsize=10)
    
    plt.tight_layout()
    plt.savefig("simulation_trajectory.png", dpi=100, bbox_inches="tight")
    print("Plot saved as: simulation_trajectory.png")
    plt.show()


def main():
    """Main entry point."""
    # Run simulation
    trajectory, landed_success, final_vy, total_steps = run_simulation("models/ppo_ep2400.pt")
    
    # Create plots
    print()
    print("Generating plots...")
    plot_trajectory(trajectory, landed_success)
    print()
    print("Simulation complete!")


if __name__ == "__main__":
    main()

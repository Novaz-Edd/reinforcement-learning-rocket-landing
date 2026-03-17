#!/usr/bin/env python3
"""Quick test to verify the RL setup works correctly."""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from env import RocketEnv
from agent import PPOAgent

def test_basic():
    """Test basic functionality."""
    print("=" * 60)
    print("Testing RocketEnv...")
    print("=" * 60)
    
    env = RocketEnv()
    obs = env.reset()
    
    print(f"✓ Environment initialized")
    print(f"  State shape: {obs.shape}")
    print(f"  State range: [{obs.min():.3f}, {obs.max():.3f}] (should be in [-1, 1])")
    print(f"  Example state: {obs}")
    
    print("\n" + "=" * 60)
    print("Testing Agent...")
    print("=" * 60)
    
    agent = PPOAgent()
    action, log_prob, value = agent.net.get_action(obs)
    
    print(f"✓ Agent initialized")
    print(f"  Action: {action}")
    print(f"  Log prob: {log_prob:.6f}")
    print(f"  Value estimate: {value:.6f}")
    
    print("\n" + "=" * 60)
    print("Running one episode...")
    print("=" * 60)
    
    obs = env.reset()
    total_reward = 0.0
    steps = 0
    
    for _ in range(100):
        action, log_prob, value = agent.net.get_action(obs)
        next_obs, reward, done, info = env.step(action)
        
        agent.store(obs, action, reward, log_prob, value, float(done))
        
        obs = next_obs
        total_reward += reward
        steps += 1
        
        if done:
            break
    
    print(f"✓ Episode completed")
    print(f"  Total steps: {steps}")
    print(f"  Total reward: {total_reward:.2f}")
    print(f"  Landed: {info['landed']}")
    print(f"  Crashed: {info['crashed']}")
    
    print("\n" + "=" * 60)
    print("Testing PPO update...")
    print("=" * 60)
    
    if len(agent.buf_actions) > 0:
        # Perform one update
        _, _, last_val = agent.net.get_action(obs)
        loss = agent.update(last_value=last_val)
        print(f"✓ PPO update completed")
        print(f"  Loss: {loss:.4f}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_basic()

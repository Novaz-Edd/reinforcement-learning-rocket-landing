import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from env   import RocketEnv
from agent import PPOAgent

# ── Hyperparameters ───────────────────────────────────────────────────────────
MAX_EPISODES    = 5000
STEPS_PER_UPDATE = 2048   # collect this many steps before each PPO update
SAVE_EVERY      = 500     # save checkpoint every N episodes
PRINT_EVERY     = 50      # print stats every N episodes

def train():
    env   = RocketEnv()
    agent = PPOAgent()

    # Metrics
    episode_rewards  = []
    success_rate_log = []
    recent_successes = []   # sliding window of last 100 episodes
    landing_velocities = []  # track successful landing velocities

    total_steps = 0
    episode     = 0

    print("Starting training...\n")
    print(f"{'Episode':>8}  {'Reward':>8}  {'Success%':>9}  {'AvgLandVy':>9}  {'Steps':>7}")
    print("-" * 50)

    while episode < MAX_EPISODES:
        obs  = env.reset()
        ep_reward = 0.0
        ep_steps  = 0
        landed    = False
        last_vy   = 0.0

        for t in range(env.MAX_STEPS):
            action, log_prob, value = agent.net.get_action(obs)
            next_obs, reward, done, info = env.step(action)

            agent.store(obs, action, reward, log_prob, value, float(done))

            obs        = next_obs
            ep_reward += reward
            ep_steps  += 1
            total_steps += 1
            landed     = info["landed"]
            last_vy    = info["vy"]

            # PPO update when buffer is full
            if total_steps % STEPS_PER_UPDATE == 0:
                _, _, last_val = agent.net.get_action(obs)
                agent.update(last_value=last_val)

            if done:
                break

        episode += 1
        episode_rewards.append(ep_reward)
        recent_successes.append(1 if landed else 0)
        if len(recent_successes) > 100:
            recent_successes.pop(0)

        success_rate = np.mean(recent_successes) * 100
        success_rate_log.append(success_rate)
        
        # Track landing velocities for successful landings
        if landed and hasattr(env, 'landing_vy') and env.landing_vy is not None:
            landing_velocities.append(env.landing_vy)

        if episode % PRINT_EVERY == 0:
            avg_reward = np.mean(episode_rewards[-PRINT_EVERY:])
            if landing_velocities:
                recent_vys = landing_velocities[-PRINT_EVERY:] if len(landing_velocities) >= PRINT_EVERY else landing_velocities
                if recent_vys:
                    avg_vy = np.mean(recent_vys)
                    landing_str = f"{avg_vy:>+8.2f}"
                else:
                    landing_str = "      N/A"
            else:
                landing_str = "      N/A"
            print(f"{episode:>8}  {avg_reward:>8.1f}  {success_rate:>8.1f}%  {landing_str}  {total_steps:>7}")

        if episode % SAVE_EVERY == 0:
            models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
            os.makedirs(models_dir, exist_ok=True)
            path = os.path.join(models_dir, f"ppo_ep{episode}.pt")
            agent.save(path)

    # Final save
    models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    os.makedirs(models_dir, exist_ok=True)
    agent.save(os.path.join(models_dir, "ppo_final.pt"))
    print("\nTraining complete.")
    return episode_rewards, success_rate_log

if __name__ == "__main__":
    rewards, success_rates = train()
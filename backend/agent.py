import torch
import torch.nn as nn
import numpy as np
from model import ActorCritic

class PPOAgent:
    def __init__(
        self,
        obs_dim      = 5,
        action_dim   = 2,
        lr           = 3e-4,
        gamma        = 0.99,    # discount factor
        lam          = 0.95,    # GAE lambda
        clip_eps     = 0.2,    # PPO clip range
        epochs       = 10,       # update passes per batch
        batch_size   = 64,
    ):
        self.gamma      = gamma
        self.lam        = lam
        self.clip_eps   = clip_eps
        self.epochs     = epochs
        self.batch_size = batch_size

        self.net       = ActorCritic(obs_dim, action_dim)
        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=lr)

        # Storage for one rollout
        self._reset_buffer()

    # ── Buffer ────────────────────────────────────────────────────────────────
    def _reset_buffer(self):
        self.buf_obs      = []
        self.buf_actions  = []
        self.buf_rewards  = []
        self.buf_logprobs = []
        self.buf_values   = []
        self.buf_dones    = []

    def store(self, obs, action, reward, log_prob, value, done):
        self.buf_obs.append(obs)
        self.buf_actions.append(action)
        self.buf_rewards.append(reward)
        self.buf_logprobs.append(log_prob)
        self.buf_values.append(value)
        self.buf_dones.append(done)

    # ── GAE — Generalized Advantage Estimation ────────────────────────────────
    def _compute_advantages(self, last_value):
        rewards   = self.buf_rewards
        values    = self.buf_values + [last_value]
        dones     = self.buf_dones

        advantages = []
        gae = 0.0
        for t in reversed(range(len(rewards))):
            delta = rewards[t] + self.gamma * values[t+1] * (1 - dones[t]) - values[t]
            gae   = delta + self.gamma * self.lam * (1 - dones[t]) * gae
            advantages.insert(0, gae)

        advantages = torch.FloatTensor(advantages)
        returns    = advantages + torch.FloatTensor(self.buf_values)

        # Normalize advantages — critical for stable training
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        return advantages, returns

    # ── PPO Update ────────────────────────────────────────────────────────────
    def update(self, last_value=0.0):
        advantages, returns = self._compute_advantages(last_value)

        obs_t      = torch.FloatTensor(np.array(self.buf_obs))
        actions_t  = torch.LongTensor(self.buf_actions)
        old_lp_t   = torch.FloatTensor(self.buf_logprobs)

        total_loss_log = 0.0

        for _ in range(self.epochs):
            # Shuffle for mini-batches
            indices = torch.randperm(len(self.buf_obs))

            for start in range(0, len(indices), self.batch_size):
                idx = indices[start : start + self.batch_size]

                new_lp, values, entropy = self.net.evaluate(obs_t[idx], actions_t[idx])

                # Ratio for PPO clip
                ratio = torch.exp(new_lp - old_lp_t[idx])

                adv = advantages[idx]

                # Clipped surrogate loss
                surr1 = ratio * adv
                surr2 = torch.clamp(ratio, 1 - self.clip_eps, 1 + self.clip_eps) * adv
                actor_loss  = -torch.min(surr1, surr2).mean()

                # Value loss
                critic_loss = nn.MSELoss()(values, returns[idx].detach())

                # Entropy bonus — encourages exploration
                entropy_loss = -0.01 * entropy.mean()

                loss = actor_loss + 0.5 * critic_loss + entropy_loss

                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.net.parameters(), 0.5)
                self.optimizer.step()

                total_loss_log += loss.item()

        self._reset_buffer()
        return total_loss_log

    # ── Save / Load ───────────────────────────────────────────────────────────
    def save(self, path):
        torch.save(self.net.state_dict(), path)
        print(f"Model saved → {path}")

    def load(self, path):
        self.net.load_state_dict(torch.load(path))
        print(f"Model loaded ← {path}")
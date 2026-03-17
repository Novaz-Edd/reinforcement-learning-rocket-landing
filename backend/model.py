import torch
import torch.nn as nn
import numpy as np

class ActorCritic(nn.Module):
    """
    Combined policy (actor) + value (critic) network.
    
    Actor:  obs → action probabilities
    Critic: obs → state value estimate (used to compute advantage)
    """

    def __init__(self, obs_dim=5, action_dim=2, hidden=64):
        super().__init__()

        # Shared feature extractor
        self.shared = nn.Sequential(
            nn.Linear(obs_dim, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
        )

        # Actor head — outputs action logits
        self.actor  = nn.Linear(hidden, action_dim)

        # Critic head — outputs a single value estimate
        self.critic = nn.Linear(hidden, 1)

        # Initialize weights small for stable early training
        self._init_weights()

    def _init_weights(self):
        for layer in self.modules():
            if isinstance(layer, nn.Linear):
                nn.init.orthogonal_(layer.weight, gain=1.0)
                nn.init.zeros_(layer.bias)
        # Smaller gain for output heads
        nn.init.orthogonal_(self.actor.weight, gain=0.01)
        nn.init.orthogonal_(self.critic.weight, gain=0.01)

    def forward(self, x):
        features = self.shared(x)
        logits    = self.actor(features)
        value     = self.critic(features).squeeze(-1)
        return logits, value

    def get_action(self, obs):
        """Sample an action and return it with its log probability."""
        obs_t   = torch.FloatTensor(obs).unsqueeze(0)
        logits, value = self(obs_t)
        dist    = torch.distributions.Categorical(logits=logits)
        action  = dist.sample()
        log_prob = dist.log_prob(action)
        return action.item(), log_prob.item(), value.item()

    def evaluate(self, obs_batch, action_batch):
        """Used during PPO update — returns log probs, values, entropy."""
        logits, values = self(obs_batch)
        dist      = torch.distributions.Categorical(logits=logits)
        log_probs = dist.log_prob(action_batch)
        entropy   = dist.entropy()
        return log_probs, values, entropy
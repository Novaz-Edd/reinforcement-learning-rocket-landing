from env import RocketEnv
import random

env = RocketEnv()
obs = env.reset()
print("Initial obs:", obs)

for step in range(50):
    action = random.choice([0, 1])   # randomly fire engine or do nothing
    obs, reward, done, info = env.step(action)
    env.render()
    if done:
        print(f"\nEpisode ended — landed={info['landed']} crashed={info['crashed']}")
        break
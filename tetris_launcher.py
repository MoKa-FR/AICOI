import gymnasium as gym

env = gym.make("ALE/Tetris-v5")
env.reset()
for _ in range(1000):
    env.render(mode='human')  # Spécifiez le mode ici
    action = env.action_space.sample()  # Choisissez une action aléatoire
    env.step(action)
env.close()

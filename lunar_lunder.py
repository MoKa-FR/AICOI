import gym

# Créer l'environnement
env = gym.make("LunarLander-v2")

# Boucle principale
done = False
observation = env.reset()

while not done:
    # Choisir une action (ici, une action aléatoire pour un exemple)
    action = env.action_space.sample()
    
    # Appliquer l'action à l'environnement
    next_observation, reward, done, info = env.step(action)
    
    # Afficher l'observation et la récompense
    print("Observation:", next_observation)
    print("Récompense:", reward)
    
    # Mettre à jour l'observation actuelle
    observation = next_observation

    # Si l'épisode est terminé, réinitialiser l'environnement
    if done:
        observation = env.reset()

# Fermer l'environnement
env.close()

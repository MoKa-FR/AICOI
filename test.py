import sys
import math

# Initialize fish scores based on their type and color
fish_scores = {(0, 0): 5, (1, 0): 10, (2, 0): 15, (3, 0): 20, # etc. for other color and type combinations
               (0, 1): 5, (1, 1): 10, (2, 1): 15, (3, 1): 20, # etc.
               (0, 2): 5, (1, 2): 10, (2, 2): 15, (3, 2): 20} # etc.

# Function to calculate the score of a fish
def calculate_fish_score(color, type):
    return fish_scores.get((color, type), 0)

# Read initial creatures data
creature_count = int(input())
creatures = {}
for i in range(creature_count):
    creature_id, color, _type = [int(j) for j in input().split()]
    creatures[creature_id] = {"color": color, "type": _type, "score": calculate_fish_score(color, _type)}

# game loop
while True:
    my_score, foe_score = int(input()), int(input())
    my_scan_count = int(input())
    my_scans = [int(input()) for _ in range(my_scan_count)]
    foe_scan_count = int(input())
    foe_scans = [int(input()) for _ in range(foe_scan_count)]
    
    # Drone's data
    my_drone_count = int(input())
    my_drones = []
    for i in range(my_drone_count):
        drone_data = input().split()
        drone_id, drone_x, drone_y, emergency, battery = map(int, drone_data)
        my_drones.append({"id": drone_id, "x": drone_x, "y": drone_y, "emergency": emergency, "battery": battery})

    foe_drone_count = int(input())
    foe_drones = []
    for i in range(foe_drone_count):
        drone_data = input().split()
        drone_id, drone_x, drone_y, emergency, battery = map(int, drone_data)
        foe_drones.append({"id": drone_id, "x": drone_x, "y": drone_y, "emergency": emergency, "battery": battery})

    visible_creature_count = int(input())
    visible_creatures = []
    for i in range(visible_creature_count):
        creature_data = input().split()
        creature_id, creature_x, creature_y, creature_vx, creature_vy = map(int, creature_data)
        visible_creatures.append(creatures[creature_id].update({"x": creature_x, "y": creature_y, "vx": creature_vx, "vy": creature_vy}))

    # Strategy implementation
    for drone in my_drones:
        # Choose the highest scoring visible fish
        target_fish = max(visible_creatures, key=lambda x: x['score'], default=None)
        if target_fish:
            print(f"MOVE {target_fish['x']} {target_fish['y']} 1")  # Move towards the fish with light on
        else:
            print("WAIT 0")  # Wait with light off if no high scoring fish is visible

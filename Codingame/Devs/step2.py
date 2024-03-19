from typing import List, NamedTuple, Dict
from queue import PriorityQueue
import random

MAX_SCAN_RADIUS = 2000
SCAN_RADIUS = 800
SURFACE_Y_THRESHOLD = 500  # Seuil pour être considéré comme proche de la surface
MAP_SIZE = 10000  # Taille de la carte

# Définition des structures de données avec des NamedTuples
class Vector(NamedTuple):
    x: int
    y: int
    
class FishDetail(NamedTuple):
    color: int
    type: int
    
class Fish(NamedTuple):
    fish_id: int
    pos: Vector
    speed: Vector
    detail: FishDetail
    
class RadarBlip(NamedTuple):
    fish_id: int
    dir: str
    
class Drone(NamedTuple):
    drone_id: int
    pos: Vector
    dead: bool
    battery: int
    scans: List[int]
    
def euclidean_distance_drone_fish(drone: Drone, fish: Fish) -> float:
    """Calcule la distance euclidienne entre un drone et un poisson."""
    return ((drone.pos.x - fish.pos.x) ** 2 + (drone.pos.y - fish.pos.y) ** 2) ** 0.5

# Fonction A* pour trouver un chemin du drone vers un poisson cible
def a_star(drone: Drone, target_fish: Fish, visible_fish: List[Fish], map_size: int) -> List[Vector]:
    # Définir le point de départ et le point d'arrivée
    start = drone.pos
    goal = target_fish.pos

    # Initialiser l'ensemble ouvert avec la position de départ du drone
    open_set = PriorityQueue()
    open_set.put((0, start))
    
    # Dictionnaire pour garder une trace de la provenance de chaque nœud
    came_from = {start: None}
    
    # Dictionnaire pour garder une trace du coût jusqu'à présent pour atteindre chaque nœud
    cost_so_far = {start: 0}

    # Tant que l'ensemble ouvert n'est pas vide, continuer à explorer
    while not open_set.empty():
        _, current = open_set.get()

        # Si le nœud actuel est le but, arrêter la recherche
        if current == goal:
            break

        # Explorer les voisins du nœud actuel
        for next in get_neighbors(current, visible_fish, map_size):
            new_cost = cost_so_far[current] + euclidean_distance_drone_fish(drone, Fish(0, next, Vector(0, 0), FishDetail(0, 0)))
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + euclidean_distance_drone_fish(drone, target_fish)
                open_set.put((priority, next))
                came_from[next] = current

    # Reconstruire et retourner le chemin une fois le but atteint
    return reconstruct_path(came_from, start, goal)

# Fonction pour obtenir les voisins d'un nœud donné
def get_neighbors(node: Vector, visible_fish: List[Fish], map_size: int) -> List[Vector]:
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Haut, Droite, Bas, Gauche
    neighbors = []
    for dx, dy in directions:
        next_x, next_y = node.x + dx, node.y + dy
        if 0 <= next_x < map_size and 0 <= next_y < map_size:
            # Vérifier si le voisin est libre (pas occupé par un poisson visible)
            if not any(fish.pos == Vector(next_x, next_y) for fish in visible_fish):
                neighbors.append(Vector(next_x, next_y))
    return neighbors

def reconstruct_path(came_from: Dict[Vector, Vector], start: Vector, goal: Vector) -> List[Vector]:
    """Reconstruit le chemin à partir du point de départ jusqu'à l'objectif."""
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)  # optionnel
    path.reverse()  # optionnel
    return path

# Ajoutez un ensemble pour suivre les poissons scannés
scanned_fish_ids = set()

# Initialize the set for tracking first scans
first_scan_bonus = set()

def calculate_potential_points(fish: Fish, scanned_fish_ids: set, first_scan_bonus: set, type_bonus_tracker: Dict[int, int], color_bonus_tracker: Dict[int, int]) -> int:
    # Points de base selon le type de poisson
    base_points = {0: 1, 1: 2, 2: 3}
    potential_points = base_points[fish.detail.type]
    
    # Bonus si c'est le premier scan de ce type de poisson
    if fish.fish_id not in first_scan_bonus:
        potential_points *= 2
    
    # Bonus pour avoir scanné tous les poissons d'une couleur
    if color_bonus_tracker[fish.detail.color] == 1:
        potential_points += 3
    
    # Bonus pour avoir scanné tous les poissons d'un type
    if type_bonus_tracker[fish.detail.type] == 1:
        potential_points += 4
    
    return potential_points

def select_target(drone: Drone, visible_fish: List[Fish], scanned_fish_ids: set, type_bonus_tracker: Dict[int, int], color_bonus_tracker: Dict[int, int]) -> (int, Vector, int):
    # Filter out scanned fish
    unscanned_fish = [fish for fish in visible_fish if fish.fish_id not in scanned_fish_ids]
    
    # If no unscanned fish are visible, return None
    if not unscanned_fish:
        return None, None, 0
    
    # Select the fish with the highest potential points
    # Sélectionnez le poisson avec le plus haut potentiel de points
    target_fish = max(unscanned_fish, key=lambda fish: calculate_potential_points(fish, scanned_fish_ids, first_scan_bonus, type_bonus_tracker, color_bonus_tracker))
    
    return target_fish.fish_id, target_fish.pos, 1

# Initialize bonus trackers
type_bonus_tracker = {0: 3, 1: 3, 2: 3}  # Assuming there are 3 of each type to begin with
color_bonus_tracker = {0: 4, 1: 4, 2: 4, 3: 4}  # Assuming there are 4 of each color

# Vérifie si le drone est proche de la surface
def drone_is_near_surface(drone: Drone) -> bool:
    return drone.pos.y <= SURFACE_Y_THRESHOLD

# Vérifie si le drone a des scans non enregistrés
def drone_has_scans(drone: Drone) -> bool:
    return len(drone.scans) > 0

# Déplacer le drone vers la surface pour enregistrer les scans
def move_to_surface(drone: Drone) -> Vector:
    # Déplacer le drone vers un point au-dessus de sa position actuelle
    return Vector(drone.pos.x, max(0, drone.pos.y - 600))  # Déplacer de 600 unités vers le haut

# Déterminer le prochain mouvement sur le chemin
def get_next_move(path: List[Vector], drone: Drone) -> Vector:
    # Retourner le prochain point sur le chemin ou la position actuelle si le chemin est vide
    return path[0] if path else drone.pos

# Mettre à jour l'état du jeu
def update_game_state(drone: Drone, visible_fish: List[Fish], scanned_fish_ids: set):
    # Ici, vous devriez mettre à jour l'état du drone (position, batterie, etc.)
    # et potentiellement la liste des poissons visibles, selon la logique de votre jeu
    pass

# Fonction pour déterminer un mouvement aléatoire des drones
def random_movement_strategy(drone: Drone, visible_fish: List[Fish], map_width: int, map_height: int, detection_radius: int):
    # Choisir un point aléatoire sur la carte
    target_x = random.randint(0, map_width)
    target_y = random.randint(0, map_height)

    # Vérifier si un poisson est à proximité
    fish_nearby = any(
        euclidean_distance_drone_fish(drone.pos, fish.pos) <= detection_radius
        for fish in visible_fish
    )

    # Allumer la lumière seulement si un poisson est à proximité
    light = 1 if fish_nearby else 0

    return target_x, target_y, light

# Boucle de jeu principale
while True:
    # Initialisation des listes et dictionnaires pour stocker les données du jeu
    my_scans: List[int] = []
    foe_scans: List[int] = []
    drone_by_id: Dict[int, Drone] = {}
    my_drones: List[Drone] = []
    foe_drones: List[Drone] = []
    visible_fish: List[Fish] = []
    my_radar_blips: Dict[int, List[RadarBlip]] = {}

    # Lecture des scores et autres informations
    my_score = int(input())
    try:
        foe_score = int(input())
    except ValueError:
        # Si la conversion échoue, nous assignons une valeur par défaut
        foe_score = 0  # ou une autre valeur par défaut appropriée

    # Lecture des informations de scan pour les joueurs
    # Lecture des informations de scan pour les joueurs
    my_scan_count_input = input().split()
    if len(my_scan_count_input) == 1:
        my_scan_count = int(my_scan_count_input[0])
    else:
        my_scan_count = 0

    for _ in range(my_scan_count):
        fish_id = int(input())

    foe_scan_count_input = input().split()
    if len(foe_scan_count_input) == 1:
        foe_scan_count = int(foe_scan_count_input[0])
    else:
        foe_scan_count = 0

    for _ in range(foe_scan_count):
        fish_id = int(input())
        foe_scans.append(fish_id)

    # Lecture des informations des drones
    my_drone_count_input = input().split()
    if len(my_drone_count_input) == 1:
        my_drone_count = int(my_drone_count_input[0])
    else:
        my_drone_count = 0

    for _ in range(my_drone_count):
        drone_id, drone_x, drone_y, dead, battery = map(int, input().split())
        pos = Vector(drone_x, drone_y)
        drone = Drone(drone_id, pos, dead == "1", battery, [])
        drone_by_id[drone_id] = drone
        my_drones.append(drone)
        my_radar_blips[drone_id] = []

    foe_drone_count_input = input().split()
    if len(foe_drone_count_input) == 1:
        foe_drone_count = int(foe_drone_count_input[0])
    else:
        foe_drone_count = 0

    for _ in range(foe_drone_count):
        drone_id, drone_x, drone_y, dead, battery = map(int, input().split())
        pos = Vector(drone_x, drone_y)
        drone = Drone(drone_id, pos, dead == "1", battery, [])
        drone_by_id[drone_id] = drone
        foe_drones.append(drone)

    # Lecture des scans des drones
    drone_scan_count_input = input().split()
    if len(drone_scan_count_input) == 1:
        drone_scan_count = int(drone_scan_count_input[0])
    else:
        drone_scan_count = 0

    for _ in range(drone_scan_count):
        drone_id, fish_id = map(int, input().split())
        drone_by_id[drone_id].scans.append(fish_id)


    # Lecture et stockage des poissons visibles
    visible_fish_count_input = input().split()
    if len(visible_fish_count_input) == 1:
        visible_fish_count = int(visible_fish_count_input[0])
    else:
        visible_fish_count = 0

    for _ in range(visible_fish_count):
        fish_id, fish_x, fish_y, fish_vx, fish_vy = map(int, input().split())
        pos = Vector(fish_x, fish_y)
        speed = Vector(fish_vx, fish_vy)
        visible_fish.append(Fish(fish_id, pos, speed, fish_details[fish_id]))

    # Lecture des informations de radar
    my_radar_blip_count_input = input().split()
    if len(my_radar_blip_count_input) == 1:
        my_radar_blip_count = int(my_radar_blip_count_input[0])
    else:
        my_radar_blip_count = 0

    for _ in range(my_radar_blip_count):
        drone_id, fish_id, dir = input().split()
        drone_id = int(drone_id)
        fish_id = int(fish_id)
        my_radar_blips[drone_id].append(RadarBlip(fish_id, dir))

    while True:
        # Initialisation des listes et dictionnaires pour stocker les données du jeu
        my_scans: List[int] = []
        foe_scans: List[int] = []
        drone_by_id: Dict[int, Drone] = {}
        my_drones: List[Drone] = []
        foe_drones: List[Drone] = []
        visible_fish: List[Fish] = []
        my_radar_blips: Dict[int, List[RadarBlip]] = {}

        # Lecture des scores et autres informations
        my_score = int(input())
        try:
            foe_score = int(input())
        except ValueError:
            # Si la conversion échoue, nous assignons une valeur par défaut
            foe_score = 0  # ou une autre valeur par défaut appropriée

        # Lecture des informations de scan pour les joueurs
        my_scan_count_input = input().split()
        if len(my_scan_count_input) == 1:
            my_scan_count = int(my_scan_count_input[0])
        else:
            my_scan_count = 0

        for _ in range(my_scan_count):
            fish_id = int(input())

        foe_scan_count_input = input().split()
        if len(foe_scan_count_input) == 1:
            foe_scan_count = int(foe_scan_count_input[0])
        else:
            foe_scan_count = 0

        for _ in range(foe_scan_count):
            fish_id = int(input())
            foe_scans.append(fish_id)

        # Lecture des informations des drones
        my_drone_count_input = input().split()
        if len(my_drone_count_input) == 1:
            my_drone_count = int(my_drone_count_input[0])
        else:
            my_drone_count = 0

        for _ in range(my_drone_count):
            drone_id, drone_x, drone_y, dead, battery = map(int, input().split())
            pos = Vector(drone_x, drone_y)
            drone = Drone(drone_id, pos, dead == "1", battery, [])
            drone_by_id[drone_id] = drone
            my_drones.append(drone)
            my_radar_blips[drone_id] = []

        foe_drone_count_input = input().split()
        if len(foe_drone_count_input) == 1:
            foe_drone_count = int(foe_drone_count_input[0])
        else:
            foe_drone_count = 0

        for _ in range(foe_drone_count):
            drone_id, drone_x, drone_y, dead, battery = map(int, input().split())
            pos = Vector(drone_x, drone_y)
            drone = Drone(drone_id, pos, dead == "1", battery, [])
            drone_by_id[drone_id] = drone
            foe_drones.append(drone)

        # Lecture des scans des drones
        drone_scan_count_input = input().split()
        if len(drone_scan_count_input) == 1:
            drone_scan_count = int(drone_scan_count_input[0])
        else:
            drone_scan_count = 0

        for _ in range(drone_scan_count):
            drone_id, fish_id = map(int, input().split())
            drone_by_id[drone_id].scans.append(fish_id)

        # Lecture et stockage des poissons visibles
        visible_fish_count_input = input().split()
        if len(visible_fish_count_input) == 1:
            visible_fish_count = int(visible_fish_count_input[0])
        else:
            visible_fish_count = 0

        for _ in range(visible_fish_count):
            fish_id, fish_x, fish_y, fish_vx, fish_vy = map(int, input().split())
            pos = Vector(fish_x, fish_y)
            speed = Vector(fish_vx, fish_vy)
            visible_fish.append(Fish(fish_id, pos, speed, fish_details[fish_id]))

        # Lecture des informations de radar
        my_radar_blip_count_input = input().split()
        if len(my_radar_blip_count_input) == 1:
            my_radar_blip_count = int(my_radar_blip_count_input[0])
        else:
            my_radar_blip_count = 0

        for _ in range(my_radar_blip_count):
            drone_id, fish_id, dir = input().split()
            drone_id = int(drone_id)
            fish_id = int(fish_id)
            my_radar_blips[drone_id].append(RadarBlip(fish_id, dir))

        # Mise à jour de l'état des drones
        for drone_id, drone in drone_by_id.items():
            if drone_is_near_surface(drone) and drone_has_scans(drone):
                # Déplacer le drone vers la surface pour enregistrer les scans
                move_to_surface(drone)
            else:
                # Sélectionner un poisson cible et calculer le chemin
                target_fish_id, target_pos, light = select_target(drone, visible_fish, scanned_fish_ids, type_bonus_tracker, color_bonus_tracker)
                
                if target_pos:
                    # Calculer le chemin vers le poisson cible
                    path = a_star(drone, Fish(target_fish_id, target_pos, Vector(0, 0), FishDetail(0, 0)), visible_fish, MAP_SIZE)

                    # Déterminer le prochain mouvement sur le chemin
                    next_move = get_next_move(path, drone)
                    print(f"MOVE {next_move.x} {next_move.y} {light}")
                else:
                    # Utiliser une stratégie de repli ou mouvement aléatoire
                    target_x, target_y, light = random_movement_strategy(drone, visible_fish, MAP_SIZE, MAP_SIZE, SCAN_RADIUS)
                    print(f"MOVE {target_x} {target_y} {light}")

            # Mettre à jour l'état du jeu en fonction de l'action du drone
            update_game_state(drone, visible_fish, scanned_fish_ids)

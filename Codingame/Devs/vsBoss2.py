"""
Dans la fonction select_target, les poissons cibles sont sélectionnés en suivant une approche basée sur leur potentiel de points. Voici comment cela fonctionne :

Filtrage des poissons déjà scannés:

Tout d'abord, la liste des poissons visibles est filtrée pour exclure ceux qui ont déjà été scannés. Cela se fait en comparant les identifiants des poissons visibles avec ceux stockés dans l'ensemble scanned_fish_ids.
Calcul du potentiel de points:

Pour chaque poisson non scanné, la fonction calculate_potential_points est utilisée pour déterminer son potentiel de points. Cette fonction prend en compte plusieurs facteurs pour calculer le nombre de points potentiels que le scan de ce poisson peut rapporter. Ces facteurs comprennent s'il s'agit du premier scan du poisson, s'il correspond à un type ou une couleur spécifique offrant un bonus, etc.
Sélection du poisson avec le plus haut potentiel de points:

Une fois que le potentiel de points de chaque poisson non scanné a été calculé, la fonction sélectionne le poisson avec le plus haut potentiel de points en utilisant la fonction max de Python avec une fonction de comparaison appropriée.
Retour de la cible sélectionnée:

La fonction retourne l'identifiant, la position et un indicateur de lumière pour la cible sélectionnée. Si aucun poisson cible n'est trouvé (par exemple, si tous les poissons visibles ont déjà été scannés), elle retourne None pour l'identifiant et la position de la cible, et 0 pour l'indicateur de lumière.
En résumé, les poissons cibles sont sélectionnés en comparant leur potentiel de points, avec des préférences données aux poissons qui n'ont pas encore été scannés et qui offrent des bonus supplémentaires en termes de type ou de couleur.
"""

from typing import List, NamedTuple, Dict
import random

MAX_SCAN_RADIUS = 2000
SCAN_RADIUS = 800

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
    
# Fonctions pour la stratégie de mouvement avancée
def distance(point1: Vector, point2: Vector) -> float:
    """Calcule la distance euclidienne entre deux points."""
    return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5

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


# def select_target(drone: Drone, visible_fish: List[Fish], scanned_fish_ids: set) -> (int, Vector, int):
#     """Sélectionne le poisson cible pour le drone, en ignorant les poissons déjà scannés."""
#     if not visible_fish:
#         return None, None, 0  # Aucun poisson visible, retourner None avec light éteinte

#     # Filtrer les poissons déjà scannés
#     unscanned_fish = [
#         fish for fish in visible_fish if fish.fish_id not in scanned_fish_ids
#     ]

#     if not unscanned_fish:
#         return None, None, 0  # Aucun poisson non-scanné, retourner None avec light éteinte
    
#     # Choisissez le poisson le plus proche ou le plus précieux parmi les non-scannés
#     target_fish = min(unscanned_fish, key=lambda fish: distance(drone.pos, fish.pos))
    
#     # Retournez également l'identifiant du poisson cible et light allumée
#     return target_fish.fish_id, target_fish.pos, 1


# Fonction pour déterminer un mouvement aléatoire des drones
def random_movement_strategy(drone: Drone, visible_fish: List[Fish], map_width: int, map_height: int, detection_radius: int):
    # Choisir un point aléatoire sur la carte
    target_x = random.randint(0, map_width)
    target_y = random.randint(0, map_height)

    # Vérifier si un poisson est à proximité
    fish_nearby = any(
        distance(drone.pos, fish.pos) <= detection_radius
        for fish in visible_fish
    )

    # Allumer la lumière seulement si un poisson est à proximité
    light = 1 if fish_nearby else 0

    return target_x, target_y, light

# Dictionnaire pour stocker les détails des poissons
fish_details: Dict[int, FishDetail] = {}

# Lecture du nombre de poissons et enregistrement de leurs détails
fish_count = int(input())
for _ in range(fish_count):
    fish_id, color, _type = map(int, input().split())
    fish_details[fish_id] = FishDetail(color, _type)

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
    foe_score = int(input())

    # Lecture des informations de scan pour les joueurs
    my_scan_count = int(input())
    for _ in range(my_scan_count):
        fish_id = int(input())
        my_scans.append(fish_id)

    foe_scan_count = int(input())
    for _ in range(foe_scan_count):
        fish_id = int(input())
        foe_scans.append(fish_id)

    # Lecture des informations des drones
    my_drone_count = int(input())
    for _ in range(my_drone_count):
        drone_id, drone_x, drone_y, dead, battery = map(int, input().split())
        pos = Vector(drone_x, drone_y)
        drone = Drone(drone_id, pos, dead == "1", battery, [])
        drone_by_id[drone_id] = drone
        my_drones.append(drone)
        my_radar_blips[drone_id] = []

    foe_drone_count = int(input())
    for _ in range(foe_drone_count):
        drone_id, drone_x, drone_y, dead, battery = map(int, input().split())
        pos = Vector(drone_x, drone_y)
        drone = Drone(drone_id, pos, dead == "1", battery, [])
        drone_by_id[drone_id] = drone
        foe_drones.append(drone)

    # Lecture des scans des drones
    drone_scan_count = int(input())
    for _ in range(drone_scan_count):
        drone_id, fish_id = map(int, input().split())
        drone_by_id[drone_id].scans.append(fish_id)

    # Lecture et stockage des poissons visibles
    visible_fish_count = int(input())
    for _ in range(visible_fish_count):
        fish_id, fish_x, fish_y, fish_vx, fish_vy = map(int, input().split())
        pos = Vector(fish_x, fish_y)
        speed = Vector(fish_vx, fish_vy)
        visible_fish.append(Fish(fish_id, pos, speed, fish_details[fish_id]))

    # Lecture des informations de radar
    my_radar_blip_count = int(input())
    for _ in range(my_radar_blip_count):
        drone_id, fish_id, dir = input().split()
        drone_id = int(drone_id)
        fish_id = int(fish_id)
        my_radar_blips[drone_id].append(RadarBlip(fish_id, dir))

    # Dans la boucle de jeu
    for drone in my_drones:
        target_fish_id, target_pos, light = select_target(drone, visible_fish, scanned_fish_ids, type_bonus_tracker, color_bonus_tracker)
        if target_pos:
            # Déplacez le drone vers le poisson cible
            print(f"MOVE {target_pos.x} {target_pos.y} {light}")
            
            # Après le déplacement, confirmez si le poisson a été scanné
            if distance(drone.pos, target_pos) <= SCAN_RADIUS:  # SCAN_RADIUS est le rayon dans lequel le poisson est considéré comme scanné
                scanned_fish_ids.add(target_fish_id)
                # Si c'est le premier scan, ajoutez à first_scan_bonus
                if target_fish_id not in first_scan_bonus:
                    first_scan_bonus.add(target_fish_id)
                    # Doublez les points pour le premier scan

                # Mettre à jour les bonus trackers
                type_bonus_tracker[fish_details[target_fish_id].type] -= 1
                color_bonus_tracker[fish_details[target_fish_id].color] -= 1

        else:
            # Si aucun poisson cible n'est trouvé, utilisez une stratégie de repli
            target_x, target_y, light = random_movement_strategy(drone, visible_fish, 10000, 10000, 800)  # Assurez-vous que le rayon de détection est correct
            print(f"MOVE {target_x} {target_y} {light}")

    # Assurez-vous que toutes les fonctions utilisées dans cette logique sont correctement définies et implémentées.
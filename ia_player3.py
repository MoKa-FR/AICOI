from typing import List, NamedTuple, Dict
import random


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


def select_target(
    drone: Drone, visible_fish: List[Fish], scanned_fish_ids: set
) -> (Vector, int):
    """Sélectionne le poisson cible pour le drone, en ignorant les poissons déjà scannés."""
    if not visible_fish:
        return None, 1  # Aucun poisson visible, retourner None avec light activé

    # Filtrer les poissons déjà scannés
    unscanned_fish = [
        fish for fish in visible_fish if fish.fish_id not in scanned_fish_ids
    ]

    if not unscanned_fish:
        return None, 1  # Aucun poisson non-scanné, retourner None avec light activé

    # Choisissez le poisson le plus proche ou le plus précieux parmi les non-scannés
    target_fish = min(unscanned_fish, key=lambda fish: distance(drone.pos, fish.pos))
    return target_fish.pos, 1  # Retourner la position du poisson avec light activé


# Fonction pour déterminer un mouvement aléatoire des drones
def random_movement_strategy(drone: Drone, max_x: int, max_y: int):
    target_x = random.randint(0, max_x)
    target_y = random.randint(0, max_y)
    light = 1  # Active toujours la lumière (peut être modifié)
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
        target_pos, light = select_target(drone, visible_fish, scanned_fish_ids)
        if target_pos:
            # Déplacez le drone vers le poisson cible
            print(f"MOVE {target_pos.x} {target_pos.y} {light}")
        else:
            # Aucun poisson cible non scanné, appliquez une stratégie de repli
            target_x, target_y, light = random_movement_strategy(
                drone, max_x=10000, max_y=10000
            )
            print(f"MOVE {target_x} {target_y} {light}")

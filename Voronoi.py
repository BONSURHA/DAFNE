import os
import math
import random
import shutil
import cv2
import numpy as np
from PIL import Image, ImageDraw
from urllib.request import urlopen


def calculate_num_sites(width, height):
    return int(math.sqrt(width * height))


def image_name(url):
    split_url = url.split("/")
    file_name = split_url[-1]
    name, _ = os.path.splitext(file_name)
    return name


def create_fragment_image(fragment_cell, input_image):
    min_x = min(point[0] for point in fragment_cell)
    max_x = max(point[0] for point in fragment_cell)
    min_y = min(point[1] for point in fragment_cell)
    max_y = max(point[1] for point in fragment_cell)

    fragment_width = max_x - min_x + 1
    fragment_height = max_y - min_y + 1

    fragment_image = Image.new("RGBA", (fragment_width, fragment_height))
    draw = ImageDraw.Draw(fragment_image)

    for point in fragment_cell:
        x, y = point
        pixel = input_image.getpixel((x, y))
        draw.point((x - min_x, y - min_y), fill=pixel)

    return fragment_image


def create_voronoi_with_centroids(width, height, n):
    points = [(int(random.uniform(0, width)), int(random.uniform(0, height))) for _ in range(n)]
    voronoi_cells = {site: [] for site in points}

    for x in range(width):
        for y in range(height):
            point = (x, y)
            closest_site = find_closest_cell(point, points)
            voronoi_cells[closest_site].append(point)

    return voronoi_cells, points


def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def find_closest_cell(point, points):
    closest_site = None
    min_distance = float('inf')

    for site in points:
        distance = euclidean_distance(point, site)
        if distance < min_distance:
            min_distance = distance
            closest_site = site

    return closest_site



# Funzione per rimuovere casualmente una percentuale dei frammenti
def remove_random_fragments(fragments, percent_to_remove):
    # Calcola il numero di frammenti da rimuovere
    num_fragments_to_remove = int(len(fragments) * percent_to_remove)

    # Assicurati che il numero di frammenti da rimuovere sia almeno 1
    num_fragments_to_remove = max(num_fragments_to_remove, 1)

    print(num_fragments_to_remove)

    # Converte le chiavi del dizionario in una lista
    fragment_keys = list(fragments.keys())

    # Estrai in modo casuale i frammenti da rimuovere
    fragments_to_remove = random.sample(fragment_keys, num_fragments_to_remove)

    # Rimuovi i frammenti estratti
    for fragment_key in fragments_to_remove:
        del fragments[fragment_key]

    return fragments


# Funzione per applicare un'erosione ai frammenti
def apply_erosion_to_fragments(fragments):
    # Trova il frammento più piccolo come struttura per l'erosione
    smallest_fragment = min(fragments.values(), key=lambda x: x.size[0] * x.size[1])

    # Applica l'erosione a tutti i frammenti utilizzando il frammento più piccolo come struttura
    eroded_fragments = {}

    smallest_fragment_gray = smallest_fragment.convert("L")
    kernel = np.array(smallest_fragment_gray)

    for centroid, fragment in fragments.items():
        # Converti l'immagine in formato OpenCV
        fragment_cv = np.array(fragment)
        fragment_cv = cv2.cvtColor(fragment_cv, cv2.COLOR_RGBA2BGRA)  # Usa BGRA invece di RGBA

        # Applica l'erosione all'immagine utilizzando il kernel
        eroded_fragment_cv = cv2.erode(fragment_cv, kernel, iterations=1)

        # Converti l'immagine risultante in formato PIL
        eroded_fragment = Image.fromarray(cv2.cvtColor(eroded_fragment_cv, cv2.COLOR_BGRA2RGBA))

        eroded_fragments[centroid] = eroded_fragment

    return eroded_fragments



def split_image_in_fragment(url, output_directory, percent_to_remove):
    image = Image.open(urlopen(url))
    width, height = image.size
    n = calculate_num_sites(width, height)
    print(n)

    path = output_directory + "/" + image_name(url)
    path_resources = output_directory + "/" + image_name(url) + "/resources"
    path_fragments = output_directory + "/" + image_name(url) + "/fragments"
    path_fragments_eroded = output_directory + "/" + image_name(url) + "/fragments/fragments_eroded"
    path_fragments_normal = output_directory + "/" + image_name(url) + "/fragments/fragments_normal"

    if os.path.exists(f"{path}"):
        shutil.rmtree(f"{path}", ignore_errors=True)

    os.makedirs(path_resources)
    os.mkdir(path_fragments)
    os.mkdir(path_fragments_eroded)
    os.mkdir(path_fragments_normal)

    voronoi_cells, voronoi_centroids = create_voronoi_with_centroids(width, height, n)

    # Dizionario per salvare i frammenti e i rispettivi angoli di rotazione
    fragments = {}

    # Lista per ordinare le chiavi (coordinate dei centroidi)
    # sorted_keys = sorted(voronoi_cells.keys(), key=lambda x: voronoi_centroids[x])

    for site in sorted_keys:
        fragment_cell = voronoi_cells[site]
        fragment_image = create_fragment_image(fragment_cell, image)

        # Estrai il centro dalla posizione ordinata
        centroid = voronoi_centroids[site]

        fragments[centroid] = fragment_image


    # Rimuovi casualmente una percentuale dei frammenti
    # fragments = remove_random_fragments(fragments, percent_to_remove)

    # Applica un'erosione ai frammenti
    # eroded_fragments = apply_erosion_to_fragments(fragments)

    for centroid, fragment_image in fragments.items():

        # Genera un angolo di rotazione casuale tra 0 e 360 gradi
        # rotation_angle = random.uniform(0, 360)

        # Ruota il frammento dell'angolo generato
        # rotated_fragment = fragment_image.rotate(rotation_angle, expand=True)

        # Aggiungi il frammento ruotato al dizionario utilizzando il centro come chiave
        # fragments[centroid] = rotated_fragment

        # fragment_image.save(f"{path_fragments_eroded}/eroded_fragment_{centroid}.png")

        # Scrivi le informazioni dei frammenti (centro e angolo di rotazione) nel file di testo
        with open(f"{path_resources}/fragment_info.txt", "a") as info_file:
            info_file.write(f"Centroid: {centroid}\n")
            # info_file.write(f"Rotation Angle: {rotation_angle} degrees\n")
            info_file.write("\n")


    for centroid, fragment_image in fragments.items():
        fragment_image.save(f"{path_fragments_normal}/eroded_fragment_{centroid}.png")



if __name__ == "__main__":
    output_directory = "./output"
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Magi.jpg/600px-Leonardo_Magi.jpg"
    percent_to_remove = 0.4
    split_image_in_fragment(url, output_directory, percent_to_remove)






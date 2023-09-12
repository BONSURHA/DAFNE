import os
import math
import random
import shutil
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
    points = [(random.uniform(0, width), random.uniform(0, height)) for _ in range(n)]
    voronoi_cells = {site: [] for site in points}

    for x in range(width):
        for y in range(height):
            point = (x, y)
            closest_site = find_closest_cell(point, points)
            voronoi_cells[closest_site].append(point)

    voronoi_centroids = {site: calculate_centroid(cell) for site, cell in voronoi_cells.items()}
    return voronoi_cells, voronoi_centroids


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


def calculate_centroid(cell):
    num_points = len(cell)
    if num_points == 0:
        return None

    sum_x = sum(point[0] for point in cell)
    sum_y = sum(point[1] for point in cell)
    centroid_x = int(sum_x / num_points)
    centroid_y = int(sum_y / num_points)
    return (centroid_x, centroid_y)


def find_closest_fragment(selected_fragment, fragments):

    # Calcola il centro di ciascun frammento selezionato
    current_centroid, current_fragment = selected_fragment

    min_distance = float('inf')
    closest_fragment = None

    for other_centroid, other_fragment in fragments.items():
        if current_centroid != other_centroid:
            # Calcola la distanza euclidea tra i centri dei frammenti
            distance = euclidean_distance(current_centroid,other_centroid)
            if distance < min_distance:
                min_distance = distance
                closest_fragment = (other_centroid, other_fragment)

    return closest_fragment


def combine_fragments(selected_fragment, closest_fragment):

    centroid1, fragment1 = selected_fragment
    centroid2, fragment2 = closest_fragment

    x1, y1 = centroid1
    x2, y2 = centroid2

    dx = x1 - x2
    dy = y1 - y2

    # Calcola le dimensioni dei tasselli
    w1, h1 = fragment1.size
    w2, h2 = fragment2.size

    print(str(w1) + " + " + str(h1))
    print(str(w2) + " + " + str(h2))

    # Sovrapponi le due immagini dei tasselli tenendo conto degli spostamenti
    new_width = w1 + w2
    new_height = h1 + h2

    print(str(new_width) + " + " + str(new_height))

    # Calcola le dimensioni dell'immagine risultante
    new_width = abs(dx) + w1 + w2
    new_height = abs(dy) + h1 + h2

    # Crea un'immagine vuota delle dimensioni corrette
    result_image = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))

    # Calcola le coordinate iniziali per il taglio delle due immagini
    x1_crop = max(0, dx)
    y1_crop = max(0, dy)
    x2_crop = max(0, -dx)
    y2_crop = max(0, -dy)

    # Copia il primo tassello nell'immagine risultante
    result_image.paste(fragment1, (x1_crop, y1_crop))

    # Calcola le coordinate iniziali per il secondo tassello in modo che sia accanto al primo
    x2_new = x1_crop + w1
    y2_new = y1_crop + h1

    # Copia il secondo tassello nell'immagine risultante
    result_image.paste(fragment2, (x2_new, y2_new))


    combined_centroid = (int((x1 + x2)/2), int((y1 + y2)/2))

    return (combined_centroid, result_image)


def split_image_in_fragment(url, output_directory, num_random_fragments):
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
    sorted_keys = sorted(voronoi_cells.keys(), key=lambda x: voronoi_centroids[x])

    for site in sorted_keys:
        fragment_cell = voronoi_cells[site]
        fragment_image = create_fragment_image(fragment_cell, image)

        # Estrai il centro dalla posizione ordinata
        centroid = voronoi_centroids[site]

        fragments[centroid] = fragment_image

    # Seleziona casualmente un numero specifico di frammenti
    selected_fragments = random.sample(list(fragments.items()), num_random_fragments)

    for selected_fragment in selected_fragments:
        closest_fragment = find_closest_fragment(selected_fragment, fragments)
        centroid1, fragment1 = selected_fragment
        centroid2, fragment2 = closest_fragment
        combined_centroid, combined_fragment = combine_fragments(selected_fragment, closest_fragment)
        del fragments[centroid1]
        del fragments[centroid2]
        fragments[combined_centroid] = combined_fragment

        # Rinomina i file di output in base alle coordinate dei centroidi
        current_filename = f"{path_fragments}/fragment_{centroid1[0]}_{centroid1[1]}.png"
        closest_filename = f"{path_fragments}/fragment_{centroid2[0]}_{centroid2[1]}.png"
        combined_filename = f"{path_fragments}/combined_fragment_{combined_centroid[0]}_{combined_centroid[1]}.png"

        fragment1.save(current_filename)
        fragment2.save(closest_filename)







if __name__ == "__main__":
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Magi.jpg/600px-Leonardo_Magi.jpg"
    output_directory = "output"
    num_random_fragments = 5  # Cambia questo numero a tuo piacimento
    split_image_in_fragment(url, output_directory, num_random_fragments)






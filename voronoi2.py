from PIL import Image, ImageDraw
import math
import random
import os
from urllib.request import urlopen


def image_name(url):

    split_url = url.split("/")
    file_name = split_url[-1]
    name, _ = os.path.splitext(file_name)
    return name


# Funzione per calcolare la distanza euclidea tra due punti
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


# Funzione per trovare la cella Voronoi più vicina a un punto
def find_closest_cell(point, sites):
    closest_site = None
    min_distance = float('inf')

    for site in sites:
        distance = euclidean_distance(point, site)
        if distance < min_distance:
            min_distance = distance
            closest_site = site

    return closest_site


# creare una tassellazione Voronoi
def create_voronoi(width, height, num_sites):
    # sites = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_sites)]
    sites = [(random.uniform(0, width), random.uniform(0, height)) for _ in range(num_sites)]

    voronoi_cells = {site: [] for site in sites}

    for x in range(width):
        for y in range(height):
            point = (x, y)
            closest_site = find_closest_cell(point, sites)
            voronoi_cells[closest_site].append(point)

    return voronoi_cells


def calculate_num_sites(width, height):
    return int(math.sqrt(width * height))


# Funzione per creare un'immagine del frammento con dimensioni adattate alla cella
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


# Funzione per calcolare il centroide di una cella Voronoi
def calculate_centroid(cell):
    num_points = len(cell)
    if num_points == 0:
        return None

    sum_x = sum(point[0] for point in cell)
    sum_y = sum(point[1] for point in cell)
    centroid_x = sum_x / num_points
    centroid_y = sum_y / num_points
    return (centroid_x, centroid_y)

# Modifica della funzione create_voronoi per restituire anche i centroidi delle celle Voronoi
def create_voronoi_with_centroids(width, height, num_sites):
    sites = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_sites)]
    voronoi_cells = {site: [] for site in sites}

    for x in range(width):
        for y in range(height):
            point = (x, y)
            closest_site = find_closest_cell(point, sites)
            voronoi_cells[closest_site].append(point)

    voronoi_centroids = {site: calculate_centroid(cell) for site, cell in voronoi_cells.items()}
    return voronoi_cells, voronoi_centroids


# Funzione per suddividere l'immagine in frammenti e salvarli uno a uno
def split_and_save_fragments(url, output_directory):
    input_image = Image.open(urlopen(url))
    width, height = input_image.size
    num_sites = calculate_num_sites(width, height)
    print(width)
    print(height)
    print(num_sites)

    path = output_directory + "/" + image_name(url) + str(int(random.uniform(0,1000)))

    try:
        os.mkdir(path)
        print("Folder %s created!" % path)
        voronoi_cells = create_voronoi(width, height, num_sites)

        for site, fragment_cell in voronoi_cells.items():
            fragment_image = create_fragment_image(fragment_cell, input_image)
            fragment_image.save(f"{path}/fragment_{site}.png")

    except FileExistsError:
        print("Folder %s already exists" % path)


def split_and_save_fragments_1(url, output_directory):
    input_image = Image.open(urlopen(url))
    width, height = input_image.size
    num_sites = calculate_num_sites(width, height)
    print(width)
    print(height)
    print(num_sites)

    sites = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_sites)]

    voronoi_cells, voronoi_centroids = create_voronoi_with_centroids(width, height, num_sites)

    # Salva le informazioni dei frammenti su un file di testo
    with open(f"{output_directory}/fragment_info.txt", "w") as info_file:
        for site, fragment_cell in voronoi_cells.items():
            # Scrivi le informazioni dei frammenti (site e centro) nel file di testo
            info_file.write(f"Fragment {site}:\n")
            info_file.write(f"Centroid: {voronoi_centroids[site]}\n\n")



# prova


if __name__ == "__main__":
    output_directory = "./output"
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Magi.jpg/600px-Leonardo_Magi.jpg"
    print(output_directory)
    split_and_save_fragments_1(url, output_directory)

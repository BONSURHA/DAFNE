import os
import math
import random
from PIL import Image
from urllib.request import urlopen


def calculate_num_sites(width, height):
    return int(math.sqrt(width * height))


def image_name(url):
    split_url = url.split("/")
    file_name = split_url[-1]
    name, _ = os.path.splitext(file_name)
    return name


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
    centroid_x = sum_x / num_points
    centroid_y = sum_y / num_points
    return (centroid_x, centroid_y)


def split_image_in_fragment(url, output_directory):
    image = Image.open(urlopen(url))
    width, height = image.size
    n = calculate_num_sites(width, height)

    voronoi_cells, voronoi_centroids = create_voronoi_with_centroids(width, height, n)

    path = output_directory + "/" + image_name(url) + "/resources"
    path_1 = output_directory + "/" + image_name(url) + "/fragments"

    os.makedirs(path)
    os.mkdir(path_1)


    # Salva le informazioni dei frammenti su un file di testo
    with open(f"{path}/fragment_info.txt", "w") as info_file:
        for site, fragment_cell in voronoi_cells.items():
            # Scrivi le informazioni dei frammenti (site e centro) nel file di testo
            info_file.write(f"Fragment {site}:\n")
            info_file.write(f"Centroid: {voronoi_centroids[site]}\n\n")


if __name__ == "__main__":
    output_directory = "./output"
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Magi.jpg/600px-Leonardo_Magi.jpg"
    split_image_in_fragment(url, output_directory)






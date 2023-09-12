import os
import math
import shutil
import numpy as np
from PIL import Image, ImageDraw
from urllib.request import urlopen


def calculate_points(height, width):
    num_points = int(math.sqrt(height * width))
    points = np.random.randint(0, height, size=(num_points, 2))
    points[:, 1] = np.random.randint(0, width, size=num_points)
    return [tuple(point) for point in points]


def save_fragments_to_folder(fragments, folder_path):
    for i, fragment in enumerate(fragments):
        # Define the file path for the fragment
        file_path = os.path.join(folder_path, f'fragment_{i}.png')
        # Save the fragment as a PNG image
        fragment.save(file_path, 'PNG')


def image_name(url):
    split_url = url.split("/")
    file_name = split_url[-1]
    name, _ = os.path.splitext(file_name)
    return name


def create_fragment_image(voronoi_cells, input_image):
    fragments = []

    for key in voronoi_cells.keys():
        cell = voronoi_cells[key]
        min_x = min(point[0] for point in cell)
        max_x = max(point[0] for point in cell)
        min_y = min(point[1] for point in cell)
        max_y = max(point[1] for point in cell)

        fragment_width = max_x - min_x + 1
        fragment_height = max_y - min_y + 1

        fragment_image = Image.new("RGBA", (fragment_width, fragment_height))
        draw = ImageDraw.Draw(fragment_image)

        for point in cell:
            x, y = point
            pixel = input_image.getpixel((x, y))
            draw.point((x - min_x, y - min_y), fill=pixel)

        fragments.append(fragment_image)

    return fragments


def create_voronoi(width, height, points):
    voronoi_cells = {site: [] for site in points}

    for x in range(width):
        for y in range(height):
            point = (x, y)
            closest_site = find_closest_cell(point, points)
            voronoi_cells[closest_site].append(point)

    return voronoi_cells


def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def find_closest_cell(point, points):
    closest_site = None
    min_distance = float('inf')

    for site in points:
        distance = euclidean_distance(point, site)
        if distance < min_distance:
            min_distance = distance
            closest_site = site

    return closest_site


def DAFNE(url, output_directory):
    image = Image.open(urlopen(url))
    width, height = image.size
    points = calculate_points(width, height)
    n = len(points)

    path = output_directory + "/" + image_name(url)

    if os.path.exists(path):
        shutil.rmtree(path)

    path = output_directory + "/" + image_name(url) + "/resources"
    path_fragment = output_directory + "/" + image_name(url) + "/fragments"

    os.makedirs(path)
    os.mkdir(path_fragment)

    voronoi_cells = create_voronoi(width, height, points)

    fragments = create_fragment_image(voronoi_cells, image)

    save_fragments_to_folder(fragments, path_fragment)


if __name__ == "__main__":
    output_directory = "./output"
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Magi.jpg/600px-Leonardo_Magi.jpg"
    DAFNE(url, output_directory)






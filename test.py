import os
import math
import shutil
import random
import numpy as np
from PIL import Image, ImageDraw
from urllib.request import urlopen


def calculate_points(height, width):
    num_points = int(math.sqrt(height * width))
    points = np.random.randint(0, height, size=(num_points, 2))
    points[:, 1] = np.random.randint(0, width, size=num_points)
    return [tuple(point) for point in points]


def find_closest_fragment(selected_fragment, fragments):
    min_distance = float('inf')
    closest_fragment = None
    sel_point, _ = selected_fragment

    for point, fragment in fragments:
        if sel_point != point:
            distance = euclidean_distance(sel_point, point)
            if distance < min_distance:
                min_distance = distance
                closest_fragment = fragment
                closest_point = point

    return (closest_point, closest_fragment)


def combine_fragment(fragments, voronoi_cells, image, num_combined_fragments):
    selected_fragments = random.sample(fragments, num_combined_fragments)
    combined_fragments = []

    for selected_fragment in selected_fragments:
        closest_fragment = find_closest_fragment(selected_fragment, fragments)
        selected_cell = voronoi_cells[selected_fragment[0]]
        closest_cell = voronoi_cells[closest_fragment[0]]

        width = selected_fragment[1].width + closest_fragment[1].width
        height = selected_fragment[1].height + closest_fragment[1].height

        combined_fragment = Image.new("RGBA", (width, height))
        draw = ImageDraw.Draw(combined_fragment)

        if selected_fragment[0] < closest_fragment[0]:
            min_x = min(point[0] for point in selected_cell)
            min_y = min(point[1] for point in selected_cell)
        else:
            min_x = min(point[0] for point in closest_cell)
            min_y = min(point[1] for point in closest_cell)


        for point in selected_cell:
            x, y = point
            pixel = image.getpixel((x, y))
            draw.point((x - min_x, y - min_y), fill=pixel)



        for point in closest_cell:
            x, y = point
            pixel = image.getpixel((x, y))
            draw.point((x - min_x, y - min_y), fill=pixel)

        combined_fragments.append((selected_fragment[0],combined_fragment))

    return combined_fragments


        


def save_fragments_to_folder(fragments, folder_path):

    for i, fragment in enumerate(fragments):
        # Define the file path for the fragment
        file_path = os.path.join(folder_path, f'fragment_{i}.png')
        # Save the fragment as a PNG image
        fragment[1].save(file_path, 'PNG')


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

        fragments.append((key, fragment_image))

    return fragments


def create_voronoi(width, height, points):
    voronoi_cells = {point: [] for point in points}

    for x in range(width):
        for y in range(height):
            point = (x, y)
            closest_point = find_closest_cell(point, points)
            voronoi_cells[closest_point].append(point)

    return voronoi_cells


def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def find_closest_cell(point, points):
    closest_point = None
    min_distance = float('inf')

    for p in points:
        distance = euclidean_distance(point, p)
        if distance < min_distance:
            min_distance = distance
            closest_point = p

    return closest_point


def DAFNE(url, output_directory, num_combined_fragment):
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

    combined_fragments = combine_fragment(fragments, voronoi_cells, image, num_combined_fragment)

    save_fragments_to_folder(combined_fragments, path_fragment)

    # save_fragments_to_folder(fragments, path_fragment)


if __name__ == "__main__":
    output_directory = "./output"
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Magi.jpg/600px-Leonardo_Magi.jpg"
    num_combined_fragment = 10
    DAFNE(url, output_directory, num_combined_fragment)






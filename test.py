import os
import math
import shutil
import random

import cv2
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
    closest_point = None
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
    combined_fragments = fragments

    for selected_fragment in selected_fragments:
        closest_fragment = find_closest_fragment(selected_fragment, fragments)
        selected_cell = voronoi_cells[selected_fragment[0]]
        closest_cell = voronoi_cells[closest_fragment[0]]

        width = selected_fragment[1].width + closest_fragment[1].width
        height = selected_fragment[1].height + closest_fragment[1].height

        combined_fragment = Image.new("RGBA", (width, height))
        draw = ImageDraw.Draw(combined_fragment)

        if selected_fragment[0][0] < closest_fragment[0][0]:
            min_x = min(point[0] for point in selected_cell)
        else:
            min_x = min(point[0] for point in closest_cell)

        if selected_fragment[0][1] < closest_fragment[0][1]:
            min_y = min(point[1] for point in selected_cell)
        else:
            min_y = min(point[1] for point in closest_cell)

        for point in selected_cell:
            x, y = point
            pixel = image.getpixel((x, y))
            draw.point((x - min_x, y - min_y), fill=pixel)

        for point in closest_cell:
            x, y = point
            pixel = image.getpixel((x, y))
            draw.point((x - min_x, y - min_y), fill=pixel)

        x = int((selected_fragment[0][0] + closest_fragment[0][0])/2)
        y = int((selected_fragment[0][1] + closest_fragment[0][1])/2)

        combined_point = (x, y)
        combined_fragments.remove(selected_fragment)
        combined_fragments.remove(closest_fragment)
        combined_fragments.append((combined_point, combined_fragment))

    return combined_fragments


def random_fragments_removal(fragments, percentage):
    fragments_list = fragments
    fragments_to_remove = random.sample(fragments, int((len(fragments_list)*percentage)))
    for fragment_to_remove in fragments_to_remove:
        fragments_list.remove(fragment_to_remove)

    return fragments_list


def save_fragments_to_folder(fragments, folder_path, path):
    for i, fragment in enumerate(fragments):
        # Define the file path for the fragment
        file_path = os.path.join(folder_path, f'fragment_{i}.png')
        # Save the fragment as a PNG image
        fragment[1].save(file_path, 'PNG')
        with open(f"{path}/fragment_info.txt", "a") as info_file:
            info_file.write(f"fragment_{i}.png: {fragment[1]},{fragment[0]},{fragment[2]}\n")
            info_file.write("\n")


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


def fragment_erosion(fragments):
    eroded_fragments = []

    for point, fragment in fragments:

        fragment_array = np.array(fragment)

        # fragment_array = cv2.cvtColor(fragment_array, cv2.COLOR_RGBA2BGRA)

        height, width, _ = fragment_array.shape

        # first erosion
        # kernel_size = (max(3, width // 20), max(3, height // 20))
        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)

        # eroded_fragment_array = cv2.erode(fragment_array, kernel, cv2.BORDER_REFLECT)

        # second erosion
        kernel_5 = np.ones((5, 5), np.uint8)
        eroded_fragment_array = cv2.erode(fragment_array, kernel_5, cv2.BORDER_REFLECT)
        # eroded_fragment_array = cv2.cvtColor(eroded_fragment_array, cv2.COLOR_BGRA2RGBA)
        eroded_fragment = Image.fromarray(eroded_fragment_array)
        eroded_fragments.append((point, eroded_fragment))

    return eroded_fragments


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


def rotate_fragment(fragments):
    rotate_fragments = []

    for point, fragment in fragments:
        angle = random.uniform(0, 360)
        fragment.rotate(angle, expand=True)
        rotate_fragments.append((point, fragment, angle))
    return rotate_fragments


def DAFNE(url, output_directory, num_combined_fragment, percentage):
    image = Image.open(urlopen(url))
    width, height = image.size
    points = calculate_points(width, height)

    path = output_directory + "/" + image_name(url)

    if os.path.exists(path):
        shutil.rmtree(path)

    path = output_directory + "/" + image_name(url) + "/resources"
    path_normal_fragment = output_directory + "/" + image_name(url) + "/fragments/normal_fragment"
    path_eroded_fragment = output_directory + "/" + image_name(url) + "/fragments/eroded_fragment"

    os.makedirs(path)
    os.makedirs(path_normal_fragment)
    os.mkdir(path_eroded_fragment)

    voronoi_cells = create_voronoi(width, height, points)

    fragments = create_fragment_image(voronoi_cells, image)

    combined_fragments = combine_fragment(fragments, voronoi_cells, image, num_combined_fragment)

    fragments = random_fragments_removal(combined_fragments, percentage)

    # eroded_fragments = fragment_erosion(fragments)

    fragments = rotate_fragment(fragments)

    save_fragments_to_folder(fragments, path_normal_fragment, path)
    # save_fragments_to_folder(eroded_fragments, path_eroded_fragment)




if __name__ == "__main__":
    output_directory = "./output"
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Magi.jpg/600px-Leonardo_Magi.jpg"
    num_combined_fragment = 10
    percentage = 0.2
    DAFNE(url, output_directory, num_combined_fragment, percentage)






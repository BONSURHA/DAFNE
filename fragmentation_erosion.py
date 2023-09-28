import os
import sys 
import cv2
import math
import io_tools
import random
import numpy as np
from PIL import Image, ImageDraw


def generate_random_points(min_distance, seed, num_fragments, width, height):
    if num_fragments == None:
        num_fragments = int(math.sqrt(height * width))

    points = []
    if seed != None:
        random.seed(seed)

    while len(points) < num_fragments:
        x = random.randint(0, width)
        y = random.randint(0, height)
        valid = True

        for point in points:
            if euclidean_distance((x, y), point) < (2 * min_distance):
                valid = False
                break

        if valid:
            points.append((x, y))

    return points


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


def create_voronoi(width, height, points):
    voronoi_cells = {point: [] for point in points}

    for x in range(width):
        for y in range(height):
            point = (x, y)
            closest_point = find_closest_cell(point, points)
            voronoi_cells[closest_point].append(point)

    return voronoi_cells


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

        diff = (min_x, min_y)
        for point in cell:
            x, y = point
            pixel = input_image.getpixel((x, y))
            draw.point((x - min_x, y - min_y), fill=pixel)
        fragments.append((key, diff, fragment_image))

    return fragments


def find_closest_fragment(selected_fragment, fragments):
    min_distance = float('inf')
    closest_fragment = None
    sel_point, _, _= selected_fragment

    for fragment in fragments:
        point,_,_ = fragment
        distance = euclidean_distance(sel_point, point)
        if distance < min_distance:
            min_distance = distance
            closest_fragment = fragment

    return closest_fragment


def combine_fragment(fragments, voronoi_cells, image, num_combined_fragments):
    selected_fragments = random.sample(fragments, num_combined_fragments)
    combined_fragments = []
    fragments_list = fragments

    for removed_fragment in selected_fragments:
        if removed_fragment in fragments:
            fragments_list.remove(removed_fragment)

    for selected_fragment in selected_fragments:
        closest_fragment = find_closest_fragment(selected_fragment, fragments)
        selected_cell = voronoi_cells[selected_fragment[0]]
        closest_cell = voronoi_cells[closest_fragment[0]]

        width = selected_fragment[2].width + closest_fragment[2].width
        height = selected_fragment[2].height + closest_fragment[2].height

        combined_fragment = Image.new("RGBA", (width, height))
        draw = ImageDraw.Draw(combined_fragment)

        x = int((selected_fragment[0][0] + closest_fragment[0][0])/2)
        y = int((selected_fragment[0][1] + closest_fragment[0][1])/2)

        combined_point = (x, y)

        if selected_fragment[0][0] < closest_fragment[0][0]:
            min_x = selected_fragment[1][0]
        else:
            min_x = closest_fragment[1][0]

        if selected_fragment[0][1] < closest_fragment[0][1]:
            min_y = selected_fragment[1][1]
        else:
            min_y = closest_fragment[1][1]

        diff = (min_x, min_y)

        for point in selected_cell:
            x, y = point
            pixel = image.getpixel((x, y))
            draw.point((x - min_x, y - min_y), fill=pixel)
        for point in closest_cell:
            x, y = point
            pixel = image.getpixel((x, y))
            draw.point((x - min_x, y - min_y), fill=pixel)

        fragments_list.remove(closest_fragment)
        combined_fragments.append((combined_point, diff, combined_fragment))

    fragments_list.extend(combined_fragments)
    random.shuffle(fragments_list)
    return fragments_list


def find_the_smallest_fragment(fragments):
    min_dimension = float('inf')
    smallest_fragment = None
    
    for _, _, fragment in fragments:
        height,  width = fragment.size
        dimension =    height * width
        if dimension < min_dimension:
            min_dimension = dimension
            smallest_fragment = fragment
            
    return smallest_fragment


def apply_random_color_degradation(fragment):

    # implementare hsv (lavorando su s e v, non h)
    r,g,b,a = fragment.split()
    cl_image = Image.merge('RGB', (r,g,b))
    fragment_array = cv2.cvtColor(np.array(cl_image), cv2.COLOR_RGB2HSV)

    s_degradation_factor = random.uniform(0.5, 1)
    v_degradation_factor = random.uniform(0.8, 1)

    fragment_array[:, :, 1] = fragment_array[:, :, 1] * s_degradation_factor
    fragment_array[:, :, 2] = fragment_array[:, :, 2] * v_degradation_factor

    degraded = Image.fromarray(cv2.cvtColor(fragment_array, cv2.COLOR_HSV2RGB))
    r, g, b = degraded.split()

    degraded_image = Image.merge('RGBA', (r, g, b, a))
        
    return degraded_image


def fragment_erosion(fragments, min_distance, erosion_probability, erosion_percentage):
    eroded_fragments = []
    probability = 1 - erosion_probability
    smallest_fragment = find_the_smallest_fragment(fragments)
    min_size = smallest_fragment.size

    for point, diff,fragment in fragments:

        size = fragment.size
        fragment_array = np.array(fragment)
        gray_array = cv2.cvtColor(fragment_array, cv2.COLOR_RGBA2GRAY)


        this_erosion_probability = random.random()

        # first erosion
        if this_erosion_probability >= probability:
            total_fragment_pixel = cv2.countNonZero(gray_array)
            ksize = int(math.sqrt(total_fragment_pixel) * erosion_percentage * 0.01)
            angle = random.uniform(0, 360)
            kernel_size = (ksize, ksize)
            rotation = cv2.getRotationMatrix2D((kernel_size[0] // 2, kernel_size[1] // 2), angle, 1)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
            kernel_rotated = cv2.warpAffine(kernel, rotation, kernel_size, borderMode=cv2.BORDER_CONSTANT)
            gray_array = cv2.erode(gray_array, kernel_rotated, iterations=1)

        # second erosion
        radius = random.randint(min_distance//2, max(min_size[0], min_size[1])//2)
        # radius = random.randint(1, min_distance//2)
        kernel = np.ones((radius, radius), np.float32) / (radius ** 2)
        gray_array = cv2.filter2D(gray_array, -1, kernel)
        fragment_array = cv2.bitwise_and(fragment_array, fragment_array, mask=gray_array)
        eroded_fragment = Image.fromarray(fragment_array)
        eroded_fragment = apply_random_color_degradation(eroded_fragment)
        eroded_fragments.append((point, diff, eroded_fragment))

    return eroded_fragments


def rotate_fragment(fragments):
    rotate_fragments = []

    for fragment in fragments:
        angle = random.uniform(0, 360)
        point, diff, fragment_to_rotate = fragment
        size = fragment_to_rotate.size
        rotated_fragment = fragment_to_rotate.rotate(angle, expand=True)
        size_rotate = rotated_fragment.size
        diff_x = diff[0] - ((size_rotate[0] - size[0])//2)
        diff_y = diff[1] - ((size_rotate[1] - size[1])//2)
        rotate_fragments.append((point, (diff_x, diff_y), rotated_fragment, angle))
    return rotate_fragments


def save_fragments_to_folder(fragments, folder_path):
    n = len(str(len(fragments)-1)) 
    for i, fragment in enumerate(fragments):
        # Define the file path for the fragment
        index = str(i).zfill(n)
        file_path = os.path.join(folder_path, f'fragment_{index}.png')
        # Save the fragment as a PNG image
        fragment[2].save(file_path, 'PNG')


def save_info(fragments, path):
    n = len(str(len(fragments)-1))
    for i, fragment in enumerate(fragments):
        coordinate, diff, _, angle = fragment
        index = str(i).zfill(n)
        with open(f"{path}/fragment_info.txt", "a") as info_file:
            file_path = f"fragment_{index}"
            info_file.write(f"{file_path}: {coordinate}; {diff}; {angle}\n")
            info_file.write("\n")


def generate_info(resources_path, seed, num_fragments, min_distance, erosion_probability, erosion_percentage):
    with open(f"{resources_path}/fragmentation_info.txt", "a") as info_file:
        info_file.write(f"seed: {seed}\n")
        info_file.write(f"num_fragments: {num_fragments}\n")
        info_file.write(f"min_distance: {min_distance}\n")
        info_file.write(f"erosion_probability: {erosion_probability}\n")
        info_file.write(f"erosion_percentage: {erosion_percentage}\n")


def generate_fragments(url, output_directory, num_fragments, min_distance, seed, erosion_probability, erosion_percentage):
    image = Image.open(url)

    name = io_tools.image_name(url)
    path, resources_path, fragment_path = io_tools.create_folder(name, output_directory)

    generate_info(resources_path, seed, num_fragments, min_distance, erosion_probability, erosion_percentage)

    width, height = image.size

    points = generate_random_points(min_distance, seed, num_fragments, width, height)
    num_combined_fragment = random.randint(1,int(math.sqrt(len(points))))

    io_tools.update_progress_bar(0, 100, "create voronoi (this op might take long)", 1)
    sys.stderr.flush()

    voronoi_cells = create_voronoi(width, height, points)
    io_tools.update_progress_bar(25, 100, "create fragments", 2)

    fragments = create_fragment_image(voronoi_cells, image)
    combined_fragments = combine_fragment(fragments, voronoi_cells, image, num_combined_fragment)
    io_tools.update_progress_bar(50, 100, "erode fragments", 3)
    sys.stderr.flush()

    eroded_fragments = fragment_erosion(combined_fragments, min_distance, erosion_probability, erosion_percentage)
    eroded_fragments = rotate_fragment(eroded_fragments)
    io_tools.update_progress_bar(75, 100, "save fragments", 4)
    save_fragments_to_folder(eroded_fragments, fragment_path)
    save_info(eroded_fragments, resources_path)
    io_tools.update_progress_bar(100, 100, "fragments saved", 4)
    sys.stderr.flush()

    return path
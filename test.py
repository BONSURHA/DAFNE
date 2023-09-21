import os
import sys 
import argparse
import math
import datetime
import random
import cv2
import numpy as np
from PIL import Image, ImageDraw


def image_name(url):
    split_url = url.split("/")
    file_name = split_url[-1]
    name, _ = os.path.splitext(file_name)
    return name


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
            if euclidean_distance((x, y), point) < min_distance:
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
        fragments.append(((key, diff), fragment_image))

    return fragments


def find_closest_fragment(selected_fragment, fragments):
    min_distance = float('inf')
    closest_fragment = None
    closest_point = None
    sel_point, _= selected_fragment

    for point, fragment in fragments:
        distance = euclidean_distance(sel_point[0], point[0])
        if distance < min_distance:
            min_distance = distance
            closest_fragment = fragment
            closest_point = point

    return (closest_point, closest_fragment)


def combine_fragment(fragments, voronoi_cells, image, num_combined_fragments):
    selected_fragments = random.sample(fragments, num_combined_fragments)
    combined_fragments = []

    for removed_fragment in selected_fragments:
        if removed_fragment in fragments:
            fragments.remove(removed_fragment)

    for selected_fragment in selected_fragments:
        closest_fragment = find_closest_fragment(selected_fragment, fragments)
        selected_cell = voronoi_cells[selected_fragment[0][0]]
        closest_cell = voronoi_cells[closest_fragment[0][0]]

        width = selected_fragment[1].width + closest_fragment[1].width
        height = selected_fragment[1].height + closest_fragment[1].height

        combined_fragment = Image.new("RGBA", (width, height))
        draw = ImageDraw.Draw(combined_fragment)

        x = int((selected_fragment[0][0][0] + closest_fragment[0][0][0])/2)
        y = int((selected_fragment[0][0][1] + closest_fragment[0][0][1])/2)

        combined_point = (x, y)

        if selected_fragment[0][0][0] < closest_fragment[0][0][0]:
            min_x = min(point[0] for point in selected_cell)
        else:
            min_x = min(point[0] for point in closest_cell)

        if selected_fragment[0][0][1] < closest_fragment[0][0][1]:
            min_y = min(point[1] for point in selected_cell)
        else:
            min_y = min(point[1] for point in closest_cell)

        diff = (min_x, min_y)

        for point in selected_cell:
            x, y = point
            pixel = image.getpixel((x, y))
            draw.point((x - min_x, y - min_y), fill=pixel)
        for point in closest_cell:
            x, y = point
            pixel = image.getpixel((x, y))
            draw.point((x - min_x, y - min_y), fill=pixel)

        fragments.remove(closest_fragment)
        combined_fragments.append(((combined_point, diff), combined_fragment))

    fragments.extend(combined_fragments)
    random.shuffle(fragments)
    return fragments

# farlo relativo all'immagine -> farlo in uno script a parte e faccio salvare eliminando i frammenti, (provare ad aggiungere gli spuri, cartella in input, opzionale), pulendo il file in resources
def random_fragments_removal(fragments, percentage):
    fragments_list = fragments
    fragments_to_remove = random.sample(fragments, int((len(fragments_list)*(percentage/100))))
    for fragment_to_remove in fragments_to_remove:
        fragments_list.remove(fragment_to_remove)

    return fragments_list


def find_the_smallest_fragment(fragments):
    min_dimension = float('inf')
    smallest_fragment = None
    
    for _, fragment in fragments:
        height,  width = fragment.size
        dimension =    height * width
        if dimension < min_dimension:
            min_dimension = dimension
            smallest_fragment = fragment
            
    return smallest_fragment


def apply_random_color_degradation(fragment):

    # implementare hsv (lavorando su s e v, non h)
    r,g,b,a = fragment.split()
    # cv2 rgb to rgba, ricreando in RGBA prelevando all'inizio il canale a 
    cl_image = Image.merge('RGB', (r,g,b))
    fragment_array = cv2.cvtColor(np.array(cl_image), cv2.COLOR_RGB2HSV)

    s_degradation_factor = random.uniform(0.3, 1)
    v_degradation_factor = random.uniform(0.8, 1)

    fragment_array[:, :, 1] = fragment_array[:, :, 1] * s_degradation_factor
    fragment_array[:, :, 2] = fragment_array[:, :, 2] * v_degradation_factor

    degraded = Image.fromarray(cv2.cvtColor(fragment_array, cv2.COLOR_HSV2RGB))
    r, g, b = degraded.split()

    degraded_image = Image.merge('RGBA', (r, g, b, a))
        
    return degraded_image


def fragment_erosion(fragments, min_distance, erosion_probability, erosion_percentage):
    eroded_fragments = []
    smallest_fragment = find_the_smallest_fragment(fragments)
    min_size = smallest_fragment.size
    probability = 1 - erosion_probability

    for point, fragment in fragments:

        size = fragment.size
        fragment_array = np.array(fragment)
        gray_array = cv2.cvtColor(fragment_array, cv2.COLOR_RGBA2GRAY)

        this_erosion_probability = random.random()

        # first erosion
        if this_erosion_probability >= probability:
            angle = random.uniform(0, 360)
            size_1 = int(erosion_percentage * 0.01 * size[0])
            size_2 = int(erosion_percentage * 0.01 * size[1])
            kernel_size = (size_1, size_2)
            rotation = cv2.getRotationMatrix2D((kernel_size[0] // 2, kernel_size[1] // 2), angle, 1)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
            kernel_rotated = cv2.warpAffine(kernel, rotation, kernel_size, borderMode=cv2.BORDER_CONSTANT)
            gray_array = cv2.erode(gray_array, kernel_rotated, iterations=1)

        # second erosion
        radius = random.randint(min_distance, max(min_size[0], min_size[1]))
        kernel = np.ones((radius, radius), np.float32) / (radius ** 2)
        gray_array = cv2.filter2D(gray_array, -1, kernel)
        

        fragment_array = cv2.bitwise_and(fragment_array, fragment_array, mask=gray_array)
        eroded_fragment = Image.fromarray(fragment_array)
        eroded_fragment = apply_random_color_degradation(eroded_fragment)
        eroded_fragments.append((point, eroded_fragment))

    return eroded_fragments


def generate_random_angles(lenght):
    angles = {}

    for i in range(lenght):
        angles[i] = random.uniform(0, 360)

    return angles


def rotate_fragment(fragments, angles):
    rotate_fragments = []

    for i, fragment in enumerate(fragments):
        angle = angles[i]
        rotated_fragment = fragment[1].rotate(angle, expand=True)
        rotate_fragments.append((fragment[0], rotated_fragment, angle))
    return rotate_fragments

# metterlo come altro eseguibile, prendendo la cartella in input
def image_ricostructed(image, fragments, path):

    image_path = os.path.join(path,"ricostructed_image.png")
    final_image = Image.new('RGBA', image.size, (255, 255, 255, 0))
    image_gray = Image.fromarray(cv2.cvtColor(cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2GRAY), cv2.COLOR_GRAY2RGBA))
    draw = ImageDraw.Draw(final_image)
    alpha_value = 128
    image_gray.putalpha(alpha_value)
    final_image.paste(image_gray, (0, 0))

    for point, fragment in fragments:
       weight, height = fragment.size
       _, _, _, a = fragment.split()

       diff_x = point[1][0]
       diff_y = point[1][1]
       for x in range(weight):
           for y in range(height):
               if a.getpixel((x, y)) != 0:
                pixel = fragment.getpixel((x, y))
                draw.point((x + diff_x, y + diff_y), fill=pixel)

    final_image.save(image_path, 'PNG')


def save_fragments_to_folder(fragments, folder_path):
    n = len(str(len(fragments)-1)) 
    for i, fragment in enumerate(fragments):
        # Define the file path for the fragment
        index = str(i).zfill(n)
        file_path = os.path.join(folder_path, f'fragment_{index}.png')
        # Save the fragment as a PNG image
        fragment[1].save(file_path, 'PNG')


def save_info(fragments, path):
    n = len(str(len(fragments)-1))
    for i, fragment in enumerate(fragments):
        index = str(i).zfill(n)
        with open(f"{path}/fragment_info.txt", "a") as info_file:
            file_path = f"fragment_{index}.png"
            info_file.write(f"{file_path}: {fragment[0]}, {fragment[2]}\n")
            info_file.write("\n")
            
            
def update_progress_bar(iteration, total, bar_length=50):
    progress = (iteration / total)
    arrow = '=' * int(round(bar_length * progress))
    spaces = ' ' * (bar_length - len(arrow))
    sys.stderr.write(f'\r[{arrow + spaces}]')
    sys.stderr.flush()


def DAFNE(url, output_directory, percentage, num_fragments, min_distance, seed, erosion_probability, erosion_percentage):
    image = Image.open(url)

    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d_%H-%M-%S")
    name = image_name(url) + "-" + date
    path = os.path.join(output_directory,name)
    resources_path = os.path.join(output_directory,name,"resources")
    # normal_fragment_path = os.path.join(output_directory, name,"fragments/normal_fragment")
    eroded_fragment_path = os.path.join(output_directory, name, "fragments/eroded_fragment")

    os.makedirs(resources_path)
    # os.makedirs(normal_fragment_path)
    os.makedirs(eroded_fragment_path)

    width, height = image.size

    points = generate_random_points(min_distance, seed, num_fragments, width, height)
    num_combined_fragment = random.randint(1,int(math.sqrt(len(points))))

    # aggiungere barra di avanzamento e print("done") sullo standard error
    update_progress_bar(1, 100)
    sys.stderr.write(f'create voronoi cells... {1}/{4}')
    sys.stderr.flush()
    voronoi_cells = create_voronoi(width, height, points)
    update_progress_bar(50, 100)
    sys.stderr.write(f'create fragments... {2}/{4}')
    sys.stderr.flush()
    fragments = create_fragment_image(voronoi_cells, image)
    combined_fragments = combine_fragment(fragments, voronoi_cells, image, num_combined_fragment)
    # fragments = random_fragments_removal(combined_fragments, percentage)
    update_progress_bar(70, 100)
    sys.stderr.write(f'erode fragments... {3}/{4}')
    sys.stderr.flush()
    eroded_fragments = fragment_erosion(combined_fragments, min_distance, erosion_probability, erosion_percentage)
    image_ricostructed(image, eroded_fragments, path)
    angles = generate_random_angles(len(fragments))
    fragments = rotate_fragment(fragments, angles)
    eroded_fragments = rotate_fragment(eroded_fragments, angles)
    update_progress_bar(90, 100)
    sys.stderr.write(f'save fragments... {4}/{4}')
    sys.stderr.flush()

    # save_fragments_to_folder(fragments, normal_fragment_path)
    save_fragments_to_folder(eroded_fragments, eroded_fragment_path)
    save_info(eroded_fragments, resources_path)
    update_progress_bar(0, 100)
    sys.stderr.write(f'all fragments saved... {4}/{4}')
    sys.stderr.flush()
    sys.stderr.write('\nOperazione completata.\n')
    


def read_input_from_file(file_path):
    input_data = {}

    try:
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split(':')
                input_data[key.strip()] = value.strip()

        return input_data
    except FileNotFoundError:
        print(f"File '{file_path}' non trovato.")
        return None
    except Exception as e:
        print(f"Si è verificato un errore durante la lettura del file: {str(e)}")
        return None


def main():

    # default values 
    seed = 1000
    num_fragments = 500
    min_distance = 6
    removal_percentage = 20
    erosion_probability = 0.6
    erosion_percentage = 30  
    #

    output_directory = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description='preleva un immagine per generare un dataset di frammenti utilizzando dei paramentri forniti dal file di testo in input')
    parser.add_argument('input_directory', type=str, help='Percorso della cartella di input che contiene le immagini')
    parser.add_argument('--output_directory', type=str, help='Percorso della cartella di output', required= False)
    parser.add_argument('--file_path', type=str, help='Percorso del file di testo di input, se non specificato vi sono dei valori di default', required= False)

    args = parser.parse_args()

    input_directory = args.input_directory
    
    if args.output_directory is not None:
        output_directory = args.output_directory

    if args.file_path is not None:
        input_data = read_input_from_file(args.file_path)
        seed = int(input_data.get("seed"))
        num_fragments = int(input_data.get("num_fragments"))
        min_distance = int(input_data.get("min_distance"))
        removal_percentage = float(input_data.get("removal_percentage"))
        erosion_probability = float(input_data.get("erosion_probability"))
        erosion_percentage = float(input_data.get("erosion_percentage"))

    elif not(os.path.exists(os.path.join(output_directory, "example_info.txt"))):
        with open(f"{output_directory}/example_info.txt", "a") as info_file:
            info_file.write(f"seed: {seed}\n")
            info_file.write(f"num_fragments: {num_fragments}\n")
            info_file.write(f"min_distance: {min_distance}\n")
            info_file.write(f"removal_percentage: {removal_percentage}\n")
            info_file.write(f"erosion_probability: {erosion_probability}\n")
            info_file.write(f"erosion_percentage: {erosion_percentage}\n")

    img_extension = ['.jpg', '.jpeg', '.png']

    for filename in os.listdir(input_directory):
        file_path = os.path.join(input_directory, filename)


        if os.path.isfile(file_path) is not None and filename.endswith(tuple(img_extension)):
            DAFNE(file_path, output_directory, removal_percentage, num_fragments, min_distance, seed, erosion_probability, erosion_percentage)
            


if __name__ == "__main__":
    main()
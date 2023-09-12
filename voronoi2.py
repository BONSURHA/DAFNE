import math
import os
import shutil
from urllib.request import urlopen
from io import BytesIO
import numpy as np
import cv2
from PIL import Image, ImageDraw
from scipy.spatial import Voronoi, voronoi_plot_2d


def image_name(url):
    split_url = url.split("/")
    file_name = split_url[-1]
    name, _ = os.path.splitext(file_name)
    return name


def download_image_from_url(url):
    response = urlopen(url)
    if response.getcode() == 200:
        image_data = BytesIO(response.read())
        image = cv2.imdecode(np.frombuffer(image_data.read(), np.uint8), -1)
        return image
    else:
        raise Exception(f"Failed to download image from URL: {url}")


def generate_random_centers(width, height):
    num_centers = int(math.sqrt((height*width)))
    centers = np.random.randint(0, width, size=(num_centers, 2))
    return centers


def compute_voronoi_with_centers(width, height, centers):
    vor = Voronoi(centers)

    # Disegna i centri dei tasselli come punti rossi
    centers_image = np.zeros((height, width, 3), dtype=np.uint8)
    centers_image[:, :, :] = (255, 255, 255)  # Colore di base
    for center in centers:
        x, y = center
        centers_image[y - 2:y + 3, x - 2:x + 3, :] = (255, 0, 0)  # Punto rosso

    return vor, centers_image


def voronoi_image(url):
    input_image = download_image_from_url(url)
    height, width, _ = input_image.shape
    centers = generate_random_centers(width, height)
    vor, centers_image = compute_voronoi_with_centers(width, height, centers)

    fragments = []



    for idx, region in enumerate(vor.regions):
        if -1 in region or not region:
            continue
        polygon = [vor.vertices[i] for i in region]

        # Calcola le dimensioni del frammento e arrotondali a interi
        min_x, min_y = min(polygon, key=lambda p: p[0]), min(polygon, key=lambda p: p[1])
        max_x, max_y = max(polygon, key=lambda p: p[0]), max(polygon, key=lambda p: p[1])
        fragment_width = int(max_x[0] - min_x[0])
        fragment_height = int(max_y[1] - min_y[1])

        # Crea un'immagine RGBA con sfondo trasparente
        fragment = Image.new('RGBA', (fragment_width, fragment_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(fragment)

        # Sposta il poligono alla posizione corretta e arrotonda le coordinate
        shifted_polygon = [(int(p[0] - min_x[0]), int(p[1] - min_y[1])) for p in polygon]

        # Disegna il poligono con sfondo trasparente
        draw.polygon(shifted_polygon, fill=(255, 255, 255, 255), outline=None)


        if idx < len(centers):
            fragments.append((fragment, centers[idx]))

    return fragments



def dafne(url, output_directory):


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

    fragments = voronoi_image(url)

    for idx, (fragment, center) in enumerate(fragments):

        # fragment = Image.fromarray(fragment)
        filename = os.path.join(path_fragments_normal, f'fragment_{center}.png')

        fragment.save(filename)






# Esempio di utilizzo:
url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Magi.jpg/600px-Leonardo_Magi.jpg"
output_directory = "output"
dafne(url, output_directory)


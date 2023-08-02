import random
import math
import matplotlib.pyplot as plt
import requests
from PIL import Image
from io import BytesIO

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def find_closest_point(point, points):
    closest_point = None
    min_distance = float('inf')
    for p in points:
        distance = euclidean_distance(point, p)
        if distance < min_distance:
            closest_point = p
            min_distance = distance
    return closest_point


def generate_voronoi_tessellation(num_tiles, width, height):
    # Genera coordinate casuali per i punti (tasselli)
    points = [(random.uniform(0, width), random.uniform(0, height)) for _ in range(num_tiles)]

    # Calcola i tasselli
    tessellation = {}
    for x in range(width):
        for y in range(height):
            closest_point = find_closest_point((x, y), points)
            tessellation[(x, y)] = closest_point

    # Disegna la tassellazione di Voronoi
    for point in points:
        plt.scatter(point[0], point[1], color='red')
    for key, value in tessellation.items():
        plt.scatter(key[0], key[1], color='blue')
        plt.plot([key[0], value[0]], [key[1], value[1]], color='black')

    plt.xlim([0, width])
    plt.ylim([0, height])
    plt.show()

# Esempio di utilizzo: genera 10 tasselli in un'area 100x100
num_tiles = 500

url = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.bv5T6lKWlirzkkMt64og-wHaFh%26pid%3DApi&f=1&ipt=63038a6006335b1016ae0db1141fa061c5547086647d1198fcee20a8b2504b70&ipo=images"
response = requests.get(url)
response.raise_for_status()

# Apri l'immagine scaricata usando PIL (o Pillow)
image = Image.open(BytesIO(response.content))
# Ottieni le dimensioni dell'immagine
width, height = image.size
print(width)
print(height)
generate_voronoi_tessellation(num_tiles, width, height)

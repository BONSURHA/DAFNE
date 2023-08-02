import numpy as np
import random
import matplotlib.pyplot as plt
import requests
from PIL import Image
from io import BytesIO


def points_generator(n_points, width, height):
    points = []
    for _ in range(n_points):
        x = random.uniform(0, width)
        y = random.uniform(0, height)
        points.append((x, y))
    return points


def euclidean_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def get_voronoi_cell(point, points):
    distances = [euclidean_distance(point, p) for p in points]
    return np.argmin(distances)


def voronoi_tessellation(points, width, height):
    # Creazione di una griglia in cui calcolare la tassellazione
    grid = np.mgrid[0:height, 0:width].reshape(2, -1).T

    # Calcolo delle celle di Voronoi per ogni punto della griglia
    voronoi_cells = [get_voronoi_cell(point, points) for point in grid]
    return voronoi_cells


# Numero di punti casuali
num_points = 700

# Carica l'immagine da internet (assicurati di avere una connessione internet attiva)
# url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Magi.jpg/600px-Leonardo_Magi.jpg"
url = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.bv5T6lKWlirzkkMt64og-wHaFh%26pid%3DApi&f=1&ipt=63038a6006335b1016ae0db1141fa061c5547086647d1198fcee20a8b2504b70&ipo=images"
response = requests.get(url)
response.raise_for_status()  # Controlla se la richiesta ha avuto successo (status code 200)

# Apri l'immagine scaricata usando PIL (o Pillow)
image = Image.open(BytesIO(response.content))
# Ottieni le dimensioni dell'immagine
width, height = image.size
print(width)
print(height)
# Generazione dei punti casuali
points = np.random.rand(num_points, 2) * np.array([width, height])
# points = points_generator(num_points, width, height)

# Calcolo della tassellazione di Voronoi
voronoi_cells = voronoi_tessellation(points, width, height)

# Visualizzazione della tassellazione
plt.imshow(np.array(voronoi_cells).reshape(height, width), interpolation='nearest', cmap='tab20')
plt.colorbar()
plt.show()

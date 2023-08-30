import numpy as np
from scipy.spatial import Voronoi
import random
import matplotlib.pyplot as plt
from urllib.request import urlopen
from PIL import Image

# Carica l'immagine di input
url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Magi.jpg/600px-Leonardo_Magi.jpg"
input_image = Image.open(urlopen(url))
input_data = np.array(input_image)

# Genera punti casuali per la tessellazione di Voronoi
num_points = 100
points = np.random.randint(0, min(input_data.shape[:2]), size=(num_points, 2))

# Calcola la tessellazione di Voronoi
vor = Voronoi(points)

# Assegna colori casuali ai punti di Voronoi
colors = np.random.randint(0, 256, size=(num_points, 3))

# Inizializza l'immagine di output con zeri
output_data = np.zeros_like(input_data)

# Per ogni pixel nell'immagine di input, trova il punto di Voronoi più vicino e assegna il colore corrispondente
for y in range(input_data.shape[0]):
    for x in range(input_data.shape[1]):
        nearest_point_index = vor.point_region[np.argmin(np.linalg.norm(points - [x, y], axis=1))]
        color = colors[nearest_point_index]
        output_data[y, x] = color

# Crea e visualizza l'immagine di output
output_image = Image.fromarray(output_data.astype(np.uint8))
output_image.show()
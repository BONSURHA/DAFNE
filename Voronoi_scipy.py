import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
import requests
from PIL import Image
from io import BytesIO

def generate_voronoi_tessellation(num_tiles, width, height):
    # Genera coordinate casuali per i punti (tasselli)
    points = np.random.rand(num_tiles, 2) * np.array([width, height])
    # Calcola la tassellazione di Voronoi
    vor = Voronoi(points)
    # Disegna la tassellazione di Voronoi
    voronoi_plot_2d(vor)
    plt.xlim([0, width])
    plt.ylim([0, height])
    plt.show()


# Esempio di utilizzo: genera 10 tasselli in un'area 100x100
num_tiles = 500
url = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.bv5T6lKWlirzkkMt64og-wHaFh%26pid%3DApi&f=1&ipt=63038a6006335b1016ae0db1141fa061c5547086647d1198fcee20a8b2504b70&ipo=images"
response = requests.get(url)
response.raise_for_status()  # Controlla se la richiesta ha avuto successo (status code 200)

# Apri l'immagine scaricata usando PIL (o Pillow)
image = Image.open(BytesIO(response.content))
# Ottieni le dimensioni dell'immagine
width, height = image.size
print(width)
print(height)
generate_voronoi_tessellation(num_tiles, width, height)

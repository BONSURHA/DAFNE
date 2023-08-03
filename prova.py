import math
import random
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt


# Funzione per calcolare la distanza euclidea tra due punti
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


# Funzione per trovare la cella Voronoi più vicina a un punto
def find_closest_cell(point, sites):
    closest_site = None
    min_distance = float('inf')

    for site in sites:
        distance = euclidean_distance(point, site)
        if distance < min_distance:
            min_distance = distance
            closest_site = site

    return closest_site


# Funzione per creare una tassellazione Voronoi
def create_voronoi(width, height, num_sites):
    # Genera punti casuali (i siti) all'interno del rettangolo delimitato da (0,0) e (width, height)
    sites = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_sites)]

    # Crea un dizionario per memorizzare le celle Voronoi
    voronoi_cells = {site: [] for site in sites}

    # Calcola la cella Voronoi per ogni punto all'interno del rettangolo
    for x in range(width):
        for y in range(height):
            point = (x, y)
            closest_site = find_closest_cell(point, sites)
            voronoi_cells[closest_site].append(point)

    return voronoi_cells


# Funzione per disegnare la tassellazione Voronoi
def plot_voronoi(voronoi_cells, width, height):
    for site, cell in voronoi_cells.items():
        x_values, y_values = zip(*cell)
        plt.scatter(x_values, y_values, label=f"Site {site}")

    plt.xlim(0, width)
    plt.ylim(0, height)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Voronoi Diagram")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    url = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.bv5T6lKWlirzkkMt64og-wHaFh%26pid%3DApi&f=1&ipt=63038a6006335b1016ae0db1141fa061c5547086647d1198fcee20a8b2504b70&ipo=images"
    response = requests.get(url)
    response.raise_for_status()

    image = Image.open(BytesIO(response.content))
    width, height = image.size
    num_sites = 500

    voronoi_cells = create_voronoi(width, height, num_sites)

    plot_voronoi(voronoi_cells, width, height)

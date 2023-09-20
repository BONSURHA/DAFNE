import math
import random
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

# Funzione per calcolare la distanza euclidea tra due punti
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def plot_voronoi(voronoi_cells, width, height):
    for site, cell in voronoi_cells.items():
        x_values, y_values = zip(*cell)
        plt.scatter(x_values, y_values, label=f"Site {site}")

    plt.xlim(0, width)
    plt.ylim(0, height)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Voronoi Diagram")
    # plt.legend()
    # plt.grid(True)
    plt.show()


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
def create_voronoi(width, height, sites):
    # Genera punti casuali (i siti) all'interno del rettangolo delimitato da (0,0) e (width, height)
    # sites = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_sites)]

    # Crea un dizionario per memorizzare le celle Voronoi
    voronoi_cells = {site: [] for site in sites}

    # Calcola la cella Voronoi per ogni punto all'interno del rettangolo
    for x in range(width):
        for y in range(height):
            point = (x, y)
            closest_site = find_closest_cell(point, sites)
            voronoi_cells[closest_site].append(point)

    return voronoi_cells

# Esempio di utilizzo
if __name__ == "__main__":
    width = 500
    height = 500
    num_sites = 200

    sites = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_sites)]

    voronoi_cells = create_voronoi(width, height, sites)
    
        # Crea un'immagine vuota
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Colora le celle Voronoi in modi diversi e i punti che le generano
    colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(num_sites)]
    for site, cell in voronoi_cells.items():
        color = colors[sites.index(site)]  # Colore corrispondente al sito
        for point in cell:
            draw.point(point, fill=color)
    
    # Salva l'immagine
    image.save("./voronoi.png")

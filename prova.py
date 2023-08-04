import math
import random
import requests
from PIL import Image
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


# creare una tassellazione Voronoi
def create_voronoi(width, height, num_sites):
    # sites = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_sites)]
    sites = [(random.uniform(0, width), random.uniform(0, height)) for _ in range(num_sites)]

    voronoi_cells = {site: [] for site in sites}

    for x in range(width):
        for y in range(height):
            point = (x, y)
            closest_site = find_closest_cell(point, sites)
            voronoi_cells[closest_site].append(point)

    return voronoi_cells


# disegnare la tassellazione Voronoi
def plot_voronoi(voronoi_cells, width, height):
    for site, cell in voronoi_cells.items():
        x_values, y_values = zip(*cell)
        plt.scatter(x_values, y_values, label=f"Site {site}")

    plt.xlim(0, width)
    plt.ylim(0, height)
    plt.xlabel("height")
    plt.ylabel("width")
    plt.show()


def calculate_num_sites(width, height):
    return int(math.sqrt(width * height))


if __name__ == "__main__":
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Magi.jpg/600px-Leonardo_Magi.jpg"
    # url = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.bv5T6lKWlirzkkMt64og-wHaFh%26pid%3DApi&f=1&ipt=63038a6006335b1016ae0db1141fa061c5547086647d1198fcee20a8b2504b70&ipo=images"
    image = Image.open(requests.get(url, stream=True).raw)
    width, height = image.size
    num_sites = calculate_num_sites(width, height)
    print(width)
    print(height)
    print(num_sites)

    voronoi_cells = create_voronoi(width, height, num_sites)
    plot_voronoi(voronoi_cells, width, height)

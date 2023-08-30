from PIL import Image, ImageDraw
from urllib.request import urlopen
import math
import random

# Funzione per calcolare la cella Voronoi per un punto
# Restituisce l'elenco dei punti all'interno della cella
def calculate_voronoi_cell(point, sites):
    voronoi_cell = []
    for x in range(point[0] - 1, point[0] + 2):
        for y in range(point[1] - 1, point[1] + 2):
            voronoi_cell.append((x, y))
    return voronoi_cell


def calculate_num_sites(width, height):
    return int(math.sqrt(width * height))


# Funzione per suddividere l'immagine in frammenti e salvarli uno a uno
def split_and_save_fragments(url, output_directory):
    input_image = Image.open(urlopen(url))
    width, height = input_image.size
    num_sites = calculate_num_sites(width, height)

    sites = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_sites)]

    for site in sites:
        voronoi_cell = calculate_voronoi_cell(site, sites)
        fragment_image = Image.new("RGB", (3, 3))
        draw = ImageDraw.Draw(fragment_image)

        for point in voronoi_cell:
            x, y = point
            if 0 <= x < width and 0 <= y < height:
                pixel = input_image.getpixel((x, y))
                draw.point((x - site[0] + 1, y - site[1] + 1), fill=pixel)

        fragment_image.save(f"{output_directory}/fragment_{site}.png")

# Esempio di utilizzo
if __name__ == "__main__":
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Leonardo_Magi.jpg/600px-Leonardo_Magi.jpg"
    output_directory = "output"

    split_and_save_fragments(url, output_directory)

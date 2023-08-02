import random

def point_generator(numero_punti, larghezza, altezza):
    points = []
    for _ in range(numero_punti):
        x = random.uniform(0, larghezza)
        y = random.uniform(0, altezza)
        points.append((x, y))
    return points


numero_punti = 500
larghezza = 500
altezza = 400

punti_generati = genera_punti(numero_punti, larghezza, altezza)


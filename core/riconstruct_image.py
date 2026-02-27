import os
import cv2
import sys
import glob
from . import io_tools
import numpy as np
from PIL import Image, ImageDraw


def image_name(url):
    split_url = url.split("/")
    file_name = split_url[-1]
    name, _ = os.path.splitext(file_name)
    return name


def read_info_file(path):
    info = {}
    file_pattern = os.path.join(path, "*.txt")
    info_path = glob.glob(file_pattern)[0]
    with open(info_path, "r") as file:
        for line in file:
            if len(line.strip().split(':')) == 2:
                name, data = line.strip().split(':')
                values = data.strip().split(';')
                coordinates = eval(values[0])
                diff = eval(values[1])
                angle = float(values[2])
                info[name] = (coordinates, diff, angle)

    return info
                    

def image_ricostruction(image_path, path):

    sys.stderr.write('\r\nimage ricostruction\n')

    image = Image.open(image_path)
    info_path = os.path.join(path, "resources")
    fragment_path = os.path.join(path, "fragments")

    image_path = os.path.join(path,"ricostructed_image.png")
    final_image = Image.new('RGBA', image.size, (255, 255, 255, 0))
    image_gray = Image.fromarray(cv2.cvtColor(cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2GRAY), cv2.COLOR_GRAY2RGBA))
    draw = ImageDraw.Draw(final_image)
    alpha_value = 128
    image_gray.putalpha(alpha_value)
    final_image.paste(image_gray, (0, 0))

    ricostruction_info = io_tools.read_info_file(info_path)

    img_extension = ['.jpg', '.jpeg', '.png']

    for filename in os.listdir(fragment_path):
        file_path = os.path.join(fragment_path, filename)
        if os.path.isfile(file_path) is not None and filename.endswith(tuple(img_extension)):
            fragment = Image.open(file_path)
            name = image_name(file_path)
            if name in ricostruction_info:
                _, diff, angle = ricostruction_info[name]
                size = fragment.size
                fragment_rotate = fragment.rotate((-angle), expand=True)
                weight, height = fragment_rotate.size
                _, _, _, a = fragment_rotate.split()

                diff_x = diff[0] - ((weight - size[0])//2)
                diff_y = diff[1] - ((height - size[1])//2)
                for x in range(weight):
                    for y in range(height):
                        if a.getpixel((x, y)) != 0:
                            pixel = fragment_rotate.getpixel((x, y))
                            draw.point((x + diff_x, y + diff_y), fill=pixel)

    final_image.save(image_path, 'PNG')
    sys.stderr.write(f'\rdone\n')




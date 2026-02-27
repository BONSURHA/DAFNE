import os
import sys
import glob
import datetime


def image_name(url):
    split_url = url.split("/")
    file_name = split_url[-1]
    name, _ = os.path.splitext(file_name)
    return name


def time_value():
    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d_%H-%M-%S")
    return date


def create_folder(name, output_directory):

    name = name + "-" + time_value()
    path = os.path.join(output_directory,name)
    resources_path = os.path.join(path, "resources")
    fragment_path = os.path.join(path, "fragments")

    os.makedirs(resources_path)
    os.makedirs(fragment_path)
    return (path, resources_path, fragment_path)

def read_input_from_file(file_path):
    input_data = {}

    try:
        with open(file_path, 'r') as file:
            for line in file:
                if len(line.strip().split(':')) == 2:
                    key, value = line.strip().split(':')
                    input_data[key.strip()] = value.strip()

        return input_data
    
    except FileNotFoundError:
        sys.stderr.write(f"\r\nFile '{file_path}' doesn't found.\n")
        sys.stderr.flush()
        return None
    except Exception as e:
        sys.stderr.write(f"\r\nError during file reading: {str(e)}\n")
        sys.stderr.flush()
        print(f"Si è verificato un errore durante la lettura del file: {str(e)}")
        return None


def read_info_file(path):
    info = {}
    try:
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
    
    except FileNotFoundError:
        sys.stderr.write(f"\r\nFile '{path}' doesn't found.\n")
        sys.stderr.flush()
        return None
    except Exception as e:
        sys.stderr.write(f"\r\nError during file reading: {str(e)}\n")
        sys.stderr.flush()
        print(f"Si è verificato un errore durante la lettura del file: {str(e)}")
        return None


def rewrite_info(name_to_remove, info, output_directory):
    num_fragments = len(info)
    for name in name_to_remove:
        del info[name]

    info_path = os.path.join(output_directory, "fragment_info.txt")
    for name in info.keys():
        val = info[name]
        coordinate, diff, angle = val
        with open(f"{info_path}", "a") as info_file:
            info_file.write(f"{name}: {coordinate}; {diff}; {angle}\n")
            info_file.write("\n")
        
    return num_fragments


def update_progress_bar(iteration, total, text, phase, bar_length=50):
    progress = ((iteration + 1)/ total)
    arrow = '=' * int(round(bar_length * progress))
    spaces = ' ' * (bar_length - len(arrow))
    max_text_length = 50
    text = f'{text}... {phase}/{4}'
    sys.stderr.write(f'\r[{arrow + spaces}] {text:<{max_text_length}}')
    sys.stderr.flush()


def generate_directories_path(image_path, output_path): 
    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d_%H-%M-%S")
    image_name = image_name(image_path) + "-" + date
    path = os.path.join(output_path,image_name)
    resources_path = os.path.join(path, "resources")
    fragment_path = os.path.join(path, "fragments")
    return (path, resources_path, fragment_path)

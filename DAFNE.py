import os
import argparse
import fragmentation_erosion


def read_input_from_file(file_path):
    input_data = {}

    try:
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split(':')
                input_data[key.strip()] = value.strip()

        return input_data
    except FileNotFoundError:
        print(f"File '{file_path}' non trovato.")
        return None
    except Exception as e:
        print(f"Si è verificato un errore durante la lettura del file: {str(e)}")
        return None


def main():

    # default values 
    seed = 1000
    num_fragments = 500
    min_distance = 6
    removal_percentage = 20
    erosion_probability = 0.6
    erosion_percentage = 30  
    #

    output_directory = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description='preleva un immagine per generare un dataset di frammenti utilizzando dei paramentri forniti dal file di testo in input')
    parser.add_argument('input_directory', type=str, help='Percorso della cartella di input che contiene le immagini')
    parser.add_argument('--output_directory', type=str, help='Percorso della cartella di output', required= False)
    parser.add_argument('--file_path', type=str, help='Percorso del file di testo di input, se non specificato vi sono dei valori di default', required= False)

    args = parser.parse_args()

    input_directory = args.input_directory
    
    if args.output_directory is not None:
        output_directory = args.output_directory

    if args.file_path is not None:
        input_data = read_input_from_file(args.file_path)
        seed = int(input_data.get("seed"))
        num_fragments = int(input_data.get("num_fragments"))
        min_distance = int(input_data.get("min_distance"))
        removal_percentage = float(input_data.get("removal_percentage"))
        erosion_probability = float(input_data.get("erosion_probability"))
        erosion_percentage = float(input_data.get("erosion_percentage"))

    elif not(os.path.exists(os.path.join(output_directory, "example_info.txt"))):
        with open(f"{output_directory}/example_info.txt", "a") as info_file:
            info_file.write(f"seed: {seed}\n")
            info_file.write(f"num_fragments: {num_fragments}\n")
            info_file.write(f"min_distance: {min_distance}\n")
            info_file.write(f"removal_percentage: {removal_percentage}\n")
            info_file.write(f"erosion_probability: {erosion_probability}\n")
            info_file.write(f"erosion_percentage: {erosion_percentage}\n")

    img_extension = ['.jpg', '.jpeg', '.png']

    for filename in os.listdir(input_directory):
        file_path = os.path.join(input_directory, filename)


        if os.path.isfile(file_path) is not None and filename.endswith(tuple(img_extension)):
            #deve ritornare il nome della cartella
            fragmentation_erosion.DAFNE(file_path, output_directory, removal_percentage, num_fragments, min_distance, seed, erosion_probability, erosion_percentage)



if __name__ == "__main__":
    main()
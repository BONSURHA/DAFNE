import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

def import_image_from_wikipedia(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        image_element = soup.find('img', {'class': 'thumbimage'})

        if image_element:
            image_url = image_element['src']
            image_response = requests.get('https:' + image_url)
            image_response.raise_for_status()

            image = Image.open(BytesIO(image_response.content))

            # Puoi fare altre operazioni con l'immagine qui, se necessario.

            return image
        else:
            print("L'URL fornito non contiene un'immagine.")
            return None
    except requests.exceptions.RequestException as e:
        print("Si è verificato un errore durante il download dell'immagine:", e)
        return None
    except IOError as e:
        print("Errore nell'apertura dell'immagine:", e)
        return None

# Esempio di utilizzo:
url = "https://it.wikipedia.org/wiki/File:Leonardo_Magi.jpg"
image = import_image_from_wikipedia(url)

if image:
    image.show()  # Mostra l'immagine utilizzando il visualizzatore di immagini predefinito del sistema

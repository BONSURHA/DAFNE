import os


def image_name(link):

    split_url = link.split("/")

    file_name = split_url[-1]

    return os.path.splitext(file_name)


# Esempio di utilizzo
link_immagine = "https://www.example.com/images/immagine.jpg"
nome_senza_estensione = estrai_nome_senza_estensione_da_link(link_immagine)
print("Nome dell'immagine senza estensione:", nome_senza_estensione)

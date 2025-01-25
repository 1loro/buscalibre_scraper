import json
import requests
from bs4 import BeautifulSoup

# URL de la wishlist pública
wishlist_url = "https://www.buscalibre.cl/v2/carro-de-compras-guardado_1785547_l.html?afiliado=157c1e5c984414edb8e5"

# Encabezados para simular un navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Archivo donde se almacenarán los datos
json_file = "wishlist_data.json"

# Realizar la solicitud HTTP
response = requests.get(wishlist_url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # Lista para almacenar los datos de los libros
    books = []

    for product in soup.find_all("div", {"class": "contenedorProducto producto"}):
        title_tag = product.find("div", {"class": "titulo"})
        title = title_tag.text.strip() if title_tag else "Sin título"

        price_tag = product.find("div", {"class": "precioAhora"})
        price = (
            float(price_tag.text.strip().replace("$", "").replace(".", ""))
            if price_tag
            else None
        )

        url_tag = product.find("a", {"title": title})
        url = url_tag["href"] if url_tag else "Sin URL"

        discount_tag = product.find("div", {"class": "precioAhorras"})
        discount = (
            discount_tag.text.strip().replace("Ahorras ", "")
            if discount_tag
            else "Sin descuento"
        )

        # Guardar los datos en un diccionario
        books.append({
            "title": title,
            "price": price,
            "url": f"https://www.buscalibre.cl{url}" if url.startswith("/") else url,
            "discount": discount,
        })

    # Escribir los datos en un archivo JSON
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(books, file, ensure_ascii=False, indent=4)

    print(f"Datos guardados correctamente en {json_file}")

else:
    print(f"Error al acceder a la wishlist: {response.status_code}")

import json
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# URL de la wishlist pública
wishlist_url = "URL_A_TU_WISHLIST"

# Archivo JSON con los precios almacenados
json_file = "wishlist_data.json"

# Encabezados para simular un navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Configuración del correo
SMTP_SERVER = "smtp.gmail.com"  # Cambiar si usas otro proveedor (ej.: Outlook usa smtp.office365.com)
SMTP_PORT = 587
EMAIL_ADDRESS = ""  # Reemplaza con tu correo
EMAIL_PASSWORD = ""       # Reemplaza con tu contraseña o contraseña de aplicación

# Función para cargar los precios almacenados
def load_stored_data():
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"El archivo {json_file} no existe. Ejecuta el script anterior primero.")
        return []

# Función para obtener los precios actuales
def get_current_prices():
    response = requests.get(wishlist_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
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

            books.append({
                "title": title,
                "price": price,
                "url": f"https://www.buscalibre.cl{url}" if url.startswith("/") else url,
            })

        return books
    else:
        print(f"Error al acceder a la wishlist: {response.status_code}")
        return []

# Comparar precios actuales con los almacenados
def compare_prices(stored_data, current_data):
    changes = []
    
    for stored_book, current_book in zip(stored_data, current_data):
        if stored_book["price"] is None or current_book["price"] is None:
            continue

        if current_book["price"] < stored_book["price"]:
            changes.append({
                "title": current_book["title"],
                "old_price": stored_book["price"],
                "new_price": current_book["price"],
                "url": current_book["url"]
            })
    
    return changes


# Guardar precios actuales en el archivo JSON
def update_stored_data(current_books):
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(current_books, file, ensure_ascii=False, indent=4)
    print(f"Datos actualizados en {json_file}")

# Función para enviar correo
def send_email(price_changes, recipient_email):
    try:
        # Crear el mensaje
        subject = "¡Alerta de baja de precio en Buscalibre!"
        
        # Crear el cuerpo del correo en formato HTML con estilo pink aesthetic
        body = """
        <html>
        <head>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    background-color: #fcd5e9;
                    color: #4f4a4a;
                    margin: 0;
                    padding: 0;
                }
                .container {
                    width: 100%;
                    max-width: 600px;
                    margin: 30px auto;
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }
                h1 {
                    color: #f39cfc;
                    font-size: 36px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    font-family: 'Courier New', Courier, monospace;
                }
                .book {
                    padding: 15px;
                    border-bottom: 2px solid #f39cfc;
                    margin-bottom: 15px;
                    background-color: #fbe6fd;
                    border-radius: 8px;
                }
                .book:last-child {
                    border-bottom: none;
                }
                .book-title {
                    font-size: 22px;
                    color: #f07bdb;
                    font-weight: bold;
                }
                .book-price {
                    font-size: 18px;
                    color: #db2d8b;
                }
                .book-old-price {
                    text-decoration: line-through;
                    color: #ff4d6d;
                    font-size: 16px;
                }
                .book-link {
                    color: #f39cfc;
                    text-decoration: none;
                    font-weight: bold;
                    font-size: 16px;
                }
                .footer {
                    text-align: center;
                    margin-top: 30px;
                    font-size: 12px;
                    color: #777;
                    font-style: italic;
                }
                .cta-button {
                    display: inline-block;
                    background-color: #f07bdb;
                    color: white;
                    padding: 10px 20px;
                    margin-top: 20px;
                    text-decoration: none;
                    font-weight: bold;
                    border-radius: 8px;
                    font-size: 18px;
                }
                .cta-button:hover {
                    background-color: #db2d8b;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>¡Alerta de baja de precio!</h1>
                <p>Los siguientes libros han bajado de precio:</p>
                <div>
        """

        for change in price_changes:
            body += f"""
            <div class="book">
                <p class="book-title">{change['title']}</p>
                <p><span class="book-old-price">Antes: ${change['old_price']:,}</span></p>
                <p><span class="book-price">Ahora: ${change['new_price']:,}</span></p>
                <p><a class="book-link" href="{change['url']}">Ver en Buscalibre</a></p>
            </div>
            """

        body += """
                </div>
                <div class="footer">
                    <p>¡Gracias por usar nuestro sistema de alertas!</p>
                    <a href="https://www.buscalibre.cl" class="cta-button">Ver más libros</a>
                </div>
            </div>
        </body>
        </html>
        """

        # Crear el mensaje MIME en formato HTML
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        # Conectar al servidor SMTP y enviar el correo
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Encriptar la conexión
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print("Correo enviado correctamente.")
    except Exception as e:
        print("Error al enviar el correo:", e)

# Script principal
stored_data = load_stored_data()
if stored_data:
    current_data = get_current_prices()
    if current_data:
        price_changes = compare_prices(stored_data, current_data)

        if price_changes:
            print("¡Alerta de baja de precios!")
            for change in price_changes:
                print(
                    f"- {change['title']} bajó de ${change['old_price']:,} a ${change['new_price']:,}. "
                    f"Ver en: {change['url']}"
                )

            # Enviar correo con las alertas de baja de precio
            recipient_email = "correo@gmail.com"  # Cambia este correo por el destino deseado
            send_email(price_changes, recipient_email)
        else:
            print("No hubo cambios en los precios.")

        # Actualizar los datos almacenados con los precios actuales
        update_stored_data(current_data)
else:
    print("Primero necesitas almacenar los datos de la wishlist.")

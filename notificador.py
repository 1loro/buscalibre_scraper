import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración del correo
SMTP_SERVER = "smtp.gmail.com"  # Cambiar si usas otro proveedor (ej.: Outlook usa smtp.office365.com)
SMTP_PORT = 587
EMAIL_ADDRESS = ""  # Reemplaza con tu correo
EMAIL_PASSWORD = ""       # Reemplaza con tu contraseña o contraseña de aplicación

# Función para enviar correo
def send_email(price_changes, recipient_email):
    try:
        # Crear el mensaje
        subject = "¡Alerta de baja de precio en Buscalibre!"
        body = "Los siguientes libros han bajado de precio:\n\n"

        for change in price_changes:
            body += (
                f"- {change['title']}\n"
                f"  Antes: ${change['old_price']:,}\n"
                f"  Ahora: ${change['new_price']:,}\n"
                f"  Enlace: {change['url']}\n\n"
            )

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Conectar al servidor SMTP y enviar el correo
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Encriptar la conexión
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print("Correo enviado correctamente.")
    except Exception as e:
        print("Error al enviar el correo:", e)

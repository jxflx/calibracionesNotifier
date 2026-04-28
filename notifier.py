import os
import requests
import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ==========================================
# MÓDULO 5.1: TRANSMISOR PUSH (NTFY)
# ==========================================
def enviar_alerta_ntfy(mensaje, url_destino):
    """Despacha la notificación HTTP Push y retorna True si el servidor responde 200 OK."""
    cabeceras = {
        "Title": f'Reporte de Calibraciones de {date.today().strftime("%d/%m/%Y")}',
        "Markdown": "yes",
        "Tags": "warning,clipboard",
        "Priority": "high"
    }
    try:
        respuesta = requests.post(url_destino, data=mensaje.encode('utf-8'), headers=cabeceras, timeout=10)
        if respuesta.status_code == 200:
            return True
        else:
            print(f"Error ntfy: Código HTTP {respuesta.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error de red ntfy: {e}")
        return False


# ==========================================
# MÓDULO 5.2: TRANSMISOR EMAIL (SMTP)
# ==========================================
def enviar_alerta_email(mensaje, destinatario):
    """Despacha el correo vía SMTP TLS y retorna True si se envía correctamente."""
    servidor_smtp = os.getenv("SMTP_SERVER")
    puerto = int(os.getenv("SMTP_PORT", 587))
    remitente = os.getenv("SMTP_USER")
    password_app = os.getenv("SMTP_PASS")

    if not all([servidor_smtp, remitente, password_app]):
        print("Error: Credenciales SMTP no configuradas en el archivo .env")
        return False

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = f"⚙️ REPORTE AUTOMATIZADO: Calibraciones Pendientes del Día {date.today().strftime('%d/%m/%Y')}"
    msg.attach(MIMEText(mensaje, 'html', 'utf-8'))

    try:
        servidor = smtplib.SMTP(servidor_smtp, puerto, timeout=15)
        servidor.ehlo()
        servidor.starttls()
        servidor.login(remitente, password_app)
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()
        return True
    except Exception as e:
        print(f"Error SMTP: {e}")
        return False


# ==========================================
# MÓDULO 5.3: ORQUESTADOR Y BASE DE DATOS
# ==========================================
def orquestar_notificaciones_y_registrar(mensaje_push, mensaje_email, info_7d, info_14d, ruta_db="calibraciones.db"):
    """
    Coordina los canales de envío recibiendo formatos diferenciados.
    info_7d e info_14d son listas de tuplas (device_function_id, due_date).
    """
    if not info_7d and not info_14d:
        print("Orquestador: No hay calibraciones pendientes. Fin del proceso.")
        return False

    url_ntfy = os.getenv("NTFY_URL")
    correo_destino = os.getenv("DESTINATION_EMAIL")

    print("Orquestador: Iniciando despachos...")

    # 1. Ejecución independiente con sus respectivos formatos
    exito_ntfy = enviar_alerta_ntfy(mensaje_push, url_ntfy)
    exito_email = enviar_alerta_email(mensaje_email, correo_destino)

    if exito_ntfy or exito_email:
        print("Orquestador: Alerta entregada en al menos un canal. Actualizando base de datos...")

        conexion = sqlite3.connect(ruta_db)
        cursor = conexion.cursor()

        try:
            if info_7d:
                cursor.executemany('''
                    UPDATE eventos_calibracion 
                    SET notif_7d_enviada = 1 
                    WHERE device_function_id = ? AND due_date = ?
                ''', info_7d)

            if info_14d:
                cursor.executemany('''
                    UPDATE eventos_calibracion 
                    SET notif_14d_enviada = 1 
                    WHERE device_function_id = ? AND due_date = ?
                ''', info_14d)

            conexion.commit()
            print("Orquestador: Transacción SQLite completada. Banderas actualizadas.")

        except sqlite3.Error as e:
            conexion.rollback()
            print(f"Fallo Crítico de Integridad en SQLite: {e}")
        finally:
            conexion.close()

        return True
    else:
        print("Orquestador: Falla total de comunicación. Ningún canal respondió.")
        return False

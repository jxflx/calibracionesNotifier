import requests
import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

# ==========================================
# MÓDULO 5.1: TRANSMISOR PUSH (NTFY)
# ==========================================
def enviar_alerta_ntfy(mensaje, url_destino):
    """Despacha la notificación HTTP Push y retorna True si el servidor responde 200 OK."""
    cabeceras = {
        "Title": f'Reporte de Calibraciones {date.today}',
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
    # Variables a configurar en tu entorno de producción
    servidor_smtp = "smtp.gmail.com"
    puerto = 587
    remitente = "avisoscalibraciones@gmail.com"
    password_app = "kzjs uvuu iprk crqs"

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = "⚙️ REPORTE AUTOMATIZADO: Calibraciones Pendientes"
    msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))

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
def orquestar_notificaciones_y_registrar(mensaje_global, ids_7d, ids_14d, ruta_db="calibraciones.db"):
    """
    Coordina los canales de envío. Actualiza SQLite estrictamente si AL MENOS UN canal tuvo éxito.
    """
    if not ids_7d and not ids_14d:
        print("Orquestador: No hay calibraciones pendientes. Fin del proceso.")
        return False

    url_ntfy = "https://ntfy.sh/calibraciones_purina_cx_9f8a7b6c5d4e3f2a1"
    correo_destino = "jesus.flores.esp@gmail.com"

    print("Orquestador: Iniciando despachos...")

    # 1. Ejecución independiente de los canales
    exito_ntfy = enviar_alerta_ntfy(mensaje_global, url_ntfy)
    exito_email = enviar_alerta_email(mensaje_global, correo_destino)

    # Optimización Y: Lógica de redundancia operativa
    # Si al menos un canal funcionó, consideramos que la alerta fue entregada
    if exito_ntfy or exito_email:
        print("Orquestador: Alerta entregada en al menos un canal. Actualizando base de datos...")

        conexion = sqlite3.connect(ruta_db)
        cursor = conexion.cursor()

        try:
            if ids_7d:
                tuplas_7d = [(id_val,) for id_val in ids_7d]
                cursor.executemany('UPDATE eventos_calibracion SET notif_7d_enviada = 1 WHERE device_function_id = ?',
                                   tuplas_7d)

            if ids_14d:
                tuplas_14d = [(id_val,) for id_val in ids_14d]
                cursor.executemany('UPDATE eventos_calibracion SET notif_14d_enviada = 1 WHERE device_function_id = ?',
                                   tuplas_14d)

            conexion.commit()
            print("Orquestador: Transacción SQLite completada. Banderas actualizadas.")

        except sqlite3.Error as e:
            conexion.rollback()
            print(f"Fallo Crítico de Integridad en SQLite: {e}")
        finally:
            conexion.close()

        return True
    else:
        print("Orquestador: Falla total de comunicación. Ningún canal respondió. La BD no se actualizará.")
        return False
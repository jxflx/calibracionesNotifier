import pandas as pd


def formatter(df):
    mapeo_columnas = {'position_id': 'Clave del Equipo', 'due_date': 'Fecha de Vencimiento'}

    df7 = df[df['tipo_alerta'] == '7_dias']
    df14 = df[df['tipo_alerta'] == '14_dias']

    # Retornamos tuplas (id, fecha) para asegurar actualización precisa en DB
    ids_7d = list(zip(df7['device_function_id'], df7['due_date'])) if not df7.empty else []
    ids_14d = list(zip(df14['device_function_id'], df14['due_date'])) if not df14.empty else []

    # 1. Mensajes Cortos (Para ntfy.sh - Teléfono)
    conteo_7 = len(df7)
    conteo_14 = len(df14)
    push_7d = f"⚠️ {conteo_7} equipos VENCIDOS o a vencer en <= 7 días." if conteo_7 > 0 else ""
    push_14d = f"ℹ️ {conteo_14} equipos preventivos (8 a 14 días)." if conteo_14 > 0 else ""

    # Unimos el mensaje push
    mensaje_push = f"REPORTE DE CALIBRACIÓN\n{push_7d}\n{push_14d}\nRevisa tu correo para ver la tabla completa."

    # 2. Mensajes Detallados (Para Correo SMTP - Tabla HTML)
    html_7d = ""
    if not df7.empty:
        # Solución X: .to_html crea una tabla web nativa
        tabla_h7 = df7[['position_id', 'due_date']].rename(columns=mapeo_columnas).to_html(index=False, border=1)
        html_7d = f"<h3>⚠️ URGENTE: {conteo_7} Calibraciones Vencidas o a vencer en <= 7 días</h3>{tabla_h7}<br>"

    html_14d = ""
    if not df14.empty:
        tabla_h14 = df14[['position_id', 'due_date']].rename(columns=mapeo_columnas).to_html(index=False, border=1)
        html_14d = f"<h3>ℹ️ AVISO: {conteo_14} Calibraciones a vencer entre 8 y 14 días</h3>{tabla_h14}"

    mensaje_email_html = f"<html><body><h2>Reporte Automatizado de Planta</h2>{html_7d}{html_14d}</body></html>"

    return mensaje_push, mensaje_email_html, ids_7d, ids_14d

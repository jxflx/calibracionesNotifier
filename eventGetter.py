import sqlite3
import pandas as pd


def extraer_alertas_pendientes(ruta_db="calibraciones.db"):
    """
    Se conecta a la base de datos y extrae los eventos que requieren notificación,
    clasificándolos en alertas de 14 días y alertas de 7 días, asegurando
    que no se dupliquen correos gracias a las banderas booleanas.
    """
    conexion = sqlite3.connect(ruta_db)

    # Consulta SQL segmentada usando UNION ALL para juntar ambos resultados
    # Utilizamos la función date() de SQLite para manejar la matemática de calendarios
    query_alertas = """
                    -- Bloque 1: Alertas de 2 semanas (Entre 8 y 14 días de distancia)
                    SELECT device_function_id, \
                           position_id, \
                           due_date, \
                           '14_dias' AS tipo_alerta
                    FROM eventos_calibracion
                    WHERE due_date <= date ('now' \
                        , 'localtime' \
                        , '+14 days')
                      AND due_date \
                        > date ('now' \
                        , 'localtime' \
                        , '+7 days')
                      AND notif_14d_enviada = 0

                    UNION ALL

                    -- Bloque 2: Alertas Críticas de 1 semana (7 días o menos)
                    SELECT device_function_id, \
                           position_id, \
                           due_date, \
                           '7_dias' AS tipo_alerta
                    FROM eventos_calibracion
                    WHERE due_date <= date ('now' \
                        , 'localtime' \
                        , '+7 days')
                      AND notif_7d_enviada = 0

                    ORDER BY due_date ASC; \
                    """

    # Solución X y Optimización Y aplicadas: Pandas ejecuta la consulta y estructura la tabla
    df_alertas = pd.read_sql_query(query_alertas, conexion)

    conexion.close()

    # Reporte analítico por consola (opcional pero recomendado para logs)
    if not df_alertas.empty:
        conteo = df_alertas['tipo_alerta'].value_counts()
        print(f"Módulo Motor de Alertas: Se encontraron {len(df_alertas)} eventos pendientes de notificación.")
        print(f"Desglose: \n{conteo.to_string()}")
    else:
        print("Módulo Motor de Alertas: 0 eventos pendientes. El sistema está al día.")

    return df_alertas

# --- EJECUCIÓN DEL MÓDULO ---
# df_pendientes = extraer_alertas_pendientes()
# print(df_pendientes.head())
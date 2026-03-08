import sqlite3
import pandas as pd


def inicializar_db_y_guardar(df_limpio, ruta_db="calibraciones.db"):
    # 1. Conexión a la base de datos (si no existe, el archivo se crea automáticamente)
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()

    # 2. Creación de la tabla con constraints lógicos
    # Usamos PRIMARY KEY compuesta para evitar duplicados del mismo dispositivo en la misma fecha
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS eventos_calibracion
                   (
                       device_function_id
                       TEXT,
                       position_id
                       TEXT,
                       period_unit
                       TEXT,
                       period_value
                       REAL,
                       due_date
                       TEXT,
                       notif_14d_enviada
                       BOOLEAN
                       DEFAULT
                       0,
                       notif_7d_enviada
                       BOOLEAN
                       DEFAULT
                       0,
                       PRIMARY
                       KEY
                   (
                       device_function_id,
                       due_date
                   )
                       )
                   ''')

    # 3. Inserción de los datos del DataFrame
    # Iteramos de forma segura. Si el registro ya existe, lo ignora (DO NOTHING)
    registros_nuevos = 0
    for _, row in df_limpio.iterrows():
        try:
            cursor.execute('''
                           INSERT INTO eventos_calibracion
                               (device_function_id, position_id, period_unit, period_value, due_date)
                           VALUES (?, ?, ?, ?, ?) ON CONFLICT(device_function_id, due_date) DO NOTHING
                           ''', (
                               row['deviceFunctionId'],
                               row['positionId'],
                               row['calibrationPeriodUnit'],
                               row['calibrationPeriodDisplayValue'],
                               # Convertimos el timestamp de pandas a string ISO para SQLite
                               row['calibrationDueDate'].strftime('%Y-%m-%d')
                           ))
            if cursor.rowcount > 0:
                registros_nuevos += 1
        except sqlite3.Error as e:
            print(f"Error de integridad en fila: {e}")

    conexion.commit()
    conexion.close()

    print(f"Módulo Gestor: Se detectaron e insertaron {registros_nuevos} eventos nuevos.")
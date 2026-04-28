import pandas as pd
import os
import glob


def procesar_calibraciones_excel(ruta_archivo_xlsx):
    columnas_requeridas = [
        'deviceFunctionId',
        'positionId',
        'calibrationPeriodUnit',
        'calibrationPeriodDisplayValue',
        'calibrationDueDate'
    ]

    try:
        # Solución X: Uso de read_excel con el motor openpyxl
        df = pd.read_excel(
            ruta_archivo_xlsx,
            engine='openpyxl',
            usecols=columnas_requeridas  # Optimización Y aplicada aquí
        )
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta {ruta_archivo_xlsx}")
        return None
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        return None

    # El resto de la lógica de limpieza y filtrado de nulos se mantiene intacta
    df['calibrationPeriodDisplayValue'] = pd.to_numeric(df['calibrationPeriodDisplayValue'], errors='coerce')
    df['calibrationDueDate'] = pd.to_datetime(df['calibrationDueDate'], errors='coerce')

    mask_errores = df['calibrationPeriodDisplayValue'].isna() | df['calibrationDueDate'].isna()
    df_errores = df[mask_errores]

    if not df_errores.empty:
        print(f"ADVERTENCIA: Se omitirán {len(df_errores)} filas con datos faltantes o inválidos. Sus deviceFunctionId son:")
        print(df_errores['deviceFunctionId'])

    df_limpio = df[~mask_errores].copy()

    return df_limpio


def buscar_ultimo_excel(directorio="input"):
    archivos = glob.glob(os.path.join(directorio, "*.xlsx"))
    if not archivos:
        return None

    # Retorna el archivo con la fecha de modificación más reciente
    return max(archivos, key=os.path.getmtime)

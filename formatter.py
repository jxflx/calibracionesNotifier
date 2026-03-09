import pandas as pd

def formatter(df):
    df7 = df[df['tipo_alerta'] == '7_dias']
    df14 = df[df['tipo_alerta'] == '14_dias']

    ids_7d = df7['device_function_id'].tolist() if not df7.empty else []
    ids_14d = df14['device_function_id'].tolist() if not df14.empty else []

    mensaje_final_7 = ''
    mensaje_final_14 = ''

    mapeo_columnas = {
        'position_id': 'Clave del Equipo',
        'due_date': 'Fecha de Vencimiento'
    }

    if not df7.empty:

        tabla_markdown_7d = (
            df7[['position_id', 'due_date']]
            .rename(columns=mapeo_columnas)
            .to_markdown(index=False)
        )


        mensaje_final_7 = f"⚠️ **URGENTE: Calibraciones a vencer en 7 días o menos** ⚠️\n\n{tabla_markdown_7d}"

    else:
        mensaje_final_7 = "No hay calibraciones pendientes en 7 días o menos."

    if not df14.empty:
        tabla_markdown_14d = (
            df14[['position_id', 'due_date']]
            .rename(columns=mapeo_columnas)
            .to_markdown(index=False)
        )

        mensaje_final_14 = f"⚠️ **AVISO: Calibraciones a vencer entre 14 y 8 días** ⚠️\n\n{tabla_markdown_14d}"

    else:
        mensaje_final_14 = "No hay calibraciones pendientes entre los próximos 14 y 8 días."


    return mensaje_final_7, mensaje_final_14, ids_7d, ids_14d


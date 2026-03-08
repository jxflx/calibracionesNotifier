from parser import procesar_calibraciones_excel
from dbmanager import inicializar_db_y_guardar
from eventGetter import extraer_alertas_pendientes

if __name__ == '__main__':
    prueba = procesar_calibraciones_excel("input/excel2.xlsx")
    # imprime los primero cinco
    print(prueba.head(5))
    # imprime la informacion general
    print(prueba.info())

    inicializar_db_y_guardar(prueba)
    df_pendientes = extraer_alertas_pendientes()
    print('ALERTAS PENDIENTES:')
    print(df_pendientes.head())

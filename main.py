from parser import procesar_calibraciones_excel


if __name__ == '__main__':
    prueba = procesar_calibraciones_excel("input/excel1.xlsx")
    # imprime los primero cinco
    print(prueba.head(5))
    # imprime la informacion general
    print(prueba.info())

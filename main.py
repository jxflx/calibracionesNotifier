import parser
import dbmanager
import eventGetter
import formatter
import notifier
import sys


def main():
    """
    Controlador principal del sistema de notificaciones de calibración.
    Ejecuta la canalización de datos (Pipeline ETL) y gestiona las alertas.
    """
    print("=== INICIANDO SISTEMA AUTOMATIZADO DE ALERTAS DE CALIBRACIÓN ===")

    # 1. Definición de Constantes de Entorno
    # Reemplaza esto con la ruta absoluta de tu archivo Excel en producción
    RUTA_EXCEL = 'input/excel2.xlsx'
    RUTA_DB = 'calibraciones.db'

    try:
        # FASE 1: Extracción y Transformación (ETL)
        print("\n[Fase 1] Analizando archivo de origen...")
        df_crudo = parser.procesar_calibraciones_excel(RUTA_EXCEL)

        if df_crudo is None or df_crudo.empty:
            print("Abortando ejecución: No se pudo extraer información válida del archivo Excel.")
            sys.exit(1)

        # FASE 2: Persistencia de Datos
        print("\n[Fase 2] Sincronizando base de datos local...")
        dbmanager.inicializar_db_y_guardar(df_crudo, ruta_db=RUTA_DB)

        # FASE 3: Motor de Reglas
        print("\n[Fase 3] Evaluando ventanas de tiempo (<= 7 días y <= 14 días)...")
        df_pendientes = eventGetter.extraer_alertas_pendientes(ruta_db=RUTA_DB)

        if df_pendientes.empty:
            print("\n=== PROCESO TERMINADO: Sistema al día. No hay acciones requeridas. ===")
            sys.exit(0)

        # FASE 4: Formateo de Presentación
        print("\n[Fase 4] Estructurando mensajes Markdown para los usuarios...")
        m7, id7, m14, id14 = formatter.formatter(df_pendientes)

        # Concatenación del payload final
        mensaje_global = f"{m7}\n\n---\n\n{m14}"

        # FASE 5: Transmisión y Cierre Transaccional
        print("\n[Fase 5] Despachando alertas hacia los canales configurados...")
        exito = notifier.orquestar_notificaciones_y_registrar(
            mensaje_global,
            id7,
            id14,
            ruta_db=RUTA_DB
        )

        if exito:
            print("\n=== PROCESO TERMINADO: Alertas despachadas y base de datos actualizada exitosamente. ===")
        else:
            print("\n=== PROCESO TERMINADO CON ERRORES: Fallo en la transmisión. Banderas no actualizadas. ===")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR CRÍTICO DEL SISTEMA] Excepción no manejada en el orquestador: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
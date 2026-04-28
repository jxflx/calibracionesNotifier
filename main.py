import parser
import dbmanager
import eventGetter
import formatter
import notifier
import sys
import os


def main():
    """
    Controlador principal del sistema de notificaciones de calibración.
    Ejecuta la canalización de datos (Pipeline ETL) y gestiona las alertas.
    """
    print("=== INICIANDO SISTEMA AUTOMATIZADO DE ALERTAS DE CALIBRACIÓN ===")

    # 1. Definición de Constantes de Entorno
    RUTA_DB = 'calibraciones.db'
    DIRECTORIO_INPUT = 'input'

    try:
        # FASE 0: Búsqueda automática de archivo
        print(f"\n[Fase 0] Buscando archivo Excel en {DIRECTORIO_INPUT}...")
        ruta_excel = parser.buscar_ultimo_excel(DIRECTORIO_INPUT)

        if not ruta_excel:
            print(f"Advertencia: No se encontraron archivos .xlsx en {DIRECTORIO_INPUT}.")
            # Aún así procedemos a la Fase 3 por si hay alertas pendientes de archivos anteriores
        else:
            print(f"Archivo detectado: {ruta_excel}")

            # FASE 1: Extracción y Transformación (ETL)
            print("\n[Fase 1] Analizando archivo de origen...")
            df_crudo = parser.procesar_calibraciones_excel(ruta_excel)

            if df_crudo is not None and not df_crudo.empty:
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
        print("\n[Fase 4] Estructurando mensajes para los usuarios...")
        msg_push, msg_email, info_7d, info_14d = formatter.formatter(df_pendientes)

        # FASE 5: Transmisión y Cierre Transaccional
        print("\n[Fase 5] Despachando alertas hacia los canales configurados...")
        exito = notifier.orquestar_notificaciones_y_registrar(
            msg_push,
            msg_email,
            info_7d,
            info_14d,
            ruta_db=RUTA_DB
        )

        if exito:
            print("\n=== PROCESO TERMINADO: Alertas despachadas y base de datos actualizada exitosamente. ===")
        else:
            print("\n=== PROCESO TERMINADO CON ERRORES: Fallo en la transmisión. Banderas no actualizadas. ===")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR CRÍTICO DEL SISTEMA] Excepción no manejada en el orquestador: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

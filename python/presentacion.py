"""Salida por consola. Este archivo no toma decisiones de planificación."""

from entrada import COLUMNAS
from evaluacion import porcentajes_proceso, reduccion_porcentual
from hilos import EjecucionTarea, ResultadoHilos
from modelos import Proceso, Resultado
from sincronizacion import ResultadoSincronizacion


def imprimir_tabla(cabeceras: list[str], filas: list[list[str]]) -> None:
    anchos = [len(cabecera) for cabecera in cabeceras]
    for fila in filas:
        for indice, valor in enumerate(fila):
            anchos[indice] = max(anchos[indice], len(valor))

    def imprimir_fila(fila: list[str]) -> None:
        print(" | ".join(valor.ljust(anchos[i]) for i, valor in enumerate(fila)))

    imprimir_fila(cabeceras)
    print("-+-".join("-" * ancho for ancho in anchos))
    for fila in filas:
        imprimir_fila(fila)


def mostrar_procesos(procesos: list[Proceso]) -> None:
    filas = []
    for proceso in procesos:
        filas.append([
            proceso.procesos, str(proceso.tiempo_llegada),
            str(proceso.duracion), str(proceso.prioridad),
        ])
    imprimir_tabla(COLUMNAS, filas)


def promedios(resultado: Resultado) -> tuple[float, float, float]:
    espera = 0
    respuesta = 0
    retorno = 0
    for metrica in resultado.metricas:
        espera += metrica.espera
        respuesta += metrica.respuesta
        retorno += metrica.retorno
    cantidad = len(resultado.metricas)
    return espera / cantidad, respuesta / cantidad, retorno / cantidad


def mostrar_resultado(resultado: Resultado) -> None:
    print(f"\n=== {resultado.algoritmo} ===")
    print("Gantt textual: cada bloque muestra [inicio, fin); ancho no proporcional.")
    for tramo in resultado.tramos:
        etiqueta = "CPU libre" if tramo.proceso is None else tramo.proceso
        print(f"  [{tramo.inicio}, {tramo.fin}) {etiqueta}")

    filas = []
    for metrica in resultado.metricas:
        eficiencia, espera_porcentaje = porcentajes_proceso(metrica)
        filas.append([
            metrica.proceso, str(metrica.inicio), str(metrica.fin),
            str(metrica.espera), str(metrica.respuesta), str(metrica.retorno),
            f"{eficiencia:.2f}%", f"{espera_porcentaje:.2f}%",
        ])
    imprimir_tabla([
        "Procesos", "Inicio", "Fin", "Espera", "Respuesta", "Retorno",
        "Efic. temporal", "En espera",
    ], filas)
    print("Eficiencia temporal = Duración / Retorno x 100; En espera = Espera / Retorno x 100.")
    mayor = max(porcentajes_proceso(m)[0] for m in resultado.metricas)
    destacados = [m.proceso for m in resultado.metricas if porcentajes_proceso(m)[0] == mayor]
    print(f"Mayor eficiencia temporal en esta planificación: {', '.join(destacados)} ({mayor:.2f}%).")
    print("Este indicador describe ejecución frente a espera; depende de la llegada y duración del trabajo.")


def formatear_porcentaje(valor: float | None) -> str:
    return "N/D" if valor is None else f"{valor:.2f}%"


def mostrar_eficiencia_por_proceso(resultados: list[Resultado]) -> None:
    """Compara el mismo trabajo bajo cada política, conservando los empates."""
    print("\n=== Eficiencia temporal por proceso (%) ===")
    filas = []
    for proceso in resultados[0].metricas:
        porcentajes = []
        for resultado in resultados:
            for metrica in resultado.metricas:
                if metrica.proceso == proceso.proceso:
                    porcentajes.append(porcentajes_proceso(metrica)[0])
                    break
        mayor = max(porcentajes)
        mejores = [
            resultado.algoritmo for resultado, valor in zip(resultados, porcentajes)
            if valor == mayor
        ]
        filas.append([proceso.proceso, *[f"{valor:.2f}%" for valor in porcentajes], ", ".join(mejores)])
    imprimir_tabla(["Procesos", *[r.algoritmo for r in resultados], "Mayor eficiencia"], filas)
    print("Se compara el mismo proceso entre algoritmos. Se muestran todos los empates.")


def mostrar_comparacion(resultados: list[Resultado]) -> None:
    print("\n=== Comparación de promedios (unidades de tiempo) ===")
    referencia = None
    for resultado in resultados:
        if resultado.algoritmo == "FCFS":
            referencia = promedios(resultado)
    filas = []
    for resultado in resultados:
        espera, respuesta, retorno = promedios(resultado)
        reduccion_espera = None if referencia is None else reduccion_porcentual(referencia[0], espera)
        reduccion_respuesta = None if referencia is None else reduccion_porcentual(referencia[1], respuesta)
        filas.append([
            resultado.algoritmo, f"{espera:.2f}", f"{respuesta:.2f}", f"{retorno:.2f}",
            formatear_porcentaje(reduccion_espera), formatear_porcentaje(reduccion_respuesta),
        ])
    imprimir_tabla([
        "Algoritmo", "Espera", "Respuesta", "Retorno",
        "Red. espera vs FCFS", "Red. respuesta vs FCFS",
    ], filas)
    print("Reducción = (FCFS - resultado) / FCFS x 100. Positivo: mejora; negativo: aumento.")
    print("N/D: falta FCFS o su valor es cero y el comparado no. Dos ceros: 0% (empate).")
    for indice, etiqueta in [(0, "espera"), (1, "respuesta")]:
        menor = min(promedios(r)[indice] for r in resultados)
        mejores = [r.algoritmo for r in resultados if promedios(r)[indice] == menor]
        print(f"Menor {etiqueta} promedio: {', '.join(mejores)} ({menor:.2f}).")
    mostrar_eficiencia_por_proceso(resultados)
    print("\nEspera promedio: cada # representa aproximadamente una unidad.")
    for resultado in resultados:
        espera, _, _ = promedios(resultado)
        # Limitamos el dibujo; los valores numéricos conservan su precisión.
        barra = "#" * min(round(espera), 60)
        if round(espera) > 60:
            barra += "..."
        print(f"{resultado.algoritmo}: {barra} ({espera:.2f})")


def mostrar_tabla_tareas(titulo: str, registros: list[EjecucionTarea]) -> None:
    print(f"\n=== {titulo} ===")
    filas = []
    for registro in registros:
        resumen = "ERROR" if registro.error else registro.resultado.resumen
        filas.append([
            registro.nombre, registro.responsable, resumen,
            f"{registro.inicio_ns / 1_000_000:.6f}",
            f"{registro.fin_ns / 1_000_000:.6f}",
            f"{(registro.fin_ns - registro.inicio_ns) / 1_000_000:.6f}",
        ])
    imprimir_tabla(["Tarea", "Responsable", "Resultado", "Inicio (ms)", "Fin (ms)", "Duración (ms)"], filas)
    for registro in registros:
        if registro.error:
            print(f"  {registro.nombre}: {registro.error}")


def mostrar_hilos(resultado: ResultadoHilos) -> None:
    print("\nSuperAlmacén: revisión de una entrega mediante tareas diferentes.")
    print(f"Fecha fija de revisión del ejemplo: {resultado.entrega.fecha_revision.isoformat()}")
    filas = []
    for producto in resultado.entrega.productos:
        filas.append([
            producto.nombre, str(producto.esperadas), str(producto.recibidas),
            str(producto.vencimiento) if producto.vencimiento else "No aplica",
            producto.ubicacion or "Sin asignar",
        ])
    imprimir_tabla(["Producto", "Esperadas", "Recibidas", "Vencimiento", "Ubicación"], filas)
    print("Las dos modalidades leen esta misma entrega; cada tarea genera su propio resultado.")
    print("Secuencial: el hilo principal termina una tarea antes de comenzar la siguiente.")
    mostrar_tabla_tareas("Modalidad secuencial: tareas de la entrega", resultado.secuencial)
    print("\nCon hilos: se inicia un hilo por tarea y después se espera a todos con join().")
    for evento in resultado.eventos:
        print(evento)
    mostrar_tabla_tareas("Modalidad con hilos: tareas de la entrega", resultado.con_hilos)
    print("Inicio y fin se miden desde el comienzo de CADA modalidad; son relojes relativos separados.")
    print("Los intervalos con hilos pueden solaparse, pero tareas pequeñas pueden terminar una tras otra.")
    print("Son tiempos reales medidos, no pausas simuladas. El total incluye medición y gestión.")
    print("\n=== Misma entrega: secuencial frente a hilos ===")
    reduccion = reduccion_porcentual(resultado.tiempo_secuencial_ns, resultado.tiempo_hilos_ns)
    filas = []
    for nombre, registros, tiempo, porcentaje in [
        ("Secuencial", resultado.secuencial, resultado.tiempo_secuencial_ns, 0.0),
        ("Hilos", resultado.con_hilos, resultado.tiempo_hilos_ns,
         reduccion if resultado.resultados_coinciden else None),
    ]:
        completadas = sum(1 for registro in registros if registro.error is None)
        filas.append([
            nombre, str(len(registros)), str(completadas),
            f"{completadas / len(registros) * 100:.2f}%",
            f"{tiempo / 1_000_000:.6f}", formatear_porcentaje(porcentaje),
        ])
    imprimir_tabla(["Modalidad", "Tareas", "Completadas", "Cumplimiento", "Tiempo total (ms)", "Reducción vs secuencial"], filas)
    print("Cumplimiento = tareas ejecutadas sin error / seleccionadas x 100; no mide productos conformes.")
    if not resultado.resultados_coinciden:
        print("Comparación no válida: hubo errores o los resultados de las modalidades difieren.")
        return
    print("Verificación: todos los resultados y detalles coinciden entre las dos modalidades.")
    if resultado.tiempo_hilos_ns == resultado.tiempo_secuencial_ns:
        print("Empate en el tiempo total medido.")
    else:
        mejor = "Hilos" if resultado.tiempo_hilos_ns < resultado.tiempo_secuencial_ns else "Secuencial"
        print(f"Menor tiempo total observado: {mejor}.")
    print("Reducción = (tiempo secuencial - tiempo con hilos) / tiempo secuencial x 100.")
    print("Un valor negativo indica aumento; N/D indica referencia cero. Dos ceros: empate de 0%.")
    print("Medición puntual: las tareas pequeñas y la gestión de hilos influyen en el resultado.")
    print("Las tareas son distintas: sus duraciones individuales no establecen qué hilo es más eficiente.")


def mostrar_sincronizacion(resultado: ResultadoSincronizacion) -> None:
    print("\nSuperAlmacén: recepción ingresa cajas y ubicación las retira para llevarlas a los estantes.")
    print("Productor = operario de recepción; Consumidor = operario de ubicación; búfer = zona de recepción.")
    print("Cada código P1-item01, etc., identifica una caja; <FIN> indica el cierre de recepción.")
    print("\nRegistro en orden de acceso al búfer (recogido durante la ejecución):")
    for numero, evento in enumerate(resultado.eventos, start=1):
        elemento = "<FIN>" if evento.elemento is None else evento.elemento
        print(
            f"{numero:03d} | {evento.hilo} | {evento.accion} {elemento}"
            f" | ocupación {evento.ocupacion}/{resultado.capacidad}"
        )
    print(f"\nCajas recibidas (producidas): {len(resultado.producidos)}")
    print(f"Cajas retiradas (consumidas): {len(resultado.consumidos)}")
    print("Verificación correcta: sin pérdidas ni duplicados; búfer vacío.")
    print("Todos los hilos terminaron. El orden entre hilos puede variar en cada ejecución.")

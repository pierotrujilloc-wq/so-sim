"""Salida por consola. Este archivo no toma decisiones de planificación."""

from entrada import COLUMNAS
from evaluacion import porcentajes_proceso, reduccion_porcentual
from hilos import ResultadoHilos
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


def mostrar_hilos(resultado: ResultadoHilos) -> None:
    print("\nSuperAlmacén: una orden de conteo se reparte en sectores, uno por hilo.")
    print("Cada sector tiene cajas distintas con 1 a N unidades; todos tienen la misma carga.")
    for evento in resultado.eventos:
        print(evento)
    esperado = resultado.limite * (resultado.limite + 1) // 2
    total_unidades = sum(resultado.resultados)
    filas = []
    for indice, unidades in enumerate(resultado.resultados):
        filas.append([
            f"Hilo-{indice + 1}", str(unidades),
            f"{unidades / esperado * 100:.2f}%",
            f"{unidades / total_unidades * 100:.2f}%",
            f"{resultado.tiempos_tareas_ns[indice] / 1_000_000:.6f}",
        ])
    print("\n=== Comparación de hilos: misma carga por sector ===")
    imprimir_tabla(["Hilo", "Unidades", "Cumplimiento", "Parte de la orden", "Tarea (ms)"], filas)
    print("Cumplimiento = unidades contadas / esperadas; parte de la orden = unidades / total; ambos x 100.")
    print("Los tiempos de tarea son tiempos transcurridos; las tareas pueden solaparse.")
    print("\n=== Misma orden: secuencial frente a hilos ===")
    reduccion = reduccion_porcentual(resultado.tiempo_secuencial_ns, resultado.tiempo_hilos_ns)
    imprimir_tabla(["Modalidad", "Sectores", "Tiempo total (ms)", "Reducción vs secuencial"], [
        ["Secuencial", str(len(resultado.resultados)), f"{resultado.tiempo_secuencial_ns / 1_000_000:.6f}", "0.00%"],
        ["Hilos", str(len(resultado.resultados)), f"{resultado.tiempo_hilos_ns / 1_000_000:.6f}", formatear_porcentaje(reduccion)],
    ])
    if resultado.tiempo_hilos_ns == resultado.tiempo_secuencial_ns:
        print("Empate en el tiempo total medido.")
    else:
        mejor = "Hilos" if resultado.tiempo_hilos_ns < resultado.tiempo_secuencial_ns else "Secuencial"
        print(f"Menor tiempo total observado: {mejor}.")
    print("Medición puntual: incluye gestión de hilos y puede variar, especialmente en tareas pequeñas.")
    print("Un porcentaje negativo indica más tiempo. Crear más hilos no garantiza acelerar este cálculo.")


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

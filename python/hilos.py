"""SuperAlmacén: colaboradores cuentan productos de una orden por sectores.

Cada hilo tiene un acumulador local y comparte el registro de la orden.
"""

from dataclasses import dataclass
from threading import Lock, Thread, current_thread
from time import perf_counter_ns

from modelos import validar_entero


@dataclass
class ResultadoHilos:
    resultados: list[int]
    eventos: list[str]
    tiempos_tareas_ns: list[int]
    tiempo_secuencial_ns: int
    tiempo_hilos_ns: int
    limite: int


def contar_unidades(limite: int) -> int:
    """Contar un sector con cajas de 1, 2, ..., limite unidades de producto.

    Cada sector contiene cajas distintas con el mismo patrón de cantidades.
    Es una tarea numérica didáctica, sin tiempos físicos de manipulación.
    Ambas modalidades ejecutan exactamente este mismo trabajo.
    """
    total = 0
    for numero in range(1, limite + 1):
        total += numero
    return total


def demostrar_hilos(cantidad: int = 3, limite: int = 5) -> ResultadoHilos:
    validar_entero("Cantidad de hilos", cantidad, 1)
    validar_entero("Límite", limite, 1)
    resultados = [0] * cantidad
    eventos = []
    mutex = Lock()
    tiempos_tareas_ns = [0] * cantidad

    # Referencia: contar los mismos sectores de la orden, uno por uno.
    inicio_secuencial = perf_counter_ns()
    resultados_secuenciales = []
    for _ in range(cantidad):
        resultados_secuenciales.append(contar_unidades(limite))
    tiempo_secuencial_ns = perf_counter_ns() - inicio_secuencial

    def tarea(indice: int) -> None:
        nombre = current_thread().name
        with mutex:
            eventos.append(f"{nombre}: inicio")

        # Tiempo transcurrido de la tarea: puede incluir pausas del SO.
        # No es tiempo de CPU exclusivo ni el tiempo total del lote.
        inicio_tarea = perf_counter_ns()
        total = contar_unidades(limite)
        duracion_tarea = perf_counter_ns() - inicio_tarea

        with mutex:
            resultados[indice] = total
            tiempos_tareas_ns[indice] = duracion_tarea
            eventos.append(f"{nombre}: fin, unidades = {total}")

    # Incluye creación, inicio, registro, coordinación y espera de los hilos.
    inicio_hilos = perf_counter_ns()
    hilos = []
    for indice in range(cantidad):
        hilo = Thread(target=tarea, args=(indice,), name=f"Hilo-{indice + 1}")
        hilos.append(hilo)
        hilo.start()

    for hilo in hilos:
        hilo.join()
    tiempo_hilos_ns = perf_counter_ns() - inicio_hilos
    # Solo consultamos los resultados después de que todos hayan terminado.
    esperado = limite * (limite + 1) // 2
    if resultados != resultados_secuenciales or any(valor != esperado for valor in resultados):
        raise RuntimeError("Las unidades contadas por sector no coinciden con lo esperado.")
    return ResultadoHilos(
        resultados, eventos, tiempos_tareas_ns,
        tiempo_secuencial_ns, tiempo_hilos_ns, limite,
    )

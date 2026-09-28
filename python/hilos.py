"""Demostración de creación y finalización de hilos mediante start y join."""

from dataclasses import dataclass
from threading import Lock, Thread, current_thread

from modelos import validar_entero


@dataclass
class ResultadoHilos:
    resultados: list[int]
    eventos: list[str]


def demostrar_hilos(cantidad: int = 3, limite: int = 5) -> ResultadoHilos:
    validar_entero("Cantidad de hilos", cantidad, 1)
    validar_entero("Límite", limite, 1)
    resultados = [0] * cantidad
    eventos = []
    mutex = Lock()

    def tarea(indice: int) -> None:
        nombre = current_thread().name
        with mutex:
            eventos.append(f"{nombre}: inicio")

        # Cada hilo calcula 1 + 2 + ... + limite con un acumulador local.
        total = 0
        for numero in range(1, limite + 1):
            total += numero

        with mutex:
            resultados[indice] = total
            eventos.append(f"{nombre}: fin, suma = {total}")

    hilos = []
    for indice in range(cantidad):
        hilo = Thread(target=tarea, args=(indice,), name=f"Hilo-{indice + 1}")
        hilos.append(hilo)
        hilo.start()

    for hilo in hilos:
        hilo.join()
    # Solo consultamos los resultados después de que todos hayan terminado.
    return ResultadoHilos(resultados, eventos)

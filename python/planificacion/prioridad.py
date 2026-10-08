"""Prioridad sin desalojo: el número más pequeño tiene mayor prioridad.

En SuperAlmacén, se elige la orden más urgente entre las disponibles.
Una verificación urgente espera si el operario ya está atendiendo otra orden.
"""

from modelos import Proceso, Resultado, Tramo, construir_resultado, validar_procesos


def por_prioridad(procesos: list[Proceso]) -> Resultado:
    validar_procesos(procesos)
    pendientes = sorted(procesos, key=lambda proceso: proceso.tiempo_llegada)
    tiempo = 0
    tramos = []

    while pendientes:
        indice_elegido = None
        for indice in range(len(pendientes)):
            candidato = pendientes[indice]
            if candidato.tiempo_llegada <= tiempo:
                if indice_elegido is None:
                    indice_elegido = indice
                elif candidato.prioridad < pendientes[indice_elegido].prioridad:
                    indice_elegido = indice

        if indice_elegido is None:
            siguiente_llegada = pendientes[0].tiempo_llegada
            tramos.append(Tramo(None, tiempo, siguiente_llegada))
            tiempo = siguiente_llegada
            continue

        # Los empates se resuelven por llegada y luego por orden de entrada.
        # No hay desalojo: incluso si llega otro de mayor prioridad, espera
        # hasta que el proceso actual termine su ráfaga.
        elegido = pendientes.pop(indice_elegido)
        fin = tiempo + elegido.duracion
        tramos.append(Tramo(elegido.procesos, tiempo, fin))
        tiempo = fin

    return construir_resultado("Prioridad sin desalojo", procesos, tramos)

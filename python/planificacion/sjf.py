"""SJF sin desalojo: elige la menor duración entre los procesos disponibles.

En SuperAlmacén, el operario elige la orden más corta que ya llegó.
"""

from modelos import Proceso, Resultado, Tramo, construir_resultado, validar_procesos


def sjf(procesos: list[Proceso]) -> Resultado:
    validar_procesos(procesos)
    pendientes = sorted(procesos, key=lambda proceso: proceso.tiempo_llegada)
    tiempo = 0
    tramos = []

    while pendientes:
        indice_elegido = None
        for indice in range(len(pendientes)):
            candidato = pendientes[indice]
            # Un proceso futuro no puede competir por la CPU todavía.
            if candidato.tiempo_llegada <= tiempo:
                if indice_elegido is None:
                    indice_elegido = indice
                elif candidato.duracion < pendientes[indice_elegido].duracion:
                    indice_elegido = indice

        if indice_elegido is None:
            siguiente_llegada = pendientes[0].tiempo_llegada
            tramos.append(Tramo(None, tiempo, siguiente_llegada))
            tiempo = siguiente_llegada
            continue

        # En empate conservamos al primero: llegada anterior y luego orden
        # de entrada. Una nueva llegada no interrumpe esta ejecución.
        elegido = pendientes.pop(indice_elegido)
        fin = tiempo + elegido.duracion
        tramos.append(Tramo(elegido.procesos, tiempo, fin))
        tiempo = fin

    return construir_resultado("SJF sin desalojo", procesos, tramos)

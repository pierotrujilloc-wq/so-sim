"""FCFS: atiende por orden de llegada, sin desalojar procesos.

En SuperAlmacén, el operario completa las órdenes según su recepción.
"""

from modelos import Proceso, Resultado, Tramo, construir_resultado, validar_procesos


def fcfs(procesos: list[Proceso]) -> Resultado:
    validar_procesos(procesos)
    # sorted crea otra lista; no modifica los datos originales. Es estable:
    # si dos procesos llegan juntos, conserva su orden en la entrada.
    pendientes = sorted(procesos, key=lambda proceso: proceso.tiempo_llegada)
    tiempo = 0
    tramos = []

    for proceso in pendientes:
        # Si el próximo proceso todavía no llegó, la CPU permanece libre.
        if tiempo < proceso.tiempo_llegada:
            tramos.append(Tramo(None, tiempo, proceso.tiempo_llegada))
            tiempo = proceso.tiempo_llegada

        # FCFS ejecuta la ráfaga completa antes de atender al siguiente.
        fin = tiempo + proceso.duracion
        tramos.append(Tramo(proceso.procesos, tiempo, fin))
        tiempo = fin

    return construir_resultado("FCFS", procesos, tramos)

"""Round Robin: turnos de CPU de hasta quantum unidades."""

from modelos import (
    Proceso, Resultado, Tramo, construir_resultado,
    validar_entero, validar_procesos,
)


def round_robin(procesos: list[Proceso], quantum: int) -> Resultado:
    validar_procesos(procesos)
    validar_entero("Quantum", quantum, 1)
    pendientes = sorted(procesos, key=lambda proceso: proceso.tiempo_llegada)
    restantes = {proceso.procesos: proceso.duracion for proceso in procesos}
    cola_listos = []
    siguiente = 0
    tiempo = 0
    tramos = []

    while cola_listos or siguiente < len(pendientes):
        # Sin procesos listos, saltamos hasta la siguiente llegada.
        if not cola_listos and tiempo < pendientes[siguiente].tiempo_llegada:
            llegada = pendientes[siguiente].tiempo_llegada
            tramos.append(Tramo(None, tiempo, llegada))
            tiempo = llegada

        while siguiente < len(pendientes):
            if pendientes[siguiente].tiempo_llegada > tiempo:
                break
            cola_listos.append(pendientes[siguiente])
            siguiente += 1

        # Lista usada como cola FIFO: sale del inicio y se agrega al final.
        actual = cola_listos.pop(0)
        ejecucion = min(quantum, restantes[actual.procesos])
        fin = tiempo + ejecucion
        tramos.append(Tramo(actual.procesos, tiempo, fin))
        restantes[actual.procesos] -= ejecucion
        tiempo = fin

        # Quienes llegaron durante el turno, incluso justo al terminar,
        # entran antes de reencolar el proceso que agotó su quantum.
        while siguiente < len(pendientes):
            if pendientes[siguiente].tiempo_llegada > tiempo:
                break
            cola_listos.append(pendientes[siguiente])
            siguiente += 1

        if restantes[actual.procesos] > 0:
            cola_listos.append(actual)

    return construir_resultado(f"Round Robin (q={quantum})", procesos, tramos)

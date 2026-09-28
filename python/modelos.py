"""Datos compartidos por los cuatro algoritmos de planificación."""

from dataclasses import dataclass


def validar_entero(nombre: str, valor: int, minimo: int) -> None:
    # bool es una subclase de int en Python; aquí solo aceptamos enteros reales.
    if type(valor) is not int or valor < minimo:
        raise ValueError(f"{nombre} debe ser un entero mayor o igual que {minimo}.")


@dataclass(frozen=True)
class Proceso:
    """Las cuatro columnas de entrada. Los tiempos son unidades simuladas."""

    procesos: str
    tiempo_llegada: int
    duracion: int
    prioridad: int

    def __post_init__(self) -> None:
        if not isinstance(self.procesos, str) or not self.procesos.strip():
            raise ValueError("El identificador del proceso no puede estar vacío.")
        if self.procesos != self.procesos.strip():
            raise ValueError("El identificador no debe tener espacios en los extremos.")
        validar_entero("Tiempo llegada", self.tiempo_llegada, 0)
        validar_entero("Duración", self.duracion, 1)
        validar_entero("Prioridad", self.prioridad, 1)


@dataclass(frozen=True)
class Tramo:
    """Uso de la CPU en el intervalo [inicio, fin). None indica CPU libre."""

    proceso: str | None
    inicio: int
    fin: int


@dataclass(frozen=True)
class Metrica:
    proceso: str
    inicio: int
    fin: int
    espera: int
    respuesta: int
    retorno: int


@dataclass
class Resultado:
    algoritmo: str
    tramos: list[Tramo]
    metricas: list[Metrica]


def validar_procesos(procesos: list[Proceso]) -> None:
    if not procesos:
        raise ValueError("Debe ingresar al menos un proceso.")
    identificadores = set()
    for proceso in procesos:
        if not isinstance(proceso, Proceso):
            raise ValueError("Cada entrada debe ser un Proceso.")
        if proceso.procesos in identificadores:
            raise ValueError(f"Identificador repetido: {proceso.procesos}.")
        identificadores.add(proceso.procesos)


def construir_resultado(
    algoritmo: str, procesos: list[Proceso], tramos: list[Tramo]
) -> Resultado:
    """Calcula las métricas a partir del historial generado por el algoritmo."""
    metricas = []
    for proceso in procesos:
        primer_inicio = None
        finalizacion = None
        for tramo in tramos:
            if tramo.proceso == proceso.procesos:
                if primer_inicio is None:
                    primer_inicio = tramo.inicio
                finalizacion = tramo.fin

        if primer_inicio is None or finalizacion is None:
            raise ValueError(f"El proceso {proceso.procesos} no fue ejecutado.")

        # Como solo existe una ráfaga de CPU y no hay E/S, todo el tiempo
        # transcurrido desde la llegada es tiempo de ejecución o de espera.
        retorno = finalizacion - proceso.tiempo_llegada
        espera = retorno - proceso.duracion
        respuesta = primer_inicio - proceso.tiempo_llegada
        metricas.append(Metrica(
            proceso.procesos, primer_inicio, finalizacion,
            espera, respuesta, retorno,
        ))
    return Resultado(algoritmo, tramos, metricas)

"""Porcentajes explicables para comparar una misma carga de trabajo."""

from modelos import Metrica


def porcentajes_proceso(metrica: Metrica) -> tuple[float, float]:
    """Parte del retorno dedicada a ejecutar y a esperar, respectivamente.

    En este modelo sin E/S: retorno = duración + espera. La eficiencia
    temporal mide la atención recibida; no mide la utilización global de CPU.
    """
    duracion = metrica.retorno - metrica.espera
    eficiencia = duracion / metrica.retorno * 100
    espera = metrica.espera / metrica.retorno * 100
    return eficiencia, espera


def reduccion_porcentual(referencia: float, actual: float) -> float | None:
    """Positivo = menos tiempo; negativo = más tiempo respecto a la referencia.

    Dos tiempos cero representan un empate. Si solo la referencia es cero,
    el porcentaje no está definido: el llamador mostrará N/D.
    """
    if referencia == 0:
        return 0.0 if actual == 0 else None
    return (referencia - actual) / referencia * 100

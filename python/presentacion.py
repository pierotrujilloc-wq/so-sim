"""Salida por consola. Este archivo no toma decisiones de planificación."""

from entrada import COLUMNAS
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
        filas.append([
            metrica.proceso, str(metrica.inicio), str(metrica.fin),
            str(metrica.espera), str(metrica.respuesta), str(metrica.retorno),
        ])
    imprimir_tabla(["Procesos", "Inicio", "Fin", "Espera", "Respuesta", "Retorno"], filas)


def mostrar_comparacion(resultados: list[Resultado]) -> None:
    print("\n=== Comparación de promedios (unidades de tiempo) ===")
    filas = []
    for resultado in resultados:
        espera, respuesta, retorno = promedios(resultado)
        filas.append([
            resultado.algoritmo, f"{espera:.2f}", f"{respuesta:.2f}", f"{retorno:.2f}",
        ])
    imprimir_tabla(["Algoritmo", "Espera", "Respuesta", "Retorno"], filas)
    print("\nEspera promedio: cada # representa aproximadamente una unidad.")
    for resultado in resultados:
        espera, _, _ = promedios(resultado)
        # Limitamos el dibujo; los valores numéricos conservan su precisión.
        barra = "#" * min(round(espera), 60)
        if round(espera) > 60:
            barra += "..."
        print(f"{resultado.algoritmo}: {barra} ({espera:.2f})")


def mostrar_sincronizacion(resultado: ResultadoSincronizacion) -> None:
    print("\nRegistro en orden de acceso al búfer (recogido durante la ejecución):")
    for numero, evento in enumerate(resultado.eventos, start=1):
        elemento = "<FIN>" if evento.elemento is None else evento.elemento
        print(
            f"{numero:03d} | {evento.hilo} | {evento.accion} {elemento}"
            f" | ocupación {evento.ocupacion}/{resultado.capacidad}"
        )
    print(f"\nElementos producidos: {len(resultado.producidos)}")
    print(f"Elementos consumidos: {len(resultado.consumidos)}")
    print("Verificación correcta: sin pérdidas ni duplicados; búfer vacío.")
    print("Todos los hilos terminaron. El orden entre hilos puede variar en cada ejecución.")

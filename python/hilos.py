"""La misma revisión de mercadería, secuencial y con un Thread por tarea."""

from dataclasses import dataclass
from threading import Lock, Thread, current_thread
from time import perf_counter_ns

from tareas_almacen import ENTREGA_EJEMPLO, TAREAS, Entrega, ResultadoTarea, Tarea


@dataclass
class EjecucionTarea:
    nombre: str
    responsable: str
    inicio_ns: int
    fin_ns: int
    resultado: ResultadoTarea | None
    error: str | None


@dataclass
class ResultadoHilos:
    entrega: Entrega
    secuencial: list[EjecucionTarea]
    con_hilos: list[EjecucionTarea]
    eventos: list[str]
    tiempo_secuencial_ns: int
    tiempo_hilos_ns: int
    resultados_coinciden: bool


def medir_tarea(tarea: Tarea, entrega: Entrega, origen_ns: int, responsable: str) -> EjecucionTarea:
    nombre, funcion = tarea
    inicio = perf_counter_ns()
    resultado = None
    error = None
    try:
        resultado = funcion(entrega)
        if not isinstance(resultado, ResultadoTarea):
            raise TypeError("La función debe devolver ResultadoTarea.")
    except Exception as fallo:
        # Registrar también los fallos de los hilos; join no los propaga.
        resultado = None
        error = f"{type(fallo).__name__}: {fallo}"
    fin = perf_counter_ns()
    return EjecucionTarea(nombre, responsable, inicio - origen_ns, fin - origen_ns, resultado, error)


def demostrar_hilos(
    tareas: list[Tarea] | None = None, entrega: Entrega = ENTREGA_EJEMPLO,
) -> ResultadoHilos:
    seleccion = list(TAREAS if tareas is None else tareas)
    if not seleccion:
        raise ValueError("Seleccione al menos una tarea.")

    # Ambas modalidades reciben el mismo objeto inmutable: dataclasses frozen
    # con una tupla de productos. Cada función crea su propio resultado.
    secuencial = []
    inicio_secuencial = perf_counter_ns()
    for tarea in seleccion:
        secuencial.append(medir_tarea(tarea, entrega, inicio_secuencial, "Hilo principal"))
    tiempo_secuencial_ns = perf_counter_ns() - inicio_secuencial

    registros: list[EjecucionTarea | None] = [None] * len(seleccion)
    eventos = []
    mutex = Lock()

    def ejecutar_tarea(indice: int) -> None:
        nombre_hilo = current_thread().name
        with mutex:
            eventos.append(f"{nombre_hilo}: inicio de {seleccion[indice][0]}")
        registro = medir_tarea(seleccion[indice], entrega, inicio_hilos, nombre_hilo)
        with mutex:
            registros[indice] = registro
            estado = "error" if registro.error else "fin"
            eventos.append(f"{nombre_hilo}: {estado} de {seleccion[indice][0]}")

    inicio_hilos = perf_counter_ns()
    hilos = []
    for indice in range(len(seleccion)):
        hilo = Thread(target=ejecutar_tarea, args=(indice,), name=f"Hilo-{indice + 1}")
        hilos.append(hilo)
        hilo.start()

    # Iniciar toda la selección antes de esperar. Las consultas simuladas
    # pueden solapar sus esperas; una tarea corta puede acabar antes de iniciar otra.
    for hilo in hilos:
        hilo.join()
    tiempo_hilos_ns = perf_counter_ns() - inicio_hilos

    con_hilos = []
    for registro in registros:
        if registro is None:
            raise RuntimeError("Un hilo terminó sin registrar su resultado.")
        con_hilos.append(registro)

    coinciden = True
    for primero, segundo in zip(secuencial, con_hilos):
        if primero.error or segundo.error or primero.resultado != segundo.resultado:
            coinciden = False
    return ResultadoHilos(entrega, secuencial, con_hilos, eventos,
                          tiempo_secuencial_ns, tiempo_hilos_ns, coinciden)

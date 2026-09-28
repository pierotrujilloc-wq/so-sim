"""Productor-consumidor con un búfer circular, semáforos y un mutex.

No se usa queue.Queue: las posiciones, la ocupación y la coordinación
se gestionan aquí para poder estudiar cada operación.
"""

from dataclasses import dataclass
from threading import Lock, Semaphore, Thread, current_thread

from modelos import validar_entero


@dataclass(frozen=True)
class Evento:
    accion: str
    hilo: str
    elemento: str | None
    ocupacion: int
    contenido: tuple[str | None, ...]


@dataclass
class ResultadoSincronizacion:
    producidos: list[str]
    consumidos: list[str]
    eventos: list[Evento]
    capacidad: int


class BufferLimitado:
    def __init__(self, capacidad: int):
        validar_entero("Capacidad", capacidad, 1)
        self.capacidad = capacidad
        self.datos = [None] * capacidad
        self.entrada = 0
        self.salida = 0
        self.ocupacion = 0
        self.eventos = []

        # Inicialmente todos los espacios están libres y no hay elementos.
        self.espacios_libres = Semaphore(capacidad)
        self.elementos_disponibles = Semaphore(0)
        self.mutex = Lock()

    def insertar(self, elemento: str | None) -> None:
        # Esperar un espacio ANTES de tomar el mutex permite que un consumidor
        # retire elementos si el búfer está lleno. Invertirlo puede bloquear.
        self.espacios_libres.acquire()
        with self.mutex:
            self.datos[self.entrada] = elemento
            self.entrada = (self.entrada + 1) % self.capacidad
            self.ocupacion += 1
            self.eventos.append(Evento(
                "insertar", current_thread().name, elemento,
                self.ocupacion, tuple(self.datos),
            ))
        # Solo anunciamos un elemento después de terminar de escribirlo.
        self.elementos_disponibles.release()

    def retirar(self) -> str | None:
        self.elementos_disponibles.acquire()
        with self.mutex:
            elemento = self.datos[self.salida]
            self.datos[self.salida] = None
            self.salida = (self.salida + 1) % self.capacidad
            self.ocupacion -= 1
            self.eventos.append(Evento(
                "retirar", current_thread().name, elemento,
                self.ocupacion, tuple(self.datos),
            ))
        self.espacios_libres.release()
        return elemento


def producir(buffer: BufferLimitado, identificador: int, cantidad: int) -> None:
    for numero in range(1, cantidad + 1):
        elemento = f"P{identificador}-item{numero:02d}"
        buffer.insertar(elemento)


def consumir(buffer: BufferLimitado) -> None:
    while True:
        elemento = buffer.retirar()
        # None es una señal de fin. No representa un elemento de trabajo.
        if elemento is None:
            return
        # En este ejemplo retirar el elemento representa su procesamiento.


def ejecutar_productor_consumidor(
    productores: int = 2,
    consumidores: int = 2,
    capacidad: int = 5,
    elementos_por_productor: int = 10,
) -> ResultadoSincronizacion:
    validar_entero("Productores", productores, 1)
    validar_entero("Consumidores", consumidores, 1)
    validar_entero("Capacidad", capacidad, 1)
    validar_entero("Elementos por productor", elementos_por_productor, 0)
    buffer = BufferLimitado(capacidad)
    hilos_productores = []
    hilos_consumidores = []

    for numero in range(1, consumidores + 1):
        hilo = Thread(target=consumir, args=(buffer,), name=f"Consumidor-{numero}")
        hilos_consumidores.append(hilo)
        hilo.start()

    for numero in range(1, productores + 1):
        hilo = Thread(
            target=producir, args=(buffer, numero, elementos_por_productor),
            name=f"Productor-{numero}",
        )
        hilos_productores.append(hilo)
        hilo.start()

    # Primero esperamos a TODOS los productores. Así ninguna señal de fin
    # puede adelantarse a un elemento que todavía no haya sido producido.
    for hilo in hilos_productores:
        hilo.join()

    # Una señal por consumidor: cada consumidor sale al retirar la suya.
    # Usamos la misma cola FIFO y respetamos también su capacidad.
    for _ in hilos_consumidores:
        buffer.insertar(None)
    for hilo in hilos_consumidores:
        hilo.join()

    producidos = []
    consumidos = []
    for evento in buffer.eventos:
        if not 0 <= evento.ocupacion <= capacidad:
            raise RuntimeError("La ocupación del búfer salió de sus límites.")
        if evento.elemento is not None:
            if evento.accion == "insertar":
                producidos.append(evento.elemento)
            else:
                consumidos.append(evento.elemento)

    total_esperado = productores * elementos_por_productor
    if len(producidos) != total_esperado or len(set(producidos)) != total_esperado:
        raise RuntimeError("La producción no coincide con la cantidad esperada.")
    # Al ser FIFO, el orden de retirada también debe coincidir con el de entrada.
    if producidos != consumidos or buffer.ocupacion != 0:
        raise RuntimeError("Se perdieron, duplicaron o desordenaron elementos.")

    return ResultadoSincronizacion(producidos, consumidos, buffer.eventos, capacidad)

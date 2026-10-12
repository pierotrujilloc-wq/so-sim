"""
Módulo 1 - Productor / Consumidor con búfer acotado
Práctica Dirigida Semana 05 - SW407 Sistemas Operativos

Requisitos implementados:
- Almacén compartido con capacidad 5.
- Semáforos: mutex, vacíos y llenos.
- Al menos 2 productores y 2 consumidores.
- Logs con marca de tiempo e identificador del hilo.
- Verificación automática de pérdidas, duplicados y capacidad.

No requiere librerías externas.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import random
import threading
import time
from typing import Optional


class EventLogger:
    """Logger sencillo y seguro para múltiples hilos."""

    def __init__(self, log_file: Optional[Path] = None, echo: bool = True):
        self.log_file = Path(log_file) if log_file else None
        self.echo = echo
        self._lock = threading.Lock()

        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self.log_file.write_text("", encoding="utf-8")

    def log(self, actor: str, event: str, detail: str = "") -> None:
        stamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        line = f"{stamp} | {actor:<14} | {event:<18} | {detail}"
        with self._lock:
            if self.echo:
                print(line)
            if self.log_file:
                with self.log_file.open("a", encoding="utf-8") as f:
                    f.write(line + "\n")


@dataclass
class ProducerConsumerResult:
    ok: bool
    produced_count: int
    consumed_count: int
    missing_count: int
    duplicate_count: int
    unexpected_count: int
    final_buffer_size: int
    max_occupancy: int
    capacity: int


def run_simulation(
    *,
    capacity: int = 5,
    producer_count: int = 2,
    consumer_count: int = 2,
    items_per_producer: int = 20,
    seed: int = 1,
    log_file: Optional[Path] = None,
    echo: bool = True,
) -> ProducerConsumerResult:
    """
    Ejecuta una simulación completa y devuelve indicadores verificables.

    Cada productor genera identificadores únicos:
      P1-I001, P1-I002, ...
    El total de elementos a consumir se reparte entre los consumidores.
    """

    if capacity <= 0:
        raise ValueError("capacity debe ser mayor que 0")
    if producer_count <= 0 or consumer_count <= 0:
        raise ValueError("Debe existir al menos un productor y un consumidor")
    if items_per_producer <= 0:
        raise ValueError("items_per_producer debe ser mayor que 0")

    logger = EventLogger(log_file, echo=echo)

    # Recurso compartido.
    almacen: list[str] = []

    # Los tres semáforos solicitados por la práctica.
    mutex = threading.Semaphore(1)
    vacios = threading.Semaphore(capacity)
    llenos = threading.Semaphore(0)

    # Datos de verificación.
    producidos: list[str] = []
    consumidos: list[str] = []
    stats_lock = threading.Lock()
    max_occupancy = 0

    total_items = producer_count * items_per_producer

    # Cantidad exacta que consumirá cada hilo para terminar sin "sentinelas".
    base_share, remainder = divmod(total_items, consumer_count)
    consumer_targets = [
        base_share + (1 if i < remainder else 0)
        for i in range(consumer_count)
    ]

    def acquire_with_wait_log(sem: threading.Semaphore, actor: str, wait_event: str) -> None:
        """Intenta adquirir sin bloqueo; si no puede, deja evidencia de la espera."""
        if sem.acquire(blocking=False):
            return
        logger.log(actor, wait_event, "bloqueado hasta que el recurso esté disponible")
        sem.acquire()

    def productor(index: int) -> None:
        nonlocal max_occupancy
        actor = f"Productor-{index + 1}"
        rng = random.Random(seed * 1000 + index)

        for n in range(1, items_per_producer + 1):
            # Simula el tiempo de preparar un nuevo insumo.
            time.sleep(rng.uniform(0.001, 0.008))
            insumo = f"P{index + 1}-I{n:03d}"

            # Orden correcto:
            # 1) esperar un espacio vacío
            # 2) entrar a la sección crítica
            acquire_with_wait_log(vacios, actor, "ESPERA_ESPACIO")
            mutex.acquire()
            try:
                almacen.append(insumo)
                ocupacion = len(almacen)
                with stats_lock:
                    producidos.append(insumo)
                    max_occupancy = max(max_occupancy, ocupacion)
                logger.log(
                    actor,
                    "INSERTA",
                    f"{insumo} | almacén={ocupacion}/{capacity}",
                )
            finally:
                mutex.release()

            # Informa que existe un elemento más disponible.
            llenos.release()

    def consumidor(index: int, target: int) -> None:
        actor = f"Consumidor-{index + 1}"
        rng = random.Random(seed * 2000 + index)

        for _ in range(target):
            # Espera hasta que exista al menos un elemento.
            acquire_with_wait_log(llenos, actor, "ESPERA_INSUMO")

            # Sección crítica: retirar exactamente un elemento.
            mutex.acquire()
            try:
                insumo = almacen.pop(0)
                ocupacion = len(almacen)
                with stats_lock:
                    consumidos.append(insumo)
                logger.log(
                    actor,
                    "RETIRA",
                    f"{insumo} | almacén={ocupacion}/{capacity}",
                )
            finally:
                mutex.release()

            # Ahora existe un espacio vacío adicional.
            vacios.release()

            # Simula utilización del insumo fuera de la sección crítica.
            time.sleep(rng.uniform(0.001, 0.009))
            logger.log(actor, "USA_INSUMO", insumo)

    logger.log(
        "SISTEMA",
        "INICIO",
        f"capacidad={capacity}, productores={producer_count}, "
        f"consumidores={consumer_count}, total={total_items}",
    )

    producers = [
        threading.Thread(
            target=productor,
            args=(i,),
            name=f"Productor-{i + 1}",
        )
        for i in range(producer_count)
    ]
    consumers = [
        threading.Thread(
            target=consumidor,
            args=(i, consumer_targets[i]),
            name=f"Consumidor-{i + 1}",
        )
        for i in range(consumer_count)
    ]

    # Se mezclan los arranques para incrementar la concurrencia real.
    all_threads = producers + consumers
    for t in all_threads:
        t.start()
    for t in all_threads:
        t.join()

    produced_set = set(producidos)
    consumed_set = set(consumidos)

    missing = produced_set - consumed_set
    unexpected = consumed_set - produced_set
    duplicate_count = len(consumidos) - len(consumed_set)

    ok = (
        len(producidos) == total_items
        and len(consumidos) == total_items
        and not missing
        and not unexpected
        and duplicate_count == 0
        and len(almacen) == 0
        and max_occupancy <= capacity
    )

    logger.log(
        "SISTEMA",
        "RESUMEN",
        f"producidos={len(producidos)}, consumidos={len(consumidos)}, "
        f"perdidos={len(missing)}, duplicados={duplicate_count}, "
        f"inesperados={len(unexpected)}, buffer_final={len(almacen)}, "
        f"ocupación_máxima={max_occupancy}/{capacity}",
    )
    logger.log("SISTEMA", "RESULTADO", "OK" if ok else "ERROR")

    return ProducerConsumerResult(
        ok=ok,
        produced_count=len(producidos),
        consumed_count=len(consumidos),
        missing_count=len(missing),
        duplicate_count=duplicate_count,
        unexpected_count=len(unexpected),
        final_buffer_size=len(almacen),
        max_occupancy=max_occupancy,
        capacity=capacity,
    )


if __name__ == "__main__":
    result = run_simulation(seed=1, echo=True)
    print("\n===== VERIFICACIÓN FINAL =====")
    print(f"Producidos      : {result.produced_count}")
    print(f"Consumidos      : {result.consumed_count}")
    print(f"Perdidos        : {result.missing_count}")
    print(f"Duplicados      : {result.duplicate_count}")
    print(f"Buffer final    : {result.final_buffer_size}")
    print(f"Ocupación máxima: {result.max_occupancy}/{result.capacity}")
    print(f"RESULTADO       : {'OK' if result.ok else 'ERROR'}")

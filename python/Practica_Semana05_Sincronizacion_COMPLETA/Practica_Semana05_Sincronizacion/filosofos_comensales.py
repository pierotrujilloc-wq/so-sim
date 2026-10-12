"""
Módulo 2 - Filósofos comensales / cinco cocineros
Práctica Dirigida Semana 05 - SW407 Sistemas Operativos

Estrategia:
- 5 cocineros y 5 utensilios representados por Lock.
- Cocineros 1-4 adquieren izquierda -> derecha.
- Cocinero 5 adquiere derecha -> izquierda.
- La asimetría rompe la espera circular y previene el deadlock.
- Se registran logs y se verifica que todos completan todas sus rondas.

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
    def __init__(self, log_file: Optional[Path] = None, echo: bool = True):
        self.log_file = Path(log_file) if log_file else None
        self.echo = echo
        self._lock = threading.Lock()

        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self.log_file.write_text("", encoding="utf-8")

    def log(self, actor: str, event: str, detail: str = "") -> None:
        stamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        line = f"{stamp} | {actor:<12} | {event:<18} | {detail}"
        with self._lock:
            if self.echo:
                print(line)
            if self.log_file:
                with self.log_file.open("a", encoding="utf-8") as f:
                    f.write(line + "\n")


@dataclass
class PhilosophersResult:
    ok: bool
    deadlock_detected: bool
    starvation_detected: bool
    rounds_per_philosopher: int
    completed_rounds: list[int]


def run_simulation(
    *,
    philosopher_count: int = 5,
    rounds: int = 6,
    seed: int = 1,
    log_file: Optional[Path] = None,
    echo: bool = True,
    join_timeout: float = 8.0,
) -> PhilosophersResult:
    if philosopher_count != 5:
        raise ValueError("Esta práctica está modelada para exactamente 5 cocineros.")
    if rounds <= 0:
        raise ValueError("rounds debe ser mayor que 0")

    logger = EventLogger(log_file, echo=echo)

    utensils = [threading.Lock() for _ in range(philosopher_count)]
    completed = [0] * philosopher_count
    completed_lock = threading.Lock()

    # Hace que los cinco inicien cada ronda casi al mismo tiempo.
    # Sirve como prueba de estrés y no es un mecanismo que evite el deadlock.
    round_barrier = threading.Barrier(philosopher_count)

    def cocinero(i: int) -> None:
        actor = f"Cocinero-{i + 1}"
        rng = random.Random(seed * 3000 + i)
        left = i
        right = (i + 1) % philosopher_count

        # Ruptura de simetría: el último invierte el orden.
        if i == philosopher_count - 1:
            first, second = right, left
            order_text = f"U{right + 1} -> U{left + 1} (orden invertido)"
        else:
            first, second = left, right
            order_text = f"U{left + 1} -> U{right + 1}"

        logger.log(actor, "ORDEN_RECURSOS", order_text)

        for round_no in range(1, rounds + 1):
            # "Pensar" / preparar antes de competir por utensilios.
            time.sleep(rng.uniform(0.001, 0.006))

            try:
                round_barrier.wait(timeout=2.0)
            except threading.BrokenBarrierError:
                logger.log(actor, "BARRERA_ROTA", f"ronda={round_no}")
                return

            logger.log(actor, "INTENTA", f"ronda={round_no}, primero=U{first + 1}")
            utensils[first].acquire()
            try:
                logger.log(actor, "TOMA", f"U{first + 1}")

                utensils[second].acquire()
                try:
                    logger.log(actor, "TOMA", f"U{second + 1}")
                    logger.log(actor, "COCINA", f"ronda={round_no}")
                    time.sleep(rng.uniform(0.001, 0.006))

                    with completed_lock:
                        completed[i] += 1
                finally:
                    utensils[second].release()
                    logger.log(actor, "LIBERA", f"U{second + 1}")
            finally:
                utensils[first].release()
                logger.log(actor, "LIBERA", f"U{first + 1}")

        logger.log(actor, "TERMINA", f"rondas_completadas={completed[i]}")

    logger.log(
        "SISTEMA",
        "INICIO",
        f"cocineros={philosopher_count}, utensilios={philosopher_count}, rondas={rounds}",
    )

    threads = [
        threading.Thread(target=cocinero, args=(i,), name=f"Cocinero-{i + 1}", daemon=True)
        for i in range(philosopher_count)
    ]

    for t in threads:
        t.start()

    # Espera global acotada: si algún hilo sigue vivo, se reporta posible deadlock.
    deadline = time.monotonic() + join_timeout
    for t in threads:
        remaining = max(0.0, deadline - time.monotonic())
        t.join(timeout=remaining)

    alive = [t.name for t in threads if t.is_alive()]
    deadlock_detected = bool(alive)

    # Para esta práctica consideramos evidencia de inanición si un cocinero
    # no completa todas las rondas dentro de la ejecución.
    starvation_detected = any(x < rounds for x in completed)

    ok = (
        not deadlock_detected
        and not starvation_detected
        and all(x == rounds for x in completed)
    )

    logger.log(
        "SISTEMA",
        "RESUMEN",
        f"rondas={completed}, deadlock={'SI' if deadlock_detected else 'NO'}, "
        f"inanición_observada={'SI' if starvation_detected else 'NO'}",
    )
    if alive:
        logger.log("SISTEMA", "HILOS_VIVOS", ", ".join(alive))
    logger.log("SISTEMA", "RESULTADO", "OK" if ok else "ERROR")

    return PhilosophersResult(
        ok=ok,
        deadlock_detected=deadlock_detected,
        starvation_detected=starvation_detected,
        rounds_per_philosopher=rounds,
        completed_rounds=completed,
    )


if __name__ == "__main__":
    result = run_simulation(seed=1, echo=True)
    print("\n===== VERIFICACIÓN FINAL =====")
    print(f"Rondas por cocinero : {result.completed_rounds}")
    print(f"Deadlock            : {'SI' if result.deadlock_detected else 'NO'}")
    print(f"Inanición observada : {'SI' if result.starvation_detected else 'NO'}")
    print(f"RESULTADO           : {'OK' if result.ok else 'ERROR'}")

"""Punto de entrada: menú interactivo o comandos reproducibles."""

import argparse
from pathlib import Path

from entrada import cargar_csv, ingresar_procesos, pedir_entero
from hilos import demostrar_hilos
from modelos import Proceso
from planificacion import fcfs, por_prioridad, round_robin, sjf
from presentacion import (
    mostrar_comparacion, mostrar_procesos, mostrar_resultado, mostrar_sincronizacion,
)
from sincronizacion import ejecutar_productor_consumidor


RAIZ = Path(__file__).resolve().parent.parent
EJEMPLO = RAIZ / "data" / "processes" / "ejemplo.csv"


def ejecutar_planificacion(procesos: list[Proceso], quantum: int, algoritmo: str) -> None:
    mostrar_procesos(procesos)
    resultados = []
    if algoritmo in ("todos", "fcfs"):
        resultados.append(fcfs(procesos))
    if algoritmo in ("todos", "sjf"):
        resultados.append(sjf(procesos))
    if algoritmo in ("todos", "prioridad"):
        resultados.append(por_prioridad(procesos))
    if algoritmo in ("todos", "rr"):
        resultados.append(round_robin(procesos, quantum))
    for resultado in resultados:
        mostrar_resultado(resultado)
    mostrar_comparacion(resultados)


def menu() -> None:
    while True:
        print("\nSO-Sim | Módulos 1 y 2")
        print("1. Comparar planificadores con el CSV de ejemplo")
        print("2. Ingresar procesos manualmente y comparar")
        print("3. Cargar otro CSV y comparar")
        print("4. Demostrar creación y finalización de hilos")
        print("5. Ejecutar productor-consumidor")
        print("6. Ver instrucciones para procesos en C")
        print("0. Salir")
        opcion = input("Opción: ").strip()
        try:
            if opcion == "0":
                return
            if opcion in ("1", "2", "3"):
                if opcion == "1":
                    procesos = cargar_csv(EJEMPLO)
                elif opcion == "2":
                    procesos = ingresar_procesos()
                else:
                    procesos = cargar_csv(input("Ruta del CSV: ").strip().strip('"'))
                quantum = pedir_entero("Quantum de Round Robin: ", 1)
                ejecutar_planificacion(procesos, quantum, "todos")
            elif opcion == "4":
                cantidad = pedir_entero("Cantidad de hilos: ", 1)
                limite = pedir_entero("Sumar desde 1 hasta: ", 1)
                for evento in demostrar_hilos(cantidad, limite).eventos:
                    print(evento)
            elif opcion == "5":
                productores = pedir_entero("Productores: ", 1)
                consumidores = pedir_entero("Consumidores: ", 1)
                capacidad = pedir_entero("Capacidad del búfer: ", 1)
                cantidad = pedir_entero("Elementos por productor: ", 0)
                mostrar_sincronizacion(ejecutar_productor_consumidor(
                    productores, consumidores, capacidad, cantidad,
                ))
            elif opcion == "6":
                print("En Linux/WSL, desde la raíz del proyecto:")
                print("  mkdir -p build")
                print("  gcc -std=c11 -Wall -Wextra -Werror c/procesos.c -o build/procesos")
                print("  ./build/procesos")
                print("Explicación: docs/modulo_1.md")
            else:
                print("Elija una opción del menú.")
        except (ValueError, OSError, UnicodeError) as error:
            print(f"Error: {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="SO-Sim: procesos, planificación y sincronización")
    comandos = parser.add_subparsers(dest="comando")
    planificar = comandos.add_parser("planificar", help="Ejecutar uno o todos los algoritmos")
    planificar.add_argument("--archivo", type=Path, default=EJEMPLO)
    planificar.add_argument("--quantum", type=int, default=2)
    planificar.add_argument("--algoritmo", choices=["todos", "fcfs", "sjf", "prioridad", "rr"], default="todos")
    hilos = comandos.add_parser("hilos", help="Crear hilos y esperar su finalización")
    hilos.add_argument("--cantidad", type=int, default=3)
    hilos.add_argument("--limite", type=int, default=5)
    sincronizar = comandos.add_parser("sincronizar", help="Ejecutar productor-consumidor")
    sincronizar.add_argument("--productores", type=int, default=2)
    sincronizar.add_argument("--consumidores", type=int, default=2)
    sincronizar.add_argument("--capacidad", type=int, default=5)
    sincronizar.add_argument("--elementos", type=int, default=10, help="Elementos por productor")
    args = parser.parse_args()

    try:
        if args.comando is None:
            menu()
        elif args.comando == "planificar":
            ejecutar_planificacion(cargar_csv(args.archivo), args.quantum, args.algoritmo)
        elif args.comando == "hilos":
            for evento in demostrar_hilos(args.cantidad, args.limite).eventos:
                print(evento)
        elif args.comando == "sincronizar":
            mostrar_sincronizacion(ejecutar_productor_consumidor(
                args.productores, args.consumidores, args.capacidad, args.elementos,
            ))
    except (ValueError, OSError, UnicodeError) as error:
        print(f"Error: {error}")
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nSalida solicitada.")
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

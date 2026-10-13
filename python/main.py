"""Punto de entrada: menú interactivo o comandos reproducibles."""

import argparse
from pathlib import Path

from entrada import cargar_csv, ingresar_procesos, pedir_entero
from hilos import demostrar_hilos
from modelos import Proceso
from procesos import ejecutar_procesos
from planificacion import fcfs, por_prioridad, round_robin, sjf
from presentacion import (
    mostrar_comparacion, mostrar_hilos, mostrar_procesos, mostrar_resultado, mostrar_sincronizacion,
)
from sincronizacion import ejecutar_productor_consumidor
from tareas_almacen import ESPERA_SERVICIO_SEGUNDOS, TAREAS, seleccionar_tareas


RAIZ = Path(__file__).resolve().parent.parent
EJEMPLO = RAIZ / "data" / "processes" / "ejemplo.csv"


def ejecutar_planificacion(
    procesos: list[Proceso], quantum: int, algoritmo: str, es_ejemplo: bool = False
) -> None:
    print("\nSuperAlmacén: cada proceso es una orden de trabajo; un operario representa la CPU.")
    print("Llegada: ingreso de la orden; Duración: tiempo de trabajo simulado; Prioridad: urgencia (1 = mayor).")
    if es_ejemplo:
        # Leyenda del CSV predeterminado, sin añadir columnas a los procesos.
        print("Órdenes del ejemplo:")
        print("  P1: contar cajas de una entrega.")
        print("  P2: preparar productos para reponer una góndola.")
        print("  P3: verificar un lote refrigerado urgente.")
        print("  P4: clasificar productos recibidos.")
        print("  P5: actualizar etiquetas de ubicación.")
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
        print("\nSO-Sim | SuperAlmacén: almacén de supermercado | Módulos 1 y 2")
        print("1. Planificar las órdenes del almacén del CSV de ejemplo")
        print("2. Ingresar procesos (órdenes de trabajo) y comparar")
        print("3. Cargar otro CSV de órdenes y comparar")
        print("4. Revisar una entrega: tareas secuenciales y con hilos")
        print("5. Coordinar recepción de cajas: productor-consumidor")
        print("6. Ejecutar jefe y operario en C (fork/exec)")
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
                ejecutar_planificacion(procesos, quantum, "todos", es_ejemplo=opcion == "1")
            elif opcion == "4":
                print(f"Las tareas 5, 6 y 7 simulan consultas externas: {ESPERA_SERVICIO_SEGUNDOS} segundos por consulta.")
                print("Tareas disponibles para la misma entrega:")
                for numero, (nombre, _) in enumerate(TAREAS, start=1):
                    print(f"  {numero}. {nombre}")
                while True:
                    try:
                        tareas = seleccionar_tareas(input("Tareas (ej. 1,3; Enter o 0 = todas): "))
                        break
                    except ValueError as error:
                        print(f"Error: {error}")
                mostrar_hilos(demostrar_hilos(tareas))
            elif opcion == "5":
                productores = pedir_entero("Operarios de recepción (productores): ", 1)
                consumidores = pedir_entero("Operarios de ubicación (consumidores): ", 1)
                capacidad = pedir_entero("Posiciones de la zona de recepción (búfer): ", 1)
                cantidad = pedir_entero("Cajas por operario de recepción: ", 0)
                mostrar_sincronizacion(ejecutar_productor_consumidor(
                    productores, consumidores, capacidad, cantidad,
                ))
            elif opcion == "6":
                ejecutar_procesos(RAIZ)
            else:
                print("Elija una opción del menú.")
        except (ValueError, OSError, UnicodeError) as error:
            print(f"Error: {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="SO-Sim | SuperAlmacén: almacén de supermercado")
    comandos = parser.add_subparsers(dest="comando")
    comandos.add_parser("procesos", help="Compilar y ejecutar fork/exec en C (Linux o Ubuntu WSL)")
    planificar = comandos.add_parser("planificar", help="Ejecutar uno o todos los algoritmos")
    planificar.add_argument("--archivo", type=Path, default=EJEMPLO)
    planificar.add_argument("--quantum", type=int, default=2)
    planificar.add_argument("--algoritmo", choices=["todos", "fcfs", "sjf", "prioridad", "rr"], default="todos")
    hilos = comandos.add_parser("hilos", help="Comparar tareas de una entrega secuencialmente y con hilos")
    hilos.add_argument("--tareas", default="todas", help="Números separados por comas (ej. 1,3) o todas")
    sincronizar = comandos.add_parser("sincronizar", help="Ejecutar productor-consumidor")
    sincronizar.add_argument("--productores", type=int, default=2)
    sincronizar.add_argument("--consumidores", type=int, default=2)
    sincronizar.add_argument("--capacidad", type=int, default=5)
    sincronizar.add_argument("--elementos", type=int, default=10, help="Cajas por operario de recepción")
    args = parser.parse_args()

    try:
        if args.comando is None:
            menu()
        elif args.comando == "procesos":
            return ejecutar_procesos(RAIZ)
        elif args.comando == "planificar":
            ejecutar_planificacion(
                cargar_csv(args.archivo), args.quantum, args.algoritmo,
                es_ejemplo=args.archivo.resolve() == EJEMPLO,
            )
        elif args.comando == "hilos":
            print(f"Las consultas externas son simuladas y esperan {ESPERA_SERVICIO_SEGUNDOS} segundos cada una.")
            resultado = demostrar_hilos(seleccionar_tareas(args.tareas))
            mostrar_hilos(resultado)
            if not resultado.resultados_coinciden:
                return 1
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

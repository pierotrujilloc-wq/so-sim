"""Lectura de las cuatro columnas acordadas con el usuario."""

import csv
from pathlib import Path

from modelos import Proceso, validar_procesos


COLUMNAS = ["Procesos", "Tiempo llegada", "Duración", "Prioridad"]


def cargar_csv(ruta: str | Path) -> list[Proceso]:
    procesos = []
    # utf-8-sig admite archivos UTF-8 con o sin la marca BOM de Excel.
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        lector = csv.reader(archivo)
        cabecera = next(lector, None)
        if cabecera != COLUMNAS:
            raise ValueError("La cabecera debe ser: " + ",".join(COLUMNAS))

        for numero, fila in enumerate(lector, start=2):
            if not fila or all(not campo.strip() for campo in fila):
                continue
            if len(fila) != 4:
                raise ValueError(f"Fila {numero}: se requieren exactamente 4 columnas.")
            try:
                proceso = Proceso(
                    fila[0].strip(), int(fila[1]), int(fila[2]), int(fila[3])
                )
            except ValueError as error:
                raise ValueError(f"Fila {numero}: {error}") from error
            procesos.append(proceso)

    validar_procesos(procesos)
    return procesos


def pedir_entero(mensaje: str, minimo: int) -> int:
    while True:
        try:
            valor = int(input(mensaje))
            if valor >= minimo:
                return valor
        except ValueError:
            pass
        print(f"Ingrese un entero mayor o igual que {minimo}.")


def ingresar_procesos() -> list[Proceso]:
    cantidad = pedir_entero("Cantidad de procesos: ", 1)
    procesos = []
    while len(procesos) < cantidad:
        print(f"\nProceso {len(procesos) + 1} de {cantidad}")
        identificador = input("Procesos (identificador, por ejemplo P1): ").strip()
        if not identificador or any(p.procesos == identificador for p in procesos):
            print("Use un identificador no vacío y que no esté repetido.")
            continue
        llegada = pedir_entero("Tiempo llegada: ", 0)
        duracion = pedir_entero("Duración: ", 1)
        prioridad = pedir_entero("Prioridad (1 es la más alta): ", 1)
        procesos.append(Proceso(identificador, llegada, duracion, prioridad))
    return procesos

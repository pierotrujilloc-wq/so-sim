"""Tareas independientes sobre una entrega compartida de solo lectura.

Para ampliar el ejemplo: escribir una función y agregarla a TAREAS.
Cada función recibe Entrega y devuelve ResultadoTarea.
"""

from dataclasses import dataclass
from datetime import date
from typing import Callable


@dataclass(frozen=True)
class ProductoEntrega:
    nombre: str
    esperadas: int
    recibidas: int
    vencimiento: date | None
    ubicacion: str


@dataclass(frozen=True)
class Entrega:
    fecha_revision: date
    productos: tuple[ProductoEntrega, ...]


@dataclass(frozen=True)
class ResultadoTarea:
    resumen: str
    detalles: tuple[str, ...]


# Fecha fija para poder reproducir los resultados en cualquier día.
ENTREGA_EJEMPLO = Entrega(date(2026, 10, 10), (
    ProductoEntrega("Arroz", 20, 18, date(2027, 6, 30), "A-01"),
    ProductoEntrega("Leche", 12, 12, date(2026, 10, 9), "R-02"),
    ProductoEntrega("Aceite", 10, 11, date(2027, 3, 31), "A-03"),
    ProductoEntrega("Detergente", 8, 8, None, ""),
))


def verificar_cantidades(entrega: Entrega) -> ResultadoTarea:
    diferencias = []
    verificadas = 0
    for producto in entrega.productos:
        diferencia = producto.recibidas - producto.esperadas
        verificadas += 1
        if diferencia != 0:
            diferencias.append(
                f"{producto.nombre}: esperadas {producto.esperadas}, "
                f"recibidas {producto.recibidas}, diferencia {diferencia:+d}."
            )
    return ResultadoTarea(f"Cantidades verificadas: {verificadas}", tuple(diferencias))


def revisar_vencimientos(entrega: Entrega) -> ResultadoTarea:
    vencidos = []
    revisados = 0
    for producto in entrega.productos:
        if producto.vencimiento is None:
            continue
        revisados += 1
        # Regla del ejemplo: fecha anterior a la revisión. La fecha igual
        # todavía no se marca vencida y None indica que no aplica.
        if producto.vencimiento < entrega.fecha_revision:
            vencidos.append(f"{producto.nombre}: venció el {producto.vencimiento.isoformat()}.")
    return ResultadoTarea(f"Vencimientos revisados: {revisados}", tuple(vencidos))


def preparar_etiquetas(entrega: Entrega) -> ResultadoTarea:
    etiquetas = []
    for producto in entrega.productos:
        # La ubicación ya viene asignada: esta tarea no espera a otra.
        # Generar una etiqueta no autoriza la venta ni valida el producto.
        if producto.ubicacion.strip():
            etiquetas.append(f"{producto.nombre} | Ubicación: {producto.ubicacion}")
    return ResultadoTarea(f"Etiquetas preparadas: {len(etiquetas)}", tuple(etiquetas))


def detectar_productos_sin_ubicacion(entrega: Entrega) -> ResultadoTarea:
    pendientes = []
    for producto in entrega.productos:
        if not producto.ubicacion.strip():
            pendientes.append(f"{producto.nombre}: falta asignar un estante.")
    return ResultadoTarea(f"Productos detectados sin ubicación: {len(pendientes)}", tuple(pendientes))


Tarea = tuple[str, Callable[[Entrega], ResultadoTarea]]

# El menú y las dos modalidades recorren esta lista, sin un límite de tres.
TAREAS: list[Tarea] = [
    ("Verificar cantidades", verificar_cantidades),
    ("Revisar vencimientos", revisar_vencimientos),
    ("Preparar etiquetas", preparar_etiquetas),
    ("Detectar productos sin ubicación", detectar_productos_sin_ubicacion),
]


def seleccionar_tareas(seleccion: str) -> list[Tarea]:
    if seleccion.strip().lower() in ("", "0", "todas"):
        return list(TAREAS)
    elegidas = []
    numeros = set()
    for texto in seleccion.split(","):
        try:
            numero = int(texto.strip())
        except ValueError as error:
            raise ValueError("Use números separados por comas, por ejemplo 1,3, o 'todas'.") from error
        if numero < 1 or numero > len(TAREAS):
            raise ValueError(f"Elija tareas entre 1 y {len(TAREAS)}.")
        if numero in numeros:
            raise ValueError(f"La tarea {numero} está repetida.")
        numeros.add(numero)
        elegidas.append(TAREAS[numero - 1])
    return elegidas

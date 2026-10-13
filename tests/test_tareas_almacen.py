"""Resultados del caso, ampliación de tareas y fallos de ejecución."""

from contextlib import redirect_stdout
from datetime import date
from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from hilos import demostrar_hilos
from presentacion import mostrar_hilos
from tareas_almacen import (
    ENTREGA_EJEMPLO, TAREAS, Entrega, ProductoEntrega, ResultadoTarea,
    detectar_productos_sin_ubicacion, preparar_etiquetas, revisar_vencimientos,
    seleccionar_tareas, verificar_cantidades,
)


class PruebasTareasAlmacen(unittest.TestCase):
    def test_cantidades_y_productos_identificados(self):
        resultado = verificar_cantidades(ENTREGA_EJEMPLO)
        self.assertEqual(resultado, ResultadoTarea("Cantidades verificadas: 4", (
            "Arroz: esperadas 20, recibidas 18, diferencia -2.",
            "Aceite: esperadas 10, recibidas 11, diferencia +1.",
        )))

    def test_vencimientos_fecha_limite_y_sin_fecha(self):
        entrega = Entrega(date(2026, 10, 10), (
            ProductoEntrega("Anterior", 1, 1, date(2026, 10, 9), "A"),
            ProductoEntrega("Hoy", 1, 1, date(2026, 10, 10), "A"),
            ProductoEntrega("Posterior", 1, 1, date(2026, 10, 11), "A"),
            ProductoEntrega("Sin fecha", 1, 1, None, "A"),
        ))
        self.assertEqual(revisar_vencimientos(entrega), ResultadoTarea(
            "Vencimientos revisados: 3", ("Anterior: venció el 2026-10-09.",),
        ))

    def test_etiquetas_y_ubicaciones_pendientes(self):
        self.assertEqual(preparar_etiquetas(ENTREGA_EJEMPLO), ResultadoTarea("Etiquetas preparadas: 3", (
            "Arroz | Ubicación: A-01", "Leche | Ubicación: R-02", "Aceite | Ubicación: A-03",
        )))
        self.assertEqual(detectar_productos_sin_ubicacion(ENTREGA_EJEMPLO), ResultadoTarea(
            "Productos detectados sin ubicación: 1", ("Detergente: falta asignar un estante.",),
        ))
        entrega = Entrega(date(2026, 10, 10), (ProductoEntrega("Otro", 1, 1, None, "  "),))
        self.assertEqual(preparar_etiquetas(entrega).resumen, "Etiquetas preparadas: 0")
        self.assertEqual(detectar_productos_sin_ubicacion(entrega).resumen, "Productos detectados sin ubicación: 1")

    def test_entrega_vacia(self):
        entrega = Entrega(date(2026, 10, 10), ())
        resultado = demostrar_hilos(TAREAS[:4], entrega=entrega)
        self.assertTrue(resultado.resultados_coinciden)
        for registro in resultado.secuencial:
            self.assertTrue(registro.resultado.resumen.endswith(": 0"))
            self.assertEqual(registro.resultado.detalles, ())

    def test_seleccion_completa_parcial_y_errores(self):
        for entrada in ("", "  ", "0", " TODAS "):
            self.assertEqual(seleccionar_tareas(entrada), TAREAS)
        self.assertEqual(seleccionar_tareas("3, 1"), [TAREAS[2], TAREAS[0]])
        for entrada in ("1,1", "0,1", str(len(TAREAS) + 1), "-1", "abc", "1,", "1.5"):
            with self.subTest(entrada=entrada), self.assertRaises(ValueError):
                seleccionar_tareas(entrada)
        with self.assertRaises(ValueError):
            demostrar_hilos([])

    def test_nueva_tarea_se_integra_en_ambas_modalidades(self):
        entregas_recibidas = []

        def contar_productos(entrega):
            entregas_recibidas.append(entrega)
            return ResultadoTarea(f"Productos: {len(entrega.productos)}", ())

        # La extensión solo registra una función, sin cambiar el ejecutor.
        TAREAS.append(("Contar productos", contar_productos))
        try:
            resultado = demostrar_hilos(seleccionar_tareas(str(len(TAREAS))))
            self.assertTrue(resultado.resultados_coinciden)
            self.assertEqual(resultado.secuencial[0].resultado.resumen, "Productos: 4")
            self.assertEqual(len(entregas_recibidas), 2)
            self.assertTrue(all(entrega is ENTREGA_EJEMPLO for entrega in entregas_recibidas))
        finally:
            TAREAS.pop()

    def test_error_de_tarea_no_oculta_resultados_de_otras(self):
        def fallar(entrega):
            raise ValueError("Fallo de ejemplo")

        resultado = demostrar_hilos([("Falla", fallar), TAREAS[0]])
        self.assertFalse(resultado.resultados_coinciden)
        for registros in (resultado.secuencial, resultado.con_hilos):
            self.assertIn("ValueError: Fallo de ejemplo", registros[0].error)
            self.assertIsNone(registros[0].resultado)
            self.assertEqual(registros[1].resultado.resumen, "Cantidades verificadas: 4")
        salida = StringIO()
        with redirect_stdout(salida):
            mostrar_hilos(resultado)
        self.assertIn("50.00%", salida.getvalue())
        self.assertIn("Comparación no válida", salida.getvalue())
        self.assertNotIn("Menor tiempo total observado", salida.getvalue())

    def test_consultas_simulan_una_espera_por_tarea_y_modalidad(self):
        with patch("tareas_almacen.sleep") as pausa:
            resultado = demostrar_hilos(seleccionar_tareas("5,6,7"))
        self.assertTrue(resultado.resultados_coinciden)
        self.assertEqual(pausa.call_count, 6)
        self.assertTrue(all(llamada.args == (2,) for llamada in pausa.call_args_list))
        self.assertEqual([r.resultado.resumen for r in resultado.secuencial], [
            "Consulta a sucursal completada (simulada)",
            "Consulta al proveedor completada (simulada)",
            "Confirmación de transporte recibida (simulada)",
        ])

    def test_resultados_distintos_invalidan_comparacion(self):
        contador = 0

        def tarea_con_estado(entrega):
            nonlocal contador
            contador += 1
            return ResultadoTarea("Mismo resumen", (str(contador),))

        resultado = demostrar_hilos([("Con estado", tarea_con_estado)])
        self.assertFalse(resultado.resultados_coinciden)
        salida = StringIO()
        with redirect_stdout(salida):
            mostrar_hilos(resultado)
        self.assertIn("N/D", salida.getvalue())
        self.assertIn("Comparación no válida", salida.getvalue())
        self.assertNotIn("Menor tiempo total observado", salida.getvalue())


if __name__ == "__main__":
    unittest.main()

"""Verifica porcentajes contra cuentas manuales y casos sin referencia."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from entrada import cargar_csv
from evaluacion import porcentajes_proceso, reduccion_porcentual
from hilos import demostrar_hilos
from modelos import Metrica, Proceso
from planificacion import fcfs, por_prioridad, round_robin, sjf
from presentacion import mostrar_comparacion, mostrar_hilos


class PruebasEvaluacion(unittest.TestCase):
    def capturar(self, funcion, argumento):
        salida = StringIO()
        with redirect_stdout(salida):
            funcion(argumento)
        return salida.getvalue()

    def test_porcentajes_de_p1_en_round_robin(self):
        # Retorno 21 = duración 8 + espera 13; primera respuesta inmediata.
        eficiencia, espera = porcentajes_proceso(Metrica("P1", 0, 21, 13, 0, 21))
        self.assertAlmostEqual(eficiencia, 38.095238095238095)
        self.assertAlmostEqual(espera, 61.904761904761905)
        self.assertAlmostEqual(eficiencia + espera, 100)

    def test_proceso_sin_espera(self):
        self.assertEqual(porcentajes_proceso(Metrica("P1", 3, 8, 0, 0, 5)), (100, 0))

    def test_mejoras_y_empeoramientos(self):
        self.assertAlmostEqual(reduccion_porcentual(8.4, 7.4), 11.904761904761905)
        self.assertAlmostEqual(reduccion_porcentual(8.4, 9.4), -11.904761904761905)
        self.assertAlmostEqual(reduccion_porcentual(8.4, 3), 64.28571428571429)

    def test_referencia_cero(self):
        self.assertEqual(reduccion_porcentual(0, 0), 0)
        self.assertIsNone(reduccion_porcentual(0, 1))

    def test_tabla_compara_el_mismo_proceso(self):
        procesos = cargar_csv(Path(__file__).resolve().parents[1] / "data/processes/ejemplo.csv")
        resultados = [fcfs(procesos), sjf(procesos), por_prioridad(procesos), round_robin(procesos, 2)]
        texto = self.capturar(mostrar_comparacion, resultados)
        fila_p3 = next(linea for linea in texto.splitlines() if linea.startswith("P3 "))
        columnas = [celda.strip() for celda in fila_p3.split("|")]
        self.assertEqual(columnas[1:5], ["16.67%", "25.00%", "25.00%", "50.00%"])
        self.assertEqual(columnas[-1], "Round Robin (q=2)")
        self.assertIn("64.29%", texto)
        self.assertIn("-11.90%", texto)

    def test_empates_y_cero_espera(self):
        procesos = [Proceso("A", 0, 2, 1)]
        texto = self.capturar(mostrar_comparacion, [fcfs(procesos), sjf(procesos)])
        fila = next(linea for linea in texto.splitlines() if linea.startswith("A "))
        self.assertIn("FCFS, SJF sin desalojo", fila)
        self.assertIn("0.00%", texto)
        self.assertNotIn("nan", texto)
        self.assertNotIn("inf%", texto)

    def test_algoritmo_individual_sin_fcfs(self):
        texto = self.capturar(mostrar_comparacion, [sjf([Proceso("A", 0, 2, 1)])])
        fila = next(linea for linea in texto.splitlines() if linea.startswith("SJF sin desalojo |"))
        self.assertEqual(fila.count("N/D"), 2)

    def test_medicion_de_lote_incluye_gestion_de_hilos(self):
        # Con un hilo, las lecturas del reloj tienen un orden determinista.
        # Evita afirmar que una modalidad siempre gana en equipos reales.
        with patch("hilos.perf_counter_ns", side_effect=[100, 200, 300, 400, 450, 600]):
            resultado = demostrar_hilos(1, 5)
        self.assertEqual(resultado.resultados, [15])
        self.assertEqual(resultado.tiempo_secuencial_ns, 100)
        self.assertEqual(resultado.tiempo_hilos_ns, 300)
        self.assertEqual(resultado.tiempos_tareas_ns, [50])
        texto = self.capturar(mostrar_hilos, resultado)
        self.assertIn("-200.00%", texto)
        self.assertIn("Menor tiempo total observado: Secuencial", texto)
        self.assertIn("100.00%", texto)


if __name__ == "__main__":
    unittest.main()

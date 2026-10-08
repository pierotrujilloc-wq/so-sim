from pathlib import Path
import subprocess
import sys
import unittest

RAIZ = Path(__file__).resolve().parents[1]


class PruebasConsola(unittest.TestCase):
    def ejecutar(self, argumentos, entrada=None):
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(RAIZ / "python/main.py"), *argumentos],
            input=entrada, capture_output=True, text=True, encoding="utf-8", timeout=15,
        )

    def test_comparacion_con_ejemplo_por_defecto(self):
        resultado = self.ejecutar(["planificar"])
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        for texto in ("SuperAlmacén", "P3: verificar un lote refrigerado urgente", "Tiempo llegada", "Duración", "FCFS", "SJF", "Prioridad", "Round Robin", "9.40"):
            self.assertIn(texto, resultado.stdout)

    def test_error_de_archivo_no_muestra_traceback(self):
        resultado = self.ejecutar(["planificar", "--archivo", "no-existe.csv"])
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("Error:", resultado.stdout)
        self.assertNotIn("Traceback", resultado.stderr)

    def test_menu_ingreso_manual_y_salida(self):
        # Opción 2, un proceso, cuatro campos, quantum, salir.
        resultado = self.ejecutar([], "2\n1\nP1\n0\n3\n1\n2\n0\n")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Round Robin (q=2)", resultado.stdout)
        self.assertNotIn("Órdenes del ejemplo:", resultado.stdout)

    def test_hilos_presenta_tablas_y_contexto(self):
        resultado = self.ejecutar(["hilos", "--cantidad", "2", "--limite", "5"])
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        for texto in ("SuperAlmacén", "Unidades", "Cumplimiento", "50.00%", "100.00%", "Reducción vs secuencial"):
            self.assertIn(texto, resultado.stdout)

    def test_menu_hilos_recepcion_y_procesos_c(self):
        resultado = self.ejecutar([], "4\n2\n5\n5\n2\n2\n1\n1\n6\n0\n")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        for texto in ("Comparación de hilos", "zona de recepción", "búfer vacío", "jefe (padre)", "gcc -std=c11"):
            self.assertIn(texto, resultado.stdout)


if __name__ == "__main__":
    unittest.main()

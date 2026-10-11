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
        resultado = self.ejecutar(["hilos"])
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        for texto in ("SuperAlmacén", "Inicio (ms)", "Fin (ms)", "Duración (ms)", "Cumplimiento", "100.00%", "Reducción vs secuencial"):
            self.assertIn(texto, resultado.stdout)
        secuencial, hilos = resultado.stdout.split("=== Modalidad con hilos: tareas de la entrega ===")
        self.assertIn("=== Modalidad secuencial: tareas de la entrega ===", secuencial)
        self.assertIn("Hilo principal", secuencial)
        for tabla in (secuencial, hilos):
            for texto in ("Cantidades verificadas: 4", "Vencimientos revisados: 3",
                          "Etiquetas preparadas: 3", "Productos detectados sin ubicación: 1"):
                self.assertIn(texto, tabla)
        for texto in ("Detalle de resultados:", "venció el", "Arroz | Ubicación:", "falta asignar un estante"):
            self.assertNotIn(texto, resultado.stdout)
        self.assertIn("todos los resultados y detalles coinciden", resultado.stdout)

    def test_hilos_seleccion_de_tareas(self):
        resultado = self.ejecutar(["hilos", "--tareas", "1,3"])
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        for texto in ("Verificar cantidades", "Preparar etiquetas", "Hilo-1", "Hilo-2"):
            self.assertIn(texto, resultado.stdout)
        for texto in ("Revisar vencimientos", "Detectar productos sin ubicación", "Hilo-3"):
            self.assertNotIn(texto, resultado.stdout)

    def test_hilos_seleccion_invalida(self):
        resultado = self.ejecutar(["hilos", "--tareas", "1,1"])
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("repetida", resultado.stdout)
        self.assertNotIn("Traceback", resultado.stderr)

    def test_menu_hilos_corrige_seleccion(self):
        resultado = self.ejecutar([], "4\n99\n\n0\n")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Error: Elija tareas", resultado.stdout)
        self.assertIn("todos los resultados y detalles coinciden", resultado.stdout)

    def test_menu_hilos_y_recepcion(self):
        resultado = self.ejecutar([], "4\n1,3\n5\n2\n2\n1\n1\n0\n")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        for texto in ("Modalidad secuencial", "Modalidad con hilos", "zona de recepción", "búfer vacío"):
            self.assertIn(texto, resultado.stdout)


if __name__ == "__main__":
    unittest.main()

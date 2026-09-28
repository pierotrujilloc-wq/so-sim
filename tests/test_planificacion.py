"""Resultados calculados a mano e invariantes de uso de la CPU."""

from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from entrada import cargar_csv
from modelos import Proceso
from planificacion import fcfs, por_prioridad, round_robin, sjf


class PruebasPlanificacion(unittest.TestCase):
    def setUp(self):
        ruta = Path(__file__).resolve().parents[1] / "data/processes/ejemplo.csv"
        self.procesos = cargar_csv(ruta)

    def verificar_caso(self, funcion, gantt, esperas, respuestas, finales):
        resultado = funcion(self.procesos)
        obtenido = [(t.proceso, t.inicio, t.fin) for t in resultado.tramos]
        self.assertEqual(obtenido, gantt)
        self.assertEqual([m.espera for m in resultado.metricas], esperas)
        self.assertEqual([m.respuesta for m in resultado.metricas], respuestas)
        self.assertEqual([m.fin for m in resultado.metricas], finales)
        self.assertEqual(
            [m.retorno for m in resultado.metricas],
            [fin - p.tiempo_llegada for fin, p in zip(finales, self.procesos)],
        )

    def test_fcfs_calculado_a_mano(self):
        self.verificar_caso(fcfs, [
            ("P1", 0, 8), ("P2", 8, 12), ("P3", 12, 14),
            ("P4", 14, 19), ("P5", 19, 22),
        ], [0, 7, 10, 11, 14], [0, 7, 10, 11, 14], [8, 12, 14, 19, 22])

    def test_sjf_calculado_a_mano(self):
        self.verificar_caso(sjf, [
            ("P1", 0, 8), ("P3", 8, 10), ("P5", 10, 13),
            ("P2", 13, 17), ("P4", 17, 22),
        ], [0, 12, 6, 14, 5], [0, 12, 6, 14, 5], [8, 17, 10, 22, 13])

    def test_prioridad_calculada_a_mano(self):
        self.verificar_caso(por_prioridad, [
            ("P1", 0, 8), ("P3", 8, 10), ("P2", 10, 14),
            ("P4", 14, 19), ("P5", 19, 22),
        ], [0, 9, 6, 11, 14], [0, 9, 6, 11, 14], [8, 14, 10, 19, 22])

    def test_round_robin_calculado_a_mano(self):
        self.verificar_caso(lambda p: round_robin(p, 2), [
            ("P1", 0, 2), ("P2", 2, 4), ("P3", 4, 6), ("P1", 6, 8),
            ("P4", 8, 10), ("P2", 10, 12), ("P5", 12, 14), ("P1", 14, 16),
            ("P4", 16, 18), ("P5", 18, 19), ("P1", 19, 21), ("P4", 21, 22),
        ], [13, 7, 2, 14, 11], [0, 1, 2, 5, 7], [21, 12, 6, 22, 19])

    def test_llegada_en_limite_de_quantum_precede_reencolado(self):
        procesos = [Proceso("A", 0, 4, 1), Proceso("B", 2, 1, 1)]
        resultado = round_robin(procesos, 2)
        self.assertEqual(
            [(t.proceso, t.inicio, t.fin) for t in resultado.tramos],
            [("A", 0, 2), ("B", 2, 3), ("A", 3, 5)],
        )

    def test_cpu_libre_y_entrada_desordenada(self):
        procesos = [Proceso("B", 7, 1, 1), Proceso("A", 2, 2, 1)]
        esperado = [(None, 0, 2), ("A", 2, 4), (None, 4, 7), ("B", 7, 8)]
        for funcion in (fcfs, sjf, por_prioridad, lambda p: round_robin(p, 2)):
            with self.subTest(algoritmo=funcion.__name__):
                resultado = funcion(procesos)
                self.assertEqual([(t.proceso, t.inicio, t.fin) for t in resultado.tramos], esperado)
                self.assertTrue(all(m.espera == 0 for m in resultado.metricas))

    def test_empates_respetan_llegada_y_orden_de_entrada(self):
        procesos = [Proceso("Z", 0, 2, 1), Proceso("A", 0, 2, 1), Proceso("B", 1, 2, 1)]
        for funcion in (fcfs, sjf, por_prioridad):
            with self.subTest(algoritmo=funcion.__name__):
                self.assertEqual([t.proceso for t in funcion(procesos).tramos], ["Z", "A", "B"])

    def test_sjf_y_prioridad_no_interrumpen_por_nuevas_llegadas(self):
        procesos = [Proceso("A", 0, 8, 4), Proceso("B", 1, 1, 1)]
        for funcion in (sjf, por_prioridad):
            self.assertEqual(funcion(procesos).tramos[0].fin, 8)

    def test_quantum_grande_equivale_a_fcfs(self):
        self.assertEqual(round_robin(self.procesos, 100).tramos, fcfs(self.procesos).tramos)

    def test_quantum_y_entradas_invalidas(self):
        for quantum in (0, -1, 1.5, True):
            with self.subTest(quantum=quantum), self.assertRaises(ValueError):
                round_robin(self.procesos, quantum)
        for funcion in (fcfs, sjf, por_prioridad, lambda p: round_robin(p, 2)):
            with self.assertRaises(ValueError):
                funcion([])
            with self.assertRaises(ValueError):
                funcion([Proceso("A", 0, 1, 1), Proceso("A", 1, 2, 1)])

    def test_invariantes_en_casos_generados(self):
        # No reimplementa los algoritmos: comprueba propiedades necesarias
        # para cualquier planificación válida con estos supuestos.
        generador = random.Random(407)
        for caso in range(40):
            procesos = [
                Proceso(f"P{i}", generador.randrange(12), generador.randrange(1, 9), generador.randrange(1, 5))
                for i in range(generador.randrange(1, 8))
            ]
            original = list(procesos)
            quantum = generador.randrange(1, 5)
            for funcion in (fcfs, sjf, por_prioridad, lambda p: round_robin(p, quantum)):
                with self.subTest(caso=caso, algoritmo=funcion.__name__):
                    resultado = funcion(procesos)
                    self.assertEqual(procesos, original)
                    ejecutado = {p.procesos: 0 for p in procesos}
                    por_nombre = {p.procesos: p for p in procesos}
                    tiempo = 0
                    for tramo in resultado.tramos:
                        self.assertEqual(tramo.inicio, tiempo)
                        self.assertGreater(tramo.fin, tramo.inicio)
                        if tramo.proceso is not None:
                            proceso = por_nombre[tramo.proceso]
                            self.assertGreaterEqual(tramo.inicio, proceso.tiempo_llegada)
                            ejecutado[tramo.proceso] += tramo.fin - tramo.inicio
                            self.assertLessEqual(ejecutado[tramo.proceso], proceso.duracion)
                            if resultado.algoritmo.startswith("Round Robin"):
                                self.assertLessEqual(tramo.fin - tramo.inicio, quantum)
                        else:
                            for p in procesos:
                                if ejecutado[p.procesos] < p.duracion:
                                    self.assertGreaterEqual(p.tiempo_llegada, tramo.fin)
                        tiempo = tramo.fin
                    self.assertEqual(ejecutado, {p.procesos: p.duracion for p in procesos})
                    for metrica in resultado.metricas:
                        self.assertGreaterEqual(metrica.espera, metrica.respuesta)
                        self.assertGreaterEqual(metrica.respuesta, 0)


if __name__ == "__main__":
    unittest.main()

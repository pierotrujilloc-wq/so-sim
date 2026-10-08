"""Cada escenario corre en un subproceso con límite de tiempo.

Si aparece un interbloqueo, la prueba falla por timeout y termina el
subproceso, sin dejar la suite esperando indefinidamente.
"""

import json
from pathlib import Path
import subprocess
import sys
import unittest

PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

from sincronizacion import ejecutar_productor_consumidor


class PruebasConcurrencia(unittest.TestCase):
    def ejecutar_aislado(self, codigo):
        resultado = subprocess.run(
            [sys.executable, "-c", codigo], cwd=PYTHON_DIR,
            capture_output=True, text=True, encoding="utf-8", timeout=15,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        return json.loads(resultado.stdout)

    def test_productores_consumidores_y_finalizacion(self):
        for productores, consumidores, capacidad, cantidad in [
            (2, 3, 1, 20), (1, 8, 2, 1), (3, 2, 5, 0), (4, 3, 7, 25),
        ]:
            with self.subTest(configuracion=(productores, consumidores, capacidad, cantidad)):
                codigo = (
                    "import json\nfrom dataclasses import asdict\n"
                    "from sincronizacion import ejecutar_productor_consumidor\n"
                    f"resultado = ejecutar_productor_consumidor({productores}, {consumidores}, {capacidad}, {cantidad})\n"
                    "print(json.dumps(asdict(resultado)))\n"
                )
                resultado = self.ejecutar_aislado(codigo)
                esperados = {
                    f"P{p}-item{n:02d}" for p in range(1, productores + 1)
                    for n in range(1, cantidad + 1)
                }
                self.assertEqual(set(resultado["producidos"]), esperados)
                self.assertEqual(len(resultado["producidos"]), len(esperados))
                self.assertEqual(resultado["producidos"], resultado["consumidos"])
                ocupacion = 0
                finales = []
                for evento in resultado["eventos"]:
                    ocupacion += 1 if evento["accion"] == "insertar" else -1
                    self.assertEqual(evento["ocupacion"], ocupacion)
                    self.assertTrue(0 <= ocupacion <= capacidad)
                    if evento["accion"] == "retirar" and evento["elemento"] is None:
                        finales.append(evento["hilo"])
                self.assertEqual(ocupacion, 0)
                self.assertEqual(len(finales), consumidores)
                self.assertEqual(len(set(finales)), consumidores)

    def test_hilos_completan_tareas_antes_de_retornar(self):
        resultado = self.ejecutar_aislado(
            "import json\nfrom dataclasses import asdict\n"
            "from hilos import demostrar_hilos\n"
            "print(json.dumps(asdict(demostrar_hilos(4, 100))))\n"
        )
        self.assertEqual(resultado["resultados"], [5050] * 4)
        for numero in range(1, 5):
            inicio = resultado["eventos"].index(f"Hilo-{numero}: inicio")
            fin = resultado["eventos"].index(f"Hilo-{numero}: fin, unidades = 5050")
            self.assertLess(inicio, fin)

    def test_configuracion_invalida(self):
        for parametros in [(0, 1, 1, 1), (1, 0, 1, 1), (1, 1, 0, 1), (1, 1, 1, -1)]:
            with self.subTest(parametros=parametros), self.assertRaises(ValueError):
                ejecutar_productor_consumidor(*parametros)


if __name__ == "__main__":
    unittest.main()

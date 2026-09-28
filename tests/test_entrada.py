from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from entrada import cargar_csv
from modelos import Proceso


class PruebasEntrada(unittest.TestCase):
    def cargar_texto(self, texto):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "entrada.csv"
            ruta.write_text(texto, encoding="utf-8-sig")
            return cargar_csv(ruta)

    def test_cuatro_columnas_utf8_y_lineas_vacias(self):
        procesos = self.cargar_texto("Procesos,Tiempo llegada,Duración,Prioridad\nP1,0,3,1\n\n")
        self.assertEqual(procesos, [Proceso("P1", 0, 3, 1)])

    def test_archivos_invalidos(self):
        cabecera = "Procesos,Tiempo llegada,Duración,Prioridad\n"
        textos = [
            "", "Nombre,Llegada,Duracion,Prioridad\nA,0,1,1\n", cabecera,
            cabecera + "A,0,1,1,extra\n", cabecera + "A,0,1\n",
            cabecera + "A,0,1.5,1\n", cabecera + "A,-1,1,1\n",
            cabecera + "A,0,0,1\n", cabecera + "A,0,1,0\n",
            cabecera + ",0,1,1\n", cabecera + "A,0,1,1\nA,2,3,1\n",
        ]
        for texto in textos:
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                self.cargar_texto(texto)

    def test_proceso_rechaza_tipos_invalidos(self):
        for datos in [(" ", 0, 1, 1), ("A", True, 1, 1), ("A", 0, 2.5, 1)]:
            with self.subTest(datos=datos), self.assertRaises(ValueError):
                Proceso(*datos)


if __name__ == "__main__":
    unittest.main()

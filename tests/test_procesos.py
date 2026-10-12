"""Pruebas del puente Python/C sin exigir WSL o GCC para ejecutar la suite."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

import main
from procesos import ejecutar_procesos


class PruebasProcesos(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name) / "proyecto con espacios"
        (self.raiz / "c").mkdir(parents=True)
        (self.raiz / "c/procesos.c").write_text("int main(void) { return 0; }", encoding="utf-8")
        self.salida = StringIO()
        self.enterContext(redirect_stdout(self.salida))

    def test_compila_antes_de_ejecutar_en_windows_y_linux(self):
        for plataforma in ("win32", "linux"):
            with self.subTest(plataforma=plataforma), patch("procesos.sys.platform", plataforma), patch("procesos.subprocess.run") as ejecutar:
                ejecutar.return_value = subprocess.CompletedProcess([], 0)
                self.assertEqual(ejecutar_procesos(self.raiz), 0)
                self.assertTrue((self.raiz / "build").is_dir())
                self.assertEqual(ejecutar.call_count, 2)
                compilar, iniciar = ejecutar.call_args_list
                prefijo = ["wsl.exe", "-d", "Ubuntu", "--cd", str(self.raiz), "--exec"] if plataforma == "win32" else []
                self.assertEqual(compilar.args[0], prefijo + [
                    "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    "c/procesos.c", "-o", "build/procesos",
                ])
                self.assertEqual(iniciar.args[0], prefijo + ["./build/procesos"])
                for llamada in ejecutar.call_args_list:
                    self.assertEqual(llamada.kwargs["cwd"], self.raiz)
                    self.assertEqual(llamada.kwargs["stdin"], subprocess.DEVNULL)
                    self.assertFalse(llamada.kwargs.get("shell", False))
                    self.assertNotIn("stdout", llamada.kwargs)  # Hereda la terminal.

    def test_error_de_compilacion_no_ejecuta_binario_anterior(self):
        (self.raiz / "build").mkdir()
        (self.raiz / "build/procesos").write_text("anterior", encoding="utf-8")
        with patch("procesos.subprocess.run") as ejecutar:
            ejecutar.return_value = subprocess.CompletedProcess([], 2)
            self.assertEqual(ejecutar_procesos(self.raiz), 2)
            ejecutar.assert_called_once()
        self.assertIn("compilación falló", self.salida.getvalue())

    def test_retorna_error_del_programa_c(self):
        with patch("procesos.subprocess.run", side_effect=[
            subprocess.CompletedProcess([], 0), subprocess.CompletedProcess([], 7),
        ]):
            self.assertEqual(ejecutar_procesos(self.raiz), 7)
        self.assertIn("programa C terminó con código 7", self.salida.getvalue())

    def test_falta_wsl_o_gcc(self):
        with patch("procesos.subprocess.run", side_effect=FileNotFoundError("ejecutable ausente")):
            self.assertEqual(ejecutar_procesos(self.raiz), 1)
        self.assertIn("Ubuntu en WSL", self.salida.getvalue())

    def test_falta_codigo_fuente(self):
        with patch("procesos.subprocess.run") as ejecutar:
            self.assertEqual(ejecutar_procesos(self.raiz / "inexistente"), 1)
            ejecutar.assert_not_called()

    def test_timeout_en_compilacion_o_ejecucion(self):
        for efectos in ([subprocess.TimeoutExpired("gcc", 60)], [
            subprocess.CompletedProcess([], 0), subprocess.TimeoutExpired("procesos", 15),
        ]):
            with self.subTest(efectos=efectos), patch("procesos.subprocess.run", side_effect=efectos):
                self.assertEqual(ejecutar_procesos(self.raiz), 124)

    def test_opcion_seis_regresa_al_menu_incluso_si_falla(self):
        for codigo in (0, 1):
            with self.subTest(codigo=codigo), patch("main.ejecutar_procesos", return_value=codigo) as ejecutar, patch("builtins.input", side_effect=["6", "0"]) as entrada:
                main.menu()
                ejecutar.assert_called_once_with(main.RAIZ)
                self.assertEqual(entrada.call_count, 2)

    def test_comando_procesos_conserva_codigo_de_salida(self):
        with patch("sys.argv", ["main.py", "procesos"]), patch("main.ejecutar_procesos", return_value=7):
            self.assertEqual(main.main(), 7)


if __name__ == "__main__":
    unittest.main()

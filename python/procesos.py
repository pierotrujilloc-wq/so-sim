"""Compilar y ejecutar la demostración de fork/exec desde el menú.

subprocess conecta Python con el programa C. En Windows, Ubuntu WSL
proporciona las llamadas POSIX; en Linux se usa GCC directamente.
"""

from pathlib import Path
import subprocess
import sys


def comando_del_entorno(argumentos: list[str], raiz: Path) -> list[str]:
    # Cada argumento viaja por separado: las rutas con espacios no se
    # convierten en instrucciones de una shell. No se utiliza shell=True.
    if sys.platform == "win32":
        return ["wsl.exe", "-d", "Ubuntu", "--cd", str(raiz), "--exec", *argumentos]
    return argumentos


def ejecutar_procesos(raiz: Path) -> int:
    """Devuelve cero al terminar correctamente o el código del paso que falló."""
    if sys.platform not in ("win32", "linux"):
        print("Esta demostración requiere Linux o Windows con Ubuntu en WSL.")
        return 1

    raiz = raiz.resolve()
    if not (raiz / "c" / "procesos.c").is_file():
        print(f"No se encontró el código C: {raiz / 'c' / 'procesos.c'}")
        return 1

    print("\nSuperAlmacén: el jefe (padre) crea un operario (hijo) para contar productos de una entrega.", flush=True)
    entorno = "Ubuntu WSL" if sys.platform == "win32" else "Linux"
    etapa = "preparar la carpeta de compilación"
    try:
        (raiz / "build").mkdir(exist_ok=True)
        etapa = "compilar"
        print(f"Compilando c/procesos.c con GCC en {entorno}...", flush=True)
        compilacion = subprocess.run(
            comando_del_entorno([
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "c/procesos.c", "-o", "build/procesos",
            ], raiz),
            cwd=raiz, stdin=subprocess.DEVNULL, timeout=60, check=False,
        )
        # Si falla, no ejecutar un binario que haya quedado de una versión anterior.
        if compilacion.returncode != 0:
            print(f"La compilación falló (código {compilacion.returncode}).")
            print(f"Revisa el error anterior y comprueba que GCC esté instalado en {entorno}.")
            return compilacion.returncode

        etapa = "ejecutar"
        print("Ejecutando la demostración de fork, execvp y waitpid...", flush=True)
        ejecucion = subprocess.run(
            comando_del_entorno(["./build/procesos"], raiz),
            cwd=raiz, stdin=subprocess.DEVNULL, timeout=15, check=False,
        )
        # stdout y stderr se heredan: la salida de C aparece en esta terminal.
        # DEVNULL evita que el programa externo consuma las opciones del menú.
        if ejecucion.returncode == 0:
            print("Demostración de procesos finalizada.")
        else:
            print(f"El programa C terminó con código {ejecucion.returncode}.")
        return ejecucion.returncode
    except subprocess.TimeoutExpired:
        print(f"Se agotó el tiempo permitido para {etapa} en {entorno}.")
        return 124
    except OSError as error:
        print(f"No se pudo {etapa}: {error}")
        print("En Windows se necesita Ubuntu en WSL con GCC; en Linux se necesita GCC.")
        return 1

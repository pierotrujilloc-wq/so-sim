# SO-Sim — Módulos 1 y 2

Simulador educativo para el curso de Sistemas Operativos. Incluye procesos
en C, hilos en Python, cuatro algoritmos de planificación y el problema
productor-consumidor. La interfaz es por consola y los algoritmos están
escritos con listas, ciclos y condiciones para facilitar su explicación.

## Requisitos

- Python 3.10 o posterior. Solo se usa su biblioteca estándar; no hay paquetes
  que instalar con `pip`.
- Linux o Ubuntu en WSL y GCC para la demostración de procesos en C.
- El planificador y los hilos también funcionan directamente en Windows.

## Ejecutar en Windows

Abre la terminal de tu editor en la carpeta `so-sim` y ejecuta:

```powershell
.\ejecutar.bat
```

El archivo usa el entorno local `.venv`, que ya está creado en este equipo.
No necesitas activar el entorno ni escribir la ruta completa de Python.
El menú permite cargar el CSV de ejemplo, ingresar procesos manualmente,
cargar otro CSV, ejecutar hilos y ejecutar productor-consumidor.

También acepta comandos:

```powershell
.\ejecutar.bat planificar --quantum 2
.\ejecutar.bat sincronizar --capacidad 3 --elementos 5
```

### Crear el entorno en otra copia del proyecto

`.venv` está excluido de Git y se crea una sola vez en cada equipo. Si el
comando `python` está disponible:

```powershell
python -m venv --without-pip .venv
```

En este equipo, la instalación base está en la siguiente ruta:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" -m venv --without-pip .venv
```

El entorno usa esa instalación base; no es una copia portátil de Python.
Se omite `pip` porque el proyecto solo necesita la biblioteca estándar.
También puedes ejecutar directamente `python python/main.py` si tienes
Python configurado en el PATH.

## Ejecutar en Linux o WSL

Desde la raíz del proyecto:

```bash
python3 python/main.py
```

También se pueden ejecutar casos directamente:

```bash
python3 python/main.py planificar --archivo data/processes/ejemplo.csv --quantum 2
python3 python/main.py planificar --algoritmo sjf
python3 python/main.py planificar --algoritmo rr --quantum 3
python3 python/main.py hilos --cantidad 3 --limite 5
python3 python/main.py sincronizar --productores 2 --consumidores 2 --capacidad 5 --elementos 10
```

En Windows, reemplaza `python3 python/main.py` por `.\ejecutar.bat`.
`--elementos` es la cantidad que produce **cada productor**.

### Procesos en C

En una terminal Linux/WSL, desde la raíz del proyecto:

```bash
mkdir -p build
gcc -std=c11 -Wall -Wextra -Werror c/procesos.c -o build/procesos
./build/procesos
```

El programa muestra el PID del padre y del hijo, ejecuta `execvp` en el hijo
y recoge su terminación mediante `waitpid`. El ejemplo requiere las llamadas
POSIX de Linux; el GCC de Windows por sí solo no proporciona `fork`.

## Datos del planificador

El CSV se guarda en UTF-8, separado por comas, y tiene exactamente esta cabecera:

```csv
Procesos,Tiempo llegada,Duración,Prioridad
P1,0,8,3
P2,1,4,2
P3,2,2,1
P4,3,5,2
P5,5,3,4
```

- **Procesos:** identificador único y no vacío.
- **Tiempo llegada:** entero mayor o igual que cero.
- **Duración:** entero positivo; tiempo total de CPU requerido.
- **Prioridad:** entero positivo; 1 representa la prioridad más alta.

El quantum se configura por separado y debe ser un entero positivo. Las
columnas de inicio, fin y métricas se calculan como resultados, no se piden
como datos de entrada. Las rutas relativas de CSV se interpretan desde la
carpeta donde se ejecuta el comando; el ejemplo predeterminado se localiza
automáticamente dentro del proyecto.

## Reglas de planificación

- Una CPU, una ráfaga por proceso, sin bloqueos por E/S y sin costo de cambio
  de contexto. Los tiempos son unidades simuladas, no segundos reales.
- FCFS, SJF y Prioridad ejecutan cada proceso hasta terminar.
- SJF y Prioridad solo comparan los procesos que ya llegaron.
- En empates se usa llegada anterior y luego orden de entrada.
- En Round Robin, las llegadas durante un turno, incluso en su instante final,
  se agregan antes de reencolar al proceso que agotó el quantum.
- Los intervalos de CPU libre se muestran explícitamente.

## Verificación

```bash
python3 -m unittest discover -s tests -v
```

En el PowerShell de este equipo:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
```

Las pruebas cubren resultados calculados a mano, empates, CPU libre, llegadas
al límite del quantum, entradas inválidas, conservación del tiempo de CPU,
uso del menú y terminación de hilos. Los escenarios concurrentes se ejecutan
en subprocesos con un límite de 15 segundos para detectar bloqueos.

## Guía para leer y documentar el código

1. [Arquitectura y ficha técnica](docs/arquitectura.md): alcance y responsabilidades.
2. [Módulo 1](docs/modulo_1.md): procesos, hilos, algoritmos, fórmulas y resultados.
3. [Módulo 2](docs/modulo_2.md): búfer circular, semáforos, mutex y cierre.
4. [Validación](docs/validacion.md): casos comprobados y límites de las pruebas.

Cada planificador tiene su propio archivo en `python/planificacion/`. La
lectura de datos, el cálculo de métricas y la presentación están separados
de las decisiones de planificación.

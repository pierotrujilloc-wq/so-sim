# SO-Sim — SuperAlmacén — Módulos 1 y 2

Simulador educativo para el curso de Sistemas Operativos. Incluye procesos
en C, hilos en Python, cuatro algoritmos de planificación y el problema
productor-consumidor. La interfaz es por consola y los algoritmos están
escritos con listas, ciclos y condiciones para facilitar su explicación.

## Caso práctico: almacén de un supermercado

**SuperAlmacén** recibe mercadería, cuenta cajas y atiende órdenes de reposición.
El jefe representa al sistema operativo; un operario representa la CPU y cada
proceso es una orden de trabajo. Los hilos cuentan distintos sectores de una
misma orden. Recepción y ubicación comparten una zona limitada de cajas.
El contexto completo está en [Caso SuperAlmacén](docs/caso_superalmacen.md).

- **Opciones 1–3:** Gantt y tablas con eficiencia temporal por proceso
  (`Duración / Retorno × 100`), porcentaje de espera y reducción de espera y
  respuesta frente a FCFS. Se indican las mejores políticas y los empates.
- **Opción 4:** tabla por hilo y comparación de la misma orden contada de forma
  secuencial y con hilos, con tiempos reales y reducción porcentual.
- **Opción 5:** recepción y retirada de cajas de la zona compartida.
- **Opción 6:** instrucciones para ejecutar el jefe y operario en C;
  el ejecutable muestra una tabla de roles, PID y cumplimiento.

La eficiencia temporal depende de llegada y duración; compara atención frente
a espera. Las mediciones de hilos son puntuales y pueden variar. Un porcentaje
negativo de reducción indica que se tardó más que la referencia.

### Continuidad del proyecto

Los módulos 1 y 2 son ejecutables. El mismo caso se extenderá, cuando se
implemente cada etapa, a:

| Módulo futuro | Metáfora |
|---|---|
| 3. Gestión de memoria | Mesa de preparación de pedidos: reservar y liberar espacio temporal; casilleros y fichas para paginación. |
| 4. E/S y archivos | Equipos de lectura y traslado; registros guardados en bloques del archivo. |
| 5. Seguridad | Identificación, permisos por rol y cifrado de reportes. |
| 6. Sistemas distribuidos | Almacenes de distintas sucursales que intercambian mensajes. |

La mesa de preparación representa la RAM y la zona de recepción representa el
búfer de sincronización. Sus funciones se explican por separado en el caso.

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
`--elementos` es la cantidad de cajas que ingresa **cada operario de recepción**.

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
5. [Caso SuperAlmacén y porcentajes](docs/caso_superalmacen.md): contexto de los seis módulos y cómo interpretar las tablas.

Cada planificador tiene su propio archivo en `python/planificacion/`. La
lectura de datos, el cálculo de métricas y la presentación están separados
de las decisiones de planificación.

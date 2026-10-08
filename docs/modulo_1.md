# Módulo 1: procesos, hilos y planificación

Caso común: [SuperAlmacén](caso_superalmacen.md).
Un operario representa la CPU y cada proceso de entrada una orden de trabajo.
La leyenda del ejemplo identifica conteo, reposición, refrigerados, clasificación
y etiquetas sin agregar campos a las cuatro columnas de entrada.

## 1. Procesos en C

Archivo: `c/procesos.c`.

1. El padre imprime su PID y vacía el búfer de salida con `fflush`.
2. `fork` crea un hijo. Devuelve su PID al padre, cero al hijo o un valor
   negativo si falla.
3. El hijo llama a `execvp` para ejecutar el mismo programa con `--hijo`.
   Reutilizar el ejecutable permite ver el reemplazo sin depender de otro
   programa instalado. El PID del hijo se conserva y `main` comienza otra vez.
4. La rama `--hijo` cuenta cinco cajas con 1 a 5 unidades de producto:
   completa el conteo de 15 unidades y termina con código cero.
5. El padre llama a `waitpid` para esperar y recoger el estado de salida.
6. Presenta una tabla del jefe y operario con PID y cumplimiento.

`execvp` es una variante de la familia `exec`; `waitpid` permite esperar al
hijo concreto. Una llamada correcta a `execvp` no vuelve a la instrucción
siguiente. Si falla, se muestra el error y el hijo termina con código 127.
El padre también detecta una terminación por señal.

Los PID y el orden relativo de algunos mensajes pueden cambiar entre
ejecuciones. La suma esperada es 15 y el padre debe informar código de salida 0.

## 2. Hilos en Python

Archivo: `python/hilos.py`.

Cada `Thread` ejecuta una función que suma desde 1 hasta un límite. `start`
inicia la tarea; `join` espera que termine. El acumulador es local a cada hilo.
Un mutex protege la escritura de los resultados y el registro compartido.

El programa muestra el inicio y el final de cada hilo. No se presupone un
orden fijo de ejecución ni una mejora de velocidad: el ejemplo enseña el
ciclo de vida de los hilos y la coordinación del acceso compartido.

Cada suma representa el conteo de unidades de un sector de una misma orden.
Los sectores contienen cajas distintas con la misma carga. También
se realiza la misma carga de forma secuencial y se miden ambos tiempos con
`perf_counter_ns`. La salida incluye tablas por hilo y por modalidad, con
cumplimiento, participación y reducción porcentual de tiempo. El tiempo total
con hilos incluye su gestión; las mediciones puntuales pueden variar.

## 3. Modelo de planificación

Cada entrada contiene `Procesos`, `Tiempo llegada`, `Duración` y `Prioridad`.
El planificador construye intervalos de ejecución mediante un reloj virtual.
No llama a `sleep` y no mide cuánto tarda Python en ejecutar sus instrucciones.

Supuestos:

- Una CPU y una sola ráfaga por proceso.
- Llegadas y duraciones enteras; duración estrictamente positiva.
- Sin E/S, bloqueos ni costo de cambios de contexto.
- Prioridad 1 es la más alta.
- SJF y Prioridad son variantes sin desalojo.
- Empates por llegada y, si persisten, por orden de las filas de entrada.

Un `Tramo` describe `[inicio, fin)`: incluye el instante inicial y excluye el
final. Si su proceso es `None`, la CPU estuvo libre. Los datos originales no
se modifican al ejecutar un algoritmo.

## 4. FCFS

Archivo: `python/planificacion/fcfs.py`.

**Criterio:** ejecutar en orden de llegada.

1. Crear una lista ordenada por llegada. El ordenamiento estable conserva el
   orden de entrada cuando las llegadas son iguales.
2. Si el próximo proceso todavía no llegó, registrar CPU libre y avanzar el reloj.
3. Ejecutar toda su duración.
4. Repetir hasta terminar la lista.

Un proceso corto puede esperar mucho si llega detrás de uno largo. Para `n`
procesos, el ordenamiento cuesta O(n log n) y el recorrido posterior O(n).

## 5. SJF sin desalojo

Archivo: `python/planificacion/sjf.py`.

**Criterio:** elegir la menor duración entre quienes ya llegaron.

1. Recorrer los procesos pendientes y descartar de la elección a los futuros.
2. Conservar el índice del candidato con menor duración.
3. Si nadie está disponible, avanzar hasta la próxima llegada.
4. Retirar al elegido y ejecutar toda su ráfaga.
5. Volver a elegir entre los pendientes.

La comparación usa `<`, por lo que una duración igual conserva al candidato
anterior. Como la lista está ordenada por llegada, se cumplen los desempates.
SJF conoce las duraciones proporcionadas como entrada; en un sistema real
estas normalmente tendrían que estimarse. La selección por recorridos cuesta
O(n²) en total.

## 6. Prioridad sin desalojo

Archivo: `python/planificacion/prioridad.py`.

**Criterio:** elegir el número de prioridad más pequeño entre los disponibles.

El recorrido es parecido a SJF, pero compara `prioridad`. La elección solo
se realiza cuando la CPU queda libre. Si llega un proceso de mayor prioridad
durante una ráfaga, debe esperar a que esta termine.

La selección cuesta O(n²). No se implementa envejecimiento de prioridades.
En una carga abierta, la llegada continua de tareas prioritarias podría hacer
esperar indefinidamente a otras; nuestros casos tienen una lista finita.

## 7. Round Robin

Archivo: `python/planificacion/round_robin.py`.

**Criterio:** atender una cola FIFO en turnos de hasta `quantum` unidades.

Variables que conviene seguir durante la explicación:

- `pendientes`: procesos ordenados por llegada.
- `siguiente`: índice del próximo proceso que todavía no ingresó a la cola.
- `cola_listos`: procesos disponibles esperando un turno.
- `restantes`: duración que falta ejecutar a cada proceso.

Pasos:

1. Si la cola está vacía, avanzar hasta la próxima llegada.
2. Agregar a la cola los procesos que ya llegaron.
3. Sacar el primero y ejecutar `min(quantum, tiempo restante)`.
4. Descontar el tiempo ejecutado y avanzar el reloj.
5. Agregar las llegadas ocurridas durante el turno, incluida su frontera final.
6. Si el proceso actual no terminó, agregarlo al final.
7. Repetir mientras haya procesos listos o llegadas pendientes.

**Ejemplo de frontera:** A llega en 0 y dura 4; B llega en 2 y dura 1. Con
quantum 2, la secuencia es A `[0,2)`, B `[2,3)`, A `[3,5)`. B se incorpora
antes de volver a encolar a A.

La cola se representa con una lista para que sus operaciones sean visibles.
`pop(0)` desplaza los elementos restantes y cuesta O(n). Si `k` es el número
de turnos, esta implementación tiene un costo de O(n log n + k·n) en el peor
caso y guarda O(k) tramos. Es apropiada para casos pequeños de estudio.

## 8. Métricas

Archivo: `python/modelos.py`, función `construir_resultado`.

Para cada proceso se busca el primer inicio y la última finalización:

```text
Retorno   = Fin - Tiempo llegada
Espera    = Retorno - Duración
Respuesta = Primer inicio - Tiempo llegada
```

La fórmula de espera usa el supuesto de una sola ráfaga sin E/S. En los
algoritmos sin desalojo, espera y respuesta coinciden. En Round Robin, un
proceso puede esperar varias veces después de haber recibido su primera
atención, por lo que esas métricas pueden diferir.

El promedio es la suma de la métrica dividida entre la cantidad de procesos.
El cálculo didáctico recorre el historial por cada proceso: O(n·s), donde `s`
es la cantidad de tramos. Este costo se añade al de cada planificador.

`python/evaluacion.py` añade eficiencia temporal (`Duración / Retorno × 100`),
porcentaje de espera y reducción respecto a FCFS. La tabla cruzada compara
el mismo proceso entre políticas y conserva todos los empates. Las fórmulas,
el manejo de referencias cero y sus límites se explican en el caso práctico.

## 9. Comparación del caso de ejemplo

Datos: `data/processes/ejemplo.csv`. Quantum: 2.

| Algoritmo | Espera promedio | Respuesta promedio | Retorno promedio |
|---|---:|---:|---:|
| FCFS | 8.40 | 8.40 | 12.80 |
| SJF sin desalojo | 7.40 | 7.40 | 11.80 |
| Prioridad sin desalojo | 8.00 | 8.00 | 12.40 |
| Round Robin | 9.40 | 3.00 | 13.80 |

Para P1 en Round Robin, el primer inicio es 0 y termina en 21:

```text
Retorno   = 21 - 0 = 21
Espera    = 21 - 8 = 13
Respuesta =  0 - 0 =  0
```

En este caso SJF tiene la menor espera promedio. Round Robin permite una
primera atención más temprana en promedio, aunque aumenta la espera total.
Prioridad refleja la importancia indicada por el usuario; su objetivo no es
minimizar necesariamente la espera. Estas conclusiones corresponden a esta
entrada, no establecen un ganador para todas las cargas.

La consola incluye el historial por intervalos, una tabla por proceso y un
gráfico sencillo de barras de espera promedio. El Gantt es textual y sus
bloques no tienen ancho proporcional; sus extremos indican la duración exacta.

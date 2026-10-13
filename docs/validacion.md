# Validación de los módulos 1 y 2

## Resultado de la comprobación de SuperAlmacén

- Windows con Python 3.13: las 50 pruebas pasaron tras actualizar las tareas
  de la opción 4.

Comprobaciones previas a esta actualización de la opción 4:

- Ubuntu en WSL: las 38 pruebas de la versión anterior pasaron.
- C en Ubuntu WSL: compiló con `-Wall -Wextra -Werror` y terminó con código 0.
  Se observó un PID diferente para padre e hijo, conservación del PID del
  hijo al ejecutar `execvp`, suma final igual a 15 y tabla de cumplimiento.
- Opción 6 desde Python en Windows: compilación y ejecución reales en Ubuntu
  WSL, salida en la terminal y regreso al menú. También se verificó el comando
  `python3 python/main.py procesos` directamente en Linux.

## Suite automatizada

Ejecutar desde la raíz:

```bash
python3 -m unittest discover -s tests -v
```

La suite contiene 50 pruebas, algunas con varios escenarios internos.

| Área | Evidencia |
|---|---|
| FCFS, SJF, Prioridad y RR | Historial, espera, respuesta y fin contrastados con el caso resuelto a mano. |
| Llegadas | Entrada desordenada, tiempos iniciales sin procesos e intervalos libres posteriores. |
| Empates | Llegada y orden original, incluso con identificadores cuyo orden alfabético sería distinto. |
| Desalojo | SJF y Prioridad mantienen la ráfaga actual ante una nueva llegada. |
| Round Robin | Llegada justo al terminar un quantum y quantum grande equivalente a FCFS. |
| Conservación | 40 casos generados con semilla fija, ejecutados con los cuatro planificadores. |
| Entrada | Cabecera exacta, UTF-8 con BOM, columnas extra o faltantes, duplicados y números inválidos. |
| Hilos | Cuatro tareas distintas, resultados iguales entre modalidades, intervalos válidos y espera de terminación. |
| Tareas de almacén | Diferencias de cantidades, fechas límite de vencimiento, etiquetas y ubicaciones vacías. |
| Ampliación y errores | Registro de una tarea adicional, selección parcial, entrada inválida, fallos y diferencias en resultados. |
| Consultas simuladas | Una espera de dos segundos por consulta y modalidad; resultados iguales y selección de las tareas 5, 6 y 7. |
| Sincronización | Búfer de capacidad 1, productores y consumidores múltiples, cero elementos y consumidores sobrantes. |
| Consola | Comando predeterminado, error de archivo y carga manual mediante el menú. |
| Porcentajes | Eficiencia y espera complementarias, mejora y empeoramiento frente a FCFS, referencia cero y ausencia de FCFS. |
| Comparación por proceso | Porcentajes de P3 calculados a mano y conservación de empates entre algoritmos. |
| Tiempos de hilos | Reloj controlado en una prueba para distinguir tiempo de tarea y tiempo total con gestión; nunca se presupone un ganador real. |
| Contexto | Órdenes del ejemplo, revisión de entregas, zona de recepción y recorrido de las opciones 4, 5 y 6 de SuperAlmacén. |
| Puente Python/C | Comandos para Windows/Linux, rutas con espacios, retorno al menú, errores de compilación y ejecución, herramientas ausentes y timeout. |

Las pruebas de `test_procesos.py` sustituyen `subprocess.run` por respuestas
controladas para cubrir errores sin exigir WSL o GCC a quien ejecute la suite.
La integración real se comprobó por separado, como se indica arriba.

En los casos generados se verifica que cada proceso ejecuta exactamente su
duración, nunca comienza antes de llegar, no hay huecos ocultos entre tramos,
solo hay CPU libre cuando no existe trabajo disponible y los turnos RR no
exceden el quantum. También se comprueba que la entrada no cambia.

En concurrencia, cada escenario corre en un subproceso con timeout de 15
segundos. Una ejecución bloqueada hace fallar la prueba y se termina ese
subproceso. Se verifica que cada consumidor retire una señal de fin diferente
y que cada elemento esperado aparezca exactamente una vez.

## Comprobación del programa en C

Compilar con advertencias tratadas como errores:

```bash
mkdir -p build
gcc -std=c11 -Wall -Wextra -Werror c/procesos.c -o build/procesos
./build/procesos
```

Resultados esperados:

- Padre e hijo tienen PID diferentes.
- El PID del hijo es el mismo antes y después de `execvp`.
- La suma calculada es 15.
- El padre recoge el código de salida 0 mediante `waitpid`.
- La tabla identifica roles y PID y muestra 100% de cumplimiento de cada tarea.

## Límites

Las pruebas de planificación corresponden al modelo de una CPU, una ráfaga
por proceso y costo de cambio de contexto cero. El registro de concurrencia
muestra un orden de ejecución válido; otras ejecuciones pueden producir otro.
La detección de bloqueos por timeout aporta evidencia para los escenarios
probados y se complementa con la explicación del protocolo en el módulo 2.

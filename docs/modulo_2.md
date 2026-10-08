# Módulo 2: productor-consumidor

Archivo principal: `python/sincronizacion.py`.

## Problema

En [SuperAlmacén](caso_superalmacen.md), los productores son operarios de
recepción, los consumidores son operarios de ubicación y el búfer es una zona
limitada de recepción de cajas. La opción 5 utiliza estos nombres junto con
sus equivalentes técnicos para facilitar la exposición. La mesa de preparación
de pedidos se reserva como metáfora de la RAM para el futuro módulo 3.

Varios productores generan elementos y varios consumidores los retiran de un
búfer con capacidad limitada. Los productores deben esperar cuando se llena,
y los consumidores cuando está vacío. Solo un hilo puede modificar su estado
a la vez.

Cada caja tiene un identificador como `P1-item01`. Esto permite verificar
que se retira exactamente una vez. Estos identificadores corresponden a los
productores; no son los procesos del CSV del planificador.

## Entrada

| Parámetro | Restricción | Predeterminado |
|---|---|---:|
| Productores | Entero positivo | 2 |
| Consumidores | Entero positivo | 2 |
| Capacidad | Entero positivo | 5 |
| Elementos por productor | Entero mayor o igual que cero | 10 |

Estas opciones pertenecen a la demostración concurrente. Los procesos de la
planificación mantienen únicamente sus cuatro columnas.

## Búfer circular

`BufferLimitado` contiene:

- `datos`: lista de tamaño fijo.
- `entrada`: siguiente posición en la que se insertará.
- `salida`: siguiente posición de la que se retirará.
- `ocupacion`: cantidad de posiciones ocupadas.

Después de insertar o retirar, el índice avanza mediante:

```text
nueva_posicion = (posicion_actual + 1) % capacidad
```

Por ejemplo, con capacidad 3 las posiciones avanzan 0, 1, 2, 0, 1, 2. La
cantidad ocupada permite distinguir un búfer lleno de uno vacío aunque los
índices coincidan.

## Semáforos y mutex

| Recurso | Valor inicial | Responsabilidad |
|---|---:|---|
| `espacios_libres` | Capacidad | Reservar un lugar para insertar. |
| `elementos_disponibles` | 0 | Reservar un elemento para retirar. |
| `mutex` | Libre | Proteger datos, índices, ocupación y registro. |

`acquire` espera si un semáforo no tiene permisos; `release` devuelve uno.
`with mutex` adquiere el bloqueo y lo libera al salir de la sección crítica.
El mutex protege una modificación; los semáforos indican si esa modificación
puede realizarse según la cantidad de elementos y espacios.

## Algoritmo del productor

```text
Por cada elemento que le corresponde producir:
    Crear un identificador único.
    Esperar un espacio libre.
    Adquirir el mutex.
        Escribir en la posición de entrada.
        Avanzar la entrada circularmente.
        Incrementar la ocupación y registrar el evento.
    Liberar el mutex.
    Anunciar un elemento disponible.
```

## Algoritmo del consumidor

```text
Repetir:
    Esperar un elemento disponible.
    Adquirir el mutex.
        Leer y limpiar la posición de salida.
        Avanzar la salida circularmente.
        Decrementar la ocupación y registrar el evento.
    Liberar el mutex.
    Anunciar un espacio libre.
    Si el elemento es la señal de fin, terminar.
```

Se espera el semáforo **antes de tomar el mutex**. Si un productor esperara
espacio manteniendo el mutex, impediría que el consumidor entrase para liberar
ese espacio. El orden elegido evita ese ciclo de espera.

## Finalización

1. El hilo principal inicia consumidores y productores.
2. Espera con `join` a todos los productores, mientras los consumidores siguen
   retirando elementos.
3. Inserta una señal `None` por consumidor mediante la misma operación protegida.
4. Cada consumidor termina al retirar una señal.
5. El principal espera a todos los consumidores.

En la salida, `None` se muestra como `<FIN>`. Estas señales también ocupan
espacio y pasan por los semáforos. No cuentan como elementos producidos para
el reporte. Al introducirlas después de que todos los productores terminaron,
ninguna se adelanta a trabajo pendiente en la cola FIFO.

Este cierre funciona incluso con cero elementos y con más consumidores que
elementos. Cada consumidor retira una única señal antes de salir.

## Registro y verificaciones

Los eventos se capturan dentro de la sección crítica y se imprimen al terminar.
Así se conserva el orden de modificación del búfer y se evita mezclar salidas
de distintos hilos. Se muestra quién insertó o retiró, el elemento y la
ocupación resultante.

Al terminar se comprueba:

- Producción total = productores × elementos por productor.
- Identificadores producidos únicos.
- Misma secuencia de elementos insertados y retirados, por tratarse de FIFO.
- Ocupación entre cero y la capacidad en cada evento.
- Búfer vacío al finalizar.

El orden entre hilos puede variar y no se garantiza un reparto equitativo
del trabajo entre consumidores. La ejecución normal termina porque el trabajo
es finito y cada consumidor recibe una señal de cierre, suponiendo que el SO
siga dando tiempo a los hilos y que no haya un fallo externo.

Las pruebas comprueban estos hechos en varios escenarios y detectan bloqueos
con un límite de tiempo. No constituyen por sí solas una demostración de todos
los posibles órdenes de ejecución; el razonamiento sobre el orden de los
bloqueos y las señales complementa la evidencia experimental.

## Casos para mostrar en clase

```bash
# Un único espacio: obliga a alternar inserciones y retiradas.
python3 python/main.py sincronizar --capacidad 1 --productores 2 --consumidores 3 --elementos 4

# Más consumidores que elementos: todos deben poder terminar.
python3 python/main.py sincronizar --capacidad 2 --productores 1 --consumidores 5 --elementos 1

# Sin elementos: únicamente se intercambian las señales de fin.
python3 python/main.py sincronizar --capacidad 2 --productores 2 --consumidores 3 --elementos 0
```

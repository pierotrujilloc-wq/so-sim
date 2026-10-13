# SuperAlmacén: el almacén de un supermercado como sistema operativo

## Historia

Durante la jornada llegan proveedores con mercadería y órdenes para contar
cajas, verificar productos refrigerados y reponer góndolas. El jefe del almacén
organiza el trabajo, asigna recursos y controla el acceso a las zonas compartidas.
Cada orden llega en un momento distinto, requiere tiempo y tiene una urgencia.

La historia sigue la forma de explicar con un caso común de las clases. Los
módulos 1 y 2 están implementados. Los módulos 3 a 6 tienen una correspondencia
prevista en este documento y se implementarán cuando se autorice esa etapa.

## Correspondencia con sistemas operativos

| Concepto | Caso práctico |
|---|---|
| Sistema operativo | Jefe del almacén que coordina recursos y órdenes. |
| Proceso simulado | Orden de trabajo P1, P2, etc. |
| CPU | Un operario que ejecuta una orden a la vez. |
| Llegada | Momento en que ingresa la orden. |
| Duración | Unidades de trabajo que necesita el operario para completarla. |
| Prioridad | Urgencia; 1 es la más alta. |
| Cola de listos | Trabajos que ya llegaron y esperan turno. |
| Quantum | Máximo tiempo de atención por turno en Round Robin. |
| Proceso padre en C | Jefe que crea y supervisa un operario. |
| Proceso hijo en C | Operario que cuenta productos de una entrega. |
| Hilo | Colaborador que realiza una tarea de revisión sobre una entrega compartida. |
| Productor | Operario de recepción que ingresa cajas. |
| Consumidor | Operario de ubicación que retira cajas para llevarlas a estantes. |
| Búfer | Zona de recepción con una cantidad limitada de posiciones. |
| Semáforos | Permisos para colocar cajas y retirar las disponibles. |
| Mutex | Acceso exclusivo al modificar posiciones y registro de recepción. |
| RAM (etapa futura) | Mesa de preparación de pedidos. |
| Disco (etapa futura) | Almacenamiento permanente y archivo de registros. |
| Nodo distribuido (etapa futura) | Almacén de una sucursal. |

El operario es una analogía de la CPU. Los tiempos son unidades simuladas de
trabajo, sin costo de desplazamiento ni cambio de tarea. Round Robin supone
que se puede guardar el avance y continuar, como al contar cajas por turnos.
Cada demostración estudia un mecanismo: las opciones no forman todavía un
sistema integrado de inventario ni transfieren órdenes entre módulos.

## Ejemplo de planificación

Se mantienen las cuatro columnas solicitadas. Las descripciones pertenecen
a esta explicación y no son campos adicionales del CSV.

| Trabajo | Interpretación del ejemplo | Llegada | Duración | Prioridad |
|---|---|---:|---:|---:|
| P1 | Contar cajas de una entrega | 0 | 8 | 3 |
| P2 | Preparar productos para reponer una góndola | 1 | 4 | 2 |
| P3 | Verificar un lote refrigerado urgente | 2 | 2 | 1 |
| P4 | Clasificar productos recibidos | 3 | 5 | 2 |
| P5 | Actualizar etiquetas de ubicación | 5 | 3 | 4 |

Los tiempos son supuestos educativos. Una entrada manual u otro CSV puede
representar trabajos diferentes. No se asignan estas descripciones a cualquier
proceso llamado P1 en otros archivos.

- **FCFS:** atender las órdenes según su llegada.
- **SJF:** elegir el trabajo más corto entre los que ya llegaron.
- **Prioridad:** elegir el más urgente entre los disponibles.
- **Round Robin:** repartir turnos de trabajo de hasta un quantum.

SJF y Prioridad se mantienen sin desalojo. Se aplican los desempates descritos
en el README. Las opciones 1, 2 y 3 permiten estudiar estas políticas.

## Qué significa la eficiencia porcentual

Para cada proceso:

```text
Retorno = Finalización - Llegada
Espera = Retorno - Duración
Respuesta = Primer inicio - Llegada
Eficiencia temporal (%) = Duración / Retorno × 100
Tiempo en espera (%) = Espera / Retorno × 100
```

Las dos últimas cantidades suman 100% en nuestro modelo sin E/S. Un trabajo
con 100% de eficiencia temporal no esperó. Un trabajo con 40% pasó el 40% de
su permanencia ejecutándose y el 60% esperando.

Este indicador es la definición elegida para el informe del simulador: mide
la atención temporal recibida. No es la utilización global de la CPU ni mide
la calidad del código de un proceso. Depende de su llegada y duración: un
trabajo largo puede obtener un porcentaje mayor que uno corto. La tabla
cruzada permite comparar **el mismo proceso** bajo diferentes algoritmos,
mostrando todos los empates.

Para comparar algoritmos se usa FCFS como referencia:

```text
Reducción de espera (%) = (Espera FCFS - Espera actual) / Espera FCFS × 100
```

Se aplica la misma fórmula a la respuesta promedio. Un porcentaje positivo
indica reducción; uno negativo indica aumento. Si falta FCFS, se muestra N/D.
Si ambos valores son cero, se informa 0% (empate). Si solo la referencia es
cero, se muestra N/D porque la división no está definida.

### Resultados reproducibles con el CSV predeterminado y quantum 2

| Algoritmo | Espera promedio | Reducción de espera vs FCFS | Respuesta promedio | Reducción de respuesta vs FCFS |
|---|---:|---:|---:|---:|
| FCFS | 8.40 | 0.00% | 8.40 | 0.00% |
| SJF | 7.40 | 11.90% | 7.40 | 11.90% |
| Prioridad | 8.00 | 4.76% | 8.00 | 4.76% |
| Round Robin | 9.40 | -11.90% | 3.00 | 64.29% |

P3 requiere 2 unidades. Con FCFS su retorno es 12, por lo que su eficiencia
temporal es 16.67%; con Round Robin su retorno es 4 y obtiene 50%. Para P3,
Round Robin ofrece la mejor eficiencia entre las cuatro políticas del ejemplo.
Para P1, las tres variantes sin desalojo empatan con 100%.

## Revisión de una entrega con tareas e hilos: opción 4

La comparación usa tareas diferentes dentro de un mismo trabajo: revisar una
entrega del supermercado. Así se traslada la idea de cortar, freír y preparar
salsa de la clase a funciones propias del almacén.

| Tarea | Función en `tareas_almacen.py` | Resultado del ejemplo |
|---|---|---|
| Verificar cantidades | `verificar_cantidades` compara lo recibido con lo esperado. | Cantidades verificadas: 4. |
| Revisar vencimientos | `revisar_vencimientos` compara fechas con la fecha de revisión. | Vencimientos revisados: 3. |
| Preparar etiquetas | `preparar_etiquetas` genera texto con nombre y ubicación asignada. | Etiquetas preparadas: 3. |
| Detectar productos sin ubicación | `detectar_productos_sin_ubicacion` busca ubicaciones vacías. | Productos detectados sin ubicación: 1. |
| Consultar existencias en sucursal (5) | `consultar_existencias_sucursal` simula esperar una respuesta externa. | Consulta a sucursal completada (simulada). |
| Consultar información al proveedor (6) | `consultar_informacion_proveedor` simula esperar información. | Consulta al proveedor completada (simulada). |
| Esperar confirmación de transporte (7) | `esperar_confirmacion_transporte` simula esperar una confirmación. | Confirmación de transporte recibida (simulada). |

La entrega contiene arroz, leche, aceite y detergente. Está definida en
`ENTREGA_EJEMPLO`, junto con una fecha fija de revisión: **2026-10-10**. Una fecha
de vencimiento anterior se considera vencida; la misma fecha aún no. `None`
indica que no aplica. Mantener la fecha fija permite reproducir los resultados.
Las ubicaciones vienen asignadas en la entrada; generar una etiqueta no aprueba
un producto ni autoriza su venta. Ninguna tarea necesita el resultado de otra.

En la opción 4 se eligen números separados por comas (`1,3`), o Enter/`0` para
todas. La cantidad de hilos corresponde a las tareas seleccionadas: siete por
defecto. Estos datos de mercadería pertenecen al ejemplo de hilos; el CSV de
planificación conserva sus cuatro columnas originales.

- **Secuencial:** un colaborador (hilo principal) termina una tarea y pasa a la
  siguiente. Un ciclo llama a cada función directamente.
- **Con hilos:** cada colaborador (`Thread`) ejecuta una función distinta sobre
  la misma entrega de solo lectura. Se inician todos con `start()` y después se
  espera a todos con `join()`. Un mutex protege el registro compartido.

La salida presenta los datos de entrada, una tabla secuencial, los eventos de
los hilos, una tabla con hilos y la comparación total. Cada fila muestra tarea,
responsable, resultado resumido, inicio, fin y duración. Se muestran cantidades
verificadas, fechas revisadas, etiquetas preparadas y productos sin ubicación.
Los detalles se conservan internamente para comprobar que ambas modalidades
producen los mismos resultados, sin imprimir fechas de vencimiento detectadas
ni el contenido de las etiquetas. Solo se cuentan como revisados los productos
que tienen fecha de vencimiento.

El reloj `perf_counter_ns` mide el tiempo real. Inicio y fin se expresan desde el
comienzo de **cada modalidad**: ambas tienen su propio origen. En secuencial,
una tarea empieza después de acabar la anterior. Con hilos puede haber intervalos
solapados, aunque estas funciones cortas pueden terminar antes de iniciar otra.
Las tareas 1–4 ejecutan las revisiones sin pausas añadidas. Las tareas 5–7 usan
`sleep(2)` para representar una espera por respuesta de un servicio externo.
Se espera una vez por consulta, independientemente de la cantidad de productos;
las respuestas son fijas y simuladas. No se contacta a ninguna sucursal o servicio.

Al seleccionar `5,6,7`, la modalidad secuencial espera aproximadamente seis
segundos y la modalidad con hilos unos dos segundos, más su gestión. El reloj
mide el tiempo realmente transcurrido, incluidas las esperas simuladas. La
comparación completa tarda unos ocho segundos. Esto permite observar el
solapamiento de esperas sin cambiar el trabajo de las cuatro revisiones originales.

```text
Cumplimiento (%) = Tareas ejecutadas sin error / Tareas seleccionadas × 100
Reducción de tiempo (%) = (Tiempo secuencial - Tiempo con hilos) / Tiempo secuencial × 100
```

El cumplimiento describe ejecución correcta de funciones. Detectar mercadería
vencida es un resultado válido, por lo que puede haber 100% de cumplimiento
aunque se detecten problemas en la entrega. Si falla una función o difieren
los resultados, se informa que la comparación no es válida y no se elige ganador.

El tiempo total con hilos incluye creación, registro, coordinación y `join`.
No se suman las duraciones individuales para deducir el total, porque pueden
solaparse. Las tareas son diferentes: sus duraciones no permiten clasificar
qué hilo es más eficiente. Se compara la selección completa entre modalidades.
Un porcentaje negativo significa que los hilos tardaron más en esa ejecución.
Son mediciones puntuales, afectadas por la carga del equipo y la gestión de hilos.

### Cómo añadir una tarea

En `python/tareas_almacen.py`:

1. Escribe una función antes de la lista `TAREAS`. Debe recibir `Entrega`, leer
   sus datos y devolver `ResultadoTarea(resumen, detalles)`.
2. Añade el nombre y la función a `TAREAS`.

Por ejemplo, para generar un reporte de los nombres recibidos:

```python
def listar_productos(entrega: Entrega) -> ResultadoTarea:
    nombres = []
    for producto in entrega.productos:
        nombres.append(producto.nombre)
    return ResultadoTarea(f"Productos: {len(nombres)}", tuple(nombres))

# Añadir esta entrada dentro de TAREAS:
# ("Listar productos", listar_productos),
```

El menú, los hilos y las tablas incorporan la nueva entrada automáticamente.
Para cambiar la mercadería, edita `ENTREGA_EJEMPLO`. Si una futura tarea necesita
un dato adicional, añade ese campo a `ProductoEntrega` y a los productos del
ejemplo. Mantén tareas independientes y datos de solo lectura para esta comparación.

## Procesos reales en C: opción 6

Al seleccionar 6, Python usa `subprocess` para compilar y ejecutar el ejemplo
automáticamente. En Windows utiliza Ubuntu WSL; en Linux, GCC directamente.
Los resultados aparecen en la misma terminal y al terminar se regresa al menú.
Si la compilación falla se informa el error y no se ejecuta una versión anterior.

El jefe crea al operario con `fork`. El operario reemplaza su
programa con `execvp` y cuenta cinco cajas con 1 a 5 unidades (15 unidades).
El padre recoge su estado mediante `waitpid`.

Al terminar normalmente, el programa muestra una tabla de responsabilidades,
PID y cumplimiento: el padre recoge un estado y el hijo cuenta una entrega.
Las tareas son diferentes, por lo que ese porcentaje no establece cuál proceso
es más rápido. Los rankings temporales corresponden a la planificación, y la
comparación secuencial/concurrente de carga idéntica corresponde a los hilos.

## Zona de recepción compartida: opción 5

Varios operarios de recepción (productores) colocan cajas en posiciones de una
zona limitada, representada con un búfer circular. Los operarios de ubicación
(consumidores) las retiran. Cada caja conserva un código único como `P1-item01`,
que identifica al productor y su elemento. Retirar una caja representa
entregarla al operario de ubicación; no se simula su recorrido por el almacén.

Recepción espera si no hay espacio; ubicación espera si no hay cajas.
Ambos toman el mutex solo durante la modificación de las posiciones y el registro.
El historial permite comprobar que no se pierden ni duplican cajas.
Las señales de fin anuncian el cierre de recepción y permiten terminar a todos.

Esta parte estudia acceso al recurso compartido. Sus operarios no son las
CPU de una simulación de planificación con múltiples procesadores.

## Continuidad para los seis módulos

| Módulo | Aplicación en SuperAlmacén | Estado |
|---|---|---|
| 1. Procesos, hilos y planificación | Órdenes de trabajo, jefe y operario, revisión de entregas y reparto de turnos. | Implementado |
| 2. Sincronización | Recepción y retirada de cajas con semáforos y mutex. | Implementado |
| 3. Memoria | Mesa de preparación, casilleros, fichas y reemplazo de páginas. | Propuesto |
| 4. E/S y archivos | Equipos de lectura y traslado, almacenamiento de registros por bloques. | Propuesto |
| 5. Seguridad y virtualización | Identificación, permisos, reportes cifrados y almacenes virtuales. | Propuesto |
| 6. Sistemas distribuidos | Consulta y transferencia de existencias entre sucursales. | Propuesto |

### Módulo 3: mesa de preparación de pedidos

Es una mesa o área de clasificación donde el operario reúne temporalmente los
productos de un pedido. Por ejemplo, trae arroz, aceite y azúcar de sus estantes,
los cuenta, arma una reposición y libera la mesa cuando sale el pedido.

La mesa representa la RAM; los productos colocados representan datos de trabajo.
No es el búfer de recepción del módulo 2. Ese búfer enseña coordinación entre
hilos, mientras que esta mesa servirá para estudiar asignación de memoria.

- **Asignación contigua:** reservar posiciones consecutivas para un pedido.
- **Fragmentación externa:** tener espacio libre repartido en huecos que no
  permiten una reserva contigua suficientemente grande.
- **Paginación:** dividir el espacio en casilleros iguales y repartir partes
  de un pedido entre ellos; una tabla indica dónde se encuentra cada parte.
- **Reemplazo de páginas:** usar una mesa con pocas posiciones para fichas de
  productos. Un fallo ocurre cuando se necesita una ficha que está en el archivo.
  FIFO retira la más antigua en la mesa; LRU, la menos recientemente consultada;
  Óptimo, la que tardará más en volver a necesitarse según una secuencia conocida.

Los casilleros y fichas son representaciones didácticas de direcciones y páginas.
Se mantendrá la diferencia entre RAM temporal y almacenamiento persistente.

### Módulo 4: entrada/salida y registros

El jefe puede consultar periódicamente si terminó una descarga (**sondeo**) o
recibir un aviso del encargado (**interrupción**). Un equipo de traslado que
mueve un lote tras recibir instrucciones iniciales representa una transferencia
**DMA**, durante la cual el jefe puede atender otras tareas.

Los registros de entregas e inventario se organizarán en compartimentos que
representen bloques: consecutivos en asignación contigua, con referencia al
siguiente en enlazada, o enumerados en una ficha central en indexada. También
se simularán operaciones de lectura, escritura y permisos básicos.

### Módulo 5: seguridad y virtualización

La identificación de un trabajador representa autenticación. Recepción,
ubicación, supervisión y administración tendrán permisos distintos; por ejemplo,
solo supervisión podrá aprobar ajustes de inventario. Se demostrará el cifrado
de un reporte. Almacenes virtuales que comparten infraestructura física servirán
para introducir la comparación conceptual entre máquinas virtuales y contenedores.

### Módulo 6: comunicación entre sucursales

Cada sucursal será un nodo. Una podrá consultar existencias a otra y recibir una
respuesta, enviar una solicitud de transferencia y obtener confirmación o rechazo.
Los mensajes permitirán demostrar la comunicación entre procesos/nodos.

## Relación con el material de clase

- Semanas 1 y 2: administrar recursos y organizar componentes.
- Semana 3: distinguir procesos e hilos; `fork`, `exec`, `start` y `join`.
- Semana 4: comparar políticas de planificación con la misma entrada.
- Semana 5: sección crítica, semáforos, mutex y productor-consumidor.

Los PDF son la referencia temática; los porcentajes adicionales y el caso del
supermercado son decisiones de esta implementación. Se distingue
primera respuesta de retorno y se calcula la espera acumulada también cuando
Round Robin interrumpe un trabajo varias veces.

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
| Hilo | Colaborador que cuenta un sector dentro de una orden compartida. |
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

## Conteo de una orden por sectores con hilos: opción 4

Una orden de conteo se divide en sectores, uno por hilo. Cada sector tiene
N cajas con 1, 2, ..., N unidades de producto. Por ejemplo, con N = 5 se cuentan
15 unidades por sector. Son cajas diferentes de una misma entrega: no se
cuenta varias veces la misma mercadería. El patrón de cantidades es idéntico
en todos los sectores para comparar la misma carga.

La función `contar_unidades` se ejecuta primero de forma secuencial para todos
los sectores y después mediante un hilo por sector. Se verifican ambos
resultados contra N × (N + 1) / 2. El reloj `perf_counter_ns` mide el tiempo real
transcurrido; estas mediciones no se mezclan con el reloj virtual del planificador.

La salida contiene:

1. Eventos de inicio y fin.
2. Tabla por hilo: unidades contadas, cumplimiento, participación en la orden
   y tiempo transcurrido en su tarea.
3. Tabla de la orden completa: tiempo secuencial, tiempo con hilos y reducción
   porcentual respecto al secuencial.

```text
Cumplimiento (%) = Unidades contadas / Unidades esperadas × 100
Parte de la orden (%) = Unidades del hilo / Unidades de todos los hilos × 100
Reducción de tiempo (%) = (Tiempo secuencial - Tiempo con hilos) / Tiempo secuencial × 100
```

Cumplimiento y participación describen trabajo realizado; no son porcentajes
de aceleración. El tiempo total con hilos incluye creación, registro de eventos,
coordinación y `join`. Los tiempos individuales pueden solaparse y no deben
sumarse para deducir el tiempo de la orden.

Es una medición puntual, secuencial primero y con hilos después, sin controlar
la carga externa del equipo. En tareas pequeñas predominan los costos de
gestión y la variabilidad del reloj. Se informa la modalidad más rápida en esa
ejecución; no se establece un ganador permanente. El trabajo es un cálculo,
por lo que más hilos no garantizan mayor velocidad.

## Procesos reales en C: opción 6

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
| 1. Procesos, hilos y planificación | Órdenes de trabajo, jefe y operario, conteo por sectores y reparto de turnos. | Implementado |
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

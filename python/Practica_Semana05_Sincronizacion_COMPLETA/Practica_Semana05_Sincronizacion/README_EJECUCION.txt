PRÁCTICA DIRIGIDA · SEMANA 05 · SINCRONIZACIÓN DE PROCESOS
============================================================

CONTENIDO
---------
productor_consumidor.py
    Solución sincronizada con:
    - mutex = Semaphore(1)
    - vacíos = Semaphore(5)
    - llenos = Semaphore(0)
    - 2 productores y 2 consumidores
    - verificación de pérdidas y duplicados

filosofos_comensales.py
    Solución con 5 cocineros y 5 Lock.
    El quinto cocinero invierte el orden de adquisición para romper
    la espera circular.

pruebas_20_corridas.py
    Ejecuta automáticamente 20 corridas de cada módulo y genera
    la evidencia dentro de logs/.

demos/
    productor_consumidor_sin_sincronizacion.py
        Muestra una condición de carrera controlada.
    filosofos_deadlock_demo.py
        Muestra el patrón de deadlock sin congelar indefinidamente
        la terminal (usa timeout solo para la demostración).

logs/
    productor_consumidor_20_corridas.txt
    filosofos_20_corridas.txt
    resumen_pruebas.csv
    resumen_pruebas.txt

Informe_Practica_Semana05.docx
    Informe breve (máximo 3 páginas) listo para completar con
    nombres de integrantes.


REQUISITOS
----------
- Python 3.10 o superior recomendado.
- No necesitas instalar librerías externas.


CÓMO EJECUTAR EN WINDOWS
------------------------

1. Abre CMD o PowerShell.

2. Entra a la carpeta. Ejemplo:

   cd "C:\Users\USUARIO\Desktop\Practica_Semana05_Sincronizacion"

3. Comprueba Python:

   python --version

   Si Windows usa el lanzador "py", también puedes usar:

   py --version

4. Ejecuta Productor-Consumidor:

   python productor_consumidor.py

5. Ejecuta Filósofos Comensales:

   python filosofos_comensales.py

6. Genera nuevamente las 20 corridas y los logs:

   python pruebas_20_corridas.py

7. Demostraciones opcionales SIN sincronización:

   python demos\productor_consumidor_sin_sincronizacion.py

   python demos\filosofos_deadlock_demo.py


QUÉ DEBES OBSERVAR
------------------

PRODUCTOR-CONSUMIDOR
- Producidos = consumidos.
- Perdidos = 0.
- Duplicados = 0.
- Buffer final = 0.
- Ocupación máxima nunca supera 5.

FILÓSOFOS COMENSALES
- Los cinco cocineros terminan.
- Cada uno completa todas las rondas.
- Deadlock = NO.
- Inanición observada = NO.

IMPORTANTE PARA LA SUSTENTACIÓN
-------------------------------

1. mutex protege la sección crítica (la lista "almacen").
2. vacíos cuenta espacios libres.
3. llenos cuenta elementos disponibles.
4. En filósofos, invertir el orden del último cocinero rompe
   la espera circular.
5. Las 20 corridas son evidencia empírica de que las soluciones
   se comportan correctamente bajo las pruebas realizadas.

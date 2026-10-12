"""
DEMOSTRACIÓN SIN SINCRONIZACIÓN
Condición de carrera de tipo "check-then-act".

Hay 1 unidad de stock, pero dos hilos:
1) leen stock=1,
2) ambos deciden retirar,
3) ambos escriben stock=0.

El valor final puede parecer correcto (0), pero se registran DOS retiros
sobre UNA sola unidad. Esa es la inconsistencia lógica.
"""

import threading

stock = 1
retiros = []
barrier = threading.Barrier(2)


def cocinero(nombre: str) -> None:
    global stock

    # Lectura NO protegida.
    observado = stock
    print(f"{nombre}: lee stock={observado}")

    # Fuerza a que ambos hayan leído antes de continuar.
    barrier.wait()

    if observado > 0:
        print(f"{nombre}: decide retirar")
        # Escritura NO protegida basada en una lectura vieja.
        stock = observado - 1
        retiros.append(nombre)
        print(f"{nombre}: escribe stock={stock}")


threads = [
    threading.Thread(target=cocinero, args=("Cocinero-A",)),
    threading.Thread(target=cocinero, args=("Cocinero-B",)),
]

for t in threads:
    t.start()
for t in threads:
    t.join()

print("\n===== RESULTADO =====")
print(f"Stock inicial : 1")
print(f"Stock final   : {stock}")
print(f"Retiros       : {len(retiros)} -> {retiros}")
print("INCONSISTENCIA:", "SI" if len(retiros) > 1 else "NO")

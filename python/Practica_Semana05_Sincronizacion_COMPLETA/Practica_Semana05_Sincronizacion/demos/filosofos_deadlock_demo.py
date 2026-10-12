"""
DEMOSTRACIÓN DEL PATRÓN DE DEADLOCK

Los cinco cocineros adquieren primero el utensilio izquierdo.
Una barrera garantiza que todos tengan ese utensilio antes de intentar
el derecho.

Para que la demostración no congele tu terminal, la segunda adquisición
usa timeout. Si todos expiran, se ha detectado exactamente el patrón
que con acquire() bloqueante quedaría esperando indefinidamente.
"""

import threading

N = 5
utensilios = [threading.Lock() for _ in range(N)]
barrier = threading.Barrier(N)
timeouts = []
guard = threading.Lock()


def cocinero(i: int) -> None:
    izq = i
    der = (i + 1) % N
    nombre = f"Cocinero-{i + 1}"

    utensilios[izq].acquire()
    print(f"{nombre}: tomó U{izq + 1}")

    # Todos llegan aquí sujetando su utensilio izquierdo.
    barrier.wait()

    print(f"{nombre}: intenta U{der + 1}")
    obtuvo_derecho = utensilios[der].acquire(timeout=1.0)

    if not obtuvo_derecho:
        with guard:
            timeouts.append(nombre)
        print(f"{nombre}: BLOQUEADO esperando U{der + 1} (timeout de demostración)")
    else:
        utensilios[der].release()

    utensilios[izq].release()


threads = [threading.Thread(target=cocinero, args=(i,)) for i in range(N)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print("\n===== RESULTADO =====")
print(f"Cocineros que no pudieron obtener el segundo utensilio: {len(timeouts)}/{N}")
if len(timeouts) == N:
    print("PATRÓN DE DEADLOCK DETECTADO: todos retienen uno y esperan otro en círculo.")
else:
    print("No se reprodujo el patrón completo en esta corrida.")

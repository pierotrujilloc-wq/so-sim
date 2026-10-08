/*
 * SuperAlmacén: jefe del almacén (padre) y operario (hijo).
 * Módulo 1: creación, sustitución y terminación de un proceso en Linux/WSL.
 * fork crea un hijo; exec reemplaza su programa; waitpid recoge su estado.
 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <errno.h>

int main(int argc, char *argv[]) {
    /* Esta rama se ejecuta después de exec: el PID del hijo se conserva,
     * pero comienza una nueva ejecución del programa desde main. */
    if (argc == 2 && strcmp(argv[1], "--hijo") == 0) {
        printf("Hijo después de exec: PID=%ld, padre=%ld\n",
               (long)getpid(), (long)getppid());
        int suma = 0;
        for (int numero = 1; numero <= 5; numero++) {
            suma += numero;
        }
        printf("Hijo: suma de 1 a 5 = %d. Finaliza correctamente.\n", suma);
        printf("Operario: entrega de 5 cajas con 1 a 5 unidades, %d unidades en total.\n", suma);
        return EXIT_SUCCESS;
    }

    puts("SuperAlmacen: contar productos de una entrega del supermercado.");
    printf("Padre: PID=%ld. Creará un proceso hijo.\n", (long)getpid());
    /* Evita duplicar texto pendiente en el búfer de salida al hacer fork. */
    fflush(stdout);
    pid_t hijo = fork();

    if (hijo < 0) {
        perror("No se pudo crear el hijo con fork");
        return EXIT_FAILURE;
    }

    if (hijo == 0) {
        printf("Hijo antes de exec: PID=%ld\n", (long)getpid());
        fflush(stdout);
        char *argumentos[] = {argv[0], "--hijo", NULL};
        execvp(argumentos[0], argumentos);

        /* exec solo retorna si falla. _exit evita volver a vaciar los
         * búferes heredados del padre en esta ruta de error. */
        perror("No se pudo ejecutar el programa del hijo");
        _exit(127);
    }

    printf("Padre: espera al hijo PID=%ld mediante waitpid.\n", (long)hijo);
    fflush(stdout);
    int estado;
    pid_t terminado;
    do {
        terminado = waitpid(hijo, &estado, 0);
    } while (terminado == -1 && errno == EINTR);

    if (terminado == -1) {
        perror("Falló waitpid");
        return EXIT_FAILURE;
    }
    if (WIFEXITED(estado)) {
        int codigo = WEXITSTATUS(estado);
        printf("Padre: hijo terminado con código %d.\n", codigo);
        puts("\nComparacion de responsabilidades y cumplimiento:");
        printf("%-12s | %-8s | %-24s | %s\n", "Proceso", "PID", "Responsabilidad", "Cumplimiento");
        printf("%-12s | %-8ld | %-24s | 100.00%% (1/1)\n",
               "Padre", (long)getpid(), "Recoger estado del hijo");
        printf("%-12s | %-8ld | %-24s | %.2f%% (%d/1)\n",
               "Hijo", (long)hijo, "Contar una entrega",
               codigo == 0 ? 100.0 : 0.0, codigo == 0 ? 1 : 0);
        puts("Cumplimiento = tareas completadas / asignadas x 100.");
        puts("Padre e hijo tienen tareas distintas; esta tabla mide cumplimiento.");
        return codigo;
    }
    if (WIFSIGNALED(estado)) {
        fprintf(stderr, "El hijo terminó por la señal %d.\n", WTERMSIG(estado));
    }
    return EXIT_FAILURE;
}

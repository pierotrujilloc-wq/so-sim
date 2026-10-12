"""
Ejecutor automático de 20 corridas por módulo.

Genera:
- logs/productor_consumidor_20_corridas.txt
- logs/filosofos_20_corridas.txt
- logs/resumen_pruebas.csv
- logs/resumen_pruebas.txt

Ejecutar:
    python pruebas_20_corridas.py
"""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import csv
import sys

from productor_consumidor import run_simulation as run_pc
from filosofos_comensales import run_simulation as run_ph


BASE = Path(__file__).resolve().parent
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(exist_ok=True)

PC_LOG = LOG_DIR / "productor_consumidor_20_corridas.txt"
PH_LOG = LOG_DIR / "filosofos_20_corridas.txt"
CSV_LOG = LOG_DIR / "resumen_pruebas.csv"
TXT_SUMMARY = LOG_DIR / "resumen_pruebas.txt"


def append_text(path: Path, text: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(text)


def main() -> int:
    PC_LOG.write_text("", encoding="utf-8")
    PH_LOG.write_text("", encoding="utf-8")

    rows: list[dict[str, object]] = []

    print("Ejecutando 20 corridas de Productor-Consumidor...")
    pc_ok = 0

    for run_no in range(1, 21):
        temp_log = LOG_DIR / "_pc_temporal.txt"
        result = run_pc(seed=100 + run_no, log_file=temp_log, echo=False)
        detail = temp_log.read_text(encoding="utf-8")
        temp_log.unlink(missing_ok=True)

        header = (
            "\n" + "=" * 78 + "\n"
            f"PRODUCTOR-CONSUMIDOR | CORRIDA {run_no:02d}\n"
            + "=" * 78 + "\n"
        )
        append_text(PC_LOG, header + detail)

        pc_ok += int(result.ok)
        rows.append({
            "modulo": "productor_consumidor",
            "corrida": run_no,
            "ok": result.ok,
            "perdidos": result.missing_count,
            "duplicados": result.duplicate_count,
            "inesperados": result.unexpected_count,
            "buffer_final": result.final_buffer_size,
            "ocupacion_maxima": result.max_occupancy,
            "deadlock": "",
            "inanicion_observada": "",
            "detalle_rondas": "",
        })

    print("Ejecutando 20 corridas de Filósofos Comensales...")
    ph_ok = 0

    for run_no in range(1, 21):
        temp_log = LOG_DIR / "_ph_temporal.txt"
        result = run_ph(seed=500 + run_no, log_file=temp_log, echo=False)
        detail = temp_log.read_text(encoding="utf-8")
        temp_log.unlink(missing_ok=True)

        header = (
            "\n" + "=" * 78 + "\n"
            f"FILÓSOFOS COMENSALES | CORRIDA {run_no:02d}\n"
            + "=" * 78 + "\n"
        )
        append_text(PH_LOG, header + detail)

        ph_ok += int(result.ok)
        rows.append({
            "modulo": "filosofos_comensales",
            "corrida": run_no,
            "ok": result.ok,
            "perdidos": "",
            "duplicados": "",
            "inesperados": "",
            "buffer_final": "",
            "ocupacion_maxima": "",
            "deadlock": result.deadlock_detected,
            "inanicion_observada": result.starvation_detected,
            "detalle_rondas": "-".join(map(str, result.completed_rounds)),
        })

    fieldnames = [
        "modulo",
        "corrida",
        "ok",
        "perdidos",
        "duplicados",
        "inesperados",
        "buffer_final",
        "ocupacion_maxima",
        "deadlock",
        "inanicion_observada",
        "detalle_rondas",
    ]
    with CSV_LOG.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summary = f"""RESUMEN DE PRUEBAS - SW407 SEMANA 05
=====================================

Productor-Consumidor
--------------------
Corridas correctas : {pc_ok}/20
Corridas con error : {20 - pc_ok}/20
Criterio            : 0 pérdidas, 0 duplicados, buffer final vacío y capacidad respetada.

Filósofos Comensales
--------------------
Corridas correctas : {ph_ok}/20
Corridas con error : {20 - ph_ok}/20
Criterio            : todos los cocineros completan sus rondas, sin deadlock y sin inanición observada.

Resultado global
----------------
{"APROBADO: 40/40 corridas correctas." if pc_ok == 20 and ph_ok == 20 else "REVISAR: existe al menos una corrida con error."}

Archivos detallados:
- {PC_LOG.name}
- {PH_LOG.name}
- {CSV_LOG.name}
"""
    TXT_SUMMARY.write_text(summary, encoding="utf-8")
    print("\n" + summary)

    return 0 if pc_ok == 20 and ph_ok == 20 else 1


if __name__ == "__main__":
    raise SystemExit(main())

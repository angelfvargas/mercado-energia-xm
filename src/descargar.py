"""Descarga las series del mercado electrico usadas en el analisis."""
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from xm_api import diario, horario  # noqa: E402

DATOS = Path(__file__).resolve().parent.parent / "datos"
INICIO, FIN = date(2025, 8, 20), date(2026, 8, 20)

SERIES_HORARIAS_SISTEMA = [
    "PrecBolsNaci", "DemaCome", "DemaComeReg", "DemaComeNoReg",
    "CompContEner", "PrecPromContRegu", "PrecPromContNoRegu", "RestSinAliv",
]
SERIES_DIARIAS_SISTEMA = ["PorcVoluUtilDiar", "PorcApor", "PrecEscaAct", "PrecPromCont"]
SERIES_HORARIAS_AGENTE = ["DemaCome", "DemaComeReg", "DemaComeNoReg", "CompContEner", "VentContEner"]


def main() -> None:
    for metrica in SERIES_HORARIAS_SISTEMA:
        print(f"sistema/horario {metrica}", flush=True)
        horario(metrica, "Sistema", INICIO, FIN).to_parquet(DATOS / f"sis_h_{metrica}.parquet")
    for metrica in SERIES_DIARIAS_SISTEMA:
        print(f"sistema/diario  {metrica}", flush=True)
        diario(metrica, "Sistema", INICIO, FIN).to_parquet(DATOS / f"sis_d_{metrica}.parquet")
    for metrica in SERIES_HORARIAS_AGENTE:
        print(f"agente/horario  {metrica}", flush=True)
        df = horario(metrica, "Agente", INICIO, FIN)
        # a nivel agente basta el total diario: ahorra 24x en disco
        diario_agente = df.groupby(["fecha", "id"], as_index=False).valor.sum()
        diario_agente.to_parquet(DATOS / f"age_d_{metrica}.parquet")
    print("listo")


if __name__ == "__main__":
    main()

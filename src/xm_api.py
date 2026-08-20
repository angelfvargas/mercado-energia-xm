"""Cliente de la API publica de XM (servapibi.xm.com.co).

XM es el operador del mercado electrico colombiano y publica los datos del
mercado en una API abierta. La API entrega maximo 31 dias por peticion, asi
que aqui se parte el rango en tramos y se guarda cada respuesta en disco para
no volver a pedir lo mismo.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

BASE = "https://servapibi.xm.com.co"
CACHE = Path(__file__).resolve().parent.parent / "datos" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

MAX_DIAS = 30
REINTENTOS = 3
ESPERA_S = 5


def _post(endpoint: str, body: dict) -> dict:
    clave = hashlib.md5(json.dumps([endpoint, body], sort_keys=True).encode()).hexdigest()
    archivo = CACHE / f"{clave}.json"
    if archivo.exists():
        return json.loads(archivo.read_text())

    for intento in range(1, REINTENTOS + 1):
        try:
            r = requests.post(f"{BASE}/{endpoint}", json=body, timeout=180)
            r.raise_for_status()
            datos = r.json()
            archivo.write_text(json.dumps(datos))
            return datos
        except Exception as exc:  # noqa: BLE001
            if intento == REINTENTOS:
                raise
            print(f"  reintento {intento} ({exc.__class__.__name__}), espero {ESPERA_S}s")
            time.sleep(ESPERA_S)
    raise RuntimeError("inalcanzable")


def _tramos(inicio: date, fin: date):
    actual = inicio
    while actual <= fin:
        ultimo = min(actual + timedelta(days=MAX_DIAS - 1), fin)
        yield actual, ultimo
        actual = ultimo + timedelta(days=1)


def horario(metrica: str, entidad: str, inicio: date, fin: date, filtro=None) -> pd.DataFrame:
    """Devuelve una serie horaria larga: columnas fecha, hora, id, valor."""
    filas = []
    for desde, hasta in _tramos(inicio, fin):
        body = {
            "MetricId": metrica,
            "StartDate": desde.isoformat(),
            "EndDate": hasta.isoformat(),
            "Entity": entidad,
        }
        if filtro:
            body["Filter"] = filtro
        datos = _post("hourly", body)
        for item in datos.get("Items", []):
            fecha = item["Date"]
            for ent in item.get("HourlyEntities", []):
                valores = ent["Values"]
                codigo = valores.get("code", ent.get("Id"))
                for hora in range(1, 25):
                    v = valores.get(f"Hour{hora:02d}")
                    if v is None or v == "":
                        continue
                    filas.append((fecha, hora, codigo, float(v)))
    df = pd.DataFrame(filas, columns=["fecha", "hora", "id", "valor"])
    if df.empty:
        return df
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["instante"] = df["fecha"] + pd.to_timedelta(df["hora"] - 1, unit="h")
    return df.sort_values("instante").reset_index(drop=True)


def diario(metrica: str, entidad: str, inicio: date, fin: date, filtro=None) -> pd.DataFrame:
    """Devuelve una serie diaria: columnas fecha, id, valor."""
    filas = []
    for desde, hasta in _tramos(inicio, fin):
        body = {
            "MetricId": metrica,
            "StartDate": desde.isoformat(),
            "EndDate": hasta.isoformat(),
            "Entity": entidad,
        }
        if filtro:
            body["Filter"] = filtro
        datos = _post("daily", body)
        for item in datos.get("Items", []):
            fecha = item["Date"]
            for ent in item.get("DailyEntities", []):
                valores = ent.get("Values", ent)
                bruto = valores.get("Value")
                if bruto is None or bruto == "":
                    continue
                filas.append((fecha, valores.get("code", ent.get("Id")), float(bruto)))
    df = pd.DataFrame(filas, columns=["fecha", "id", "valor"])
    if df.empty:
        return df
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df.sort_values("fecha").reset_index(drop=True)


def lista(metrica: str, entidad: str = "Sistema") -> pd.DataFrame:
    datos = _post("lists", {"MetricId": metrica, "Entity": entidad})
    return pd.json_normalize(datos["Items"], "ListEntities", "Date", sep="_")

"""Analisis del mercado electrico colombiano con datos publicos de XM.

Produce las graficas del informe y un hallazgos.json con las cifras que se
citan en el texto, para que ningun numero del informe este escrito a mano.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.dates as mdates
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from estilo import (AZUL, GRIS, NARANJA, REJILLA, ROJO, SUAVE, TINTA, VERDE, base,  # noqa: E402
                    etiquetas_es, guardar, mes_es, titular)
from xm_api import lista  # noqa: E402

DATOS = RAIZ / "datos"
GRAF = RAIZ / "graficas"
VATIA = "GNCC"          # codigo de Vatia S.A. E.S.P. como comercializador en el MEM
MES_RARO = "2025-12"    # mes con contratos incompletos en la API (ver README)


def _sis_h(m):
    return pd.read_parquet(DATOS / f"sis_h_{m}.parquet")


def _sis_d(m):
    return pd.read_parquet(DATOS / f"sis_d_{m}.parquet")


def _age(m):
    d = pd.read_parquet(DATOS / f"age_d_{m}.parquet")
    return d.pivot_table(index="fecha", columns="id", values="valor", aggfunc="sum").fillna(0)


def cargar():
    precio = _sis_h("PrecBolsNaci")
    datos = {
        "precio_horario": precio,
        "precio_dia": precio.groupby("fecha").valor.mean(),
        "contrato_reg": _sis_h("PrecPromContRegu").groupby("fecha").valor.mean(),
        "contrato_nor": _sis_h("PrecPromContNoRegu").groupby("fecha").valor.mean(),
        "embalse": _sis_d("PorcVoluUtilDiar").set_index("fecha").valor * 100,
        "aportes": _sis_d("PorcApor").set_index("fecha").valor * 100,
        "demanda_sis": _sis_h("DemaCome").groupby("fecha").valor.sum(),
        "dem_ag": _age("DemaCome"),
        "comp_ag": _age("CompContEner"),
        "vent_ag": _age("VentContEner"),
        "reg_ag": _age("DemaComeReg"),
        "nor_ag": _age("DemaComeNoReg"),
    }
    agentes = lista("ListadoAgentes").drop_duplicates("Values_Code").set_index("Values_Code")
    datos["agentes"] = agentes
    datos["comercializadores"] = [
        c for c in datos["dem_ag"].columns
        if c in agentes.index and agentes.loc[c, "Values_Activity"] == "COMERCIALIZACIÓN"
    ]
    return datos


def posicion_contractual(d: dict) -> pd.DataFrame:
    """Exposicion mensual a bolsa de cada comercializador, en % de su demanda.

    XM invierte la orientacion de las etiquetas Compras/Ventas de contratos en
    algunos meses (ver README). Para cada agente y mes se toma el mayor de los
    dos como la energia que respalda su demanda y el menor como sus ventas a
    terceros, que es lo unico consistente en toda la ventana.
    """
    com = d["comercializadores"]
    mes = lambda x: x.resample("ME").sum() / 1e6  # noqa: E731
    dem = mes(d["dem_ag"][com])
    comp = mes(d["comp_ag"]).reindex(columns=com).fillna(0)
    vent = mes(d["vent_ag"]).reindex(columns=com).fillna(0)
    respaldo = pd.concat([comp, vent]).groupby(level=0).max()
    ventas = pd.concat([comp, vent]).groupby(level=0).min()
    expuesto = dem + ventas - respaldo
    return pd.DataFrame({
        "demanda": dem.stack(), "respaldo": respaldo.stack(),
        "ventas": ventas.stack(), "expuesto": expuesto.stack(),
    }).reset_index().rename(columns={"level_1": "agente", "id": "agente"})


def g1_precio(d, h):
    fig, ax = base()
    p = d["precio_dia"]
    ax.plot(p.index, p.values, color=AZUL, lw=1.6, label="Precio de bolsa (promedio diario)")
    ax.plot(d["contrato_reg"].index, d["contrato_reg"].values, color=VERDE, lw=1.4, ls="--",
            label="Contratos mercado regulado")
    ax.plot(d["contrato_nor"].index, d["contrato_nor"].values, color=NARANJA, lw=1.4, ls=":",
            label="Contratos mercado no regulado")
    pico = p.idxmax()
    ax.annotate(mes_es(f"{p.max():,.0f} COP/kWh\n{pico:%d %b %Y}".replace(",", ".")),
                xy=(pico, p.max()), xytext=(-95, -30), textcoords="offset points",
                color=ROJO, fontsize=9, weight="bold",
                arrowprops=dict(arrowstyle="->", color=ROJO, lw=1))
    valle = p.idxmin()
    ax.annotate(f"mínimo del año: {p.min():,.0f} COP/kWh".replace(",", "."), xy=(valle, p.min()),
                xytext=(-30, -34), textcoords="offset points", color=SUAVE, fontsize=9,
                ha="center", bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none"),
                arrowprops=dict(arrowstyle="->", color=GRIS, lw=0.9))
    ax.set_ylim(bottom=p.min() - 80)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    fig.canvas.draw()
    etiquetas_es(ax)
    ax.set_ylabel("COP/kWh", color=SUAVE, fontsize=9)
    ax.legend(frameon=False, fontsize=9, labelcolor=TINTA, loc="upper left")
    titular(ax, "La bolsa se despegó de los contratos",
            f"Precio de bolsa nacional y precio promedio de contratos · {p.index.min():%d/%m/%Y} a {p.index.max():%d/%m/%Y}")
    guardar(fig, GRAF / "01_precio_bolsa.png")
    h["precio_prom_12m"] = round(p.mean(), 1)
    h["precio_max"] = round(p.max(), 1)
    h["precio_max_fecha"] = f"{p.idxmax():%Y-%m-%d}"
    h["precio_min"] = round(p.min(), 1)
    h["precio_min_fecha"] = f"{p.idxmin():%Y-%m-%d}"
    h["precio_ago26"] = round(p[p.index >= "2026-08-01"].mean(), 1)
    h["precio_feb26"] = round(p[(p.index >= "2026-02-01") & (p.index < "2026-03-01")].mean(), 1)
    h["contrato_reg_ult"] = round(d["contrato_reg"].tail(30).mean(), 1)
    h["contrato_nor_ult"] = round(d["contrato_nor"].tail(30).mean(), 1)
    h["multiplo_bolsa_contrato"] = round(h["precio_ago26"] / h["contrato_reg_ult"], 1)


def g2_hidrologia(d, h):
    fig, ax = base()
    p = d["precio_dia"]
    ax.plot(p.index, p.values, color=AZUL, lw=1.5, label="Precio de bolsa (COP/kWh)")
    ax.set_ylabel("COP/kWh", color=AZUL, fontsize=9)
    ax2 = ax.twinx()
    ax2.plot(d["embalse"].index, d["embalse"].values, color=VERDE, lw=1.8, label="Embalses (% volumen útil)")
    ax2.plot(d["aportes"].index, d["aportes"].rolling(15).mean(), color=NARANJA, lw=1.3, ls="--",
             label="Aportes hídricos (% media histórica, media móvil 15d)")
    ax2.set_ylabel("%", color=VERDE, fontsize=9)
    ax2.grid(False)
    for lado in ("top",):
        ax2.spines[lado].set_visible(False)
    ax2.tick_params(colors=SUAVE, labelsize=9)
    lineas = ax.get_lines() + ax2.get_lines()
    ax.legend(lineas, [l.get_label() for l in lineas], frameon=False, fontsize=9,
              labelcolor=TINTA, loc="upper left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    fig.canvas.draw()
    etiquetas_es(ax)
    junto = pd.concat([p.rename("precio"), d["embalse"].rename("emb"), d["aportes"].rename("apo")], axis=1).dropna()
    corr_emb = junto.precio.corr(junto.emb)
    corr_apo = junto.precio.corr(junto.apo)
    titular(ax, "El nivel de los embalses no explica el precio de hoy",
            f"Correlación precio–embalses: {corr_emb:+.2f} · precio–aportes: {corr_apo:+.2f}")
    guardar(fig, GRAF / "02_hidrologia.png")
    h["corr_precio_embalse"] = round(corr_emb, 2)
    h["corr_precio_aportes"] = round(corr_apo, 2)
    h["embalse_actual"] = round(d["embalse"].tail(7).mean(), 1)
    h["embalse_prom_12m"] = round(d["embalse"].mean(), 1)
    h["aportes_ago26"] = round(d["aportes"][d["aportes"].index >= "2026-08-01"].mean(), 1)


def g3_perfil_horario(d, h):
    ph = d["precio_horario"].copy()
    ph["mes"] = ph.fecha.dt.to_period("M").astype(str)
    fig, ax = base(figsize=(11, 4.8))
    for mes, color, ancho in [("2026-02", GRIS, 1.6), ("2026-05", VERDE, 1.6), ("2026-08", ROJO, 2.4)]:
        sub = ph[ph.mes == mes].groupby("hora").valor.mean()
        if sub.empty:
            continue
        ax.plot(sub.index, sub.values, color=color, lw=ancho, marker="o", ms=3,
                label=f"{mes_es(pd.Period(mes).strftime('%b %Y'))} (promedio {sub.mean():,.0f} COP/kWh)".replace(",", "."))
    ax.set_xticks(range(1, 25, 2))
    ax.set_xlabel("Hora del día", color=SUAVE, fontsize=9)
    ax.set_ylabel("COP/kWh", color=SUAVE, fontsize=9)
    ax.legend(frameon=False, fontsize=9, labelcolor=TINTA)
    ult = ph[ph.mes == ph.mes.max()].groupby("hora").valor.mean()
    titular(ax, "Ya casi no quedan horas baratas",
            f"Precio promedio por hora del día · en agosto la hora más cara solo supera "
            f"en {100 * (ult.max() / ult.min() - 1):.0f}% a la más barata, y el piso está en "
            f"{ult.min():,.0f} COP/kWh".replace(",", "."))
    guardar(fig, GRAF / "03_perfil_horario.png")
    h["hora_pico"] = int(ult.idxmax())
    h["hora_valle"] = int(ult.idxmin())
    h["brecha_horaria_pct"] = round(100 * (ult.max() / ult.min() - 1), 1)


def g4_exposicion(d, pos, h):
    com = pos[pos.agente != ""].copy()
    com["mes"] = com.fecha.dt.to_period("M").astype(str)
    com = com[com.demanda > 5]
    com["pct"] = 100 * com.expuesto / com.demanda
    sano = com[com.mes != MES_RARO]
    mediana = sano.groupby("mes").pct.median()
    vat = sano[sano.agente == VATIA].set_index("mes").pct
    fig, ax = base(figsize=(11, 4.8))
    x = np.arange(len(mediana))
    ax.bar(x - 0.2, mediana.values, width=0.4, color=REJILLA, edgecolor=GRIS, lw=0.6,
           label="Mediana de los comercializadores del país")
    ax.bar(x + 0.2, vat.reindex(mediana.index).values, width=0.4, color=AZUL,
           label="Vatia S.A. E.S.P.")
    ax.set_xticks(x)
    ax.set_xticklabels([mes_es(pd.Period(m).strftime("%b %y")) for m in mediana.index], fontsize=8.5)
    ax.set_ylabel("% de la demanda comprada en bolsa", color=SUAVE, fontsize=9)
    ax.legend(frameon=False, fontsize=9, labelcolor=TINTA, loc="upper left")
    titular(ax, "Cuánta energía queda expuesta al precio de bolsa",
            "Demanda no respaldada por contratos, mes a mes · diciembre 2025 excluido por datos incompletos")
    guardar(fig, GRAF / "04_exposicion.png")
    h["vatia_expo_prom"] = round(vat.mean(), 1)
    h["vatia_expo_ult"] = round(vat.iloc[-1], 1)
    MESES_LARGOS = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
                    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre",
                    12: "diciembre"}
    ultimo = pd.Period(vat.index[-1])
    h["vatia_expo_ult_mes"] = f"{MESES_LARGOS[ultimo.month]} {ultimo.year}"
    h["mercado_expo_prom"] = round(mediana.mean(), 1)
    h["mercado_expo_ult"] = round(mediana.iloc[-1], 1)


def g5_ranking(d, h):
    com = d["comercializadores"]
    tot = (d["dem_ag"][com].sum() / 1e6).sort_values(ascending=False)
    top = tot.head(15)
    def nombre_corto(codigo: str) -> str:
        crudo = d["agentes"].loc[codigo, "Values_Name"].title()
        for sufijo in (" S.A.S. E.S.P.", " S.A. E.S.P.", " S.A.S.", " E.S.P.", " E.I.C.E."):
            crudo = crudo.replace(sufijo, "")
        crudo = crudo.replace(" Sa Esp", "").strip(" -")
        return crudo if len(crudo) <= 36 else crudo[:35] + "…"

    nombres = [nombre_corto(c) for c in top.index]
    fig, ax = base(figsize=(10, 6))
    colores = [AZUL if c == VATIA else REJILLA for c in top.index]
    bordes = [AZUL if c == VATIA else GRIS for c in top.index]
    ax.barh(range(len(top)), top.values, color=colores, edgecolor=bordes, lw=0.7)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(nombres, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Demanda comercial atendida en 12 meses (GWh)", color=SUAVE, fontsize=9)
    for i, (c, v) in enumerate(top.items()):
        ax.text(v + tot.max() * 0.01, i, f"{v:,.0f}".replace(",", "."), va="center",
                fontsize=8.5, color=AZUL if c == VATIA else SUAVE,
                weight="bold" if c == VATIA else "normal")
    puesto = list(tot.index).index(VATIA) + 1
    titular(ax, f"Vatia es el comercializador N.° {puesto} del país",
            f"{len(tot)} comercializadores activos · Vatia atiende {100 * tot[VATIA] / tot.sum():.2f}% de la demanda nacional")
    guardar(fig, GRAF / "05_ranking.png")
    h["vatia_puesto"] = puesto
    h["vatia_gwh_12m"] = round(tot[VATIA], 1)
    h["vatia_cuota_pct"] = round(100 * tot[VATIA] / tot.sum(), 2)
    h["comercializadores_activos"] = int(len(tot))
    reg = d["reg_ag"][VATIA].sum() / 1e6
    nor = d["nor_ag"][VATIA].sum() / 1e6
    h["vatia_regulado_pct"] = round(100 * reg / (reg + nor), 1)
    h["vatia_gwh_regulado"] = round(reg, 1)
    h["vatia_gwh_no_regulado"] = round(nor, 1)


def g6_costo(d, pos, h):
    p_mes = d["precio_dia"].resample("ME").mean()
    c_mes = d["contrato_reg"].resample("ME").mean()
    vat = pos[(pos.agente == VATIA)].copy()
    vat["mes"] = vat.fecha.dt.to_period("M").astype(str)
    vat = vat[vat.mes != MES_RARO].set_index("fecha")
    brecha = (p_mes - c_mes).reindex(vat.index)
    costo = (vat.expuesto * 1e6 * brecha) / 1e9  # miles de millones de COP
    fig, ax = base(figsize=(11, 4.8))
    colores = [ROJO if v > 0 else VERDE for v in costo.values]
    ax.bar(range(len(costo)), costo.values, color=colores, width=0.6)
    ax.axhline(0, color=GRIS, lw=1)
    ax.set_xticks(range(len(costo)))
    ax.set_xticklabels([mes_es(f"{i:%b %y}") for i in costo.index], fontsize=8.5)
    ax.set_ylabel("Miles de millones de COP", color=SUAVE, fontsize=9)
    for i, v in enumerate(costo.values):
        ax.text(i, v + (0.6 if v >= 0 else -1.2), f"{v:,.1f}".replace(".", ","), ha="center",
                fontsize=8.5, color=TINTA)
    titular(ax, "Lo que cuesta comprar en bolsa en vez de en contratos",
            "Energía expuesta de Vatia × (precio de bolsa − precio de contratos regulados) · estimación de orden de magnitud")
    guardar(fig, GRAF / "06_costo_exposicion.png")
    h["costo_ult_mes_mmm"] = round(costo.iloc[-1], 1)
    h["costo_jul26_mmm"] = round(float(costo[costo.index.strftime("%Y-%m") == "2026-07"].iloc[0]), 1)
    h["costo_12m_mmm"] = round(costo.sum(), 1)


def main():
    GRAF.mkdir(exist_ok=True)
    d = cargar()
    h = {}
    pos = posicion_contractual(d)
    pos.to_csv(RAIZ / "datos" / "posicion_contractual.csv", index=False)
    g1_precio(d, h)
    g2_hidrologia(d, h)
    g3_perfil_horario(d, h)
    g4_exposicion(d, pos, h)
    g5_ranking(d, h)
    g6_costo(d, pos, h)
    h["ventana_inicio"] = f"{d['precio_dia'].index.min():%Y-%m-%d}"
    h["ventana_fin"] = f"{d['precio_dia'].index.max():%Y-%m-%d}"
    h["demanda_pais_gwh"] = round(d["demanda_sis"].sum() / 1e6, 0)
    (RAIZ / "hallazgos.json").write_text(json.dumps(h, indent=2, ensure_ascii=False))
    print(json.dumps(h, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

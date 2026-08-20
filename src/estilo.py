"""Estilo comun de las graficas."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TINTA = "#1d2733"
SUAVE = "#6b7a8d"
REJILLA = "#e4e9ef"
AZUL = "#2f6fb0"
NARANJA = "#e08a2b"
ROJO = "#c0392b"
VERDE = "#2e8b6f"
GRIS = "#9aa7b5"


def base(figsize=(11, 5.2)):
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.grid(True, color=REJILLA, linewidth=0.9)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(REJILLA)
    ax.tick_params(colors=SUAVE, labelsize=9)
    return fig, ax


MESES = {
    "Jan": "ene", "Feb": "feb", "Mar": "mar", "Apr": "abr", "May": "may", "Jun": "jun",
    "Jul": "jul", "Aug": "ago", "Sep": "sep", "Oct": "oct", "Nov": "nov", "Dec": "dic",
}


def mes_es(texto: str) -> str:
    """Traduce los meses en ingles que trae matplotlib por defecto."""
    for ing, esp in MESES.items():
        texto = texto.replace(ing, esp)
    return texto


def etiquetas_es(ax, eje="x"):
    objetivo = ax.get_xticklabels() if eje == "x" else ax.get_yticklabels()
    fijar = ax.set_xticklabels if eje == "x" else ax.set_yticklabels
    fijar([mes_es(t.get_text()) for t in objetivo])


def titular(ax, titulo, subtitulo=None):
    ax.set_title(titulo, color=TINTA, fontsize=13.5, weight="bold", loc="left",
                 pad=30 if subtitulo else 14)
    if subtitulo:
        ax.text(0, 1.035, mes_es(subtitulo), transform=ax.transAxes, color=SUAVE,
                fontsize=9.5, va="bottom")


def guardar(fig, ruta):
    fig.text(0.005, 0.005, "Fuente: API publica de XM (servapibi.xm.com.co)", color=GRIS, fontsize=7.5)
    fig.tight_layout()
    fig.savefig(ruta, bbox_inches="tight", facecolor="white")
    print("grafica:", ruta)

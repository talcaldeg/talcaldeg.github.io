"""Gráficos de «La medición era el producto» (palancas-chicas y small-levers).

Genera los tres gráficos en español e inglés, cada uno en tema claro y oscuro, con la paleta
del sitio (validada con validate_palette.js de la skill dataviz) y la tipografía Inter.

    python _graficos/palancas_chicas.py

Salida: articulos/<slug>/img/<nombre>.png (claro, también es la og:image) y
<nombre>-oscuro.png (oscuro, lo sirve <picture> con prefers-color-scheme: dark).
"""
import glob
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath
from matplotlib.transforms import blended_transform_factory

RAIZ = Path(__file__).resolve().parent.parent

for f in glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts\Inter-*.ttf")):
    font_manager.fontManager.addfont(f)
assert "Inter" in {f.name for f in font_manager.fontManager.ttflist}, "falta instalar Inter (rsms/inter)"
plt.rcParams.update({"font.family": "Inter", "svg.fonttype": "none"})

# Superficie = --card del sitio. Acento y negativo validados en ambos modos.
TEMAS = {
    "claro": dict(sup="#ffffff", tinta="#132338", suave="#4d637f", linea="#dbe4ef",
                  neutro="#aebdd0", acento="#0d9488", negativo="#d64545"),
    "oscuro": dict(sup="#17293f", tinta="#eaf1f9", suave="#9db2ca", linea="#26405e",
                   neutro="#4f6a8c", acento="#13a593", negativo="#e85d5d"),
}

ANCHO, DPI = 8.0, 200          # 1600 px de ancho
RADIO_PX = 9                   # extremo redondeado (~4 px de pantalla)
HUECO_PX = 5                   # separación de superficie entre tramos que se tocan


def mezclar(c, fondo, a):
    """Color c con opacidad a sobre el fondo, como hex opaco."""
    c = [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    f = [int(fondo[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(a * x + (1 - a) * y):02x}" for x, y in zip(c, f))


def num(v, idioma, dec=None, signo=False):
    s = f"{v:.{dec}f}" if dec is not None else f"{v:.2f}".rstrip("0").rstrip(".")
    if idioma == "es":
        s = s.replace(".", ",")
    if signo and v > 0:
        s = "+" + s
    return s.replace("-", "−") + " %"


class Lienzo:
    """Figura con márgenes fijos, para que el radio en píxeles sea exacto."""

    def __init__(self, t, alto, izq_px, titulo, subtitulo, nota=None, abajo=40, der=70):
        self.t = t
        self.fig = plt.figure(figsize=(ANCHO, alto), dpi=DPI, facecolor=t["sup"])
        W, H = ANCHO * DPI, alto * DPI
        arriba = 150 if subtitulo else 105
        self.ax = self.fig.add_axes([izq_px / W, abajo / H, 1 - (izq_px + der) / W,
                                     1 - (arriba + abajo) / H])
        self.ax.set_facecolor(t["sup"])
        for s in self.ax.spines.values():
            s.set_visible(False)
        self.ax.tick_params(length=0, colors=t["tinta"], labelsize=10.5)
        self.fig.text(56 / W, 1 - 42 / H, titulo, fontsize=15, fontweight="semibold",
                      color=t["tinta"], va="top")
        if subtitulo:
            self.fig.text(56 / W, 1 - 94 / H, subtitulo, fontsize=10.5, color=t["suave"], va="top")
        if nota:
            self.fig.text(56 / W, 24 / H, nota, fontsize=8.8, color=t["suave"], va="bottom")

    def escalas(self):
        bb = self.ax.get_window_extent()
        x0, x1 = self.ax.get_xlim()
        y0, y1 = self.ax.get_ylim()
        return abs(x1 - x0) / bb.width, abs(y1 - y0) / bb.height

    def barra(self, a, b, centro, grueso, color, horizontal=True, redondo=True):
        """Tramo de a a b; si redondo, redondea el extremo b (el de los datos)."""
        dx, dy = self.escalas()
        if not horizontal:
            dx, dy = dy, dx
        r_largo = min(RADIO_PX * dx, abs(b - a)) if redondo else 0
        r_ancho = min(RADIO_PX * dy, grueso / 2) if redondo else 0
        s = 1 if b >= a else -1
        lo, hi = centro - grueso / 2, centro + grueso / 2
        e = b - s * r_largo
        pts = [(a, lo), (e, lo), (b, lo), (b, lo + r_ancho), (b, hi - r_ancho), (b, hi),
               (e, hi), (a, hi), (a, lo)]
        codigos = [MPath.MOVETO, MPath.LINETO, MPath.CURVE3, MPath.CURVE3, MPath.LINETO,
                   MPath.CURVE3, MPath.CURVE3, MPath.LINETO, MPath.CLOSEPOLY]
        if not horizontal:
            pts = [(y, x) for x, y in pts]
        self.ax.add_patch(PathPatch(MPath(pts, codigos), facecolor=color, edgecolor="none"))

    def hueco(self, horizontal=True):
        dx, dy = self.escalas()
        return HUECO_PX * (dx if horizontal else dy)

    def texto(self, x, y, s, **kw):
        kw.setdefault("color", self.t["tinta"])
        kw.setdefault("fontsize", 10.5)
        self.ax.text(x, y, s, **kw)

    def guardar(self, destino):
        self.fig.savefig(destino, dpi=DPI, facecolor=self.t["sup"])
        plt.close(self.fig)


TXT = {
    "es": dict(
        slug="palancas-chicas",
        p_tit="Techo de cada palanca, suponiendo obediencia total",
        p_sub="% del costo ponderado. En color, la única medida después de aplicarla.",
        p_filas=["Registrar la memoria en un solo comando", "Achicar los argumentos de herramientas",
                 "Juntar lecturas independientes", "Mapa de carpetas en vez de buscar",
                 "Partir las notas de memoria grandes", "No buscar en el lugar equivocado",
                 "Cargar instrucciones solo por ruta", "Recortar 10 % de las instrucciones globales"],
        p_medido="medido",
        r_tit="Una instrucción escrita rinde tres días",
        r_sub="% de llamadas que mandan dos o más herramientas juntas",
        r_cols=["Dos semanas antes", "11 al 13 de sep.\nregla recién escrita", "Desde el 14 de sep.",
                "Régimen siguiente"],
        r_rango="9-16 %",
        s_tit="Cortar sesiones sale negativo; seguir en la misma, a veces rinde",
        s_sub="Ahorro simulado sobre los transcripts, % del costo ponderado",
        s_g1="Cortar la sesión a mitad de tarea", s_g2="Seguir con la tarea siguiente en la misma",
        s_filas=["Al pasar 25 mil tokens de exceso", "Al pasar 50 mil", "Desde 75 mil (no corta nunca)",
                 "Oráculo que sabe el futuro", "Primer día", "Segundo día"],
        s_oraculo="techo imposible",
        s_rango="+1,7 a +1,9 %",
    ),
    "en": dict(
        slug="small-levers",
        p_tit="Ceiling of each lever, assuming full compliance",
        p_sub="% of weighted cost. In color, the only one measured after applying it.",
        p_filas=["Log memory with a single command", "Shrink tool arguments", "Batch independent reads",
                 "Folder map instead of searching", "Split the large memory notes",
                 "Don't search in the wrong place", "Load instructions by path only",
                 "Trim 10 % of the global instructions"],
        p_medido="measured",
        r_tit="A written instruction pays off for three days",
        r_sub="% of calls that send two or more tools together",
        r_cols=["Two weeks before", "Sep 11-13\nrule just written", "From Sep 14", "Next regime"],
        r_rango="9-16 %",
        s_tit="Cutting sessions comes out negative; staying in one sometimes pays",
        s_sub="Simulated savings on the transcripts, % of weighted cost",
        s_g1="Cut the session mid-task", s_g2="Carry on with the next task in the same one",
        s_filas=["Above 25k tokens of excess", "Above 50k", "From 75k (never cuts)",
                 "Oracle that knows the future", "First day", "Second day"],
        s_oraculo="impossible ceiling",
        s_rango="+1.7 to +1.9 %",
    ),
}


def ancho_etiquetas(textos, tam=10.5):
    fig = plt.figure(dpi=DPI)
    r = fig.canvas.get_renderer()
    w = max(fig.text(0, 0, s, fontsize=tam).get_window_extent(r).width for s in textos)
    plt.close(fig)
    return w


def palancas(t, L, idioma, destino):
    vals = [3.4, 2.7, 1.8, 1.07, 1.0, 0.25, 0.2, 0.18]
    izq = 56 + ancho_etiquetas(L["p_filas"]) + 28
    c = Lienzo(t, 4.6, izq, L["p_tit"], L["p_sub"])
    ax = c.ax
    n = len(vals)
    ax.set_xlim(0, 4.3); ax.set_ylim(n - 0.45, -0.55)
    ax.set_xticks([]); ax.set_yticks(range(n)); ax.set_yticklabels(L["p_filas"])
    for i, v in enumerate(vals):
        medido = i == 0
        c.barra(0, v, i, 0.52, t["acento"] if medido else t["neutro"])
        et = num(v, idioma) + (f"  {L['p_medido']}" if medido else "")
        c.texto(v + 0.06, i, et, va="center", fontweight="semibold" if medido else "normal")
    ax.get_yticklabels()[0].set_fontweight("semibold")
    ax.axvline(0, color=t["suave"], lw=0.9)
    c.guardar(destino)


def regla(t, L, idioma, destino):
    vals = [47, 18, 10]
    c = Lienzo(t, 4.6, 56, L["r_tit"], L["r_sub"], abajo=120, der=56)
    ax = c.ax
    ax.set_xlim(-0.55, 3.55); ax.set_ylim(0, 54)
    ax.set_yticks([]); ax.set_xticks(range(4)); ax.set_xticklabels(L["r_cols"], fontsize=10.2)
    ax.tick_params(axis="x", pad=8)
    g = 0.46
    # Columna 1: rango 9-16 %, tramo firme hasta 9 y tramo claro de 9 a 16.
    c.barra(0, 9, 0, g, t["neutro"], horizontal=False, redondo=False)
    c.barra(9 + c.hueco(False), 16, 0, g, mezclar(t["neutro"], t["sup"], 0.45), horizontal=False)
    c.texto(0, 17.4, L["r_rango"], ha="center", va="bottom")
    for x, v in zip((1, 2, 3), vals):
        destacado = x == 1
        c.barra(0, v, x, g, t["acento"] if destacado else t["neutro"], horizontal=False)
        c.texto(x, v + 1.4, num(v, idioma, 0), ha="center", va="bottom",
                fontweight="semibold" if destacado else "normal", fontsize=12 if destacado else 10.5)
    ax.get_xticklabels()[1].set_fontweight("semibold")
    ax.axhline(0, color=t["suave"], lw=0.9)
    c.guardar(destino)


def sesiones(t, L, idioma, destino):
    # (fila, valor, tipo); tipo: neg, cero, oraculo, rango, pos
    filas = [(0.9, -2.7, "neg"), (1.9, -0.6, "neg"), (2.9, 0.0, "cero"), (3.9, 2.9, "oraculo"),
             (5.9, 1.8, "rango"), (6.9, 0.53, "pos")]
    izq = 56 + ancho_etiquetas(L["s_filas"]) + 28
    c = Lienzo(t, 4.9, izq, L["s_tit"], L["s_sub"])
    ax = c.ax
    ax.set_xlim(-3.9, 5.9); ax.set_ylim(7.45, -0.35)
    ax.set_xticks([]); ax.set_yticks([f[0] for f in filas]); ax.set_yticklabels(L["s_filas"])
    borde = blended_transform_factory(c.fig.transFigure, ax.transData)
    for y, s in ((0, L["s_g1"]), (5.0, L["s_g2"])):
        ax.text(56 / (ANCHO * DPI), y, s, transform=borde, fontsize=10.5, fontweight="semibold",
                color=t["tinta"], va="center", ha="left", clip_on=False)
    g = 0.5
    for (y, v, tipo), et in zip(filas, L["s_filas"]):
        sep = 0.07
        if tipo == "neg":
            c.barra(0, v, y, g, t["negativo"])
            c.texto(v - sep, y, num(v, idioma, signo=True), ha="right", va="center")
        elif tipo == "cero":
            ax.plot([0], [y], "o", ms=5.5, color=t["neutro"], mec=t["sup"], mew=1.5, zorder=3)
            c.texto(sep + 0.05, y, num(0, idioma), ha="left", va="center")
        elif tipo == "oraculo":
            c.barra(0, v, y, g, mezclar(t["acento"], t["sup"], 0.38))
            c.texto(v + sep, y, f"{num(v, idioma, signo=True)}  {L['s_oraculo']}", ha="left",
                    va="center", color=t["suave"])
        elif tipo == "rango":
            c.barra(0, 1.7, y, g, t["acento"], redondo=False)
            c.barra(1.7 + c.hueco(), 1.9, y, g, mezclar(t["acento"], t["sup"], 0.45))
            c.texto(1.9 + sep, y, L["s_rango"], ha="left", va="center")
        else:
            c.barra(0, v, y, g, t["acento"])
            c.texto(v + sep, y, num(v, idioma, signo=True), ha="left", va="center")
    ax.axvline(0, color=t["suave"], lw=0.9)
    c.guardar(destino)


def main():
    hechos = []
    for idioma, L in TXT.items():
        img = RAIZ / "articulos" / L["slug"] / "img"
        img.mkdir(parents=True, exist_ok=True)
        for tema, t in TEMAS.items():
            suf = "" if tema == "claro" else "-oscuro"
            for nombre, fn in (("palancas", palancas), ("regla", regla), ("sesiones", sesiones)):
                p = img / f"{nombre}{suf}.png"
                fn(t, L, idioma, p)
                hechos.append(p)
    for p in hechos:
        print(p.relative_to(RAIZ))


if __name__ == "__main__":
    main()

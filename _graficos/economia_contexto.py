"""Gráficos de «Lo caro de un agente no es lo que hace» (economia-de-contexto y context-economy).

Rehace los cuatro gráficos de agosto con el estilo de la segunda parte (palancas_chicas.py):
español e inglés, tema claro y oscuro, tipografía Inter.

    python _graficos/economia_contexto.py

Los datos vienen de economia_contexto_datos.json, no de los transcripts: esos ya no existen y
las cifras del texto se midieron con el conteo anterior a la corrección. La procedencia de cada
serie está anotada en el propio JSON.

Salida: articulos/<slug>/img/<nombre>.png (claro, también es la og:image) y
<nombre>-oscuro.png (oscuro, lo sirve <picture> con prefers-color-scheme: dark).
"""
import json

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullLocator

from palancas_chicas import ANCHO, DPI, RAIZ, TEMAS, Lienzo, ancho_etiquetas, mezclar, num

DATOS = json.loads((RAIZ / "_graficos" / "economia_contexto_datos.json").read_text(encoding="utf-8"))

TXT = {
    "es": dict(
        slug="economia-de-contexto",
        re_tit="El trabajo no es lo que se paga",
        re_sub="Los 2.356 millones de tokens de la medición, por tipo",
        re_filas=["releer contexto ya acumulado (cache_read)",
                  "contexto nuevo (entrada + escritura de caché)",
                  "lo que el modelo escribe (output)"],
        de_tit="El mismo trabajo, más caro cada vez",
        de_sub="Contexto leído por turno, por décimo de la sesión. 45 sesiones de 120 turnos o más",
        de_arranque="contexto al arrancar",
        de_x="avance de la sesión (décimos de los turnos)",
        mil=lambda v: "0" if v == 0 else f"{v // 1000:.0f} mil",
        cu_tit="Una sesión el doble de larga cuesta 2,3 veces, no 4",
        cu_sub="Tokens por sesión contra turnos, escala logarítmica. Cada punto es una de las 313 sesiones",
        cu_ajuste="costo ∝ turnos^{b}  ·  R² {r2}",
        cu_lineal="si cada turno costara lo mismo",
        cu_x="turnos de la sesión (llamadas al modelo)",
        cu_y=["100 mil", "1 M", "10 M", "100 M"],
        ar_tit="Qué es lo que se relee tantas veces",
        ar_sub="Arrastre: tokens del resultado × turnos que vinieron después. 380 millones en total",
        ar_filas={"archivos": "Leer archivos enteros", "shell": "Comandos de shell",
                  "web": "Web y otros conectores", "correo": "Conectores (correo, documentos)",
                  "resto": "Resto", "busqueda": "Búsqueda filtrada"},
    ),
    "en": dict(
        slug="context-economy",
        re_tit="The work is not what you pay for",
        re_sub="The 2.36 billion tokens measured, by type",
        re_filas=["re-reading context already there (cache_read)",
                  "new context (input + cache writes)",
                  "what the model writes (output)"],
        de_tit="The same work, more expensive every time",
        de_sub="Context read per turn, by tenth of the session. 45 sessions of 120 turns or more",
        de_arranque="context at the start",
        de_x="progress through the session (tenths of the turns)",
        mil=lambda v: "0" if v == 0 else f"{v // 1000:.0f}k",
        cu_tit="A session twice as long costs 2.3 times as much, not 4",
        cu_sub="Tokens per session against turns, log scale. Each dot is one of the 313 sessions",
        cu_ajuste="cost ∝ turns^{b}  ·  R² {r2}",
        cu_lineal="if every turn cost the same",
        cu_x="turns in the session (calls to the model)",
        cu_y=["100k", "1M", "10M", "100M"],
        ar_tit="What it is that gets re-read so many times",
        ar_sub="Carry: result tokens × turns that came after. 380 million in total",
        ar_filas={"archivos": "Reading whole files", "shell": "Shell commands",
                  "web": "Web and other connectors", "correo": "Connectors (mail, documents)",
                  "resto": "The rest", "busqueda": "Filtered search"},
    ),
}


def decimal(v, idioma, dec):
    s = f"{v:.{dec}f}"
    return s.replace(".", ",") if idioma == "es" else s


def reparto(t, L, idioma, destino):
    pct = DATOS["reparto"]["pct"]
    colores = [t["acento"], t["neutro"], t["suave"]]
    c = Lienzo(t, 2.9, 56, L["re_tit"], L["re_sub"], abajo=150, der=56)
    ax = c.ax
    ax.set_xlim(0, 100); ax.set_ylim(1, -0.62)
    ax.set_xticks([]); ax.set_yticks([])
    x = 0
    for i, (v, col) in enumerate(zip(pct, colores)):
        c.barra(x + (c.hueco() if i else 0), x + v, 0, 0.62, col, redondo=i == len(pct) - 1)
        x += v
    # Rótulos directos bajo la barra: el grande a la izquierda, los dos chicos a la derecha.
    c.texto(0, 0.52, num(pct[0], idioma), fontsize=17, fontweight="semibold", color=t["acento"], va="top")
    c.texto(0, 0.95, L["re_filas"][0], va="top")
    for y, v, col, et in ((0.52, pct[1], colores[1], L["re_filas"][1]),
                          (0.84, pct[2], colores[2], L["re_filas"][2])):
        c.texto(100, y, f"{et}   ", ha="right", va="top", color=t["suave"])
        c.texto(100, y, num(v, idioma), ha="right", va="top", color=col, fontweight="semibold",
                transform=ax.transData)
    c.guardar(destino)


def reparto_derecha(ax, textos):
    """Deja el rótulo de texto a la izquierda del porcentaje, sin pisarse."""
    r = ax.figure.canvas.get_renderer()
    for et, pc in textos:
        w = pc.get_window_extent(r).width
        x, y = et.get_position()
        inv = ax.transData.inverted()
        px, py = ax.transData.transform((x, y))
        et.set_position(inv.transform((px - w - 10, py)))


def deriva(t, L, idioma, destino):
    m = DATOS["deriva"]["medias"]
    n = len(m)
    etq = [L["mil"](v) for v in range(0, 200001, 50000)]
    izq = 56 + ancho_etiquetas(etq) + 18
    c = Lienzo(t, 4.4, izq, L["de_tit"], L["de_sub"], abajo=110, der=90)
    ax = c.ax
    xs = list(range(1, n + 1))
    ax.set_xlim(0.6, n + 0.4); ax.set_ylim(0, 225000)
    ax.set_xticks(xs); ax.set_yticks(range(0, 200001, 50000)); ax.set_yticklabels(etq)
    ax.tick_params(axis="x", pad=8)
    ax.grid(axis="y", color=t["linea"], lw=0.9); ax.set_axisbelow(True)
    ax.fill_between(xs, [m[0]] * n, m, color=mezclar(t["acento"], t["sup"], 0.16), lw=0)
    ax.axhline(m[0], color=t["suave"], lw=1.1, ls=(0, (4, 3)))
    c.texto(1.1, m[0] - 6000, f"{L['de_arranque']}: {L['mil'](round(m[0], -3))}", va="top",
            color=t["suave"], fontsize=10)
    ax.plot(xs, m, color=t["acento"], lw=2.4, zorder=3)
    ax.plot(xs, m, "o", ms=6.5, color=t["acento"], mec=t["sup"], mew=1.6, zorder=4)
    c.texto(n + 0.22, m[-1], "×" + decimal(m[-1] / m[0], idioma, 1), va="center", ha="left",
            fontsize=15, fontweight="semibold", color=t["acento"])
    ax.axhline(0, color=t["suave"], lw=0.9)
    ax.set_xlabel(L["de_x"], color=t["suave"], fontsize=10, labelpad=10)
    c.guardar(destino)


def curva(t, L, idioma, destino):
    d = DATOS["curva"]
    xs = [p[0] for p in d["puntos"]]
    ys = [p[1] for p in d["puntos"]]
    izq = 56 + ancho_etiquetas(L["cu_y"]) + 18
    c = Lienzo(t, 5.4, izq, L["cu_tit"], L["cu_sub"], abajo=110, der=40)
    ax = c.ax
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.8, 800); ax.set_ylim(4e4, 1.6e8)
    ax.xaxis.set_major_locator(FixedLocator([1, 10, 100])); ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xticklabels(["1", "10", "100"])
    ax.yaxis.set_major_locator(FixedLocator([1e5, 1e6, 1e7, 1e8])); ax.yaxis.set_minor_locator(NullLocator())
    ax.set_yticklabels(L["cu_y"])
    ax.tick_params(axis="x", pad=8)
    ax.grid(color=t["linea"], lw=0.9); ax.set_axisbelow(True)
    ax.scatter(xs, ys, s=22, color=t["neutro"], alpha=0.75, edgecolors="none", zorder=2)
    x0, x1 = min(xs), max(xs)
    finos = [x0 * (x1 / x0) ** (i / 100) for i in range(101)]
    k_lin = ys[xs.index(x0)] / x0
    ax.plot(finos, [k_lin * x for x in finos], color=t["suave"], lw=1.3, ls=(0, (4, 3)), zorder=3)
    b, k = d["recta_exponente"], d["recta_k"]
    ax.plot(finos, [k * x ** b for x in finos], color=t["acento"], lw=2.4, zorder=4)
    rot = L["cu_ajuste"].format(b=decimal(d["exponente_publicado"], idioma, 2),
                                r2=decimal(d["r2_publicado"], idioma, 2))
    c.texto(1.2, 1.05e8, rot, color=t["acento"], fontweight="semibold", va="center")
    c.texto(x1 * 0.93, k_lin * x1 * 0.62, L["cu_lineal"], color=t["suave"], ha="right", va="top", fontsize=10)
    ax.axhline(4e4, color=t["suave"], lw=0.9)
    ax.set_xlabel(L["cu_x"], color=t["suave"], fontsize=10, labelpad=10)
    c.guardar(destino)


def arrastre(t, L, idioma, destino):
    pct = DATOS["arrastre"]["pct"]
    claves = sorted(pct, key=lambda k: -pct[k])
    filas = [L["ar_filas"][k] for k in claves]
    izq = 56 + ancho_etiquetas(filas) + 28
    c = Lienzo(t, 3.9, izq, L["ar_tit"], L["ar_sub"])
    ax = c.ax
    n = len(claves)
    ax.set_xlim(0, 62); ax.set_ylim(n - 0.45, -0.55)
    ax.set_xticks([]); ax.set_yticks(range(n)); ax.set_yticklabels(filas)
    for i, kc in enumerate(claves):
        v = pct[kc]
        destacado = i == 0
        c.barra(0, v, i, 0.56, t["acento"] if destacado else t["neutro"])
        c.texto(v + 0.9, i, num(v, idioma, 0), va="center",
                fontweight="semibold" if destacado else "normal")
    ax.get_yticklabels()[0].set_fontweight("semibold")
    ax.axvline(0, color=t["suave"], lw=0.9)
    c.guardar(destino)


def main():
    hechos = []
    for idioma, L in TXT.items():
        img = RAIZ / "articulos" / L["slug"] / "img"
        for tema, t in TEMAS.items():
            suf = "" if tema == "claro" else "-oscuro"
            for nombre, fn in (("reparto", reparto), ("deriva", deriva), ("curva", curva),
                               ("arrastre", arrastre)):
                p = img / f"{nombre}{suf}.png"
                fn(t, L, idioma, p)
                hechos.append(p)
    for p in hechos:
        print(p.relative_to(RAIZ))


if __name__ == "__main__":
    main()

"""Gráficos de «La nota estaba bien; el problema era encontrarla» (memoria-ruteo y memory-routing).

Reusa el lienzo, la paleta (validada con validate_palette.js de la skill dataviz) y la
tipografía de palancas_chicas.py. Las cifras salen de `tokens/banco_respuestas.py` del repo
privado, corrido el 6-oct-2026 (191 pares, bodega de 220 notas).

    python _graficos/memoria_ruteo.py

Salida: articulos/<slug>/img/<nombre>.png (claro, también es la og:image) y
<nombre>-oscuro.png (oscuro, lo sirve <picture> con prefers-color-scheme: dark).
"""
from palancas_chicas import RAIZ, TEMAS, Lienzo, ancho_etiquetas, mezclar, num

# (tokens por pregunta, % de acierto)
FRAGMENTOS = [(1061, 7), (2164, 14), (4322, 19), (8707, 26)]
ESCALERA = [(3298, 11), (6055, 17)]
ORACULO = (2710, 32)
# zona: (aciertos con la nota correcta dada, pares)
ZONAS = [(18, 18), (22, 78), (21, 95)]

TXT = {
    "es": dict(
        slug="memoria-ruteo",
        d_tit="Con la nota correcta, la escalera gana; con el ruteo real, pierde",
        d_sub="% de preguntas cuya respuesta quedó dentro de lo leído, contra tokens leídos por pregunta",
        d_frag="Fragmentos sueltos (a la Mem0)",
        d_frag_k=["5", "10", "20", "40"],
        d_esc="Escalera con el ruteo real",
        d_esc_k=["1 nota", "2 notas"],
        d_ora="Escalera con la nota correcta dada",
        d_eje="tokens leídos por pregunta",
        mil=lambda v: f"{v / 1000:.0f} mil",
        z_tit="Lo vigente se encuentra; la historia, no",
        z_sub="Acierto con la nota correcta dada, según dónde estaba la respuesta",
        z_filas=["Estado vigente", "Cuerpo de la nota", "Historia fechada"],
        z_de="de",
        z_nota="La mitad de las respuestas (95 de 191) estaba en la historia.",
    ),
    "en": dict(
        slug="memory-routing",
        d_tit="Given the right note, the ladder wins; with real routing, it loses",
        d_sub="% of questions whose answer ended up inside what was read, against tokens read per question",
        d_frag="Loose fragments (Mem0-style)",
        d_frag_k=["5", "10", "20", "40"],
        d_esc="Ladder with real routing",
        d_esc_k=["1 note", "2 notes"],
        d_ora="Ladder given the right note",
        d_eje="tokens read per question",
        mil=lambda v: f"{v / 1000:.0f}k",
        z_tit="The current state is found; the history is not",
        z_sub="Recall given the right note, by where the answer was",
        z_filas=["Current state", "Body of the note", "Dated history"],
        z_de="of",
        z_nota="Half of the answers (95 of 191) were in the history.",
    ),
}


def dispersion(t, L, idioma, destino):
    c = Lienzo(t, 5.0, 110, L["d_tit"], L["d_sub"], abajo=110, der=60)
    ax = c.ax
    ax.set_xlim(0, 10000); ax.set_ylim(0, 37)
    ax.set_yticks([0, 10, 20, 30]); ax.set_yticklabels([num(v, idioma, 0) for v in (0, 10, 20, 30)])
    ax.set_xticks([0, 2000, 4000, 6000, 8000, 10000])
    ax.set_xticklabels(["0"] + [L["mil"](v) for v in (2000, 4000, 6000, 8000, 10000)])
    ax.set_xlabel(L["d_eje"], color=t["suave"], fontsize=10, labelpad=10)
    ax.tick_params(axis="y", colors=t["suave"]); ax.tick_params(axis="x", colors=t["suave"])
    for y in (10, 20, 30):
        ax.axhline(y, color=t["linea"], lw=0.8, zorder=0)
    ax.axhline(0, color=t["suave"], lw=0.9)

    xs, ys = zip(*FRAGMENTOS)
    ax.plot(xs, ys, color=t["neutro"], lw=2, zorder=2)
    ax.plot(xs, ys, "o", ms=8, color=t["neutro"], mec=t["sup"], mew=2, zorder=3)
    for (x, y), k in zip(FRAGMENTOS, L["d_frag_k"]):
        c.texto(x, y - 2.6, f"top-{k}", ha="center", va="top", color=t["suave"], fontsize=9.5)
    c.texto(8707, 26 + 1.8, L["d_frag"], ha="right", va="bottom", color=t["suave"], fontsize=10)

    esc = mezclar(t["acento"], t["sup"], 0.45)
    xs, ys = zip(*ESCALERA)
    ax.plot(xs, ys, color=esc, lw=2, zorder=2)
    ax.plot(xs, ys, "o", ms=8, color=esc, mec=t["sup"], mew=2, zorder=3)
    for (x, y), k in zip(ESCALERA, L["d_esc_k"]):
        c.texto(x + 180, y - 0.4, f"{num(y, idioma, 0)}  ·  {k}", ha="left", va="top", fontsize=9.5)
    c.texto(6055 + 180, 17 + 1.4, L["d_esc"], ha="left", va="bottom", color=t["suave"], fontsize=10)

    x, y = ORACULO
    ax.plot([x], [y], "o", ms=11, color=t["acento"], mec=t["sup"], mew=2, zorder=4)
    c.texto(x + 260, y, f"{num(y, idioma, 0)}  ·  {L['d_ora']}", ha="left", va="center",
            fontweight="semibold")
    c.guardar(destino)


def zonas(t, L, idioma, destino):
    izq = 56 + ancho_etiquetas(L["z_filas"]) + 28
    c = Lienzo(t, 3.6, izq, L["z_tit"], L["z_sub"], nota=L["z_nota"], abajo=80, der=150)
    ax = c.ax
    n = len(ZONAS)
    ax.set_xlim(0, 128); ax.set_ylim(n - 0.45, -0.55)
    ax.set_xticks([]); ax.set_yticks(range(n)); ax.set_yticklabels(L["z_filas"])
    for i, (a, tot) in enumerate(ZONAS):
        v = 100.0 * a / tot
        c.barra(0, v, i, 0.52, t["acento"] if i == 0 else t["neutro"])
        c.texto(v + 1.2, i, f"{num(v, idioma, 0)}   ({a} {L['z_de']} {tot})", va="center",
                fontweight="semibold" if i == 0 else "normal")
    ax.axvline(0, color=t["suave"], lw=0.9)
    c.guardar(destino)


def main():
    hechos = []
    for idioma, L in TXT.items():
        img = RAIZ / "articulos" / L["slug"] / "img"
        img.mkdir(parents=True, exist_ok=True)
        for tema, t in TEMAS.items():
            suf = "" if tema == "claro" else "-oscuro"
            for nombre, fn in (("acierto", dispersion), ("zonas", zonas)):
                p = img / f"{nombre}{suf}.png"
                fn(t, L, idioma, p)
                hechos.append(p)
    for p in hechos:
        print(p.relative_to(RAIZ))


if __name__ == "__main__":
    main()

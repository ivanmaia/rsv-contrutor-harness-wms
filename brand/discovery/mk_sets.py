"""Gera o sets.json da marca Discovery: a Pilha de Lançamento (fonte editável do conjunto A)."""
import json
from pathlib import Path

AQUI = Path(__file__).parent


def font(fam, w, loc, tr=0):
    return {"family": fam, "source": "google", "license": "OFL-1.1", "weights": w, "location": loc,
            "features": [], "case": "as-is", "tracking": tr, "fallback": "system-ui, sans-serif", "file": None}


def brand(i, name, hx, usage):
    return {"id": f"brand-{i}", "name": name, "hex": hx, "source": "chosen", "locked": True, "usage": usage,
            "print": None}


# A pilha de lançamento simplificada: orbitador à frente do tanque externo e dos dois foguetes laterais.
# O nariz do orbitador é curvo e da cor do corpo (ponta colorida e arredondada dava leitura indesejada);
# as pontas do tanque e dos foguetes são agudas. Uma folga separa o orbitador das peças de trás.


def _quad(p0, c, p1, n=8):
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u * u * p1[0],
             (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u * u * p1[1]) for u in (i / n for i in range(n + 1))]


def _espelho(lado_esq, cx=50):
    """Polígono simétrico a partir do contorno esquerdo (de baixo para cima até o eixo)."""
    return lado_esq + [(2 * cx - x, y) for x, y in reversed(lado_esq[1:-1])]


def _desloca(pts, d):
    """Contorno deslocado para fora por d (junta em quina), para abrir a folga entre as peças."""
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sinal = 1 if area > 0 else -1
    saida = []
    for i in range(n):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[(i + 1) % n]
        def normal(ax, ay, bx, by):
            dx, dy = bx - ax, by - ay
            L = (dx * dx + dy * dy) ** 0.5
            return (sinal * dy / L, -sinal * dx / L)
        n1, n2 = normal(x0, y0, x1, y1), normal(x1, y1, x2, y2)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]
        cos = max(0.35, (1 + n1[0] * n2[0] + n1[1] * n2[1]) / 2) ** 0.5
        L = (bx * bx + by * by) ** 0.5 or 1
        saida.append((x1 + bx / L * d / cos, y1 + by / L * d / cos))
    return saida


def _d(pts):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"


_ORBITADOR = _espelho([(50, 96), (44, 96), (43, 90), (16, 90), (16, 84), (43, 58), (43, 42)]
                      + _quad((43, 42), (43, 30.5), (50, 29.5), n=10)[1:])
_TANQUE = _espelho([(50, 88), (38, 88), (38, 34)] + _quad((38, 34), (38, 16), (50, 4))[1:])
_SRB_E = [(22, 92), (31, 92), (31, 28), (26.5, 15), (22, 28)]
_SRB_D = [(100 - x, y) for x, y in reversed(_SRB_E)]
_FOLGA = _d(_desloca(_ORBITADOR, 2.6))


def _simbolo(cor_tanque="brand-2", cor_foguetes="brand-3"):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            f'<g id="tank" data-color="{cor_tanque}"><path id="external-tank" d="{_d(_TANQUE)}"/>'
            f'<path id="tank-gap" d="{_FOLGA}" data-op="subtract"/></g>'
            f'<g id="boosters" data-color="{cor_foguetes}"><path id="booster-left" d="{_d(_SRB_E)}"/>'
            f'<path id="booster-right" d="{_d(_SRB_D)}"/>'
            f'<path id="booster-gap" d="{_FOLGA}" data-op="subtract"/></g>'
            f'<g id="orbiter" data-color="text"><path id="orbiter-shape" d="{_d(_ORBITADOR)}"/></g></svg>')


# Usos incorretos próprios desta marca (desenhados a partir do master do símbolo)
MISUSE = {"misuse-1": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path id="external-tank" data-color="brand-2" data-parts="external-tank" d="M62 59.201L59.6 56.89L59.6 41.96L59.53 39.63L59.29 37.43L58.89 35.4L58.31 33.54L57.52 31.84L56.51 30.33L55.26 29.05L53.79 28.04L52.14 27.32L50 26.83L47.86 27.32L46.21 28.04L44.74 29.05L43.49 30.33L42.48 31.84L41.69 33.54L41.11 35.4L40.71 37.43L40.47 39.63L40.4 41.96L40.4 56.89L38 59.201L38 34L38.19 29.59L38.75 25.38L39.69 21.34L41 17.5L42.69 13.84L44.75 10.38L47.19 7.09L50 4L52.81 7.09L55.25 10.38L57.31 13.84L59 17.5L60.31 21.34L61.25 25.38L61.81 29.59L62 34Z"/><path id="part-brand-3" data-color="brand-3" data-parts="booster-left booster-right" d="M78 28L78 74.609L69 65.942L69 28L73.5 15ZM22 74.609L22 28L26.5 15L31 28L31 65.942Z"/><path id="orbiter-shape" data-color="text" data-parts="orbiter-shape" d="M44 96L43 90L16 90L16 84L43 58L43 42L43.07 39.81L43.28 37.82L43.63 36.05L44.12 34.48L44.75 33.12L45.52 31.98L46.43 31.05L47.48 30.32L48.67 29.81L50 29.5L51.33 29.81L52.52 30.32L53.57 31.05L54.48 31.98L55.25 33.12L55.88 34.48L56.37 36.05L56.72 37.82L56.93 39.81L57 42L57 58L84 84L84 90L57 90L56 96Z"/><path id="nose-painted" data-color="brand-2" d="M43 42 L43.07 39.81 L43.28 37.82 L43.63 36.05 L44.12 34.48 L44.75 33.12 L45.52 31.98 L46.43 31.05 L47.48 30.32 L48.67 29.81 L50 29.5 L51.33 29.81 L52.52 30.32 L53.57 31.05 L54.48 31.98 L55.25 33.12 L55.88 34.48 L56.37 36.05 L56.72 37.82 L56.93 39.81 L57 42Z"/></svg>',
             "misuse-2": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path id="external-tank" data-color="brand-3" data-parts="external-tank" d="M62 59.201L59.6 56.89L59.6 41.96L59.53 39.63L59.29 37.43L58.89 35.4L58.31 33.54L57.52 31.84L56.51 30.33L55.26 29.05L53.79 28.04L52.14 27.32L50 26.83L47.86 27.32L46.21 28.04L44.74 29.05L43.49 30.33L42.48 31.84L41.69 33.54L41.11 35.4L40.71 37.43L40.47 39.63L40.4 41.96L40.4 56.89L38 59.201L38 34L38.19 29.59L38.75 25.38L39.69 21.34L41 17.5L42.69 13.84L44.75 10.38L47.19 7.09L50 4L52.81 7.09L55.25 10.38L57.31 13.84L59 17.5L60.31 21.34L61.25 25.38L61.81 29.59L62 34Z"/><path id="part-brand-3" data-color="brand-2" data-parts="booster-left booster-right" d="M78 28L78 74.609L69 65.942L69 28L73.5 15ZM22 74.609L22 28L26.5 15L31 28L31 65.942Z"/><path id="orbiter-shape" data-color="text" data-parts="orbiter-shape" d="M44 96L43 90L16 90L16 84L43 58L43 42L43.07 39.81L43.28 37.82L43.63 36.05L44.12 34.48L44.75 33.12L45.52 31.98L46.43 31.05L47.48 30.32L48.67 29.81L50 29.5L51.33 29.81L52.52 30.32L53.57 31.05L54.48 31.98L55.25 33.12L55.88 34.48L56.37 36.05L56.72 37.82L56.93 39.81L57 42L57 58L84 84L84 90L57 90L56 96Z"/></svg>'}

CONJUNTO = {
    "identity": {
        "set": {"id": "A", "name": "Pilha de Lançamento", "recommended": True,
                "mechanism": "A pilha de lançamento do ônibus espacial em quatro peças: orbitador em grafite, "
                             "tanque externo em Laranja Internacional e foguetes laterais em Azul Cobalto.",
                "expression_move": "O tanque laranja atrás do orbitador: a única cor quente do símbolo.",
                "differs_by": "Nenhuma ferramenta de dev usada pelo time tem um símbolo figurativo; o laranja é de "
                              "sinalização, não o terracota do Claude Code, e o azul é cobalto, não o azul médio do "
                              "Azure DevOps."},
        "axes": {"classic_contemporary": -1, "quiet_loud": 0, "playful_serious": 1, "warm_cool": 0},
        "type": {"pairing_mode": "single-family",
                 "display": font("Hanken Grotesk", [800], {"wght": 800}, tr=-10),
                 "text": font("Hanken Grotesk", [400, 600], {"wght": 400}), "mono": None},
        "logo": {"type": "symbol+wordmark",
                 "concept": "A pilha de lançamento simplificada: orbitador, tanque externo e os dois foguetes "
                            "laterais.",
                 "symbol": "logo/symbol.svg",
                 "wordmark": {"text": "Discovery", "role": "display", "location": None, "tracking": -10,
                              "case": "as-is"},
                 "monogram": None, "lockups": ["horizontal", "stacked"],
                 "colors": {"orbiter-shape": "text", "boosters": "brand-3", "external-tank": "brand-2",
                            "wordmark": "text"},
                 "tags": ["literal-object"],
                 "defect": "A ponta colorida e arredondada do nariz dava leitura indesejada: a cor passou para o "
                           "tanque inteiro e o nariz virou curva suave na cor do corpo.",
                 "clear_space": {"unit": "cap-height", "multiple": 1, "inferred": True},
                 "min_size": {"px": 24, "mm": 8},
                 "misuse": [{"do": "stretch"}, {"do": "rotate"}, {"do": "effects"}, {"do": "crowd"},
                            {"svg": "logo/misuse-1.svg", "label": "Não pinte o nariz do orbitador"},
                            {"svg": "logo/misuse-2.svg", "label": "Não troque as cores do tanque e dos foguetes"}]},
        "palette_build": {"strategy": None, "accent": None, "light_bg": "#eef0ef", "dark_bg": None,
                          "neutral_tint": None, "neutral_chroma": None, "extra": []},
        "defaults_used": [{"id": "logo-literal-object",
                           "why": "Pedido explícito do usuário: o nome vem do ônibus espacial e ele quer a nave no "
                                  "logo. O ônibus é o único veículo espacial que pousava numa pista, o que sustenta "
                                  "a leitura de toda missão volta pra casa."}],
        "rationale": [
            {"claim": "O ônibus espacial era o único que voltava pousando como avião numa pista, e era reutilizável.",
             "evidence": "practice", "source": "história do programa"},
            {"claim": "Logo descritivo ajuda marca nova e interna a ser lembrada; custa distinção.",
             "evidence": "limited", "source": "references/logo.md (Luffarelli 2019)"},
            {"claim": "A silhueta é genérica do veículo; nada de insígnia, logotipo ou letreiro da NASA.",
             "evidence": "judgement", "source": "designer"}]},
    "palette": {"schema": "brand-identity/palette@1", "name": "Pilha de Lançamento",
                "direction": "Grafite de cabine para texto e símbolo, Laranja Internacional para o tanque e os "
                             "destaques da interface, Azul Cobalto para os foguetes laterais e gráficos.",
                "brand": [brand(1, "Grafite de Cabine", "#1a1d22", "o orbitador, o nome, texto e títulos"),
                          brand(2, "Laranja Internacional", "#ff4f00",
                                "o tanque externo do logo, destaques da interface e chamadas para ação"),
                          brand(3, "Azul Cobalto", "#2350a8",
                                "os dois foguetes laterais do logo; ilustrações e gráficos")],
                "feels": ["preciso", "calmo", "checado"]},
    "symbol_svg": _simbolo(), "symbol_small_svg": None, "wordmark_detail_svg": None,
    "misuse_svgs": MISUSE,
}

(AQUI / "sets.json").write_text(json.dumps({"schema": "brand-identity/sets@1", "sets": [CONJUNTO]},
                                           ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")

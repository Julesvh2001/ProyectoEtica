"""
Módulo: Comparador Físico y Pases entre Líneas
----------------------------------------------
Se usa desde analisisdetallado.py:
    import centrales_lineas
    centrales_lineas.render()
Sube un CSV/XLSX con el formato de "centrales_eredivisie.csv".
"""

import inspect
import io
import math
import re
import unicodedata

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# Compatibilidad entre versiones de Streamlit:
# las nuevas usan width="stretch", las antiguas use_container_width=True
if "width" in inspect.signature(st.plotly_chart).parameters:
    PLOT_FULL = {"width": "stretch"}
else:
    PLOT_FULL = {"use_container_width": True}


def show_table(data):
    try:
        st.dataframe(data, width="stretch", hide_index=True)
    except TypeError:
        st.dataframe(data, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# Configuración de variables
# key = nombre de columna en el archivo (se compara de forma flexible)
# ----------------------------------------------------------------------------
PHYSICAL_VARS = [
    ("Total Distance (m)", "Distancia total (m)"),
    ("Meters/Min", "Metros por minuto"),
    ("Running Distance (15–20 km/h)", "Distancia a 15–20 km/h (m)"),
    ("High Intensity Distance (+20 km/h)", "Distancia alta intensidad +20 km/h (m)"),
    ("High Speed Running Distance (20–25 km/h)", "Distancia a 20–25 km/h (m)"),
    ("Sprinting Distance (+25 km/h)", "Distancia en sprint +25 km/h (m)"),
    ("Count High Intensity Efforts (+20 km/h)", "Esfuerzos alta intensidad +20 km/h"),
    ("Count High Speed Running (20–25 km/h)", "Carreras a 20–25 km/h"),
    ("Count Sprint (+25 km/h)", "Sprints +25 km/h"),
    ("Count High Acceleration (+3 m/s²)", "Aceleraciones altas (+3 m/s²)"),
    ("Count High Deceleration (−3 m/s²)", "Desaceleraciones altas (−3 m/s²)"),
    ("Count Medium Acceleration (1.5–3 m/s²)", "Aceleraciones medias (1.5–3 m/s²)"),
    ("Count Medium Deceleration (−1.5 to −3 m/s²)", "Desaceleraciones medias (−1.5 a −3 m/s²)"),
    ("Repeatable Max Speed (avg of fastest 50% of matches)", "Velocidad máx. repetible (km/h)"),
]

LBP_VARS = [
    ("Line Breaking Passes Completed", "Pases entre líneas completados"),
    ("Line Breaking Passes/Pass%", "% de pases que rompen líneas"),
]

# Variables donde "menos es mejor" (ninguna por defecto; añade la columna aquí si hace falta)
LOWER_IS_BETTER: set[str] = set()

# Variables que vienen como fracción 0–1 y se muestran como %
AS_PERCENT = {"Line Breaking Passes/Pass%"}

# Paleta por percentil (rojo → verde), igual que el ejemplo
BINS = [
    (0, 20, "#E5533D"),    # rojo
    (20, 40, "#F0A58A"),   # salmón
    (40, 60, "#F2D94E"),   # amarillo
    (60, 80, "#7CB342"),   # verde claro
    (80, 101, "#4E7A27"),  # verde oscuro
]
HIGHLIGHT = "#111111"
COMPARE = "#2F6FDB"


def color_for_pct(p: float) -> str:
    for lo, hi, c in BINS:
        if lo <= p < hi:
            return c
    return BINS[-1][2]


# ----------------------------------------------------------------------------
# Carga y limpieza
# ----------------------------------------------------------------------------
def norm(s: str) -> str:
    """Normaliza un nombre de columna para compararlo sin depender de guiones/acentos."""
    s = str(s)
    for ch in ["–", "—", "−", "‐"]:
        s = s.replace(ch, "-")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9%+/.-]", "", s.lower())


@st.cache_data(show_spinner=False)
def load_file(data: bytes, name: str) -> pd.DataFrame:
    if name.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(data))
    else:
        df = None
        for enc in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(io.BytesIO(data), sep=None, engine="python", encoding=enc)
                break
            except UnicodeDecodeError:
                continue
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.select_dtypes(include=["object", "string"]).columns:
        df[c] = df[c].astype(str).str.strip().replace({"nan": np.nan, "": np.nan})
    return df


def resolve_columns(df: pd.DataFrame, spec):
    """Devuelve [(columna_real, etiqueta, clave_spec)] para las columnas que existan."""
    lookup = {norm(c): c for c in df.columns}
    out = []
    for key, label in spec:
        real = lookup.get(norm(key))
        if real is not None:
            out.append((real, label, key))
    return out


def find_col(df, *candidates):
    lookup = {norm(c): c for c in df.columns}
    for c in candidates:
        if norm(c) in lookup:
            return lookup[norm(c)]
    return None


# ----------------------------------------------------------------------------
# Cálculos
# ----------------------------------------------------------------------------
def percentiles(df: pd.DataFrame, cols) -> pd.DataFrame:
    pct = pd.DataFrame(index=df.index)
    for real, _, key in cols:
        s = pd.to_numeric(df[real], errors="coerce")
        p = s.rank(pct=True, method="average") * 100
        if key in LOWER_IS_BETTER:
            p = 100 - p + (100 / s.notna().sum())
        pct[real] = p
    return pct


def ranking(df, pct, cols, player_col):
    score = pct[[c for c, _, _ in cols]].mean(axis=1)
    r = pd.DataFrame({"Jugador": df[player_col], "Puntuación": score.round(1)})
    if "team" in df.attrs:
        r["Equipo"] = df[df.attrs["team"]]
    r = r.dropna(subset=["Puntuación"]).sort_values("Puntuación", ascending=False)
    r.insert(0, "#", range(1, len(r) + 1))
    return r.reset_index(drop=True)


def beeswarm_y(x: np.ndarray, width_px: float = 1000, r_px: float = 7.5) -> np.ndarray:
    """Coloca los puntos en un enjambre (beeswarm) sin solaparse. Devuelve offsets Y en px."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    y = np.zeros(n)
    if n == 0:
        return y
    lo, hi = np.nanmin(x), np.nanmax(x)
    span = (hi - lo) or 1.0
    px = (x - lo) / span * width_px
    order = np.argsort(px)
    placed = []  # (x_px, y_px)
    d = 2 * r_px
    for i in order:
        xi = px[i]
        near = [(xp, yp) for xp, yp in placed if abs(xp - xi) < d]
        k = 0
        while True:
            # 0, +1, -1, +2, -2 ...
            step = (k + 1) // 2 * (1 if k % 2 == 1 else -1)
            cand = step * d * 0.9
            if all(math.hypot(xi - xp, cand - yp) >= d * 0.95 for xp, yp in near):
                y[i] = cand
                placed.append((xi, cand))
                break
            k += 1
    return y


def fmt(v, key):
    if pd.isna(v):
        return "–"
    if key in AS_PERCENT:
        return f"{v * 100:.1f}%"
    if abs(v) >= 100:
        return f"{v:,.0f}"
    return f"{v:.2f}" if abs(v) < 10 else f"{v:.1f}"


# ----------------------------------------------------------------------------
# Gráficos
# ----------------------------------------------------------------------------
def strip_chart(df, pct, real, label, key, player_col, team_col, sel_idx, cmp_idx=None):
    s = pd.to_numeric(df[real], errors="coerce")
    mask = s.notna()
    vals = s[mask]
    idx = vals.index
    disp = vals * 100 if key in AS_PERCENT else vals
    yoff = beeswarm_y(disp.values)
    colors = [color_for_pct(p) for p in pct.loc[idx, real]]
    mean = disp.mean()

    hover = [
        f"<b>{df.at[i, player_col]}</b>"
        + (f"<br>{df.at[i, team_col]}" if team_col else "")
        + f"<br>{label}: {fmt(vals[i], key)}<br>Percentil: {pct.at[i, real]:.0f}"
        for i in idx
    ]

    fig = go.Figure()
    others = [k for k, i in enumerate(idx) if i not in (sel_idx, cmp_idx)]
    fig.add_trace(go.Scatter(
        x=disp.values[others], y=yoff[others], mode="markers",
        marker=dict(size=13, color=[colors[k] for k in others], line=dict(color="white", width=1.5)),
        hovertext=[hover[k] for k in others], hoverinfo="text", showlegend=False,
    ))

    # Línea de la media de la competición
    fig.add_vline(x=mean, line=dict(color="rgba(128,128,128,0.9)", width=1.5, dash="dash"))
    fig.add_annotation(x=mean, y=1, yref="paper", text=f"Media liga: {fmt(mean / 100 if key in AS_PERCENT else mean, key)}",
                       showarrow=False, yanchor="bottom", font=dict(size=11), opacity=0.75)

    for target, col, size in [(cmp_idx, COMPARE, 20), (sel_idx, HIGHLIGHT, 24)]:
        if target is not None and target in idx:
            k = list(idx).index(target)
            fig.add_trace(go.Scatter(
                x=[disp.values[k]], y=[yoff[k]], mode="markers",
                marker=dict(size=size, color=col, line=dict(color="white", width=2)),
                hovertext=[hover[k]], hoverinfo="text", showlegend=False,
            ))

    ymax = max(40, np.abs(yoff).max() + 18)
    lo, hi = disp.min(), disp.max()
    pad = (hi - lo) * 0.04 or 1
    fig.update_layout(
        height=int(110 + ymax * 1.1),
        margin=dict(l=10, r=10, t=28, b=35),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[lo - pad, hi + pad], showgrid=False, zeroline=False, automargin=True,
                   showline=True, linecolor="rgba(128,128,128,0.8)", ticks="outside", tickfont=dict(size=12)),
        yaxis=dict(range=[-ymax, ymax], visible=False),
        hoverlabel=dict(bgcolor="white"),
    )
    return fig


def gauge_chart(rank_df, player_name, title):
    """Medidor semicircular con la posición del jugador en el ranking."""
    n = len(rank_df)
    r = rank_df[rank_df["Jugador"] == player_name].iloc[0]
    pos = int(r["#"])
    fill = (n - pos) / (n - 1) * 100 if n > 1 else 100   # percentil de posición
    top = math.ceil(pos / n * 100)
    fig = go.Figure(go.Indicator(
        mode="gauge", value=fill,
        domain=dict(x=[0, 1], y=[0.18, 1]),
        gauge=dict(
            shape="angular",
            axis=dict(range=[0, 100], visible=False),
            bar=dict(color=color_for_pct(fill), thickness=1),
            bgcolor="rgba(200,200,200,0.35)",
            borderwidth=0,
        ),
    ))
    fig.add_annotation(x=0.5, y=0.2, xref="paper", yref="paper", showarrow=False,
                       text=f"<b>Top {top}%</b>", font=dict(size=30))
    fig.add_annotation(x=0.5, y=0.02, xref="paper", yref="paper", showarrow=False,
                       text=f"Puntuación: {r['Puntuación']:.0f}/100 | Ranking {pos}/{n}",
                       font=dict(size=13), opacity=0.75)
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center", font=dict(size=16)),
        height=290, margin=dict(l=30, r=30, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ----------------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------------
def render():
    st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem;}
    .var-title {font-size: 1.15rem; font-weight: 700; margin: 0.6rem 0 0 0;}
    .var-sub {opacity: 0.7; font-size: 0.9rem; margin-bottom: -0.4rem;}
    </style>
    """, unsafe_allow_html=True)

    st.title("Comparador Físico y Pases entre Líneas")

    with st.sidebar:
        st.markdown("---")
        st.subheader("Archivo")
        up = st.file_uploader("Sube tu archivo (CSV o Excel)", type=["csv", "xlsx", "xls"], key="cl_upload")

    if up is None:
        st.info("Sube un archivo CSV o Excel desde la barra lateral para empezar. "
                "Debe tener una columna **Player** y las métricas físicas / de pases entre líneas.")
        return

    df = load_file(up.getvalue(), up.name)

    player_col = find_col(df, "Player", "Jugador", "Nickname")
    team_col = find_col(df, "Current Team", "Team", "Equipo")
    min_col = find_col(df, "Minutes", "Minutos")
    age_col = find_col(df, "Age", "Edad")
    height_col = find_col(df, "Height", "Altura")
    foot_col = find_col(df, "Preferred Foot", "Pie")

    if player_col is None:
        st.error("No encontré la columna de jugador (Player).")
        return

    phys_cols = resolve_columns(df, PHYSICAL_VARS)
    lbp_cols = resolve_columns(df, LBP_VARS)
    if not phys_cols and not lbp_cols:
        st.error("No encontré ninguna de las métricas esperadas en el archivo.")
        return

    with st.sidebar:
        st.subheader("Filtros")
        if min_col:
            mins = pd.to_numeric(df[min_col], errors="coerce")
            max_m = int(np.nanmax(mins))
            min_minutes = st.slider("Minutos mínimos jugados", 0, max_m, 0, step=50, key="cl_min")
            df = df[mins >= min_minutes]
        if age_col:
            ages = pd.to_numeric(df[age_col], errors="coerce")
            a_lo, a_hi = int(np.nanmin(ages)), int(np.nanmax(ages))
            if a_lo < a_hi:
                age_rng = st.slider("Edad", a_lo, a_hi, (a_lo, a_hi), key="cl_edad")
                df = df[ages.between(*age_rng) | ages.isna()]
        df = df.reset_index(drop=True)
        st.caption(f"{len(df)} jugadores en la muestra")

    if len(df) < 2:
        st.warning("Hay muy pocos jugadores con estos filtros.")
        return

    if team_col:
        df.attrs["team"] = team_col

    # Buscador de jugador
    names = sorted(df[player_col].dropna().unique().tolist())
    c1, c2 = st.columns([2, 2])
    with c1:
        player = st.selectbox("🔎 Buscar jugador", names, index=0, placeholder="Escribe un nombre…", key="cl_player")
    with c2:
        compare = st.selectbox("Comparar con (opcional)", ["—"] + [n for n in names if n != player], key="cl_compare")
    compare = None if compare == "—" else compare

    sel_idx = df.index[df[player_col] == player][0]
    cmp_idx = df.index[df[player_col] == compare][0] if compare else None

    all_cols = phys_cols + lbp_cols
    pct = percentiles(df, all_cols)
    rank_phys = ranking(df, pct, phys_cols, player_col) if phys_cols else None
    rank_lbp = ranking(df, pct, lbp_cols, player_col) if lbp_cols else None

    # Ficha del jugador
    row = df.loc[sel_idx]
    info = []
    if team_col: info.append(str(row[team_col]))
    if age_col and pd.notna(row[age_col]): info.append(f"{int(float(row[age_col]))} años")
    if height_col and pd.notna(row[height_col]): info.append(f"{int(float(row[height_col]))} cm")
    if foot_col and pd.notna(row[foot_col]): info.append(f"Pie: {row[foot_col]}")
    if min_col: info.append(f"{float(row[min_col]):,.0f} min")
    st.subheader(player)
    st.caption(" · ".join(info))


    g1, g2 = st.columns(2)
    if rank_phys is not None:
        g1.plotly_chart(gauge_chart(rank_phys, player, "Ranking físico"), **PLOT_FULL,
                        config={"displayModeBar": False})
    if rank_lbp is not None:
        g2.plotly_chart(gauge_chart(rank_lbp, player, "Ranking pases entre líneas"), **PLOT_FULL,
                        config={"displayModeBar": False})
    if compare:
        bits = []
        for lab, rdf in [("físico", rank_phys), ("pases entre líneas", rank_lbp)]:
            if rdf is not None:
                rc = rdf[rdf["Jugador"] == compare].iloc[0]
                bits.append(f"{lab} #{int(rc['#'])}/{len(rdf)}")
        st.caption(f"🔵 {compare}: " + " · ".join(bits))
    st.caption("Puntuación = media de los percentiles del jugador en las variables del bloque, "
               "frente a la muestra filtrada.")

    tab_phys, tab_lbp, tab_data = st.tabs(["🏃 Variables físicas", "🎯 Pases entre líneas", "📋 Datos"])


    def legend_html():
        items = "".join(
            f"<span style='display:inline-flex;align-items:center;margin-right:14px'>"
            f"<span style='width:12px;height:12px;border-radius:50%;background:{c};display:inline-block;margin-right:5px'></span>"
            f"{lab}</span>"
            for c, lab in [(BINS[4][2], "Top 20%"), (BINS[3][2], "60–80"), (BINS[2][2], "40–60"),
                           (BINS[1][2], "20–40"), (BINS[0][2], "Bottom 20%"), (HIGHLIGHT, player)]
            + ([(COMPARE, compare)] if compare else [])
        )
        st.markdown(f"<div style='font-size:0.85rem;opacity:0.85'>{items} · "
                    f"<span>- - - media de la competición</span></div>",
                    unsafe_allow_html=True)


    def render_vars(cols):
        legend_html()
        for real, label, key in cols:
            v = df.at[sel_idx, real]
            p = pct.at[sel_idx, real]
            sub = f"{player}: <b>{fmt(v, key)}</b> · percentil {p:.0f}" if pd.notna(p) else f"{player}: sin dato"
            if cmp_idx is not None and pd.notna(pct.at[cmp_idx, real]):
                sub += f" &nbsp;|&nbsp; {compare}: <b>{fmt(df.at[cmp_idx, real], key)}</b> · percentil {pct.at[cmp_idx, real]:.0f}"
            st.markdown(f"<div class='var-title'>{label}</div><div class='var-sub'>{sub}</div>",
                        unsafe_allow_html=True)
            st.plotly_chart(
                strip_chart(df, pct, real, label, key, player_col, team_col, sel_idx, cmp_idx),
                **PLOT_FULL, config={"displayModeBar": False},
            )


    with tab_phys:
        if phys_cols:
            render_vars(phys_cols)
        else:
            st.info("No hay variables físicas en el archivo.")

    with tab_lbp:
        if lbp_cols:
            render_vars(lbp_cols)
        else:
            st.info("No hay variables de pases entre líneas en el archivo.")

    with tab_data:
        show = [c for c in [player_col, team_col, min_col, age_col, height_col] if c] + [c for c, _, _ in all_cols]
        show_table(df[show])
        out = df[[player_col]].copy()
        if rank_phys is not None:
            out = out.merge(rank_phys[["Jugador", "#", "Puntuación"]].rename(
                columns={"Jugador": player_col, "#": "Rank físico", "Puntuación": "Punt. físico"}), on=player_col)
        if rank_lbp is not None:
            out = out.merge(rank_lbp[["Jugador", "#", "Puntuación"]].rename(
                columns={"Jugador": player_col, "#": "Rank pases entre líneas", "Puntuación": "Punt. pases entre líneas"}), on=player_col)
        st.download_button("⬇️ Descargar rankings (CSV)", out.to_csv(index=False).encode("utf-8"),
                           "rankings.csv", "text/csv", key="cl_download")

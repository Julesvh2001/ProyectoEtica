import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from xlwings import Sheet
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import altair as alt
import altair as alt  # dejar este import arriba en tu script


def scatter_interactivo_altair(
    df,
    x,
    y,
    size_col="Minutes",
    tooltip_cols=("Name","Team","Primary Position","Age","Nationality","Minutes"),
    color_sel="#f9ae34",   # color para resaltados
    color_base="#C5C5C5",  # color base
    highlight_names=None,  # lista de jugadores a resaltar desde un multiselect
):
    import pandas as pd
    import altair as alt
    import streamlit as st

    df = df.copy()

    # Marcamos los jugadores resaltados por lista
    highlight_names = set(highlight_names or [])
    df["is_highlight"] = df["Name"].isin(highlight_names)

    # Estilos
    _axis_col = "#2B2B2B"
    _mean_col = "#9A9A9A"
    _bg       = "transparent"

    # Promedios
    x_mean = float(df[x].mean())
    y_mean = float(df[y].mean())

    # Selección por clic (multi)
    sel = alt.selection_multi(
        fields=["Name", "Team"],
        on="click",
        clear="dblclick",
        empty="none"
    )

    # Base chart
    base_chart = alt.Chart(df).encode(
        x=alt.X(x, title=x, axis=alt.Axis(format=",.0f")),
        y=alt.Y(y, title=y, axis=alt.Axis(format=",.0f")),
        tooltip=[c for c in tooltip_cols if c in df.columns]
    )

    # Tamaño
    if size_col in df.columns:
        size_enc = alt.Size(size_col, legend=None, scale=alt.Scale(range=[30, 500]))
    else:
        size_enc = alt.value(120)

    # 1) Base gris
    pts_base = base_chart.mark_circle().encode(
        size=size_enc,
        color=alt.value(color_base),
        opacity=alt.value(0.35)
    )

    # 2) Resaltados por multiselect (lista)
    pts_list = base_chart.transform_filter(
        alt.datum.is_highlight
    ).mark_circle().encode(
        size=size_enc,
        color=alt.value(color_sel),
        opacity=alt.value(1.0)
    )

    # 3) Resaltados por clic (selección)
    pts_click = base_chart.mark_circle().encode(
        size=size_enc,
        color=alt.value(color_sel),
        opacity=alt.value(1.0)
    ).add_selection(sel).transform_filter(sel)

    # Labels por lista
    labels_list = base_chart.transform_filter(
        alt.datum.is_highlight
    ).mark_text(
        dx=6, dy=-6, fontWeight="bold", color="#000000", clip=False
    ).encode(text="Name")

    # Labels por clic
    labels_click = base_chart.transform_filter(
        sel
    ).mark_text(
        dx=6, dy=-6, fontWeight="bold", color="#000000", clip=False
    ).encode(text="Name")

    # Líneas de promedio
    vline = alt.Chart(pd.DataFrame({"v": [x_mean]})).mark_rule(
        strokeDash=[5, 5], color=_mean_col, opacity=0.8
    ).encode(x="v:Q")

    hline = alt.Chart(pd.DataFrame({"h": [y_mean]})).mark_rule(
        strokeDash=[5, 5], color=_mean_col, opacity=0.8
    ).encode(y="h:Q")

    chart = (
        pts_base
        + pts_list
        + pts_click
        + labels_list
        + labels_click
        + vline
        + hline
    ).properties(
        height=520,
        background=_bg,
        padding={"left": 10, "right": 160, "top": 40, "bottom": 30}
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        grid=False,
        domain=False,
        tickColor=_axis_col,
        labelColor=_axis_col,
        titleColor=_axis_col
    ).configure_title(
        color=_axis_col
    )

    st.altair_chart(chart, use_container_width=True, theme=None)





# Configuración inicial
st.set_page_config(page_title="Dashboard de Jugadores", layout="wide")

with st.sidebar:
    # Espacio visual arriba
    st.markdown("<br>", unsafe_allow_html=True)

    # Imagen del logo más grande y centrada visualmente
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image("TigresDS.png", width=300)

    seleccion = option_menu(
        menu_title="Menú Principal",
        options=[
            "Perfil de Jugadores",
            "Radares Estadísticos",
            "Estadísticas Físicas",
            "Juego Bajo Presión",
            "Pases al Espacio",
            "Movimientos sin Balón",
            "Ligas Alternas",
            "Radares Ligas Alternas"
        ],
        icons=[
            "person-badge", "radar", "activity",
            "exclamation-triangle", "arrows-move", "shuffle", "globe", "radar"
        ],
        menu_icon="list",
        default_index=0,
        orientation="vertical",
        styles={
            "container": {
                "padding": "0",
                "background-color": "transparent"
            },
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "2px",
                "color": "#2B2B2B"       # <- más oscuro
            },
            "nav-link-selected": {
                "background-color": "#FAAF35",
                "font-weight": "bold",
                "color": "#000000"        # negro al estar seleccionado
            },
            "menu-title": {
                "color": "#2B2B2B",       # <- más oscuro para el título
                "font-size": "16px",
                "font-weight": "bold"
            }
        }
    )




##############################################################################################################
############################## Perfil de Jugadores ###########################################################
##############################################################################################################


if seleccion == "Perfil de Jugadores":
    st.markdown("<h3 style='margin-bottom: 15px; text-align: center;'>Perfil de Jugadores</h3>", unsafe_allow_html=True)

    st.sidebar.markdown("### Selecciona la Liga y Temporada")

    ligas_temporadas = {
        "Liga MX": ["2024/2025", "2025/2026"],
        "Liga Profesional, Argentina": ["2025"],
        "Jupiler Pro League, Bélgica": ["2024/2025", "2025/2026"],
        "Serie A, Brasil": ["2025"],
        "Primera División, Chile": ["2025"],
        "Primera A, Colombia": ["2025"],
        "Liga Pro, Ecuador": ["2025"],
        "Premier League, Inglaterra": ["2024/2025"],
        "Ligue 1, Francia": ["2024/2025"],
        "1. Bundesliga, Alemania": ["2024/2025"],
        "Serie A, Italia": ["2024/2025"],
        "Serie B, Italia": ["2024/2025"],
        "Eredivisie, Países Bajos": ["2024/2025"],
        "División Profesional, Paraguay": ["2025"],
        "Primeira Liga, Portugal": ["2024/2025", "2025/2026"],
        "Premier League, Rusia": ["2024/2025"],
        "Pro League, Arabia": ["2024/2025"],
        "La Liga, España": ["2024/2025", "2025/2026"],
        "La Liga 2, España": ["2024/2025", "2025/2026"],
        "Primera División, Uruguay": ["2025"],
        "MLS, Estados Unidos": ["2025"],


    }

    archivos_csv = {
        ("Liga MX", "2024/2025"): "ligamxp902425.csv",
        ("Liga MX", "2025/2026"): "ligamxp902526.csv",
        ("Liga Profesional, Argentina", "2025"): "argp902025.csv",
        ("Jupiler Pro League, Bélgica", "2024/2025"): "belp902425.csv",
        ("Jupiler Pro League, Bélgica", "2025/2026"): "belp902526.csv",
        ("Serie A, Brasil", "2025"): "brap902025.csv",
        ("Primera División, Chile", "2025"): "chip902025.csv",
        ("Primera A, Colombia", "2025"): "colp902025.csv",
        ("Liga Pro, Ecuador", "2025"): "ecup902025.csv",
        ("Premier League, Inglaterra", "2024/2025"): "engp902425.csv",
        ("Ligue 1, Francia", "2024/2025"): "frap902425.csv",
        ("1. Bundesliga, Alemania", "2024/2025"): "gerp902425.csv",
        ("Serie A, Italia", "2024/2025"): "ita1p902425.csv",
        ("Serie B, Italia", "2024/2025"): "seriebp902425.csv",
        ("Eredivisie, Países Bajos", "2024/2025"): "nedp902425.csv",
        ("División Profesional, Paraguay", "2025"): "parp902025.csv",
        ("Primeira Liga, Portugal", "2024/2025"): "porp902425.csv",
        ("Primeira Liga, Portugal", "2025/2026"): "porp902526.csv",
        ("Premier League, Rusia", "2024/2025"): "rusp902425.csv",
        ("Pro League, Arabia", "2024/2025"): "arap902425.csv",
        ("La Liga, España", "2024/2025"): "espp902425.csv",
        ("La Liga, España", "2025/2026"): "laligap902526.csv",
        ("La Liga 2, España", "2024/2025"): "esp2p902425.csv",
        ("La Liga 2, España", "2025/2026"): "laliga22526.csv",
        ("Primera División, Uruguay", "2025"): "urup902025.csv",
        ("MLS, Estados Unidos", "2025"): "mlsp902025.csv",
    }

    ligas_disponibles = list(ligas_temporadas.keys())
    liga_seleccionada = st.sidebar.selectbox("Liga", ligas_disponibles, index=0)
    temporadas_disponibles = ligas_temporadas[liga_seleccionada]
    temporada_seleccionada = st.sidebar.selectbox("Temporada", temporadas_disponibles, index=0)

    archivo = archivos_csv.get((liga_seleccionada, temporada_seleccionada))
    if archivo:
        df = pd.read_csv(archivo)
    else:
        st.error("No hay datos disponibles para esta combinación de liga y temporada.")
        st.stop()

    df["Competition"] = df["Competition"].astype(str).str.strip()

    # Mapeo de nombre visible a nombre real en la base de datos
    nombre_base_liga = {

        "Liga Profesional, Argentina": "Liga Profesional",
        "Jupiler Pro League, Bélgica": "Jupiler Pro League",
        "Primera División, Chile": "Primera División",
        "Primera A, Colombia": "Primera A",
        "Liga Pro, Ecuador": "Liga Pro",
        "Premier League, Inglaterra": "Premier League",
        "Ligue 1, Francia": "Ligue 1",
        "1. Bundesliga, Alemania": "1. Bundesliga",
        "Serie B, Italia": "Serie B",
        "Eredivisie, Países Bajos": "Eredivisie",
        "División Profesional, Paraguay": "División Profesional, Paraguay",
        "Primeira Liga, Portugal": "Primeira Liga",
        "Premier League, Rusia": "Premier League",
        "Pro League, Arabia": "Pro League",
        "La Liga, España": "La Liga",
        "La Liga 2, España": "La Liga 2",
        "Primera División, Uruguay": "Primera División",
        "MLS, Estados Unidos": "Major League Soccer",

    }.get(liga_seleccionada, liga_seleccionada)
    df["Season"] = df["Season"].astype(str).str.strip()
    df_filtrado = df[
        (df["Competition"] == str(nombre_base_liga)) &
        (df["Season"] == str(temporada_seleccionada))
    ].copy()

    if df_filtrado.empty:
        st.warning("No hay datos disponibles en la base para esta liga y temporada.")
        st.stop()

    st.sidebar.markdown("### Grupo de Posición")
    grupos_posicion = [
        "Porteros", "Centrales", "Carrileros/Laterales", "Contenciones",
        "Interiores", "Volantes Ofensivos", "Extremos", "Delanteros"
    ]
    grupo_seleccionado = st.sidebar.radio("Grupo", grupos_posicion)

    st.markdown(f"Has seleccionado: **{grupo_seleccionado}** en {liga_seleccionada} – {temporada_seleccionada}")



    ### Para Porteros
    def perfil_porteros(df):
        df = df.copy()
        df["PosPrim"] = df["Primary Position"].astype(str).str.strip()
        df = df[df["PosPrim"] == "Goalkeeper"]

        st.sidebar.markdown("### Minutos Jugados")
        min_mins = int(df["Minutes"].min())
        max_mins = int(df["Minutes"].max())
        min_default = max(600, min_mins)

        minutos_sel = st.sidebar.slider(
            "Rango de Minutos Jugados",
            min_mins, max_mins,
            (min_default, max_mins)
        )
        df = df[df["Minutes"].between(minutos_sel[0], minutos_sel[1])]

        df["Birth Date"] = pd.to_datetime(df["Date of Birth"], errors="coerce")
        df["Age"] = ((pd.to_datetime("today") - df["Birth Date"]).dt.days / 365.25).astype(int)

        st.sidebar.markdown("### Edad")
        min_age = int(df["Age"].min())
        max_age = int(df["Age"].max())

        edad_sel = st.sidebar.slider(
            "Rango de Edad",
            min_age, max_age,
            (17, 36)
        )
        df = df[df["Age"].between(edad_sel[0], edad_sel[1])]

        st.sidebar.markdown("### Filtrar por Nacionalidad")
        nationalities = sorted(df["Nationality"].dropna().astype(str).unique())
        select_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True)

        if select_all:
            selected_nats = nationalities
        else:
            selected_nats = st.sidebar.multiselect("Nacionalidades", nationalities, default=nationalities)

        df = df[df["Nationality"].isin(selected_nats)]

        if df.empty:
            st.warning("No hay jugadores que cumplan los filtros."); st.stop()

        variables_def = [
            "PSxG Faced", 'GSAA', 'Save%', 'xSv%', 'Shot Stopping%', 'Shots Faced', 'Shots Faced OT%', 'Goalkeeper OBV'
        ]
        variables_ball = [
            'GK Aggressive Dist.', 'Claims%', 'Pass OBV', 'OP Passes', 'Passing%', 'Passes Pressured%', 'Pass Forward%', 'Carries', 'Successful Dribbles'
        ]

        scaler = MinMaxScaler()
        df["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_def].fillna(0)))
        df["_ball"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_ball].fillna(0)))

        df["Ranking General Atajadas"] = 100 * (df["_def"] - df["_def"].min()) / (df["_def"].max() - df["_def"].min())
        df["Ranking Juego de Pies"] = 100 * (df["_ball"] - df["_ball"].min()) / (df["_ball"].max() - df["_ball"].min())

        grupos_variables = {
            "Con Balón": variables_ball,
            "Defensivas": variables_def,
            "Rankings": ["Ranking General Atajadas", "Ranking Juego de Pies"]
        }

        st.markdown("<h3 style='margin-bottom: 15px;'>Variables del gráfico</h3>", unsafe_allow_html=True)
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo de variable para eje X", list(grupos_variables.keys()), index=2, key="tipo_x")
            var_x = st.selectbox("Variable en eje X", grupos_variables[tipo_x], index=0, key="var_x")
        with coly:
            tipo_y = st.selectbox("Grupo de variable para eje Y", list(grupos_variables.keys()), index=2, key="tipo_y")
            var_y = st.selectbox("Variable en eje Y", grupos_variables[tipo_y], index=1, key="var_y")

        st.markdown("#### Highlight players")
        jugadores_disponibles = sorted(df["Name"].dropna().astype(str).unique())
        highlight_sel = st.multiselect(
            "Selecciona jugadores a resaltar (además del clic en el gráfico)",
            jugadores_disponibles,
            default=[]
        )


        scatter_interactivo_altair(
            df,
            x=var_x,
            y=var_y,
            size_col="Minutes",
            tooltip_cols=[
                "Name","Team","Primary Position","Age","Nationality","Minutes",
                "Ranking General Defensivo","Ranking General Con Balón",
                "Ranking General Creación","Ranking General Definición", "Ranking General Atajadas", "Ranking Juego de Pies"
            ],
            highlight_names=highlight_sel
        )


    if grupo_seleccionado == "Porteros":
        perfil_porteros(df_filtrado)

 ### Para Centrales
    def perfil_centrales(df):
        df = df.copy()
        df["PosPrim"] = df["Primary Position"].astype(str).str.strip()
        df = df[df["PosPrim"].isin(["Left Centre Back", "Centre Back", "Right Centre Back"])]

        st.sidebar.markdown("### Minutos Jugados")
        min_mins = int(df["Minutes"].min())
        max_mins = int(df["Minutes"].max())
        min_default = max(600, min_mins)

        minutos_sel = st.sidebar.slider(
            "Rango de Minutos Jugados",
            min_mins, max_mins,
            (min_default, max_mins)
        )
        df = df[df["Minutes"].between(minutos_sel[0], minutos_sel[1])]

        df["Birth Date"] = pd.to_datetime(df["Date of Birth"], errors="coerce")
        df["Age"] = ((pd.to_datetime("today") - df["Birth Date"]).dt.days / 365.25).astype(int)

        st.sidebar.markdown("### Edad")
        min_age = int(df["Age"].min())
        max_age = int(df["Age"].max())

        edad_sel = st.sidebar.slider(
            "Rango de Edad",
            min_age, max_age,
            (17, 37)
        )
        df = df[df["Age"].between(edad_sel[0], edad_sel[1])]

        st.sidebar.markdown("### Filtrar por Nacionalidad")
        nationalities = sorted(df["Nationality"].dropna().astype(str).unique())
        select_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True)

        if select_all:
            selected_nats = nationalities
        else:
            selected_nats = st.sidebar.multiselect("Nacionalidades", nationalities, default=nationalities)

        df = df[df["Nationality"].isin(selected_nats)]

        if df.empty:
            st.warning("No hay jugadores que cumplan los filtros."); st.stop()

        variables_def = [
            'PAdj Tackles', 'PAdj Interceptions', 'Blocks/Shot', 'Clearances', 'Aerial Win%', 'Aerial Wins', 'Dribbles Stopped%', 'DA OBV', 'Aggressive Actions', 'PAdj Pressures',
            'Ball Recoveries', 'Counterpress Regains'
        ]
        variables_ball = [
            'xGBuildup', 'xGChain', 'OBV', 'Pass OBV', 'Long Ball%', 'Long Balls', 'Passing%', 'Passes Pressured%', 'OP F3 Passes', 'Pass Forward%', 'OP Passes'
        ]

        scaler = MinMaxScaler()
        df["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_def].fillna(0)))
        df["_ball"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_ball].fillna(0)))

        df["Ranking General Defensivo"] = 100 * (df["_def"] - df["_def"].min()) / (df["_def"].max() - df["_def"].min())
        df["Ranking General Con Balón"] = 100 * (df["_ball"] - df["_ball"].min()) / (df["_ball"].max() - df["_ball"].min())

        grupos_variables = {
            "Con Balón": variables_ball,
            "Defensivas": variables_def,
            "Rankings": ["Ranking General Con Balón", "Ranking General Defensivo"]
        }

        st.markdown("<h3 style='margin-bottom: 15px;'>Variables del gráfico</h3>", unsafe_allow_html=True)
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo de variable para eje X", list(grupos_variables.keys()), index=2, key="tipo_x")
            var_x = st.selectbox("Variable en eje X", grupos_variables[tipo_x], index=0, key="var_x")
        with coly:
            tipo_y = st.selectbox("Grupo de variable para eje Y", list(grupos_variables.keys()), index=2, key="tipo_y")
            var_y = st.selectbox("Variable en eje Y", grupos_variables[tipo_y], index=1, key="var_y")

        st.markdown("#### Highlight players")
        jugadores_disponibles = sorted(df["Name"].dropna().astype(str).unique())
        highlight_sel = st.multiselect(
            "Selecciona jugadores a resaltar (además del clic en el gráfico)",
            jugadores_disponibles,
            default=[]
        )

        scatter_interactivo_altair(
            df,
            x=var_x,
            y=var_y,
            size_col="Minutes",
            tooltip_cols=[
                "Name","Team","Primary Position","Age","Nationality","Minutes",
                "Ranking General Defensivo","Ranking General Con Balón",
                "Ranking General Creación","Ranking General Definición"
            ],
            highlight_names=highlight_sel
        )


    if grupo_seleccionado == "Centrales":
        perfil_centrales(df_filtrado)


### Para Carrileros
    def perfil_carrileros(df):
        df = df.copy()
        df["PosPrim"] = df["Primary Position"].astype(str).str.strip()
        df = df[df["PosPrim"].isin(["Left Back", "Left Wing Back", "Right Back", "Right Wing Back"])]

        st.sidebar.markdown("### Minutos Jugados")
        min_mins = int(df["Minutes"].min())
        max_mins = int(df["Minutes"].max())
        min_default = max(600, min_mins)

        minutos_sel = st.sidebar.slider(
            "Rango de Minutos Jugados",
            min_mins, max_mins,
            (min_default, max_mins)
        )
        df = df[df["Minutes"].between(minutos_sel[0], minutos_sel[1])]

        df["Birth Date"] = pd.to_datetime(df["Date of Birth"], errors="coerce")
        df["Age"] = ((pd.to_datetime("today") - df["Birth Date"]).dt.days / 365.25).astype(int)

        st.sidebar.markdown("### Edad")
        min_age = int(df["Age"].min())
        max_age = int(df["Age"].max())

        edad_sel = st.sidebar.slider(
            "Rango de Edad",
            min_age, max_age,
            (17, 37)
        )
        df = df[df["Age"].between(edad_sel[0], edad_sel[1])]

        st.sidebar.markdown("### Filtrar por Nacionalidad")
        nationalities = sorted(df["Nationality"].dropna().astype(str).unique())
        select_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True)

        if select_all:
            selected_nats = nationalities
        else:
            selected_nats = st.sidebar.multiselect("Nacionalidades", nationalities, default=nationalities)

        df = df[df["Nationality"].isin(selected_nats)]

        if df.empty:
            st.warning("No hay jugadores que cumplan los filtros."); st.stop()

        variables_def = [
           'PAdj Interceptions', 'PAdj Clearances', 'Blocks/Shot', 'Defensive Regains', 'Ball Recoveries', 'PAdj Tackles', 'Dribbles Stopped%',
            'Pressure Regains', 'Counterpress Regains', "DA OBV"
        ]
        variables_ball = [
            'Assists', 'xG Assisted', 'Key Passes', 'Successful Dribbles', 'Dribble%', 'OP Passes', 'Passing%', 'Deep Progressions', 'xGBuildup', 'xGChain', 
            'Carries', 'PintoB', 'PinTin', 'Successful Box Cross%', 'Successful Crosses', 'Deep Completions', 'Pass OBV', 'D&C OBV', "OBV"
        ]

        scaler = MinMaxScaler()
        df["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_def].fillna(0)))
        df["_ball"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_ball].fillna(0)))

        df["Ranking General Defensivo"] = 100 * (df["_def"] - df["_def"].min()) / (df["_def"].max() - df["_def"].min())
        df["Ranking General Ofensivo"] = 100 * (df["_ball"] - df["_ball"].min()) / (df["_ball"].max() - df["_ball"].min())

        grupos_variables = {
            "Ofensivas": variables_ball,
            "Defensivas": variables_def,
            "Rankings": ["Ranking General Ofensivo", "Ranking General Defensivo"]
        }

        st.markdown("<h3 style='margin-bottom: 15px;'>Variables del gráfico</h3>", unsafe_allow_html=True)
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo de variable para eje X", list(grupos_variables.keys()), index=2, key="tipo_x")
            var_x = st.selectbox("Variable en eje X", grupos_variables[tipo_x], index=0, key="var_x")
        with coly:
            tipo_y = st.selectbox("Grupo de variable para eje Y", list(grupos_variables.keys()), index=2, key="tipo_y")
            var_y = st.selectbox("Variable en eje Y", grupos_variables[tipo_y], index=1, key="var_y")

        st.markdown("#### Highlight players")
        jugadores_disponibles = sorted(df["Name"].dropna().astype(str).unique())
        highlight_sel = st.multiselect(
            "Selecciona jugadores a resaltar (además del clic en el gráfico)",
            jugadores_disponibles,
            default=[]
        )
        scatter_interactivo_altair(
            df,
            x=var_x,
            y=var_y,
            size_col="Minutes",
            tooltip_cols=[
                "Name","Team","Primary Position","Age","Nationality","Minutes",
                "Ranking General Defensivo","Ranking General Con Balón",
                "Ranking General Creación","Ranking General Definición", "Ranking General Ofensivo"
            ],
            highlight_names=highlight_sel
        )

    if grupo_seleccionado == "Carrileros/Laterales":
        perfil_carrileros(df_filtrado)

### Para Contenciones
    def perfil_contenciones(df):
        df = df.copy()
        df["PosPrim"] = df["Primary Position"].astype(str).str.strip()
        df = df[df["PosPrim"].isin(["Centre Defensive Midfielder", "Left Defensive Midfielder", "Right Defensive Midfielder"])]

        st.sidebar.markdown("### Minutos Jugados")
        min_mins = int(df["Minutes"].min())
        max_mins = int(df["Minutes"].max())
        min_default = max(600, min_mins)

        minutos_sel = st.sidebar.slider(
            "Rango de Minutos Jugados",
            min_mins, max_mins,
            (min_default, max_mins)
        )
        df = df[df["Minutes"].between(minutos_sel[0], minutos_sel[1])]

        df["Birth Date"] = pd.to_datetime(df["Date of Birth"], errors="coerce")
        df["Age"] = ((pd.to_datetime("today") - df["Birth Date"]).dt.days / 365.25).astype(int)

        st.sidebar.markdown("### Edad")
        min_age = int(df["Age"].min())
        max_age = int(df["Age"].max())

        edad_sel = st.sidebar.slider(
            "Rango de Edad",
            min_age, max_age,
            (17, 37)
        )
        df = df[df["Age"].between(edad_sel[0], edad_sel[1])]

        st.sidebar.markdown("### Filtrar por Nacionalidad")
        nationalities = sorted(df["Nationality"].dropna().astype(str).unique())
        select_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True)

        if select_all:
            selected_nats = nationalities
        else:
            selected_nats = st.sidebar.multiselect("Nacionalidades", nationalities, default=nationalities)

        df = df[df["Nationality"].isin(selected_nats)]

        if df.empty:
            st.warning("No hay jugadores que cumplan los filtros."); st.stop()

        variables_def = [
            'PAdj Interceptions', 'Defensive Regains', 'PAdj Tackles', 'Dribbles Stopped%',
            'PAdj Pressures', 'Counterpress Regains', 'Blocks/Shot',
            'DA OBV', 'Aggressive Actions'

        ]
        variables_ball = [
           'xG', 'Shooting%', 'Assists', 'xG Assisted', 'Key Passes', 'Successful Dribbles',
            'OP Passes', 'Deep Progressions', 'xGBuildup', 'xGChain', 'Carries',
            'PintoB', 'Throughballs', 'Pass OBV', 'Shot OBV', 'OBV'
        ]

        scaler = MinMaxScaler()
        df["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_def].fillna(0)))
        df["_ball"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_ball].fillna(0)))

        df["Ranking General Defensivo"] = 100 * (df["_def"] - df["_def"].min()) / (df["_def"].max() - df["_def"].min())
        df["Ranking General Con Balón"] = 100 * (df["_ball"] - df["_ball"].min()) / (df["_ball"].max() - df["_ball"].min())

        grupos_variables = {
            "Con Balón": variables_ball,
            "Defensivas": variables_def,
            "Rankings": ["Ranking General Con Balón", "Ranking General Defensivo"]
        }

        st.markdown("<h3 style='margin-bottom: 15px;'>Variables del gráfico</h3>", unsafe_allow_html=True)
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo de variable para eje X", list(grupos_variables.keys()), index=2, key="tipo_x")
            var_x = st.selectbox("Variable en eje X", grupos_variables[tipo_x], index=0, key="var_x")
        with coly:
            tipo_y = st.selectbox("Grupo de variable para eje Y", list(grupos_variables.keys()), index=2, key="tipo_y")
            var_y = st.selectbox("Variable en eje Y", grupos_variables[tipo_y], index=1, key="var_y")
        
        st.markdown("#### Highlight players")
        jugadores_disponibles = sorted(df["Name"].dropna().astype(str).unique())
        highlight_sel = st.multiselect(
            "Selecciona jugadores a resaltar (además del clic en el gráfico)",
            jugadores_disponibles,
            default=[]
        )

        scatter_interactivo_altair(
            df,
            x=var_x,
            y=var_y,
            size_col="Minutes",
            tooltip_cols=[
                "Name","Team","Primary Position","Age","Nationality","Minutes",
                "Ranking General Defensivo","Ranking General Con Balón",
                "Ranking General Creación","Ranking General Definición"
            ],
            highlight_names=highlight_sel
        )

    if grupo_seleccionado == "Contenciones":
        perfil_contenciones(df_filtrado)


### Para Interiores
    def perfil_interiores(df):
        df = df.copy()
        df["PosPrim"] = df["Primary Position"].astype(str).str.strip()
        df = df[df["PosPrim"].isin(["Right Centre Midfielder", "Left Centre Midfielder"])]

        st.sidebar.markdown("### Minutos Jugados")
        min_mins = int(df["Minutes"].min())
        max_mins = int(df["Minutes"].max())
        min_default = max(600, min_mins)

        minutos_sel = st.sidebar.slider(
            "Rango de Minutos Jugados",
            min_mins, max_mins,
            (min_default, max_mins)
        )
        df = df[df["Minutes"].between(minutos_sel[0], minutos_sel[1])]

        df["Birth Date"] = pd.to_datetime(df["Date of Birth"], errors="coerce")
        df["Age"] = ((pd.to_datetime("today") - df["Birth Date"]).dt.days / 365.25).astype(int)

        st.sidebar.markdown("### Edad")
        min_age = int(df["Age"].min())
        max_age = int(df["Age"].max())

        edad_sel = st.sidebar.slider(
            "Rango de Edad",
            min_age, max_age,
            (17, 37)
        )
        df = df[df["Age"].between(edad_sel[0], edad_sel[1])]

        st.sidebar.markdown("### Filtrar por Nacionalidad")
        nationalities = sorted(df["Nationality"].dropna().astype(str).unique())
        select_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True)

        if select_all:
            selected_nats = nationalities
        else:
            selected_nats = st.sidebar.multiselect("Nacionalidades", nationalities, default=nationalities)

        df = df[df["Nationality"].isin(selected_nats)]

        if df.empty:
            st.warning("No hay jugadores que cumplan los filtros."); st.stop()

        variables_def = [
            'PAdj Interceptions', 'Defensive Regains', 'PAdj Tackles', 'Dribbles Stopped%',
            'PAdj Pressures', 'Counterpress Regains', 'Blocks/Shot', 'Dribbles Stopped%',
            'DA OBV', 'Aggressive Actions'

        ]
        variables_ball = [
           'xG', 'Shooting%', 'Assists', 'xG Assisted', 'Key Passes', 'Successful Dribbles',
            'OP Passes', 'Deep Progressions', 'xGBuildup', 'xGChain', 'Carries',
            'PintoB', 'Throughballs', 'Pass OBV', 'Shot OBV', 'OBV'
        ]

        scaler = MinMaxScaler()
        df["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_def].fillna(0)))
        df["_ball"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_ball].fillna(0)))

        df["Ranking General Defensivo"] = 100 * (df["_def"] - df["_def"].min()) / (df["_def"].max() - df["_def"].min())
        df["Ranking General Con Balón"] = 100 * (df["_ball"] - df["_ball"].min()) / (df["_ball"].max() - df["_ball"].min())

        grupos_variables = {
            "Con Balón": variables_ball,
            "Defensivas": variables_def,
            "Rankings": ["Ranking General Con Balón", "Ranking General Defensivo"]
        }

        st.markdown("<h3 style='margin-bottom: 15px;'>Variables del gráfico</h3>", unsafe_allow_html=True)
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo de variable para eje X", list(grupos_variables.keys()), index=2, key="tipo_x")
            var_x = st.selectbox("Variable en eje X", grupos_variables[tipo_x], index=0, key="var_x")
        with coly:
            tipo_y = st.selectbox("Grupo de variable para eje Y", list(grupos_variables.keys()), index=2, key="tipo_y")
            var_y = st.selectbox("Variable en eje Y", grupos_variables[tipo_y], index=1, key="var_y")

        st.markdown("#### Highlight players")
        jugadores_disponibles = sorted(df["Name"].dropna().astype(str).unique())
        highlight_sel = st.multiselect(
            "Selecciona jugadores a resaltar (además del clic en el gráfico)",
            jugadores_disponibles,
            default=[]
        )

        scatter_interactivo_altair(
            df,
            x=var_x,
            y=var_y,
            size_col="Minutes",
            tooltip_cols=[
                "Name","Team","Primary Position","Age","Nationality","Minutes",
                "Ranking General Defensivo","Ranking General Con Balón",
                "Ranking General Creación","Ranking General Definición"
            ],
            highlight_names=highlight_sel
        )

    if grupo_seleccionado == "Interiores":
        perfil_interiores(df_filtrado)

### Para Volantes Ofensivos
    def perfil_volantes(df):
        df = df.copy()
        df["PosPrim"] = df["Primary Position"].astype(str).str.strip()
        df = df[df["PosPrim"].isin(["Centre Attacking Midfielder", "Right Attacking Midfielder", "Left Attacking Midfielder"])]

        st.sidebar.markdown("### Minutos Jugados")
        min_mins = int(df["Minutes"].min())
        max_mins = int(df["Minutes"].max())
        min_default = max(600, min_mins)

        minutos_sel = st.sidebar.slider(
            "Rango de Minutos Jugados",
            min_mins, max_mins,
            (min_default, max_mins)
        )
        df = df[df["Minutes"].between(minutos_sel[0], minutos_sel[1])]

        df["Birth Date"] = pd.to_datetime(df["Date of Birth"], errors="coerce")
        df["Age"] = ((pd.to_datetime("today") - df["Birth Date"]).dt.days / 365.25).astype(int)

        st.sidebar.markdown("### Edad")
        min_age = int(df["Age"].min())
        max_age = int(df["Age"].max())

        edad_sel = st.sidebar.slider(
            "Rango de Edad",
            min_age, max_age,
            (17, 37)
        )
        df = df[df["Age"].between(edad_sel[0], edad_sel[1])]

        st.sidebar.markdown("### Filtrar por Nacionalidad")
        nationalities = sorted(df["Nationality"].dropna().astype(str).unique())
        select_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True)

        if select_all:
            selected_nats = nationalities
        else:
            selected_nats = st.sidebar.multiselect("Nacionalidades", nationalities, default=nationalities)

        df = df[df["Nationality"].isin(selected_nats)]

        if df.empty:
            st.warning("No hay jugadores que cumplan los filtros."); st.stop()

        variables_def = [
            'xG Assisted', 'Key Passes', 'Assists', 'Throughballs', 'OP F3 Passes', 'F3 Pass Forward%', 'Passes Inside Box', 'PintoB', 'xGChain', 'OBV', 'Pass OBV', 'D&C OBV',
            'Counterpress Regains', 'Pressures', 'Deep Progressions', 'Carries', 'Dribbles'

        ]
        variables_ball = [
           'Shot OBV', 'NP Goals', 'xG/Shot', 'Shot Touch%', 'PSxG', 'Shots', 'Goal Conversion%'
        ]

        scaler = MinMaxScaler()
        df["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_def].fillna(0)))
        df["_ball"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_ball].fillna(0)))

        df["Ranking General Creación"] = 100 * (df["_def"] - df["_def"].min()) / (df["_def"].max() - df["_def"].min())
        df["Ranking General Definición"] = 100 * (df["_ball"] - df["_ball"].min()) / (df["_ball"].max() - df["_ball"].min())

        grupos_variables = {
            "Definición": variables_ball,
            "Creación": variables_def,
            "Rankings": ["Ranking General Creación", "Ranking General Definición"]
        }

        st.markdown("<h3 style='margin-bottom: 15px;'>Variables del gráfico</h3>", unsafe_allow_html=True)
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo de variable para eje X", list(grupos_variables.keys()), index=2, key="tipo_x")
            var_x = st.selectbox("Variable en eje X", grupos_variables[tipo_x], index=0, key="var_x")
        with coly:
            tipo_y = st.selectbox("Grupo de variable para eje Y", list(grupos_variables.keys()), index=2, key="tipo_y")
            var_y = st.selectbox("Variable en eje Y", grupos_variables[tipo_y], index=1, key="var_y")

        st.markdown("#### Highlight players")
        jugadores_disponibles = sorted(df["Name"].dropna().astype(str).unique())
        highlight_sel = st.multiselect(
            "Selecciona jugadores a resaltar (además del clic en el gráfico)",
            jugadores_disponibles,
            default=[]
        )

        scatter_interactivo_altair(
            df,
            x=var_x,
            y=var_y,
            size_col="Minutes",
            tooltip_cols=[
                "Name","Team","Primary Position","Age","Nationality","Minutes",
                "Ranking General Defensivo","Ranking General Con Balón",
                "Ranking General Creación","Ranking General Definición"
            ],
            highlight_names=highlight_sel
        )

    if grupo_seleccionado == "Volantes Ofensivos":
        perfil_volantes(df_filtrado)


### Para Extremos
    def perfil_extremos(df):
        df = df.copy()
        df["PosPrim"] = df["Primary Position"].astype(str).str.strip()
        df = df[df["PosPrim"].isin(["Left Wing", "Right Wing", "Left Midfielder", "Right Midfielder"])]

        st.sidebar.markdown("### Minutos Jugados")
        min_mins = int(df["Minutes"].min())
        max_mins = int(df["Minutes"].max())
        min_default = max(600, min_mins)

        minutos_sel = st.sidebar.slider(
            "Rango de Minutos Jugados",
            min_mins, max_mins,
            (min_default, max_mins)
        )
        df = df[df["Minutes"].between(minutos_sel[0], minutos_sel[1])]

        df["Birth Date"] = pd.to_datetime(df["Date of Birth"], errors="coerce")
        df["Age"] = ((pd.to_datetime("today") - df["Birth Date"]).dt.days / 365.25).astype(int)

        st.sidebar.markdown("### Edad")
        min_age = int(df["Age"].min())
        max_age = int(df["Age"].max())

        edad_sel = st.sidebar.slider(
            "Rango de Edad",
            min_age, max_age,
            (17, 37)
        )
        df = df[df["Age"].between(edad_sel[0], edad_sel[1])]

        st.sidebar.markdown("### Filtrar por Nacionalidad")
        nationalities = sorted(df["Nationality"].dropna().astype(str).unique())
        select_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True)

        if select_all:
            selected_nats = nationalities
        else:
            selected_nats = st.sidebar.multiselect("Nacionalidades", nationalities, default=nationalities)

        df = df[df["Nationality"].isin(selected_nats)]

        if df.empty:
            st.warning("No hay jugadores que cumplan los filtros."); st.stop()

        variables_def = [
            'xG Assisted', 'Key Passes', 'Assists', 'Throughballs', 'OP F3 Passes', 'F3 Pass Forward%', 'Passes Inside Box', 'PintoB', 'xGChain', 'OBV', 'Pass OBV', 'D&C OBV',
            'Counterpress Regains', 'Pressures', 'Deep Progressions', 'Carries', 'Successful Dribbles', 'Defensive Regains'

        ]
        variables_ball = [
           'Shot OBV', 'NP Goals', 'xG/Shot', 'Shot Touch%', 'PSxG', 'Shots', 'Goal Conversion%'
        ]

        scaler = MinMaxScaler()
        df["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_def].fillna(0)))
        df["_ball"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_ball].fillna(0)))

        df["Ranking General Creación"] = 100 * (df["_def"] - df["_def"].min()) / (df["_def"].max() - df["_def"].min())
        df["Ranking General Definición"] = 100 * (df["_ball"] - df["_ball"].min()) / (df["_ball"].max() - df["_ball"].min())

        grupos_variables = {
            "Definición": variables_ball,
            "Creación": variables_def,
            "Rankings": ["Ranking General Creación", "Ranking General Definición"]
        }

        st.markdown("<h3 style='margin-bottom: 15px;'>Variables del gráfico</h3>", unsafe_allow_html=True)
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo de variable para eje X", list(grupos_variables.keys()), index=2, key="tipo_x")
            var_x = st.selectbox("Variable en eje X", grupos_variables[tipo_x], index=0, key="var_x")
        with coly:
            tipo_y = st.selectbox("Grupo de variable para eje Y", list(grupos_variables.keys()), index=2, key="tipo_y")
            var_y = st.selectbox("Variable en eje Y", grupos_variables[tipo_y], index=1, key="var_y")

        st.markdown("#### Highlight players")
        jugadores_disponibles = sorted(df["Name"].dropna().astype(str).unique())
        highlight_sel = st.multiselect(
            "Selecciona jugadores a resaltar (además del clic en el gráfico)",
            jugadores_disponibles,
            default=[]
        )

        scatter_interactivo_altair(
            df,
            x=var_x,
            y=var_y,
            size_col="Minutes",
            tooltip_cols=[
                "Name","Team","Primary Position","Age","Nationality","Minutes",
                "Ranking General Defensivo","Ranking General Con Balón",
                "Ranking General Creación","Ranking General Definición"
            ],
            highlight_names=highlight_sel
        )

    if grupo_seleccionado == "Extremos":
        perfil_extremos(df_filtrado)



### Para Delanteros
    def perfil_delanteros(df):
        df = df.copy()
        df["PosPrim"] = df["Primary Position"].astype(str).str.strip()
        df = df[df["PosPrim"].isin(["Centre Forward", "Left Centre Forward", 'Right Centre Forward'])]

        st.sidebar.markdown("### Minutos Jugados")
        min_mins = int(df["Minutes"].min())
        max_mins = int(df["Minutes"].max())
        min_default = max(600, min_mins)

        minutos_sel = st.sidebar.slider(
            "Rango de Minutos Jugados",
            min_mins, max_mins,
            (min_default, max_mins)
        )
        df = df[df["Minutes"].between(minutos_sel[0], minutos_sel[1])]

        df["Birth Date"] = pd.to_datetime(df["Date of Birth"], errors="coerce")
        df["Age"] = ((pd.to_datetime("today") - df["Birth Date"]).dt.days / 365.25).astype(int)

        st.sidebar.markdown("### Edad")
        min_age = int(df["Age"].min())
        max_age = int(df["Age"].max())

        edad_sel = st.sidebar.slider(
            "Rango de Edad",
            min_age, max_age,
            (17, 37)
        )
        df = df[df["Age"].between(edad_sel[0], edad_sel[1])]

        st.sidebar.markdown("### Filtrar por Nacionalidad")
        nationalities = sorted(df["Nationality"].dropna().astype(str).unique())
        select_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True)

        if select_all:
            selected_nats = nationalities
        else:
            selected_nats = st.sidebar.multiselect("Nacionalidades", nationalities, default=nationalities)

        df = df[df["Nationality"].isin(selected_nats)]

        if df.empty:
            st.warning("No hay jugadores que cumplan los filtros."); st.stop()

        variables_def = [
            'xG Assisted', 'Key Passes', 'Assists', 'Throughballs', 'OP F3 Passes', 'F3 Pass Forward%', 'Passes Inside Box', 'PintoB', 'xGChain', 'OBV', 'Pass OBV', 'D&C OBV',
            'Counterpress Regains', 'Pressures', 'Deep Progressions', 'Carries', 'Dribbles', 'Aerial Win%'

        ]
        variables_ball = [
           'Shot OBV', 'NP Goals', 'xG/Shot', 'Shot Touch%', 'PSxG', 'Shots', 'Goal Conversion%'
        ]

        scaler = MinMaxScaler()
        df["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_def].fillna(0)))
        df["_ball"] = PCA(n_components=1).fit_transform(scaler.fit_transform(df[variables_ball].fillna(0)))

        df["Ranking General Creación"] = 100 * (df["_def"] - df["_def"].min()) / (df["_def"].max() - df["_def"].min())
        df["Ranking General Definición"] = 100 * (df["_ball"] - df["_ball"].min()) / (df["_ball"].max() - df["_ball"].min())

        grupos_variables = {
            "Definición": variables_ball,
            "Creación": variables_def,
            "Rankings": ["Ranking General Creación", "Ranking General Definición"]
        }

        st.markdown("<h3 style='margin-bottom: 15px;'>Variables del gráfico</h3>", unsafe_allow_html=True)
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo de variable para eje X", list(grupos_variables.keys()), index=2, key="tipo_x")
            var_x = st.selectbox("Variable en eje X", grupos_variables[tipo_x], index=0, key="var_x")
        with coly:
            tipo_y = st.selectbox("Grupo de variable para eje Y", list(grupos_variables.keys()), index=2, key="tipo_y")
            var_y = st.selectbox("Variable en eje Y", grupos_variables[tipo_y], index=1, key="var_y")

        st.markdown("#### Highlight players")
        jugadores_disponibles = sorted(df["Name"].dropna().astype(str).unique())
        highlight_sel = st.multiselect(
            "Selecciona jugadores a resaltar (además del clic en el gráfico)",
            jugadores_disponibles,
            default=[]
        )

        scatter_interactivo_altair(
            df,
            x=var_x,
            y=var_y,
            size_col="Minutes",
            tooltip_cols=[
                "Name","Team","Primary Position","Age","Nationality","Minutes",
                "Ranking General Defensivo","Ranking General Con Balón",
                "Ranking General Creación","Ranking General Definición"
            ],
            highlight_names=highlight_sel
        )

    if grupo_seleccionado == "Delanteros":
        perfil_delanteros(df_filtrado)




##############################################################################################################
############################## Radares Estadísticos ##########################################################
##############################################################################################################


elif seleccion == "Radares Estadísticos":
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    import altair as alt

    st.markdown("<h3 style='margin-bottom: 15px;'>Radares Estadísticos</h3>", unsafe_allow_html=True)

    # =========================
    # Colores para distribuciones
    # =========================
    FILL_ORANGE = "#f9ae34"   # naranja del proyecto
    LINE_BLACK  = "#111111"   # negro para contorno/curva/regla

    # =========================
    # Utils / Helpers
    # =========================
    def _normalize_metrics(df, metrics, invert=None):
        """
        Normaliza 0–1 por métrica con coerción a numérico.
        Si está en 'invert', aplica 1 - z. NaN -> 0.5
        """
        invert = set(invert or [])
        out = df.copy()
        for m in metrics:
            if m not in out.columns:
                continue
            s = pd.to_numeric(out[m], errors="coerce")
            mn, mx = s.min(), s.max()
            if pd.isna(mn) or pd.isna(mx) or mx == mn:
                out[m] = 0.5
            else:
                z = (s - mn) / (mx - mn)
                out[m] = (1 - z) if m in invert else z
                out[m] = out[m].fillna(0.5)
        return out

    # Radar genérico (barras por fase, contorno perimetral, etiquetas)
    def radar_barras_plotly(
        jugador,
        df,
        fases_juego,
        invertir_vars=None,
        colores_fases=("rgba(59,130,246,0.90)", "rgba(245,158,11,0.90)", "rgba(16,185,129,0.90)"),
        chart_height=640,   # tamaño del radar
        show_silueta=False  # polígono de valores (opcional)
    ):
        if "Name" not in df.columns:
            st.warning("La base no tiene la columna 'Name'."); return None
        if jugador not in df["Name"].values:
            st.warning(f"El jugador '{jugador}' no está en la base."); return None

        invertir = set(invertir_vars or [])

        # Atributos en orden por fase
        atributos, fase_idx = [], []
        fases_orden = list(fases_juego.keys())
        for i, (fase, vars_fase) in enumerate(fases_juego.items()):
            presentes = [v for v in vars_fase if v in df.columns]
            atributos.extend(presentes)
            fase_idx.extend([i] * len(presentes))
        if not atributos:
            st.warning("No hay variables presentes para construir el radar."); return None

        # Normalización → 0–100
        df_norm = _normalize_metrics(df, atributos, invert=invertir)
        row = df_norm.loc[df_norm["Name"] == jugador].iloc[0]
        r_vals = [float(row[a]) * 100 for a in atributos]

        # Ángulos
        n = len(atributos)
        thetas = np.linspace(0, 360, n, endpoint=False)

        fig = go.Figure()

        # Barras por fase (sin bordes internos)
        for i, fase in enumerate(fases_orden):
            idxs = [k for k, fidx in enumerate(fase_idx) if fidx == i]
            if not idxs:
                continue
            fig.add_trace(
                go.Barpolar(
                    r=[r_vals[k] for k in idxs],
                    theta=[thetas[k] for k in idxs],
                    width=[(360/n)*0.98]*len(idxs),
                    marker=dict(color=colores_fases[i], line=dict(width=0)),
                    name=fase,
                    hovertemplate="<b>%{customdata[0]}</b><br>Percentil: %{r:.1f}<extra></extra>",
                    customdata=[[atributos[k]] for k in idxs],
                    opacity=0.95,
                )
            )

        # (opcional) silueta poligonal de valores del jugador
        if show_silueta:
            fig.add_trace(
                go.Scatterpolar(
                    r=r_vals + [r_vals[0]],
                    theta=thetas.tolist() + [thetas[0]],
                    mode="lines",
                    line=dict(color="rgba(0,0,0,0.35)", width=1),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

        # Etiquetas de variables (r=110 para aire)
        fig.add_trace(
            go.Scatterpolar(
                r=[110]*n,
                theta=thetas,
                mode="text",
                text=atributos,
                textfont=dict(size=11, color="#2B2B2B"),
                textposition="middle center",
                hoverinfo="skip",
                showlegend=False,
            )
        )

        fig.update_layout(
            template="plotly_white",
            height=chart_height,
            margin=dict(l=10, r=10, t=40, b=40),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    range=[0,112],
                    tickvals=[0,20,40,60,80,100],
                    ticktext=["0","20","40","60","80","100"],
                    showline=True, gridcolor="#E5E5E5", gridwidth=1,
                    tickfont=dict(size=11, color="#2B2B2B"),
                ),
                angularaxis=dict(
                    rotation=0, direction="clockwise", showline=False,
                    gridcolor="#F0F0F0", gridwidth=1,
                    tickfont=dict(size=10, color="#B3B3B3"),
                    ticks="",
                ),
            ),
            legend=dict(
                orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5,
                font=dict(size=12, color="#2B2B2B"), bgcolor="rgba(0,0,0,0)",
            ),
            title=dict(text=f"Radar · {jugador}", x=0.01, y=0.98, font=dict(size=18, color="#111111")),
        )
        return fig

    # -------- Distribution plots (Altair KDE) en grilla 3×N --------
    def _kde_chart_altair(
        df,
        metric,
        jugador_val,
        fill_color=FILL_ORANGE,
        line_color=LINE_BLACK,
        height=120
    ):
        """KDE compacto: relleno naranja, contorno/curva negro."""
        if metric not in df.columns:
            return None

        serie = (
            pd.to_numeric(df[metric], errors="coerce")
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
            .astype(float)
        )
        if serie.empty or pd.isna(jugador_val):
            return None

        # Dominio con margen
        mn, mx = float(serie.min()), float(serie.max())
        if mn == mx:
            pad = max(abs(mn), 1.0) * 0.1
            mn, mx = mn - pad, mx + pad
        else:
            pad = (mx - mn) * 0.10
            mn, mx = mn - pad, mx + pad

        data_num = pd.DataFrame({"value": serie})

        base = alt.Chart(data_num).transform_density(
            "value", as_=["x", "density"], extent=[mn, mx], steps=200
        )

        # Relleno naranja bajo la curva hasta el valor del jugador
        area = base.transform_filter(
            alt.datum.x <= float(jugador_val)
        ).mark_area(
            opacity=0.22, color=fill_color
        ).encode(
            x=alt.X("x:Q", title=None),
            y=alt.Y("density:Q", title=None)
        )

        # Curva/contorno negro
        line = base.mark_line(color=line_color, size=1.4).encode(
            x="x:Q", y="density:Q"
        )

        # Regla vertical del jugador en negro
        rule = alt.Chart(pd.DataFrame({"x": [float(jugador_val)]})).mark_rule(
            color=line_color, strokeWidth=2
        ).encode(
            x="x:Q",
            tooltip=[alt.Tooltip("x:Q", title="Valor", format=".3f")]
        )

        title = alt.TitleParams(metric, fontSize=12, anchor="middle", color="#1F2937")
        chart = (area + line + rule).properties(height=height, title=title)

        # Estilo
        chart = chart.configure_axis(
            grid=False, domain=True, domainColor="#E6E6E6", labelColor="#2B2B2B"
        ).configure_view(
            strokeWidth=0
        ).configure_title(
            font="Inter", color="#111111", anchor="middle"
        )

        return chart

    def build_kde_charts(df, jugador, fases_juego, height_each=120):
        """Devuelve una lista de charts Altair (uno por métrica)."""
        charts = []
        if "Name" not in df.columns or jugador not in df["Name"].values:
            return charts
        for fase, vars_fase in fases_juego.items():
            presentes = [v for v in vars_fase if v in df.columns]
            for m in presentes:
                val = pd.to_numeric(df.loc[df["Name"] == jugador, m], errors="coerce").iloc[0]
                ch = _kde_chart_altair(
                    df, m, val,
                    fill_color=FILL_ORANGE,
                    line_color=LINE_BLACK,
                    height=height_each
                )
                if ch is not None:
                    charts.append(ch)
        return charts

    # =========================
    # Selección de liga / temporada (mismo catálogo que Perfil)
    # =========================
    st.sidebar.markdown("### Selecciona la Liga y Temporada")

    ligas_temporadas = {
        "Liga MX": ["2024/2025", "2025/2026"],
        "Liga Profesional, Argentina": ["2025"],
        "Jupiler Pro League, Bélgica": ["2024/2025", "2025/2026"],
        "Serie A, Brasil": ["2025"],
        "Primera División, Chile": ["2025"],
        "Primera A, Colombia": ["2025"],
        "Liga Pro, Ecuador": ["2025"],
        "Premier League, Inglaterra": ["2024/2025"],
        "Ligue 1, Francia": ["2024/2025"],
        "1. Bundesliga, Alemania": ["2024/2025"],
        "Serie A, Italia": ["2024/2025"],
        "Serie B, Italia": ["2024/2025"],
        "Eredivisie, Países Bajos": ["2024/2025"],
        "División Profesional, Paraguay": ["2025"],
        "Primeira Liga, Portugal": ["2024/2025", "2025/2026"],
        "Premier League, Rusia": ["2024/2025"],
        "Pro League, Arabia": ["2024/2025"],
        "La Liga, España": ["2024/2025", "2025/2026"],
        "La Liga 2, España": ["2024/2025", "2025/2026"],
        "Primera División, Uruguay": ["2025"],
        "MLS, Estados Unidos": ["2025"],
    }

    archivos_csv = {
        ("Liga MX", "2024/2025"): "ligamxp902425.csv",
        ("Liga MX", "2025/2026"): "ligamxp902526.csv",
        ("Liga Profesional, Argentina", "2025"): "argp902025.csv",
        ("Jupiler Pro League, Bélgica", "2024/2025"): "belp902425.csv",
        ("Jupiler Pro League, Bélgica", "2025/2026"): "belp902526.csv",
        ("Serie A, Brasil", "2025"): "brap902025.csv",
        ("Primera División, Chile", "2025"): "chip902025.csv",
        ("Primera A, Colombia", "2025"): "colp902025.csv",
        ("Liga Pro, Ecuador", "2025"): "ecup902025.csv",
        ("Premier League, Inglaterra", "2024/2025"): "engp902425.csv",
        ("Ligue 1, Francia", "2024/2025"): "frap902425.csv",
        ("1. Bundesliga, Alemania", "2024/2025"): "gerp902425.csv",
        ("Serie A, Italia", "2024/2025"): "ita1p902425.csv",
        ("Serie B, Italia", "2024/2025"): "seriebp902425.csv",
        ("Eredivisie, Países Bajos", "2024/2025"): "nedp902425.csv",
        ("División Profesional, Paraguay", "2025"): "parp902025.csv",
        ("Primeira Liga, Portugal", "2024/2025"): "porp902425.csv",
        ("Primeira Liga, Portugal", "2025/2026"): "porp902526.csv",
        ("Premier League, Rusia", "2024/2025"): "rusp902425.csv",
        ("Pro League, Arabia", "2024/2025"): "arap902425.csv",
        ("La Liga, España", "2024/2025"): "espp902425.csv",
        ("La Liga, España", "2025/2026"): "laligap902526.csv",
        ("La Liga 2, España", "2024/2025"): "esp2p902425.csv",
        ("La Liga 2, España", "2025/2026"): "laliga22526.csv",
        ("Primera División, Uruguay", "2025"): "urup902025.csv",
        ("MLS, Estados Unidos", "2025"): "mlsp902025.csv",
    }

    ligas_disponibles = list(ligas_temporadas.keys())
    liga_seleccionada = st.sidebar.selectbox("Liga", ligas_disponibles, index=0)
    temporadas_disponibles = ligas_temporadas[liga_seleccionada]
    temporada_seleccionada = st.sidebar.selectbox("Temporada", temporadas_disponibles, index=0)

    archivo = archivos_csv.get((liga_seleccionada, temporada_seleccionada))
    if not archivo:
        st.error("No hay datos disponibles para esta combinación de liga y temporada."); st.stop()

    df_radar = pd.read_csv(archivo)
    df_radar["Competition"] = df_radar["Competition"].astype(str).str.strip()
    nombre_base_liga = {
        "Liga Profesional, Argentina": "Liga Profesional",
        "Jupiler Pro League, Bélgica": "Jupiler Pro League",
        "Primera División, Chile": "Primera División",
        "Primera A, Colombia": "Primera A",
        "Liga Pro, Ecuador": "Liga Pro",
        "Premier League, Inglaterra": "Premier League",
        "Ligue 1, Francia": "Ligue 1",
        "1. Bundesliga, Alemania": "1. Bundesliga",
        "Serie B, Italia": "Serie B",
        "Eredivisie, Países Bajos": "Eredivisie",
        "División Profesional, Paraguay": "División Profesional, Paraguay",
        "Primeira Liga, Portugal": "Primeira Liga",
        "Premier League, Rusia": "Premier League",
        "Pro League, Arabia": "Pro League",
        "La Liga, España": "La Liga",
        "La Liga 2, España": "La Liga 2",
        "Primera División, Uruguay": "Primera División",
        "MLS, Estados Unidos": "Major League Soccer",
    }.get(liga_seleccionada, liga_seleccionada)

    df_radar["Season"] = df_radar["Season"].astype(str).str.strip()
    df_radar = df_radar[
        (df_radar["Competition"] == str(nombre_base_liga)) &
        (df_radar["Season"] == str(temporada_seleccionada))
    ].copy()

    if df_radar.empty:
        st.warning("No hay datos disponibles en la base para esta liga y temporada."); st.stop()

    # =========================
    # Grupo de Posición (incluye todos)
    # =========================
    st.sidebar.markdown("### Grupo de Posición")
    grupo = st.sidebar.radio(
        "Grupo",
        [
            "Porteros", "Centrales", "Carrileros/Laterales",
            "Contenciones", "Interiores", "Volantes Ofensivos",
            "Extremos", "Delanteros"
        ],
        index=0
    )

    df_radar["PosPrim"] = df_radar["Primary Position"].astype(str).str.strip()

    if grupo == "Porteros":
        df_radar = df_radar[df_radar["PosPrim"] == "Goalkeeper"].copy()
    elif grupo == "Centrales":
        df_radar = df_radar[df_radar["PosPrim"].isin(
            ["Left Centre Back", "Centre Back", "Right Centre Back"]
        )].copy()
    elif grupo == "Carrileros/Laterales":
        df_radar = df_radar[df_radar["PosPrim"].isin(
            ["Left Back", "Left Wing Back", "Right Back", "Right Wing Back"]
        )].copy()
    elif grupo == "Contenciones":
        df_radar = df_radar[df_radar["PosPrim"].isin(
            ["Centre Defensive Midfielder", "Left Defensive Midfielder", "Right Defensive Midfielder"]
        )].copy()
    elif grupo == "Interiores":
        pos_interiores = [
            "Centre Midfielder", "Central Midfielder",
            "Left Centre Midfielder", "Right Centre Midfielder"
        ]
        df_radar = df_radar[df_radar["PosPrim"].isin(pos_interiores)].copy()
    elif grupo == "Volantes Ofensivos":
        pos_vo = [
            "Centre Attacking Midfielder", "Right Attacking Midfielder", "Left Attacking Midfielder"
        ]
        df_radar = df_radar[df_radar["PosPrim"].isin(pos_vo)].copy()
    elif grupo == "Extremos":
        pos_extremos = [
            "Left Wing", "Right Wing",
            "Left Winger", "Right Winger",
            "Left Midfielder", "Right Midfielder"
        ]
        df_radar = df_radar[df_radar["PosPrim"].isin(pos_extremos)].copy()
    else:  # Delanteros
        pos_del = [
            "Centre Forward", "Left Centre Forward", "Right Centre Forward",
            "Striker", "Second Striker",
            "Left Forward", "Right Forward", "Forward"
        ]
        df_radar = df_radar[df_radar["PosPrim"].isin(pos_del)].copy()

    # Minutos (convertimos a numérico por si vienen strings)
    st.sidebar.markdown("### Minutos Jugados")
    if not df_radar.empty and "Minutes" in df_radar.columns:
        df_radar["Minutes"] = pd.to_numeric(df_radar["Minutes"], errors="coerce")
        if df_radar["Minutes"].notna().any():
            min_mins = int(np.nanmin(df_radar["Minutes"]))
            max_mins = int(np.nanmax(df_radar["Minutes"]))
            min_default = max(600, min_mins)
            if min_mins < max_mins:
                minutos_sel = st.sidebar.slider("Rango de Minutos Jugados", min_mins, max_mins, (min_default, max_mins))
                df_radar = df_radar[df_radar["Minutes"].between(minutos_sel[0], minutos_sel[1])]
            else:
                st.sidebar.info(f"Todos los jugadores tienen {min_mins} minutos — se omite el filtro.")
        else:
            st.sidebar.info("Todos los 'Minutes' son NaN — se omite el filtro.")
    else:
        st.warning("La base no contiene la columna 'Minutes' o está vacía."); st.stop()

    # Nacionalidad
    st.sidebar.markdown("### Filtrar por Nacionalidad")
    nationalities = sorted(df_radar["Nationality"].dropna().astype(str).unique())
    select_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True)
    selected_nats = nationalities if select_all else st.sidebar.multiselect("Nacionalidades", nationalities, default=nationalities)
    df_radar = df_radar[df_radar["Nationality"].isin(selected_nats)]
    if df_radar.empty:
        st.warning("No hay jugadores que cumplan los filtros."); st.stop()

    # =========================
    # Fases por grupo + métricas a invertir
    # =========================
    if grupo == "Porteros":
        fases_juego = {
            "Defensivas": [
                "PSxG Faced", "GSAA", "Save%", "xSv%", "Shot Stopping%", "Shots Faced", "Shots Faced OT%"
            ],
            "Posesión": [
                "GK Aggressive Dist.", "Claims%", "OP Passes", "Passing%", "Passes Pressured%", "Pass Forward%",
                "Carries", "Successful Dribbles"
            ],
            "Ofensivas": [
                "Pass OBV", "Goalkeeper OBV"
            ],
        }
        invertir_vars = {"PSxG Faced", "Shots Faced", "Shots Faced OT%"}

    elif grupo == "Centrales":
        fases_juego = {
            "Defensivas": [
                "PAdj Tackles", "PAdj Interceptions", "Blocks/Shot", "Clearances",
                "Aerial Win%", "Aerial Wins", "Dribbles Stopped%", "DA OBV",
                "Aggressive Actions", "PAdj Pressures", "Ball Recoveries", "Counterpress Regains"
            ],
            "Posesión": [
                "Pass OBV", "xGBuildup", "xGChain", "OP Passes", "OP F3 Passes",
                "Pass Forward%", "Passing%", "Passes Pressured%",
                "Long Balls", "Long Ball%", "Carries"
            ],
            "Ofensivas": [
                "Assists", "xG Assisted", "Key Passes", "D&C OBV", "OBV", "Shot OBV", "Throughballs"
            ],
        }
        invertir_vars = {"Dribbled Past", "Errors Leading to Shots"} & set(df_radar.columns)

    elif grupo == "Carrileros/Laterales":
        fases_juego = {
            "Defensivas": [
                "PAdj Interceptions", "PAdj Clearances",
                "Defensive Regains", "Ball Recoveries", "PAdj Tackles",
                "Dribbles Stopped%", "Counterpress Regains",
                "DA OBV"
            ],
            "Posesión": [
                "OP Passes", "Passing%",
                "Carries", "Successful Dribbles", "Deep Progressions",
                "xGBuildup", "xGChain", "Long Ball%",
                "Pass OBV", "D&C OBV"
            ],
            "Ofensivas": [
                "xG Assisted", "Key Passes", "Assists", "Successful Crosses", "Successful Box Cross%",
                "Passes Inside Box", "PintoB", "Shot OBV", "OBV"
            ],
        }
        invertir_vars = {"Dribbled Past", "Errors Leading to Shots"} & set(df_radar.columns)

    elif grupo == "Contenciones":
        fases_juego = {
            "Defensivas": [
                "PAdj Interceptions", "Defensive Regains", "PAdj Tackles",
                "Dribbles Stopped%", "PAdj Pressures", "Counterpress Regains",
                "Blocks/Shot", "DA OBV", "Aggressive Actions", "Ball Recoveries"
            ],
            "Posesión": [
                "OP Passes", "Passing%", "Passes Pressured%", "Pass Forward%",
                "Carries", "Successful Dribbles", "Deep Progressions",
                "xGBuildup", "xGChain", "Pass OBV", "D&C OBV"
            ],
            "Ofensivas": [
                "Assists", "xG Assisted", "Key Passes",
                "Throughballs", "PintoB", "Shot OBV", "OBV",
                "xG", "Shooting%"
            ],
        }
        invertir_vars = {"Dribbled Past", "Errors Leading to Shots"} & set(df_radar.columns)

    elif grupo == "Interiores":
        fases_juego = {
            "Defensivas": [
                "PAdj Interceptions", "Defensive Regains", "PAdj Tackles",
                "Dribbles Stopped%", "PAdj Pressures", "Counterpress Regains",
                "Blocks/Shot", "DA OBV", "Aggressive Actions", "Ball Recoveries"
            ],
            "Posesión": [
                "OP Passes", "Passing%", "Passes Pressured%", "Pass Forward%",
                "Carries", "Successful Dribbles", "Deep Progressions",
                "xGBuildup", "xGChain", "Pass OBV", "D&C OBV"
            ],
            "Ofensivas": [
                "Assists", "xG Assisted", "Key Passes",
                "Throughballs", "PintoB", "Shot OBV", "OBV",
                "xG", "Shooting%"
            ],
        }
        invertir_vars = {"Dribbled Past", "Errors Leading to Shots"} & set(df_radar.columns)

    elif grupo == "Volantes Ofensivos":
        fases_juego = {
            "Defensivas": [
                "Counterpress Regains", "PAdj Pressures", "Pressures",
                "Ball Recoveries", "PAdj Tackles", "PAdj Interceptions"
            ],
            "Posesión": [
                "OP Passes", "Passing%", "Passes Pressured%", "Pass Forward%",
                "Carries", "Successful Dribbles", "Deep Progressions",
                "xGBuildup", "xGChain", "OP F3 Passes", "F3 Pass Forward%",
                "Passes Inside Box", "PintoB",
                "Pass OBV", "D&C OBV"
            ],
            "Ofensivas": [
                "Assists", "xG Assisted", "Key Passes", "Throughballs",
                "OBV", "Shot OBV",
                "NP Goals", "xG/Shot", "PSxG", "Shots", "Goal Conversion%"
            ],
        }
        invertir_vars = {"Dribbled Past", "Errors Leading to Shots"} & set(df_radar.columns)

    elif grupo == "Extremos":
        fases_juego = {
            "Defensivas": [
                "Counterpress Regains", "Pressures", "PAdj Pressures",
                "Defensive Regains", "Ball Recoveries",
                "PAdj Tackles", "PAdj Interceptions", "Dribbles Stopped%"
            ],
            "Posesión": [
                "Carries", "Successful Dribbles", "Deep Progressions",
                "OP Passes", "Passing%", "Passes Pressured%", "Pass Forward%",
                "OP F3 Passes", "F3 Pass Forward%",
                "xGBuildup", "xGChain",
                "Pass OBV", "D&C OBV"
            ],
            "Ofensivas": [
                "xG Assisted", "Key Passes", "Assists",
                "Successful Crosses", "Successful Box Cross%",
                "Passes Inside Box", "PintoB",
                "OBV", "Shot OBV",
                "NP Goals", "xG/Shot", "PSxG", "Shots", "Goal Conversion%"
            ],
        }
        invertir_vars = {"Dribbled Past", "Errors Leading to Shots"} & set(df_radar.columns)

    else:  # Delanteros
        fases_juego = {
            "Defensivas": [
                "Counterpress Regains", "Pressures", "PAdj Pressures",
                "Ball Recoveries", "PAdj Tackles", "PAdj Interceptions",
                "Dribbles Stopped%", "Aerial Wins", "Aerial Win%"
            ],
            "Posesión": [
                "Carries", "Successful Dribbles", "Deep Progressions",
                "OP Passes", "Passing%", "Passes Pressured%", "Pass Forward%",
                "OP F3 Passes", "F3 Pass Forward%",
                "Passes Inside Box", "xGBuildup", "xGChain",
                "PintoB", "Pass OBV", "D&C OBV"
            ],
            "Ofensivas": [
                "Shot OBV", "OBV",
                "NP Goals", "xG/Shot", "PSxG", "Shots", "Goal Conversion%",
                "xG Assisted", "Key Passes", "Assists", "Throughballs"
            ],
        }
        invertir_vars = {"Dribbled Past", "Errors Leading to Shots"} & set(df_radar.columns)

    # Jugador
    st.markdown("### Jugador")
    jugadores_disponibles = sorted(df_radar["Name"].dropna().astype(str).unique())
    if not jugadores_disponibles:
        st.warning("No hay jugadores tras aplicar filtros."); st.stop()
    jugador_sel = st.selectbox("Jugador", jugadores_disponibles, index=0)

    # =========================
    # Modo de selección de variables
    # =========================
    st.markdown("### Modo de variables para el radar")
    modo_radar = st.radio(
        "Elige cómo quieres armar el radar:",
        ["Radar predeterminado", "Seleccionar variables para el radar"],
        index=0,
        horizontal=True
    )

    # Construimos el diccionario de fases efectivas según el modo
    fases_activas = {}

    if modo_radar == "Radar predeterminado":
        # Usamos todas las variables definidas originalmente
        fases_activas = {
            fase: [v for v in vars_fase if v in df_radar.columns]
            for fase, vars_fase in fases_juego.items()
        }
        # Quitamos fases vacías
        fases_activas = {f: vs for f, vs in fases_activas.items() if vs}

    else:
        # Modo personalizado: el usuario elige variables por fase
        st.markdown("#### Selecciona las variables por fase de juego")
        st.caption("Solo se muestran variables que existen en la base filtrada.")
        for fase, vars_fase in fases_juego.items():
            disponibles = [v for v in vars_fase if v in df_radar.columns]
            if not disponibles:
                continue

            seleccionadas = st.multiselect(
                f"{fase}",
                options=disponibles,
                default=disponibles,   # si quieres obligar a elegir desde cero, pon default=[]
                key=f"ms_{fase}_{grupo}"
            )
            if seleccionadas:
                fases_activas[fase] = seleccionadas

        if not fases_activas:
            st.warning("No has seleccionado ninguna métrica para el radar.")
            st.stop()

    # =========================
    # Render: radar centrado + grilla 3×N de distribuciones
    # =========================
    if jugador_sel and fases_activas:
        # Radar centrado
        left, mid, right = st.columns([0.05, 0.90, 0.05])
        with mid:
            fig = radar_barras_plotly(
                jugador=jugador_sel,
                df=df_radar,
                fases_juego=fases_activas,   # usamos fases activas (default o custom)
                invertir_vars=invertir_vars,
                colores_fases=("rgba(59,130,246,0.90)", "rgba(245,158,11,0.90)", "rgba(16,185,129,0.90)"),
                chart_height=640,
                show_silueta=False
            )
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, theme=None)

        # Distribuciones en grilla 3×N (relleno naranja, línea negra)
        st.markdown("#### Distribuciones por métrica")
        charts = build_kde_charts(
            df=df_radar,
            jugador=jugador_sel,
            fases_juego=fases_activas,   # también solo para las variables activas
            height_each=120
        )
        if charts:
            for i in range(0, len(charts), 3):
                cols = st.columns(3, gap="large")
                for j in range(3):
                    if i + j < len(charts):
                        with cols[j]:
                            st.altair_chart(charts[i + j], use_container_width=True, theme=None)



##############################################################################################################
############################## Datos Físicos #################################################################
##############################################################################################################


elif seleccion == "Estadísticas Físicas":
    import numpy as np
    import pandas as pd
    import altair as alt
    import plotly.graph_objects as go
    import unicodedata

    st.markdown("<h3 style='margin-bottom: 15px;'>Estadísticas Físicas</h3>", unsafe_allow_html=True)

    # =========================
    # Colores / estilo
    # =========================
    ORANGE    = "#f9ae34"   # resaltados y relleno KDE
    GRAY_BASE = "#C5C5C5"   # puntos base
    AXIS_COL  = "#2B2B2B"

    # =========================
    # Helpers
    # =========================
    def _load_fisico(path: str) -> pd.DataFrame:
        """Lee CSV delimitado por ';' y castea numéricos en lo posible."""
        df = pd.read_csv(path, sep=";")
        non_numeric = {"Player","Short Name","Player ID","Birthdate","Position","Position Group"}
        for c in df.columns:
            if c not in non_numeric:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        if "Player" in df.columns:
            df["Player"] = df["Player"].astype(str).str.strip()
        return df

    def _pick_mpm_column(df: pd.DataFrame) -> str | None:
        """Intenta detectar la columna 'minutos por partido' si existiera (por nombre)."""
        explicit = [
            "Minutes per Match", "Minutos por Partido", "Min/Match", "Minutes/Match",
            "Minutos promedio por partido", "Min per match", "MPM"
        ]
        for c in explicit:
            if c in df.columns:
                return c
        for c in df.columns:
            cl = c.lower()
            if ("min" in cl or "minut" in cl) and ("match" in cl or "partido" in cl or "/match" in cl or " per " in cl):
                return c
        return None

    def _norm_text(s: str) -> str:
        if not isinstance(s, str):
            s = "" if pd.isna(s) else str(s)
        s = s.strip()
        s = unicodedata.normalize("NFKD", s)
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
        s = " ".join(s.split())
        return s

    def _player_key_series(df: pd.DataFrame) -> pd.Series:
        if "Player ID" in df.columns and df["Player ID"].notna().any():
            return df["Player ID"].astype(str).str.strip()
        if "Player" in df.columns:
            return df["Player"].astype(str).map(_norm_text)
        return pd.Series([f"row_{i}" for i in range(len(df))], index=df.index)

    def _map_grupo(pos_code: str) -> str:
        """Mapea códigos de posición a grupos estándar (sin GK/Otros en selector)."""
        if not isinstance(pos_code, str):
            return "Otros"
        p = pos_code.upper().strip()
        if p in {"CB","LCB","RCB"}: return "Centrales"
        if p in {"LB","LWB","RB","RWB"}: return "Carrileros/Laterales"
        if p in {"DM","CDM","LDM","RDM"}: return "Contenciones"
        if p in {"CM","LCM","RCM","CMF","LM","RM"}: return "Interiores"
        if p in {"AM","CAM"}: return "Volantes Ofensivos"
        if p in {"LW","RW"}: return "Extremos"
        if p in {"CF","ST","LF","RF","SS","FW","FWD"}: return "Delanteros"
        if p in {"GK","GKP","GOALKEEPER"}: return "Porteros"
        return "Otros"

    def _dedupe_by_player_within_group(df: pd.DataFrame, mpm_col: str | None, minutes_fallback: str = "Minutes") -> pd.DataFrame:
        """
        Conservar UNA fila por (Jugador, Grupo):
        - Prioriza mayor Minutes (si existe),
        - Si no existe Minutes, usa mayor minutos/partido (MPM).
        """
        key = _player_key_series(df)
        df = df.copy()
        df["_PlayerKey"] = key

        if "Minutes" in df.columns and df["Minutes"].notna().any():
            base = pd.to_numeric(df["Minutes"], errors="coerce").fillna(-1e12)
        elif mpm_col and mpm_col in df.columns:
            base = pd.to_numeric(df[mpm_col], errors="coerce").fillna(-1e12)
        else:
            base = pd.Series(-1e12, index=df.index, dtype=float)

        df["_score"] = base
        idx = df.groupby(["_PlayerKey", "Grupo"], dropna=False)["_score"].idxmax()
        out = df.loc[idx].copy()
        return out.drop(columns=["_score"])

    def _numeric_cols(df: pd.DataFrame, exclude_cols=(), exclude_contains=()):
        out = []
        exclude_contains = set(exclude_contains or [])
        for c in df.columns:
            if c in exclude_cols: continue
            if any(substr in c for substr in exclude_contains): continue
            if pd.api.types.is_numeric_dtype(df[c]): out.append(c)
        return out

    def _compute_age_col(df: pd.DataFrame) -> pd.Series:
        if "Birthdate" not in df.columns:
            return pd.Series([np.nan]*len(df), index=df.index)
        bd = pd.to_datetime(df["Birthdate"], errors="coerce", utc=True)
        today = pd.Timestamp("today", tz="UTC")
        return (today - bd).dt.days / 365.25

    def _domain_with_pad(series: pd.Series, pad_ratio=0.08):
        s = pd.to_numeric(series, errors="coerce").dropna()
        if s.empty:
            return None
        mn, mx = float(s.min()), float(s.max())
        if mn == mx:
            pad = max(abs(mn), 1.0) * pad_ratio
            return [mn - pad, mx + pad]
        span = (mx - mn) * pad_ratio
        return [mn - span, mx + span]

    def _is_inverse_metric(name: str) -> bool:
        """Métricas donde menor=mejor (tiempos)."""
        if not isinstance(name, str): return False
        n = name.lower()
        return ("time to hsr" in n) or ("time to sprint" in n)

    # Normalización (0–1) para radar
    def _normalize_metrics(df, metrics, invert=None):
        invert = set(invert or [])
        out = df.copy()
        for m in metrics:
            if m not in out.columns: continue
            s = pd.to_numeric(out[m], errors="coerce")
            mn, mx = s.min(), s.max()
            if pd.isna(mn) or pd.isna(mx) or mx == mn:
                out[m] = 0.5
            else:
                z = (s - mn) / (mx - mn)
                out[m] = (1 - z) if m in invert else z
                out[m] = out[m].fillna(0.5)
        return out

    # ------------- Radar por fases (Plotly) -------------
    def radar_barras_plotly_player(
        jugador,
        df,
        fases_juego,
        id_col="Player",
        invertir_vars=None,
        colores_fases=("rgba(59,130,246,0.90)", "rgba(245,158,11,0.90)", "rgba(16,185,129,0.90)"),
        chart_height=640
    ):
        if id_col not in df.columns:
            st.warning(f"La base no tiene la columna '{id_col}'."); return None
        if jugador not in df[id_col].values:
            st.warning(f"El jugador '{jugador}' no está en la base."); return None

        invertir = set(invertir_vars or [])
        atributos, fase_idx = [], []
        fases_orden = list(fases_juego.keys())
        for i, (fase, vars_fase) in enumerate(fases_juego.items()):
            presentes = [v for v in vars_fase if v in df.columns]
            atributos.extend(presentes)
            fase_idx.extend([i] * len(presentes))
        if not atributos:
            st.warning("No hay variables presentes para construir el radar."); return None

        df_norm = _normalize_metrics(df, atributos, invert=invertir)
        row = df_norm.loc[df_norm[id_col] == jugador].iloc[0]
        r_vals = [float(row[a]) * 100 for a in atributos]

        n = len(atributos)
        thetas = np.linspace(0, 360, n, endpoint=False)

        fig = go.Figure()
        for i, fase in enumerate(fases_orden):
            idxs = [k for k, fidx in enumerate(fase_idx) if fidx == i]
            if not idxs: continue
            fig.add_trace(go.Barpolar(
                r=[r_vals[k] for k in idxs],
                theta=[thetas[k] for k in idxs],
                width=[(360/n)*0.98]*len(idxs),
                marker=dict(color=colores_fases[i], line=dict(width=0)),
                name=fase,
                hovertemplate="<b>%{customdata[0]}</b><br>Percentil: %{r:.1f}<extra></extra>",
                customdata=[[atributos[k]] for k in idxs],
                opacity=0.95,
            ))

        # etiquetas
        fig.add_trace(go.Scatterpolar(
            r=[110]*n, theta=thetas, mode="text", text=atributos,
            textfont=dict(size=11, color=AXIS_COL),
            textposition="middle center", hoverinfo="skip", showlegend=False
        ))

        fig.update_layout(
            template="plotly_white", height=chart_height,
            margin=dict(l=10, r=10, t=40, b=40),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    range=[0,112], tickvals=[0,20,40,60,80,100],
                    ticktext=["0","20","40","60","80","100"],
                    showline=True, gridcolor="#E5E5E5", gridwidth=1,
                    tickfont=dict(size=11, color=AXIS_COL),
                ),
                angularaxis=dict(
                    rotation=0, direction="clockwise", showline=False,
                    gridcolor="#F0F0F0", gridwidth=1,
                    tickfont=dict(size=10, color="#B3B3B3"),
                    ticks="",
                ),
            ),
            legend=dict(
                orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5,
                font=dict(size=12, color=AXIS_COL), bgcolor="rgba(0,0,0,0)",
            ),
            title=dict(text=f"Radar físico · {jugador}", x=0.01, y=0.98, font=dict(size=18, color="#111111")),
        )
        return fig

    # ---------- KDE (relleno naranja, línea/contorno negro, con inversión opcional) ----------
    def _kde_chart_altair(df, metric, jugador_val, invert=False, fill_color=ORANGE, height=120):
        serie = (
            pd.to_numeric(df[metric], errors="coerce")
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
            .astype(float)
        )
        if serie.empty or pd.isna(jugador_val):
            return None

        mn, mx = float(serie.min()), float(serie.max())
        if mn == mx:
            pad = max(abs(mn), 1.0) * 0.10
            mn, mx = mn - pad, mx + pad
        else:
            pad = (mx - mn) * 0.10
            mn, mx = mn - pad, mx + pad

        data_num = pd.DataFrame({"value": serie})

        base = alt.Chart(data_num).transform_density(
            "value", as_=["x", "density"], extent=[mn, mx], steps=200
        )

        # Relleno naranja hasta el valor del jugador
        area = base.transform_filter(
            alt.datum.x <= float(jugador_val)
        ).mark_area(
            opacity=0.28, color=fill_color
        ).encode(
            x=alt.X("x:Q", title=None, scale=alt.Scale(reverse=bool(invert))),
            y=alt.Y("density:Q", title=None)
        )

        # Línea/contorno negro
        line = base.mark_line(color="#000000", size=1.2).encode(
            x=alt.X("x:Q", scale=alt.Scale(reverse=bool(invert))),
            y="density:Q"
        )

        # Regla negra en el valor del jugador
        rule = alt.Chart(pd.DataFrame({"x": [float(jugador_val)]})).mark_rule(
            color="#000000", strokeWidth=2
        ).encode(
            x=alt.X("x:Q", scale=alt.Scale(reverse=bool(invert))),
            tooltip=[alt.Tooltip("x:Q", title="Valor", format=".3f")]
        )

        title = alt.TitleParams(metric, fontSize=12, anchor="middle", color="#1F2937")
        chart = (area + line + rule).properties(height=height, title=title)

        chart = chart.configure_axis(
            grid=False, domain=True, domainColor="#E6E6E6", labelColor="#2B2B2B"
        ).configure_view(
            strokeWidth=0
        ).configure_title(
            font="Inter", color="#111111", anchor="middle"
        )
        return chart

    def build_kde_charts(
        df,
        jugador,
        fases_juego,
        id_col="Player",
        invertir_vars_kde=None,   # set con nombres a invertir
        height_each=120
    ):
        invertir_vars_kde = set(invertir_vars_kde or [])
        charts = []
        if id_col not in df.columns or jugador not in df[id_col].values:
            return charts

        row = df.loc[df[id_col] == jugador].iloc[0]
        for fase, vars_fase in fases_juego.items():
            presentes = [v for v in vars_fase if v in df.columns]
            for m in presentes:
                val = pd.to_numeric(row.get(m, np.nan), errors="coerce")
                ch = _kde_chart_altair(
                    df, m, val,
                    invert=(m in invertir_vars_kde),
                    fill_color=ORANGE,
                    height=height_each
                )
                if ch is not None:
                    charts.append(ch)
        return charts

    # =========================
    # Catálogo ligas/temporadas (físico)
    # =========================
    ligas_temporadas_fis = {
        "Liga MX": ["2024/2025"],  # agrega más aquí
        "Liga Profesional, Argentina": ["2024"],  # agrega más aquí
        "Jupiler Pro League, Bélgica": ["2024/2025"],  # agrega más aquí
        "Serie A, Brasil": ["2024"],  # agrega más aquí
        "Primera División, Chile": ["2024"],  # agrega más aquí
        "Primera A, Colombia": ["2024"],  # agrega más aquí
        "Liga Pro, Ecuador": ["2024"],  # agrega más aquí
        "Premier League, Inglaterra": ["2024/2025"],  # agrega más aqui
        "La Liga, España": ["2024/2025"],  # agrega más aquí
        "Ligue 1, Francia": ["2024/2025"],  # agrega más aquí
        "Bundesliga, Alemania": ["2024/2025"],  # agrega más aquí
        "Serie A, Italia": ["2024/2025"],  # agrega más aquí
        "Primeira Liga, Portugal": ["2024/2025"],  # agrega más aqu
        "Primera División, Uruguay": ["2024"],  # agrega más aqu
        "MLS, Estados Unidos": ["2024"],  # agrega más aquí


    }
    archivos_fis = {
        ("Liga MX", "2024/2025"): "ligamxfisico.csv",
        ("Liga Profesional, Argentina", "2024"): "argfisico.csv",
        ("Jupiler Pro League, Bélgica", "2024/2025"): "belfisico.csv",
        ("Serie A, Brasil", "2024"): "brafisico.csv",
        ("Primera División, Chile", "2024"): "chifisico.csv",
        ("Primera A, Colombia", "2024"): "colfisico.csv",
        ("Liga Pro, Ecuador", "2024"): "ecufisico.csv",
        ("Premier League, Inglaterra", "2024/2025"): "engfisico.csv",
        ("La Liga, España", "2024/2025"): "espfisico.csv",
        ("Ligue 1, Francia", "2024/2025"): "frafisico.csv",
        ("Bundesliga, Alemania", "2024/2025"): "gerfisico.csv",
        ("Serie A, Italia", "2024/2025"): "itafisico.csv",
        ("Primeira Liga, Portugal", "2024/2025"): "porfisico.csv",
        ("Primera División, Uruguay", "2024"): "urufisico.csv",
        ("MLS, Estados Unidos", "2024"): "usafisico.csv",
    }

    # =========================
    # Sidebar (Liga -> Vista -> Grupo -> Filtros)
    # =========================
    with st.sidebar:
        st.markdown("### Liga y Temporada")
        liga = st.selectbox("Liga", list(ligas_temporadas_fis.keys()), index=0)
        temporada = st.selectbox("Temporada", ligas_temporadas_fis[liga], index=0)

        path = archivos_fis.get((liga, temporada))
        if not path:
            st.error("No hay archivo configurado para esa liga/temporada."); st.stop()
        df_f = _load_fisico(path)

        MPM_COL = _pick_mpm_column(df_f)   # para posible fallback
        df_f["Grupo"] = df_f["Position"].apply(_map_grupo)
        df_f["Age"] = _compute_age_col(df_f)

        st.markdown("### Vista")
        modo = st.radio("Selecciona", ["Scatterplot", "Radares Físicos"], index=0, horizontal=False)

        st.markdown("### Grupo de Posición")
        grupos_ok = ["Centrales","Carrileros/Laterales","Contenciones","Interiores","Volantes Ofensivos","Extremos","Delanteros"]
        grupo_sel = st.radio("Grupo", grupos_ok, index=0)

        st.markdown("### Filtros")
        if df_f["Age"].notna().any():
            age_min = int(np.nanmin(df_f["Age"]))
            age_max = int(np.nanmax(df_f["Age"]))
            edad_sel = st.slider("Edad", min_value=age_min, max_value=age_max, value=(max(17, age_min), age_max))
        else:
            edad_sel = None
            st.caption("No se pudo derivar 'Edad' desde Birthdate.")

    # Subset por grupo y filtros
    df_view = df_f[df_f["Grupo"] == grupo_sel].copy()
    if edad_sel:
        df_view = df_view[df_view["Age"].between(edad_sel[0], edad_sel[1])]

    # Deduplicar por jugador dentro del grupo (Minutes -> MPM -> fallback)
    df_view = _dedupe_by_player_within_group(df_view, MPM_COL, minutes_fallback="Minutes")

    if df_view.empty:
        st.info("No hay jugadores tras aplicar los filtros seleccionados."); st.stop()

    # =========================
    # SCATTERPLOT
    # =========================
    if modo == "Scatterplot":
        st.markdown("#### Variables del gráfico (elige X e Y)")

        exclude_exact = {"Player","Short Name","Player ID","Birthdate","Position","Position Group","Grupo","Age","Minutes"}
        exclude_contains = {"Count Performances"}
        num_cols = _numeric_cols(df_view, exclude_cols=exclude_exact, exclude_contains=exclude_contains)
        if not num_cols:
            st.warning("No se encontraron métricas físicas numéricas válidas para graficar."); st.stop()

        def _first_present(cands, pool):
            for c in cands:
                if c in pool: return c
            return pool[0]

        default_x = ["HSR Distance P60BIP","PSV-99","Sprint Distance P60BIP","Running Distance P60BIP","Distance P60BIP"]
        default_y = ["Sprint Distance P60BIP","TOP 5 PSV-99","HSR Count P60BIP","HI Distance BIP P60BIP","M/min BIP P60BIP"]

        colx, coly = st.columns(2)
        with colx:
            x_var = st.selectbox("Eje X", options=num_cols, index=num_cols.index(_first_present(default_x, num_cols)))
        with coly:
            y_var = st.selectbox("Eje Y", options=num_cols, index=num_cols.index(_first_present(default_y, num_cols)))

        # tamaño fijo por Minutes (si existe)
        SIZE_COL = "Minutes" if "Minutes" in df_view.columns and pd.api.types.is_numeric_dtype(df_view["Minutes"]) else None

        # dominios con padding (para que "re-zoomee" al cambiar variables)
        x_dom = _domain_with_pad(df_view[x_var])
        y_dom = _domain_with_pad(df_view[y_var])

        # invertir ejes si son métricas de tiempo (menor=mejor)
        x_scale = alt.Scale(domain=x_dom, nice=True, zero=False, reverse=_is_inverse_metric(x_var))
        y_scale = alt.Scale(domain=y_dom, nice=True, zero=False, reverse=_is_inverse_metric(y_var))

        jugadores = sorted(df_view["Player"].dropna().astype(str).unique())
        hi_sel = st.multiselect("Resalta jugadores", jugadores, default=[])

        d = df_view.copy()
        d["is_highlight"] = d["Player"].isin(hi_sel)

        sel = alt.selection_point(fields=["Player"], on="click", toggle=True, clear="dblclick", empty="none")

        base = alt.Chart(d).encode(
            x=alt.X(x_var, title=x_var, axis=alt.Axis(format="~s"), scale=x_scale),
            y=alt.Y(y_var, title=y_var, axis=alt.Axis(format="~s"), scale=y_scale),
            tooltip=[
                alt.Tooltip("Player:N", title="Jugador"),
                alt.Tooltip("Position:N", title="Posición"),
                alt.Tooltip("Grupo:N", title="Grupo"),
                alt.Tooltip(x_var, title=x_var, format=",.2f"),
                alt.Tooltip(y_var, title=y_var, format=",.2f"),
                alt.Tooltip("Minutes:Q", title="Minutes", format=",.0f") if SIZE_COL else alt.Tooltip("Player:N", title=""),
            ]
        )

        size_enc = alt.Size(SIZE_COL, legend=None, scale=alt.Scale(range=[30, 500])) if SIZE_COL else alt.value(120)

        pts_base = base.mark_circle().encode(size=size_enc, color=alt.value(GRAY_BASE), opacity=alt.value(0.35))
        pts_sel  = base.transform_filter(sel).mark_circle().encode(size=size_enc, color=alt.value(ORANGE), opacity=alt.value(1.0)).add_params(sel)
        pts_list = base.transform_filter(alt.datum.is_highlight).mark_circle().encode(size=size_enc, color=alt.value(ORANGE), opacity=alt.value(1.0))

        labels_sel = base.transform_filter(sel).mark_text(dx=6, dy=-6, fontWeight="bold", color="#000000", clip=False).encode(text="Player:N")
        labels_list = base.transform_filter(alt.datum.is_highlight).mark_text(dx=6, dy=-6, fontWeight="bold", color="#000000", clip=False).encode(text="Player:N")

        x_mean = float(d[x_var].mean(skipna=True)); y_mean = float(d[y_var].mean(skipna=True))
        vline  = alt.Chart(pd.DataFrame({"v":[x_mean]})).mark_rule(strokeDash=[5,5], color="#9A9A9A", opacity=0.8).encode(x="v:Q")
        hline  = alt.Chart(pd.DataFrame({"h":[y_mean]})).mark_rule(strokeDash=[5,5], color="#9A9A9A", opacity=0.8).encode(y="h:Q")

        chart = (pts_base + pts_sel + pts_list + labels_sel + labels_list + vline + hline).properties(
            height=560, background="transparent",
            padding={"left": 10, "right": 160, "top": 40, "bottom": 30}
        ).configure_view(strokeWidth=0).configure_axis(
            grid=False, domain=False, tickColor=AXIS_COL, labelColor=AXIS_COL, titleColor=AXIS_COL
        )

        st.altair_chart(chart, use_container_width=True, theme=None)

    # =========================
    # Radares FÍSICOS + KDE
    # =========================
    else:
        st.markdown("#### Radares Físicos")

        fases_fisicas = {
            "Volumen": [
                "Distance P60BIP", "M/min BIP P60BIP", "Running Distance P60BIP",
                "HI Distance BIP P60BIP", "HI Count BIP P60BIP"
            ],
            "Alta Intensidad & Sprints": [
                "HSR Distance P60BIP", "HSR Count P60BIP",
                "Sprint Distance P60BIP", "Sprint Count P60BIP",
                "Explosive Acceleration to HSR Count P60BIP",
                "Explosive Acceleration to Sprint Count P60BIP"
            ],
            "Velocidad / Tiempo": [
                "PSV-99", "TOP 5 PSV-99",
                "TOP 3 Time to HSR", "TOP 3 Time to Sprint"  # inversas (menor=mejor)
            ],
        }
        invertir_vars = {"TOP 3 Time to HSR", "TOP 3 Time to Sprint"}

        jugadores = sorted(df_view["Player"].dropna().astype(str).unique())
        if not jugadores:
            st.warning("No hay jugadores tras aplicar filtros."); st.stop()
        jugador_sel = st.selectbox("Jugador", jugadores, index=0)

        # Radar centrado
        left, mid, right = st.columns([0.05, 0.90, 0.05])
        with mid:
            fig = radar_barras_plotly_player(
                jugador=jugador_sel,
                df=df_view,
                fases_juego=fases_fisicas,
                id_col="Player",
                invertir_vars=invertir_vars,
                colores_fases=("rgba(59,130,246,0.90)", "rgba(245,158,11,0.90)", "rgba(16,185,129,0.90)"),
                chart_height=640
            )
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, theme=None)

        # KDE por métrica (3 por fila), con inversión de eje para métricas inversas
        st.markdown("#### Distribuciones por métrica")
        charts = build_kde_charts(
            df=df_view,
            jugador=jugador_sel,
            fases_juego=fases_fisicas,
            id_col="Player",
            invertir_vars_kde=invertir_vars,
            height_each=120
        )
        if charts:
            for i in range(0, len(charts), 3):
                cols = st.columns(3, gap="large")
                for j in range(3):
                    if i + j < len(charts):
                        with cols[j]:
                            st.altair_chart(charts[i + j], use_container_width=True, theme=None)







##############################################################################################################
############################## Juego Bajo Presión ############################################################
##############################################################################################################



elif seleccion == "Juego Bajo Presión":
    import numpy as np
    import pandas as pd
    import altair as alt
    import plotly.graph_objects as go

    st.markdown("<h3 style='margin-bottom: 15px;'>Juego Bajo Presión</h3>", unsafe_allow_html=True)

    # ===== Estilo (idéntico a 'Estadísticas Físicas') =====
    ORANGE     = "#f9ae34"
    GRAY_BASE  = "#C5C5C5"
    AXIS_COL   = "#2B2B2B"
    LINE_BLACK = "#111111"

    # =========================
    # Helpers
    # =========================
    def _load_presion(path: str) -> pd.DataFrame:
        # Intentar ';' y fallback a ','
        try:
            df = pd.read_csv(path, sep=";")
            if df.shape[1] == 1:
                df = pd.read_csv(path)  # fallback coma
        except Exception:
            df = pd.read_csv(path)

        # Cast a numérico lo que no sea texto/ID
        non_numeric = {"Player","Short name","Player ID","Birthdate","Position","third","channel"}
        for c in df.columns:
            if c not in non_numeric:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        if "Player" in df.columns:
            df["Player"] = df["Player"].astype(str).str.strip()
        return df

    def _minutes_for_score_original(df: pd.DataFrame) -> pd.Series:
        """
        Construye un score de 'minutos por partido' usando SOLO nombres ORIGINALES,
        para deduplicar ANTES de renombrar/descartar columnas.
        Orden de prioridad:
        1) Minutes played per match
        2) Adjusted min TIP per match
        3) Count Pressures received in sample (proxy)
        """
        cands = [
            "Minutes played per match",
            "Adjusted min TIP per match",
            "Count Pressures received in sample"
        ]
        base = pd.Series(-1e12, index=df.index, dtype=float)
        for c in cands:
            if c in df.columns:
                s = pd.to_numeric(df[c], errors="coerce")
                base = pd.Series(np.where(base < 0, s, base), index=df.index)
        return base

    def _map_grupo(pos_code: str) -> str:
        if not isinstance(pos_code, str): return "Otros"
        p = pos_code.upper().strip()
        if p in {"CB","LCB","RCB"}: return "Centrales"
        if p in {"LB","LWB","RB","RWB"}: return "Carrileros/Laterales"
        if p in {"DM","CDM","LDM","RDM"}: return "Contenciones"
        if p in {"CM","LCM","RCM","CMF","LM","RM"}: return "Interiores"
        if p in {"AM","CAM"}: return "Volantes Ofensivos"
        if p in {"LW","RW"}: return "Extremos"
        if p in {"CF","ST","LF","RF","SS","FW","FWD"}: return "Delanteros"
        if p in {"GK","GKP","GOALKEEPER"}: return "Porteros"
        return "Otros"

    def _compute_age_col(df: pd.DataFrame) -> pd.Series:
        if "Birthdate" not in df.columns:
            return pd.Series([np.nan]*len(df), index=df.index)
        bd = pd.to_datetime(df["Birthdate"], errors="coerce", utc=True)
        today = pd.Timestamp("today", tz="UTC")
        return (today - bd).dt.days / 365.25

    def _domain_with_pad(series: pd.Series, pad_ratio=0.08):
        s = pd.to_numeric(series, errors="coerce").dropna()
        if s.empty: return None
        mn, mx = float(s.min()), float(s.max())
        if mn == mx:
            pad = max(abs(mn), 1.0) * pad_ratio
            return [mn - pad, mx + pad]
        span = (mx - mn) * pad_ratio
        return [mn - span, mx + span]

    def _normalize_metrics(df, metrics, invert=None):
        invert = set(invert or [])
        out = df.copy()
        for m in metrics:
            if m not in out.columns: continue
            s = pd.to_numeric(out[m], errors="coerce")
            mn, mx = s.min(), s.max()
            if pd.isna(mn) or pd.isna(mx) or mx == mn:
                out[m] = 0.5
            else:
                z = (s - mn) / (mx - mn)
                out[m] = (1 - z) if m in invert else z
                out[m] = out[m].fillna(0.5)
        return out

    # ----- Radar (idéntico estilo al de Físicos) -----
    def radar_barras_plotly_player(
        jugador, df, fases_juego, id_col="Player",
        invertir_vars=None,
        colores_fases=("rgba(59,130,246,0.90)", "rgba(245,158,11,0.90)", "rgba(16,185,129,0.90)"),
        chart_height=640
    ):
        if id_col not in df.columns or jugador not in df[id_col].values:
            return None
        invertir = set(invertir_vars or [])
        atributos, fase_idx = [], []
        fases_orden = list(fases_juego.keys())
        for i, (fase, vars_fase) in enumerate(fases_juego.items()):
            prs = [v for v in vars_fase if v in df.columns]
            atributos.extend(prs)
            fase_idx.extend([i]*len(prs))
        if not atributos: return None

        df_norm = _normalize_metrics(df, atributos, invert=invertir)
        row = df_norm.loc[df_norm[id_col] == jugador].iloc[0]
        r_vals = [float(row[a])*100 for a in atributos]

        n = len(atributos)
        thetas = np.linspace(0, 360, n, endpoint=False)

        fig = go.Figure()
        for i, fase in enumerate(fases_orden):
            idxs = [k for k, fidx in enumerate(fase_idx) if fidx == i]
            if not idxs: continue
            fig.add_trace(go.Barpolar(
                r=[r_vals[k] for k in idxs],
                theta=[thetas[k] for k in idxs],
                width=[(360/n)*0.98]*len(idxs),
                marker=dict(color=colores_fases[i], line=dict(width=0)),
                name=fase,
                hovertemplate="<b>%{customdata[0]}</b><br>Percentil: %{r:.1f}<extra></extra>",
                customdata=[[atributos[k]] for k in idxs],
                opacity=0.95,
            ))

        fig.add_trace(go.Scatterpolar(
            r=[110]*n, theta=thetas, mode="text", text=atributos,
            textfont=dict(size=11, color=AXIS_COL),
            textposition="middle center", hoverinfo="skip", showlegend=False
        ))

        fig.update_layout(
            template="plotly_white", height=chart_height,
            margin=dict(l=10, r=10, t=40, b=40),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    range=[0,112], tickvals=[0,20,40,60,80,100],
                    ticktext=["0","20","40","60","80","100"],
                    showline=True, gridcolor="#E5E5E5", gridwidth=1,
                    tickfont=dict(size=11, color=AXIS_COL),
                ),
                angularaxis=dict(
                    rotation=0, direction="clockwise", showline=False,
                    gridcolor="#F0F0F0", gridwidth=1,
                    tickfont=dict(size=10, color="#B3B3B3"),
                    ticks="",
                ),
            ),
            legend=dict(
                orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5,
                font=dict(size=12, color=AXIS_COL), bgcolor="rgba(0,0,0,0)",
            ),
            title=dict(text=f"Radar · {jugador}", x=0.01, y=0.98, font=dict(size=18, color="#111111")),
        )
        return fig

    # ----- KDE (mismo estilo que Físicos) -----
    def _kde_chart_altair(df, metric, jugador_val, invert=False, fill_color=ORANGE, height=120):
        serie = (
            pd.to_numeric(df[metric], errors="coerce")
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
            .astype(float)
        )
        if serie.empty or pd.isna(jugador_val): return None

        mn, mx = float(serie.min()), float(serie.max())
        if mn == mx:
            pad = max(abs(mn), 1.0) * 0.10; mn, mx = mn - pad, mx + pad
        else:
            pad = (mx - mn) * 0.10; mn, mx = mn - pad, mx + pad

        data_num = pd.DataFrame({"value": serie})
        base = alt.Chart(data_num).transform_density("value", as_=["x","density"], extent=[mn, mx], steps=200)

        area = base.transform_filter(alt.datum.x <= float(jugador_val)).mark_area(opacity=0.28, color=fill_color)\
            .encode(x=alt.X("x:Q", title=None, scale=alt.Scale(reverse=bool(invert))),
                    y=alt.Y("density:Q", title=None))
        line = base.mark_line(color=LINE_BLACK, size=1.2)\
            .encode(x=alt.X("x:Q", scale=alt.Scale(reverse=bool(invert))), y="density:Q")
        rule = alt.Chart(pd.DataFrame({"x":[float(jugador_val)]})).mark_rule(color=LINE_BLACK, strokeWidth=2)\
            .encode(x=alt.X("x:Q", scale=alt.Scale(reverse=bool(invert))),
                    tooltip=[alt.Tooltip("x:Q", title="Valor", format=".3f")])

        chart = (area + line + rule).properties(height=height, title=alt.TitleParams(metric, fontSize=12, anchor="middle", color="#1F2937"))\
            .configure_axis(grid=False, domain=True, domainColor="#E6E6E6", labelColor=AXIS_COL)\
            .configure_view(strokeWidth=0)\
            .configure_title(font="Inter", color="#111111", anchor="middle")
        return chart

    def build_kde_charts(df, jugador, fases_juego, id_col="Player", invertir_vars_kde=None, height_each=120):
        invertir_vars_kde = set(invertir_vars_kde or [])
        charts = []
        if id_col not in df.columns or jugador not in df[id_col].values:
            return charts
        row = df.loc[df[id_col] == jugador].iloc[0]
        for _, vars_fase in fases_juego.items():
            prs = [v for v in vars_fase if v in df.columns]
            for m in prs:
                val = pd.to_numeric(row.get(m, np.nan), errors="coerce")
                ch = _kde_chart_altair(df, m, val, invert=(m in invertir_vars_kde), fill_color=ORANGE, height=height_each)
                if ch is not None: charts.append(ch)
        return charts

    # =========================
    # Sidebar (Liga / Temporada)
    # =========================

# =========================
    # Catálogo ligas/temporadas (físico)
    # =========================
    ligas_temporadas_presion = {
        "Liga MX": ["2024/2025"],  # agrega más aquí
        "Liga Profesional, Argentina": ["2024"],  # agrega más aquí
        "Jupiler Pro League, Bélgica": ["2024/2025"],  # agrega más aquí
        "Serie A, Brasil": ["2024"],  # agrega más aquí
        "Primera División, Chile": ["2024"],  # agrega más aquí
        "Primera A, Colombia": ["2024"],  # agrega más aquí
        "Liga Pro, Ecuador": ["2024"],  # agrega más aquí
        "Premier League, Inglaterra": ["2024/2025"],  # agrega más aqui
        "La Liga, España": ["2024/2025"],  # agrega más aquí
        "Ligue 1, Francia": ["2024/2025"],  # agrega más aquí
        "Bundesliga, Alemania": ["2024/2025"],  # agrega más aquí
        "Serie A, Italia": ["2024/2025"],  # agrega más aquí
        "Primeira Liga, Portugal": ["2024/2025"],  # agrega más aqu
        "Primera División, Uruguay": ["2024"],  # agrega más aqu
        "MLS, Estados Unidos": ["2024"],  # agrega más aquí


    }
    archivos_presion = {
        ("Liga MX", "2024/2025"): "ligamxpresion.csv",
        ("Liga Profesional, Argentina", "2024"): "argpresion.csv",
        ("Jupiler Pro League, Bélgica", "2024/2025"): "belpresion.csv",
        ("Serie A, Brasil", "2024"): "brapresion.csv",
        ("Primera División, Chile", "2024"): "chipresion.csv",
        ("Primera A, Colombia", "2024"): "colpresion.csv",
        ("Liga Pro, Ecuador", "2024"): "ecupresion.csv",
        ("Premier League, Inglaterra", "2024/2025"): "engpresion.csv",
        ("La Liga, España", "2024/2025"): "esppresion.csv",
        ("Ligue 1, Francia", "2024/2025"): "frapresion.csv",
        ("Bundesliga, Alemania", "2024/2025"): "gerpresion.csv",
        ("Serie A, Italia", "2024/2025"): "itapresion.csv",
        ("Primeira Liga, Portugal", "2024/2025"): "porpresion.csv",
        ("Primera División, Uruguay", "2024"): "urupresion.csv",
        ("MLS, Estados Unidos", "2024"): "usapresion.csv",
    }

    with st.sidebar:
        st.markdown("### Liga y Temporada")
        liga = st.selectbox("Liga", list(ligas_temporadas_presion.keys()), index=0)
        temporada = st.selectbox("Temporada", ligas_temporadas_presion[liga], index=0)

        path = archivos_presion.get((liga, temporada))
        if not path:
            st.error("No hay archivo configurado para esa liga/temporada."); st.stop()

        # ---------- ORDEN CORRECTO ----------
        # 1) Cargar (RAW)
        df_p_raw = _load_presion(path)

        # 2) Asignar Grupo (antes de deduplicar)
        df_p_raw["Grupo"] = df_p_raw["Position"].apply(_map_grupo)

        # 3) Deduplicar por (Jugador, Grupo) usando minutos del archivo ORIGINAL
        d = df_p_raw.copy()
        d["_score_min"] = _minutes_for_score_original(d)
        idx = d.groupby(["Player","Grupo"], dropna=False)["_score_min"].idxmax()
        df_p = d.loc[idx].drop(columns=["_score_min"])

        # 4) Crear columna interna de tamaño (_MinutesSize) ANTES de renombrar y dropear
        size_cands = ["Minutes played per match", "Adjusted min TIP per match", "Count Pressures received in sample"]
        df_p["_MinutesSize"] = np.nan
        for sc in size_cands:
            if sc in df_p.columns:
                df_p["_MinutesSize"] = df_p["_MinutesSize"].fillna(pd.to_numeric(df_p[sc], errors="coerce"))

        # 5) Renombrar MANUAL al español (nombres cortos)
        RENAME_MAP = {
            # Retención
            "Ball retention ratio under Pressure": "Índice de retención bajo presión",
            "Count ball retentions under Pressure per 100 Pressures": "Retenciones bajo presión",
            "Count forced losses under Pressure per 100 Pressures": "Pérdidas bajo presión",

            # Pase bajo presión
            "Pass completion ratio under Pressure": "Precisión de pases bajo presión",
            "Count pass attempts under Pressure per 100 Pressures": "Intentos de pase bajo presión",
            "Count completed passes under Pressure per 100 Pressures": "Pases completados bajo presión",

            # Pase peligroso
            "Dangerous pass completion ratio under Pressure": "Precisión de pase peligroso bajo presión",
            "Count dangerous pass attempts under Pressure per 100 Pressures": "Intentos de pase peligroso bajo presión",
            "Count dangerous passes completed under Pressure per 100 Pressures": "Pases peligrosos completados bajo presión",

            # Pase difícil
            "Difficult pass completion ratio under Pressure": "Precisión de pase difícil bajo presión",
            "Count difficult pass attempts under Pressure per 100 Pressures": "Intentos de pase difícil bajo presión",
            "Count difficult passes completed under Pressure per 100 Pressures": "Pases difíciles completados bajo presión",
        }
        df_p = df_p.rename(columns=RENAME_MAP)

        # 6) Eliminar por completo las 6 columnas vetadas (tanto en inglés original como en español)
        NEVER_OFFER_ORIGINAL = {
            "Minutes played per match",
            "Adjusted min TIP per match",
            "Count performances that pass the quality check",
            "Count performances that fail the quality check",
            "Count Pressures received in sample",
            "Count Pressures received per 100 Pressures",
        }
        NEVER_OFFER_SPANISH = {
            "Minutos por partido",
            "Min TIP ajustados por partido",
            "Perf. que pasan quality",
            "Perf. que fallan quality",
            "Presiones recibidas (muestra)",
            "Presiones recibidas (por 100)",
        }
        drop_cols = [c for c in df_p.columns if c in NEVER_OFFER_ORIGINAL or c in NEVER_OFFER_SPANISH]
        df_p = df_p.drop(columns=drop_cols, errors="ignore")

        # 7) Edad
        df_p["Age"] = _compute_age_col(df_p)

        st.markdown("### Vista")
        modo = st.radio("Selecciona", ["Scatterplot", "Radares Presión"], index=0, horizontal=False)

        st.markdown("### Grupo de Posición")
        grupos_ok = ["Centrales","Carrileros/Laterales","Contenciones","Interiores","Volantes Ofensivos","Extremos","Delanteros"]
        grupo_sel = st.radio("Grupo", grupos_ok, index=0)

        st.markdown("### Filtros")
        if df_p["Age"].notna().any():
            age_min = int(np.nanmin(df_p["Age"])); age_max = int(np.nanmax(df_p["Age"]))
            edad_sel = st.slider("Edad", min_value=age_min, max_value=age_max, value=(max(17, age_min), age_max))
        else:
            edad_sel = None
            st.caption("No se pudo derivar 'Edad' desde Birthdate.")

    # -------- Subset + filtros (ahora con dedupe por grupo) --------
    df_view = df_p[df_p["Grupo"] == grupo_sel].copy()
    if edad_sel:
        df_view = df_view[df_view["Age"].between(edad_sel[0], edad_sel[1])]
    if df_view.empty:
        st.info("No hay jugadores tras aplicar los filtros seleccionados."); st.stop()

    # ========================= Scatter =========================
    if modo == "Scatterplot":
        st.markdown("#### Variables del gráfico (elige X e Y)")

        exclude_exact = {"Player","Short name","Player ID","Birthdate","Position","Grupo","third","channel","Age","_MinutesSize"}
        num_cols = [c for c in df_view.columns if c not in exclude_exact and not c.startswith("_") and pd.api.types.is_numeric_dtype(df_view[c])]
        if not num_cols:
            st.warning("No se encontraron métricas numéricas válidas para graficar."); st.stop()

        SIZE_COL = "_MinutesSize" if "_MinutesSize" in df_view.columns and pd.api.types.is_numeric_dtype(df_view["_MinutesSize"]) else None

        def _first_present(cands, pool):
            for c in cands:
                if c in pool: return c
            return pool[0]

        default_x = ["Retenciones bajo presión"]
        default_y = ["Pases completados bajo presión"]

        colx, coly = st.columns(2)
        with colx:
            x_var = st.selectbox("Eje X", options=num_cols, index=num_cols.index(_first_present(default_x, num_cols)) if num_cols else 0)
        with coly:
            y_var = st.selectbox("Eje Y", options=num_cols, index=num_cols.index(_first_present(default_y, num_cols)) if num_cols else 1)

        x_dom = _domain_with_pad(df_view[x_var]); y_dom = _domain_with_pad(df_view[y_var])
        x_scale = alt.Scale(domain=x_dom, nice=True, zero=False)
        y_scale = alt.Scale(domain=y_dom, nice=True, zero=False)

        jugadores = sorted(df_view["Player"].dropna().astype(str).unique())
        hi_sel = st.multiselect("Resalta jugadores", jugadores, default=[])

        d = df_view.copy(); d["is_highlight"] = d["Player"].isin(hi_sel)

        sel = alt.selection_point(fields=["Player"], on="click", toggle=True, clear="dblclick", empty="none")

        base = alt.Chart(d).encode(
            x=alt.X(x_var, title=x_var, axis=alt.Axis(format="~s"), scale=x_scale),
            y=alt.Y(y_var, title=y_var, axis=alt.Axis(format="~s"), scale=y_scale),
            tooltip=[
                alt.Tooltip("Player:N", title="Jugador"),
                alt.Tooltip("Position:N", title="Posición"),
                alt.Tooltip("Grupo:N", title="Grupo"),
                alt.Tooltip(x_var, title=x_var, format=",.2f"),
                alt.Tooltip(y_var, title=y_var, format=",.2f"),
            ] + ([alt.Tooltip("_MinutesSize:Q", title="Min/partido (proxy)", format=",.1f")] if SIZE_COL else [])
        )

        size_enc = alt.Size("_MinutesSize", legend=None, scale=alt.Scale(range=[30, 500])) if SIZE_COL else alt.value(120)

        pts_base = base.mark_circle().encode(size=size_enc, color=alt.value(GRAY_BASE), opacity=alt.value(0.35))
        pts_sel  = base.transform_filter(sel).mark_circle().encode(size=size_enc, color=alt.value(ORANGE), opacity=alt.value(1.0)).add_params(sel)
        pts_list = base.transform_filter(alt.datum.is_highlight).mark_circle().encode(size=size_enc, color=alt.value(ORANGE), opacity=alt.value(1.0))

        labels_sel = base.transform_filter(sel).mark_text(dx=6, dy=-6, fontWeight="bold", color="#000000", clip=False).encode(text="Player:N")
        labels_list = base.transform_filter(alt.datum.is_highlight).mark_text(dx=6, dy=-6, fontWeight="bold", color="#000000", clip=False).encode(text="Player:N")

        x_mean = float(d[x_var].mean(skipna=True)); y_mean = float(d[y_var].mean(skipna=True))
        vline  = alt.Chart(pd.DataFrame({"v":[x_mean]})).mark_rule(strokeDash=[5,5], color="#9A9A9A", opacity=0.8).encode(x="v:Q")
        hline  = alt.Chart(pd.DataFrame({"h":[y_mean]})).mark_rule(strokeDash=[5,5], color="#9A9A9A", opacity=0.8).encode(y="h:Q")

        chart = (pts_base + pts_sel + pts_list + labels_sel + labels_list + vline + hline).properties(
            height=560, background="transparent",
            padding={"left": 10, "right": 160, "top": 40, "bottom": 30}
        ).configure_view(strokeWidth=0).configure_axis(
            grid=False, domain=False, tickColor=AXIS_COL, labelColor=AXIS_COL, titleColor=AXIS_COL
        )
        st.altair_chart(chart, use_container_width=True, theme=None)

    # ========================= Radar + KDE =========================
    else:
        st.markdown("#### Radares de Presión")

        fases_presion = {
            "Retención bajo presión": [
                "Índice de retención bajo presión",
                "Retenciones bajo presión",
                "Pérdidas bajo presión",
            ],
            "Pases bajo presión": [
                "Precisión de pases bajo presión",
                "Intentos de pase bajo presión",
                "Pases completados bajo presión",
            ],
            "Pases peligrosos": [
                "Precisión de pase peligroso bajo presión",
                "Intentos de pase peligroso bajo presión",
                "Pases peligrosos completados bajo presión",
                "Precisión de pase difícil bajo presión",
                "Intentos de pase difícil bajo presión",
                "Pases difíciles completados bajo presión",
            ],
        }
        invertir_vars = {"Pérdidas bajo presión"}  # menor=mejor

        jugadores = sorted(df_view["Player"].dropna().astype(str).unique())
        if not jugadores:
            st.warning("No hay jugadores tras aplicar filtros."); st.stop()
        jugador_sel = st.selectbox("Jugador", jugadores, index=0)

        left, mid, right = st.columns([0.05, 0.90, 0.05])
        with mid:
            fig = radar_barras_plotly_player(
                jugador=jugador_sel,
                df=df_view,
                fases_juego=fases_presion,
                id_col="Player",
                invertir_vars=invertir_vars,
                colores_fases=("rgba(59,130,246,0.90)", "rgba(245,158,11,0.90)", "rgba(16,185,129,0.90)"),
                chart_height=640
            )
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, theme=None)

        st.markdown("#### Distribuciones por métrica")
        charts = build_kde_charts(
            df=df_view,
            jugador=jugador_sel,
            fases_juego=fases_presion,
            id_col="Player",
            invertir_vars_kde=invertir_vars,
            height_each=120
        )
        if charts:
            for i in range(0, len(charts), 3):
                cols = st.columns(3, gap="large")
                for j in range(3):
                    if i + j < len(charts):
                        with cols[j]:
                            st.altair_chart(charts[i + j], use_container_width=True, theme=None)



##############################################################################################################
############################## Pases al Espacio ##############################################################
##############################################################################################################

elif seleccion == "Pases al Espacio":
    import numpy as np
    import pandas as pd
    import altair as alt
    import plotly.graph_objects as go

    st.markdown("<h3 style='margin-bottom: 15px;'>Pases al Espacio</h3>", unsafe_allow_html=True)

    # ===== Estilo (consistente con otras secciones) =====
    ORANGE     = "#f9ae34"
    GRAY_BASE  = "#C5C5C5"
    AXIS_COL   = "#2B2B2B"
    LINE_BLACK = "#111111"

    # =========================
    # Helpers
    # =========================
    def _load_espacio(path: str) -> pd.DataFrame:
        """Lee CSV delimitado por ';' y convierte columnas numéricas."""
        # Intentar ';' y fallback a ','
        try:
            df = pd.read_csv(path, sep=";")
            if df.shape[1] == 1:
                df = pd.read_csv(path)  # fallback coma
        except Exception:
            df = pd.read_csv(path)

        non_numeric = {"Player","Short name","Player ID","Birthdate","Position","third","channel"}
        for c in df.columns:
            if c not in non_numeric:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        if "Player" in df.columns:
            df["Player"] = df["Player"].astype(str).str.strip()
        return df

    def _minutes_for_score_original(df: pd.DataFrame) -> pd.Series:
        """
        Score para deduplicar por (Jugador, Grupo) usando SOLO nombres ORIGINALES.
        Prioridad:
        1) Minutes played per match
        2) Adjusted min TIP per match
        3) Count opportunities to pass to Runs in sample (proxy)
        """
        cands = [
            "Minutes played per match",
            "Adjusted min TIP per match",
            "Count opportunities to pass to Runs in sample"
        ]
        base = pd.Series(-1e12, index=df.index, dtype=float)
        for c in cands:
            if c in df.columns:
                s = pd.to_numeric(df[c], errors="coerce")
                base = np.where(base < 0, s, base)
        return pd.to_numeric(base, errors="coerce")

    def _map_grupo(pos_code: str) -> str:
        if not isinstance(pos_code, str): return "Otros"
        p = pos_code.upper().strip()
        if p in {"CB","LCB","RCB"}: return "Centrales"
        if p in {"LB","LWB","RB","RWB"}: return "Carrileros/Laterales"
        if p in {"DM","CDM","LDM","RDM"}: return "Contenciones"
        if p in {"CM","LCM","RCM","CMF","LM","RM"}: return "Interiores"
        if p in {"AM","CAM"}: return "Volantes Ofensivos"
        if p in {"LW","RW"}: return "Extremos"
        if p in {"CF","ST","LF","RF","SS","FW","FWD"}: return "Delanteros"
        if p in {"GK","GKP","GOALKEEPER"}: return "Porteros"
        return "Otros"

    def _compute_age_col(df: pd.DataFrame) -> pd.Series:
        if "Birthdate" not in df.columns:
            return pd.Series([np.nan]*len(df), index=df.index)
        bd = pd.to_datetime(df["Birthdate"], errors="coerce", utc=True)
        today = pd.Timestamp("today", tz="UTC")
        return (today - bd).dt.days / 365.25

    def _domain_with_pad(series: pd.Series, pad_ratio=0.08):
        s = pd.to_numeric(series, errors="coerce").dropna()
        if s.empty: return None
        mn, mx = float(s.min()), float(s.max())
        if mn == mx:
            pad = max(abs(mn), 1.0) * pad_ratio
            return [mn - pad, mx + pad]
        span = (mx - mn) * pad_ratio
        return [mn - span, mx + span]

    def _normalize_metrics(df, metrics, invert=None):
        invert = set(invert or [])
        out = df.copy()
        for m in metrics:
            if m not in out.columns: continue
            s = pd.to_numeric(out[m], errors="coerce")
            mn, mx = s.min(), s.max()
            if pd.isna(mn) or pd.isna(mx) or mx == mn:
                out[m] = 0.5
            else:
                z = (s - mn) / (mx - mn)
                out[m] = (1 - z) if m in invert else z
                out[m] = out[m].fillna(0.5)
        return out

    # ----- Radar (igual estilo al de otras secciones) -----
    def radar_barras_plotly_player(
        jugador, df, fases_juego, id_col="Player",
        invertir_vars=None,
        colores_fases=("rgba(59,130,246,0.90)", "rgba(245,158,11,0.90)", "rgba(16,185,129,0.90)"),
        chart_height=640
    ):
        if id_col not in df.columns or jugador not in df[id_col].values:
            return None
        invertir = set(invertir_vars or [])
        atributos, fase_idx = [], []
        fases_orden = list(fases_juego.keys())
        for i, (_, vars_fase) in enumerate(fases_juego.items()):
            prs = [v for v in vars_fase if v in df.columns]
            atributos.extend(prs)
            fase_idx.extend([i]*len(prs))
        if not atributos:
            return None

        df_norm = _normalize_metrics(df, atributos, invert=invertir)
        row = df_norm.loc[df_norm[id_col] == jugador].iloc[0]
        r_vals = [float(row[a])*100 for a in atributos]

        n = len(atributos)
        thetas = np.linspace(0, 360, n, endpoint=False)

        fig = go.Figure()
        for i, fase in enumerate(fases_orden):
            idxs = [k for k, fidx in enumerate(fase_idx) if fidx == i]
            if not idxs: continue
            fig.add_trace(go.Barpolar(
                r=[r_vals[k] for k in idxs],
                theta=[thetas[k] for k in idxs],
                width=[(360/n)*0.98]*len(idxs),
                marker=dict(color=colores_fases[i], line=dict(width=0)),
                name=fase,
                hovertemplate="<b>%{customdata[0]}</b><br>Percentil: %{r:.1f}<extra></extra>",
                customdata=[[atributos[k]] for k in idxs],
                opacity=0.95,
            ))

        fig.add_trace(go.Scatterpolar(
            r=[110]*n, theta=thetas, mode="text", text=atributos,
            textfont=dict(size=11, color=AXIS_COL),
            textposition="middle center", hoverinfo="skip", showlegend=False
        ))

        fig.update_layout(
            template="plotly_white", height=chart_height,
            margin=dict(l=10, r=10, t=40, b=40),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    range=[0,112], tickvals=[0,20,40,60,80,100],
                    ticktext=["0","20","40","60","80","100"],
                    showline=True, gridcolor="#E5E5E5", gridwidth=1,
                    tickfont=dict(size=11, color=AXIS_COL),
                ),
                angularaxis=dict(
                    rotation=0, direction="clockwise", showline=False,
                    gridcolor="#F0F0F0", gridwidth=1,
                    tickfont=dict(size=10, color="#B3B3B3"),
                    ticks="",
                ),
            ),
            legend=dict(
                orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5,
                font=dict(size=12, color=AXIS_COL), bgcolor="rgba(0,0,0,0)",
            ),
            title=dict(text=f"Radar · {jugador}", x=0.01, y=0.98, font=dict(size=18, color="#111111")),
        )
        return fig

    # ----- KDE -----
    def _kde_chart_altair(df, metric, jugador_val, invert=False, fill_color=ORANGE, height=120):
        serie = (
            pd.to_numeric(df[metric], errors="coerce")
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
            .astype(float)
        )
        if serie.empty or pd.isna(jugador_val):
            return None

        mn, mx = float(serie.min()), float(serie.max())
        if mn == mx:
            pad = max(abs(mn), 1.0) * 0.10; mn, mx = mn - pad, mx + pad
        else:
            pad = (mx - mn) * 0.10; mn, mx = mn - pad, mx + pad

        data_num = pd.DataFrame({"value": serie})
        base = alt.Chart(data_num).transform_density("value", as_=["x","density"], extent=[mn, mx], steps=200)

        area = base.transform_filter(alt.datum.x <= float(jugador_val)).mark_area(opacity=0.28, color=fill_color)\
            .encode(x=alt.X("x:Q", title=None, scale=alt.Scale(reverse=bool(invert))),
                    y=alt.Y("density:Q", title=None))
        line = base.mark_line(color=LINE_BLACK, size=1.2)\
            .encode(x=alt.X("x:Q", scale=alt.Scale(reverse=bool(invert))), y="density:Q")
        rule = alt.Chart(pd.DataFrame({"x":[float(jugador_val)]})).mark_rule(color=LINE_BLACK, strokeWidth=2)\
            .encode(x=alt.X("x:Q", scale=alt.Scale(reverse=bool(invert))),
                    tooltip=[alt.Tooltip("x:Q", title="Valor", format=".3f")])

        chart = (area + line + rule).properties(
            height=height,
            title=alt.TitleParams(metric, fontSize=12, anchor="middle", color="#1F2937")
        ).configure_axis(
            grid=False, domain=True, domainColor="#E6E6E6", labelColor=AXIS_COL
        ).configure_view(
            strokeWidth=0
        ).configure_title(
            font="Inter", color="#111111", anchor="middle"
        )
        return chart

    def build_kde_charts(df, jugador, fases_juego, id_col="Player", invertir_vars_kde=None, height_each=120):
        invertir_vars_kde = set(invertir_vars_kde or [])
        charts = []
        if id_col not in df.columns or jugador not in df[id_col].values:
            return charts
        row = df.loc[df[id_col] == jugador].iloc[0]
        for _, vars_fase in fases_juego.items():
            prs = [v for v in vars_fase if v in df.columns]
            for m in prs:
                val = pd.to_numeric(row.get(m, np.nan), errors="coerce")
                ch = _kde_chart_altair(df, m, val, invert=(m in invertir_vars_kde), fill_color=ORANGE, height=height_each)
                if ch is not None:
                    charts.append(ch)
        return charts

    # =========================
    # Sidebar (Liga / Temporada)
    # =========================

    
    ligas_temporadas_espacio = {
        "Liga MX": ["2024/2025"],  # agrega más aquí
        "Liga Profesional, Argentina": ["2024"],  # agrega más aquí
        "Jupiler Pro League, Bélgica": ["2024/2025"],  # agrega más aquí
        "Serie A, Brasil": ["2024"],  # agrega más aquí
        "Primera División, Chile": ["2024"],  # agrega más aquí
        "Primera A, Colombia": ["2024"],  # agrega más aquí
        "Liga Pro, Ecuador": ["2024"],  # agrega más aquí
        "Premier League, Inglaterra": ["2024/2025"],  # agrega más aqui
        "La Liga, España": ["2024/2025"],  # agrega más aquí
        "Ligue 1, Francia": ["2024/2025"],  # agrega más aquí
        "Bundesliga, Alemania": ["2024/2025"],  # agrega más aquí
        "Serie A, Italia": ["2024/2025"],  # agrega más aquí
        "Primeira Liga, Portugal": ["2024/2025"],  # agrega más aqu
        "Primera División, Uruguay": ["2024"],  # agrega más aqu
        "MLS, Estados Unidos": ["2024"],  # agrega más aquí


    }
    archivos_espacio = {
        ("Liga MX", "2024/2025"): "ligamxespacio.csv",
        ("Liga Profesional, Argentina", "2024"): "argespacio.csv",
        ("Jupiler Pro League, Bélgica", "2024/2025"): "belespacio.csv",
        ("Serie A, Brasil", "2024"): "braespacio.csv",
        ("Primera División, Chile", "2024"): "chiespacio.csv",
        ("Primera A, Colombia", "2024"): "colespacio.csv",
        ("Liga Pro, Ecuador", "2024"): "ecuespacio.csv",
        ("Premier League, Inglaterra", "2024/2025"): "engespacio.csv",
        ("La Liga, España", "2024/2025"): "espespacio.csv",
        ("Ligue 1, Francia", "2024/2025"): "fraespacio.csv",
        ("Bundesliga, Alemania", "2024/2025"): "gerespacio.csv",
        ("Serie A, Italia", "2024/2025"): "itaespacio.csv",
        ("Primeira Liga, Portugal", "2024/2025"): "porespacio.csv",
        ("Primera División, Uruguay", "2024"): "uruespacio.csv",
        ("MLS, Estados Unidos", "2024"): "usaespacio.csv",
    }

    with st.sidebar:
        st.markdown("### Liga y Temporada")
        liga = st.selectbox("Liga", list(ligas_temporadas_espacio.keys()), index=0)
        temporada = st.selectbox("Temporada", ligas_temporadas_espacio[liga], index=0)

        path = archivos_espacio.get((liga, temporada))
        if not path:
            st.error("No hay archivo configurado para esa liga/temporada."); st.stop()

        # 1) Cargar RAW
        df_e_raw = _load_espacio(path)

        # 2) Grupo, Edad
        df_e_raw["Grupo"] = df_e_raw["Position"].apply(_map_grupo)
        df_e_raw["Age"] = _compute_age_col(df_e_raw)

        # 3) Deduplicar por (Jugador, Grupo) usando minutos/partido del archivo ORIGINAL
        d = df_e_raw.copy()
        d["_score_min"] = _minutes_for_score_original(d)
        idx = d.groupby(["Player","Grupo"], dropna=False)["_score_min"].idxmax()
        df_e = d.loc[idx].drop(columns=["_score_min"])

        # 4) _MinutesSize para tamaño de puntos (antes de renombrar/dropear)
        size_cands = [
            "Minutes played per match",
            "Adjusted min TIP per match",
            "Count opportunities to pass to Runs in sample"
        ]
        df_e["_MinutesSize"] = np.nan
        for sc in size_cands:
            if sc in df_e.columns:
                df_e["_MinutesSize"] = df_e["_MinutesSize"].fillna(pd.to_numeric(df_e[sc], errors="coerce"))

        # 5) Renombrar a español (corto/legible)
        # 5) Renombrar a español (corto/legible)
        RENAME_MAP = {
            "Minutes played per match": "Minutos por partido",
            "Adjusted min TIP per match": "Min TIP ajustados por partido",
            "Count performances that pass the quality check": "Perf. que pasan quality",
            "Count performances that fail the quality check": "Perf. que fallan quality",
            "Count opportunities to pass to Runs in sample": "Oportunidades a carreras (muestra)",

            "Count opportunities to pass to Runs per 100 Pass Opportunities": "Oportunidades de pases al espacio",
            "Count pass attempts for Runs per 100 Pass Opportunities": "Intentos de pase al espacio",
            "Threat of all opportunities to pass to Runs per 100 Pass Opportunities": "Peligrosidad de oportunidades de pase al espacio",
            "Threat of Runs to which a pass was attempted per 100 Pass Opportunities": "Peligrosidad de desmarque que buscaba el pase",
            "Pass completion ratio to Runs": "Precisión pases al espacio",
            "Count Runs made by teammate per 100 Pass Opportunities": "Desmarques de compañeros",
            "Threat of Runs to which a pass was completed per 100 Pass Opportunities": "Peligrosidad de desmarques con pase exitoso",
            "Count completed passes for Runs per 100 Pass Opportunities": "Pases al espacio completados",
            "Count completed passes leading to shot for Runs per 100 Pass Opportunities": "Pases al espacio que terminan en remate",
            "Count completed passes leading to goal for Runs per 100 Pass Opportunities": "Pases al espacio que terminan en gol",
            "Count opportunities to pass to dangerous Runs per 100 Pass Opportunities": "Oportunidades de pase peligroso al espacio",
            "Count pass attempts for dangerous Runs per 100 Pass Opportunities": "Intentos de pase peligroso al espacio",
            "Count completed passes for dangerous Runs per 100 Pass Opportunities": "Pases peligrosos al espacio",
        }
        df_e = df_e.rename(columns=RENAME_MAP)

        # 6) Eliminar columnas administrativas no ofrecibles en selects
        NEVER_OFFER_ORIGINAL = {
            "Minutes played per match",
            "Adjusted min TIP per match",
            "Count performances that pass the quality check",
            "Count performances that fail the quality check",
            "Count opportunities to pass to Runs in sample",
            "Count opportunities to pass to Runs per 100 Pass Opportunities",  # 👈 añadido
        }
        NEVER_OFFER_SPANISH = {
            "Minutos por partido",
            "Min TIP ajustados por partido",
            "Perf. que pasan quality",
            "Perf. que fallan quality",
            "Oportunidades a carreras (muestra)",
            "Oportunidades a carreras por 100",  # 👈 añadido
        }
        drop_cols = [c for c in df_e.columns if c in NEVER_OFFER_ORIGINAL or c in NEVER_OFFER_SPANISH]
        df_e = df_e.drop(columns=drop_cols, errors="ignore")

        drop_cols = [c for c in df_e.columns if c in NEVER_OFFER_ORIGINAL or c in NEVER_OFFER_SPANISH]
        df_e = df_e.drop(columns=drop_cols, errors="ignore")

        # 7) Controles
        st.markdown("### Vista")
        modo = st.radio("Selecciona", ["Scatterplot", "Radares Espacio"], index=0, horizontal=False)

        st.markdown("### Grupo de Posición")
        grupos_ok = ["Centrales","Carrileros/Laterales","Contenciones","Interiores","Volantes Ofensivos","Extremos","Delanteros"]
        grupo_sel = st.radio("Grupo", grupos_ok, index=0)

        st.markdown("### Filtros")
        if df_e["Age"].notna().any():
            age_min = int(np.nanmin(df_e["Age"])); age_max = int(np.nanmax(df_e["Age"]))
            edad_sel = st.slider("Edad", min_value=age_min, max_value=age_max, value=(max(17, age_min), age_max))
        else:
            edad_sel = None
            st.caption("No se pudo derivar 'Edad' desde Birthdate.")

    # -------- Subset + filtros --------
    df_view = df_e[df_e["Grupo"] == grupo_sel].copy()
    if edad_sel:
        df_view = df_view[df_view["Age"].between(edad_sel[0], edad_sel[1])]
    if df_view.empty:
        st.info("No hay jugadores tras aplicar los filtros seleccionados."); st.stop()

    # ========================= Scatter =========================
    if modo == "Scatterplot":
        st.markdown("#### Variables del gráfico (elige X e Y)")

        exclude_exact = {"Player","Short name","Player ID","Birthdate","Position","Grupo","third","channel","Age","_MinutesSize"}
        num_cols = [c for c in df_view.columns if c not in exclude_exact and not c.startswith("_") and pd.api.types.is_numeric_dtype(df_view[c])]
        if not num_cols:
            st.warning("No se encontraron métricas válidas para graficar."); st.stop()

        # Defaults simples
        def _first_present(cands, pool):
            for c in cands:
                if c in pool: return c
            return pool[0]

        default_x = _first_present(["Pases al espacio completados"], num_cols)
        default_y = _first_present(["Pases al espacio que terminan en remate"], num_cols)

        colx, coly = st.columns(2)
        with colx:
            x_var = st.selectbox("Eje X", options=num_cols, index=num_cols.index(default_x))
        with coly:
            y_var = st.selectbox("Eje Y", options=num_cols, index=num_cols.index(default_y))

        SIZE_COL = "_MinutesSize" if "_MinutesSize" in df_view.columns and pd.api.types.is_numeric_dtype(df_view["_MinutesSize"]) else None

        x_dom = _domain_with_pad(df_view[x_var]); y_dom = _domain_with_pad(df_view[y_var])
        x_scale = alt.Scale(domain=x_dom, nice=True, zero=False)
        y_scale = alt.Scale(domain=y_dom, nice=True, zero=False)

        jugadores = sorted(df_view["Player"].dropna().astype(str).unique())
        hi_sel = st.multiselect("Resalta jugadores", jugadores, default=[])

        d = df_view.copy(); d["is_highlight"] = d["Player"].isin(hi_sel)

        sel = alt.selection_point(fields=["Player"], on="click", toggle=True, clear="dblclick", empty="none")

        base = alt.Chart(d).encode(
            x=alt.X(x_var, title=x_var, axis=alt.Axis(format="~s"), scale=x_scale),
            y=alt.Y(y_var, title=y_var, axis=alt.Axis(format="~s"), scale=y_scale),
            tooltip=[
                alt.Tooltip("Player:N", title="Jugador"),
                alt.Tooltip("Position:N", title="Posición"),
                alt.Tooltip("Grupo:N", title="Grupo"),
                alt.Tooltip(x_var, title=x_var, format=",.2f"),
                alt.Tooltip(y_var, title=y_var, format=",.2f"),
            ] + ([alt.Tooltip("_MinutesSize:Q", title="Min/partido (proxy)", format=",.1f")] if SIZE_COL else [])
        )

        size_enc = alt.Size("_MinutesSize", legend=None, scale=alt.Scale(range=[30, 500])) if SIZE_COL else alt.value(120)

        pts_base = base.mark_circle().encode(size=size_enc, color=alt.value(GRAY_BASE), opacity=alt.value(0.35))
        pts_sel  = base.transform_filter(sel).mark_circle().encode(size=size_enc, color=alt.value(ORANGE), opacity=alt.value(1.0)).add_params(sel)
        pts_list = base.transform_filter(alt.datum.is_highlight).mark_circle().encode(size=size_enc, color=alt.value(ORANGE), opacity=alt.value(1.0))

        labels_sel = base.transform_filter(sel).mark_text(dx=6, dy=-6, fontWeight="bold", color="#000000", clip=False).encode(text="Player:N")
        labels_list = base.transform_filter(alt.datum.is_highlight).mark_text(dx=6, dy=-6, fontWeight="bold", color="#000000", clip=False).encode(text="Player:N")

        x_mean = float(d[x_var].mean(skipna=True)); y_mean = float(d[y_var].mean(skipna=True))
        vline  = alt.Chart(pd.DataFrame({"v":[x_mean]})).mark_rule(strokeDash=[5,5], color="#9A9A9A", opacity=0.8).encode(x="v:Q")
        hline  = alt.Chart(pd.DataFrame({"h":[y_mean]})).mark_rule(strokeDash=[5,5], color="#9A9A9A", opacity=0.8).encode(y="h:Q")

        chart = (pts_base + pts_sel + pts_list + labels_sel + labels_list + vline + hline).properties(
            height=560, background="transparent",
            padding={"left": 10, "right": 160, "top": 40, "bottom": 30}
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            grid=False, domain=False, tickColor=AXIS_COL, labelColor=AXIS_COL, titleColor=AXIS_COL
        )

        # >>> ESTA LÍNEA ES LA QUE FALTABA <<<
        st.altair_chart(chart, use_container_width=True, theme=None)

    # ========================= Radar + KDE =========================
    else:
        st.markdown("#### Radares de Pases al Espacio")

        fases_espacio = {
            "Volumen": [
                "Oportunidades de pases al espacio",
                "Desmarques de compañeros",
                "Intentos de pase al espacio",
                "Pases al espacio completados",
                "Oportunidades de pase peligroso al espacio",
                "Intentos de pase peligroso al espacio",
                "Pases peligrosos al espacio",
            ],
            "Amenaza": [
                "Peligrosidad de oportunidades de pase al espacio",
                "Peligrosidad de desmarque que buscaba el pase",
                "Peligrosidad de desmarques con pase exitoso",
                "Pases al espacio que terminan en remate",
                "Pases al espacio que terminan en gol",
            ],
            "Eficacia": [
                "Precisión pases al espacio",
            ],
        }
        invertir_vars = set()  # aquí no hay métricas "menor=mejor"

        jugadores = sorted(df_view["Player"].dropna().astype(str).unique())
        if not jugadores:
            st.warning("No hay jugadores tras aplicar filtros."); st.stop()
        jugador_sel = st.selectbox("Jugador", jugadores, index=0)

        left, mid, right = st.columns([0.05, 0.90, 0.05])
        with mid:
            fig = radar_barras_plotly_player(
                jugador=jugador_sel,
                df=df_view,
                fases_juego=fases_espacio,
                id_col="Player",
                invertir_vars=invertir_vars,
                colores_fases=("rgba(59,130,246,0.90)", "rgba(245,158,11,0.90)", "rgba(16,185,129,0.90)"),
                chart_height=640
            )
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, theme=None)

        st.markdown("#### Distribuciones por métrica")
        charts = build_kde_charts(
            df=df_view,
            jugador=jugador_sel,
            fases_juego=fases_espacio,
            id_col="Player",
            invertir_vars_kde=invertir_vars,
            height_each=120
        )
        if charts:
            for i in range(0, len(charts), 3):
                cols = st.columns(3, gap="large")
                for j in range(3):
                    if i + j < len(charts):
                        with cols[j]:
                            st.altair_chart(charts[i + j], use_container_width=True, theme=None)





##############################################################################################################
############################## Movimientos sin Balón #########################################################
##############################################################################################################



elif seleccion == "Movimientos sin Balón":
    import numpy as np
    import pandas as pd
    import altair as alt
    import plotly.graph_objects as go

    st.markdown("<h3 style='margin-bottom: 15px;'>Movimientos sin Balón</h3>", unsafe_allow_html=True)

    # ===== Estilo =====
    ORANGE     = "#f9ae34"
    GRAY_BASE  = "#C5C5C5"
    AXIS_COL   = "#2B2B2B"
    LINE_BLACK = "#111111"

    # =========================
    # Helpers
    # =========================
    def _load_desmarque(path: str) -> pd.DataFrame:
        """Lee CSV delimitado por ';' (fallback a ',') y castea números."""
        try:
            df = pd.read_csv(path, sep=";")
            if df.shape[1] == 1:
                df = pd.read_csv(path)
        except Exception:
            df = pd.read_csv(path)

        non_numeric = {"Player","Short name","Player ID","Birthdate","Position","third","channel"}
        for c in df.columns:
            if c not in non_numeric:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        if "Player" in df.columns:
            df["Player"] = df["Player"].astype(str).str.strip()
        return df

    def _map_grupo(pos_code: str) -> str:
        if not isinstance(pos_code, str): return "Otros"
        p = pos_code.upper().strip()
        if p in {"CB","LCB","RCB"}: return "Centrales"
        if p in {"LB","LWB","RB","RWB"}: return "Carrileros/Laterales"
        if p in {"DM","CDM","LDM","RDM"}: return "Contenciones"
        if p in {"CM","LCM","RCM","CMF","LM","RM"}: return "Interiores"
        if p in {"AM","CAM"}: return "Volantes Ofensivos"
        if p in {"LW","RW"}: return "Extremos"
        if p in {"CF","ST","LF","RF","SS","FW","FWD"}: return "Delanteros"
        if p in {"GK","GKP","GOALKEEPER"}: return "Porteros"
        return "Otros"

    def _compute_age_col(df: pd.DataFrame) -> pd.Series:
        if "Birthdate" not in df.columns:
            return pd.Series([np.nan]*len(df), index=df.index)
        bd = pd.to_datetime(df["Birthdate"], errors="coerce", utc=True)
        today = pd.Timestamp("today", tz="UTC")
        return (today - bd).dt.days / 365.25

    def _domain_with_pad(series: pd.Series, pad_ratio=0.08):
        s = pd.to_numeric(series, errors="coerce").dropna()
        if s.empty: return None
        mn, mx = float(s.min()), float(s.max())
        if mn == mx:
            pad = max(abs(mn), 1.0) * pad_ratio
            return [mn - pad, mx + pad]
        span = (mx - mn) * pad_ratio
        return [mn - span, mx + span]

    def _normalize_metrics(df, metrics, invert=None):
        invert = set(invert or [])
        out = df.copy()
        for m in metrics:
            if m not in out.columns: continue
            s = pd.to_numeric(out[m], errors="coerce")
            mn, mx = s.min(), s.max()
            if pd.isna(mn) or pd.isna(mx) or mx == mn:
                out[m] = 0.5
            else:
                z = (s - mn) / (mx - mn)
                out[m] = (1 - z) if m in invert else z
                out[m] = out[m].fillna(0.5)
        return out

    # Score para dedupe usando columnas del archivo ORIGINAL
    def _minutes_score_original(df: pd.DataFrame) -> pd.Series:
        cands = [
            "Minutes",
            "Minutes played per match",
            "Adjusted min TIP per match",
        ]
        base = pd.Series(-1e12, index=df.index, dtype=float)
        for c in cands:
            if c in df.columns:
                s = pd.to_numeric(df[c], errors="coerce")
                base = pd.Series(np.where(base < 0, s, base), index=df.index)
        return base

    # ----- Radar -----
    def radar_barras_plotly_player(
        jugador, df, fases_juego, id_col="Player",
        invertir_vars=None,
        colores_fases=("rgba(59,130,246,0.90)", "rgba(245,158,11,0.90)", "rgba(16,185,129,0.90)"),
        chart_height=640
    ):
        if id_col not in df.columns or jugador not in df[id_col].values:
            return None
        invertir = set(invertir_vars or [])
        atributos, fase_idx = [], []
        fases_orden = list(fases_juego.keys())
        for i, (fase, vars_fase) in enumerate(fases_juego.items()):
            prs = [v for v in vars_fase if v in df.columns]
            atributos.extend(prs)
            fase_idx.extend([i]*len(prs))
        if not atributos: return None

        df_norm = _normalize_metrics(df, atributos, invert=invertir)
        row = df_norm.loc[df_norm[id_col] == jugador].iloc[0]
        r_vals = [float(row[a])*100 for a in atributos]

        n = len(atributos)
        thetas = np.linspace(0, 360, n, endpoint=False)

        fig = go.Figure()
        for i, fase in enumerate(fases_orden):
            idxs = [k for k, fidx in enumerate(fase_idx) if fidx == i]
            if not idxs: continue
            fig.add_trace(go.Barpolar(
                r=[r_vals[k] for k in idxs],
                theta=[thetas[k] for k in idxs],
                width=[(360/n)*0.98]*len(idxs),
                marker=dict(color=colores_fases[i], line=dict(width=0)),
                name=fase,
                hovertemplate="<b>%{customdata[0]}</b><br>Percentil: %{r:.1f}<extra></extra>",
                customdata=[[atributos[k]] for k in idxs],
                opacity=0.95,
            ))

        fig.add_trace(go.Scatterpolar(
            r=[110]*n, theta=thetas, mode="text", text=atributos,
            textfont=dict(size=11, color=AXIS_COL),
            textposition="middle center", hoverinfo="skip", showlegend=False
        ))

        fig.update_layout(
            template="plotly_white", height=chart_height,
            margin=dict(l=10, r=10, t=40, b=40),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    range=[0,112], tickvals=[0,20,40,60,80,100],
                    ticktext=["0","20","40","60","80","100"],
                    showline=True, gridcolor="#E5E5E5", gridwidth=1,
                    tickfont=dict(size=11, color=AXIS_COL),
                ),
                angularaxis=dict(
                    rotation=0, direction="clockwise", showline=False,
                    gridcolor="#F0F0F0", gridwidth=1,
                    tickfont=dict(size=10, color="#B3B3B3"),
                    ticks="",
                ),
            ),
            legend=dict(
                orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5,
                font=dict(size=12, color=AXIS_COL), bgcolor="rgba(0,0,0,0)",
            ),
            title=dict(text=f"Radar · {jugador}", x=0.01, y=0.98, font=dict(size=18, color="#111111")),
        )
        return fig

    # ----- KDE -----
    def _kde_chart_altair(df, metric, jugador_val, invert=False, fill_color=ORANGE, height=120):
        serie = (
            pd.to_numeric(df[metric], errors="coerce")
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
            .astype(float)
        )
        if serie.empty or pd.isna(jugador_val): return None

        mn, mx = float(serie.min()), float(serie.max())
        if mn == mx:
            pad = max(abs(mn), 1.0) * 0.10; mn, mx = mn - pad, mx + pad
        else:
            pad = (mx - mn) * 0.10; mn, mx = mn - pad, mx + pad

        data_num = pd.DataFrame({"value": serie})
        base = alt.Chart(data_num).transform_density("value", as_=["x","density"], extent=[mn, mx], steps=200)

        area = base.transform_filter(alt.datum.x <= float(jugador_val)).mark_area(opacity=0.28, color=fill_color)\
            .encode(x=alt.X("x:Q", title=None, scale=alt.Scale(reverse=bool(invert))),
                    y=alt.Y("density:Q", title=None))
        line = base.mark_line(color=LINE_BLACK, size=1.2)\
            .encode(x=alt.X("x:Q", scale=alt.Scale(reverse=bool(invert))), y="density:Q")
        rule = alt.Chart(pd.DataFrame({"x":[float(jugador_val)]})).mark_rule(color=LINE_BLACK, strokeWidth=2)\
            .encode(x=alt.X("x:Q", scale=alt.Scale(reverse=bool(invert))),
                    tooltip=[alt.Tooltip("x:Q", title="Valor", format=".3f")])

        chart = (area + line + rule).properties(height=height, title=alt.TitleParams(metric, fontSize=12, anchor="middle", color="#1F2937"))\
            .configure_axis(grid=False, domain=True, domainColor="#E6E6E6", labelColor=AXIS_COL)\
            .configure_view(strokeWidth=0)\
            .configure_title(font="Inter", color="#111111", anchor="middle")
        return chart

    def build_kde_charts(df, jugador, fases_juego, id_col="Player", invertir_vars_kde=None, height_each=120):
        invertir_vars_kde = set(invertir_vars_kde or [])
        charts = []
        if id_col not in df.columns or jugador not in df[id_col].values:
            return charts
        row = df.loc[df[id_col] == jugador].iloc[0]
        for _, vars_fase in fases_juego.items():
            prs = [v for v in vars_fase if v in df.columns]
            for m in prs:
                val = pd.to_numeric(row.get(m, np.nan), errors="coerce")
                ch = _kde_chart_altair(df, m, val, invert=(m in invertir_vars_kde), fill_color=ORANGE, height=height_each)
                if ch is not None: charts.append(ch)
        return charts

    # =========================
    # Sidebar (Liga / Temporada)
    # =========================
    ligas_temporadas_desmarque = {
        "Liga MX": ["2024/2025"],  # agrega más aquí
        "Liga Profesional, Argentina": ["2024"],  # agrega más aquí
        "Jupiler Pro League, Bélgica": ["2024/2025"],  # agrega más aquí
        "Serie A, Brasil": ["2024"],  # agrega más aquí
        "Primera División, Chile": ["2024"],  # agrega más aquí
        "Primera A, Colombia": ["2024"],  # agrega más aquí
        "Liga Pro, Ecuador": ["2024"],  # agrega más aquí
        "Premier League, Inglaterra": ["2024/2025"],  # agrega más aqui
        "La Liga, España": ["2024/2025"],  # agrega más aquí
        "Ligue 1, Francia": ["2024/2025"],  # agrega más aquí
        "Bundesliga, Alemania": ["2024/2025"],  # agrega más aquí
        "Serie A, Italia": ["2024/2025"],  # agrega más aquí
        "Primeira Liga, Portugal": ["2024/2025"],  # agrega más aqu
        "Primera División, Uruguay": ["2024"],  # agrega más aqu
        "MLS, Estados Unidos": ["2024"],  # agrega más aquí


    }
    archivos_desmarque = {
        ("Liga MX", "2024/2025"): "ligamxdesmarque.csv",
        ("Liga Profesional, Argentina", "2024"): "argdesmarque.csv",
        ("Jupiler Pro League, Bélgica", "2024/2025"): "beldesmarque.csv",
        ("Serie A, Brasil", "2024"): "bradesmarque.csv",
        ("Primera División, Chile", "2024"): "chidesmarque.csv",
        ("Primera A, Colombia", "2024"): "coldesmarque.csv",
        ("Liga Pro, Ecuador", "2024"): "ecudesmarque.csv",
        ("Premier League, Inglaterra", "2024/2025"): "engdesmarque.csv",
        ("La Liga, España", "2024/2025"): "espdesmarque.csv",
        ("Ligue 1, Francia", "2024/2025"): "fradesmarque.csv",
        ("Bundesliga, Alemania", "2024/2025"): "gerdesmarque.csv",
        ("Serie A, Italia", "2024/2025"): "itadesmarque.csv",
        ("Primeira Liga, Portugal", "2024/2025"): "pordesmarque.csv",
        ("Primera División, Uruguay", "2024"): "urudesmarque.csv",
        ("MLS, Estados Unidos", "2024"): "usadesmarque.csv",
    }

    with st.sidebar:
        st.markdown("### Liga y Temporada")
        liga = st.selectbox("Liga", list(ligas_temporadas_desmarque.keys()), index=0)
        temporada = st.selectbox("Temporada", ligas_temporadas_desmarque[liga], index=0)

        path = archivos_desmarque.get((liga, temporada))
        if not path:
            st.error("No hay archivo configurado para esa liga/temporada."); st.stop()

        # 1) Cargar RAW
        df_d_raw = _load_desmarque(path)

        # 2) Grupo + Edad (antes de dedupe)
        df_d_raw["Grupo"] = df_d_raw["Position"].apply(_map_grupo)
        df_d_raw["Age"] = _compute_age_col(df_d_raw)

        # 3) Dedupe por (Player, Grupo) con score de minutos del ORIGINAL
        d = df_d_raw.copy()
        d["_score_min"] = _minutes_score_original(d)
        idx = d.groupby(["Player","Grupo"], dropna=False)["_score_min"].idxmax()
        df_d = d.loc[idx].drop(columns=["_score_min"])

        # 4) Construir columna de tamaño ANTES de renombrar (igual que en Presión)
        size_cands = ["Minutes", "Minutes played per match", "Adjusted min TIP per match"]
        df_d["_MinutesSize"] = np.nan
        for sc in size_cands:
            if sc in df_d.columns:
                df_d["_MinutesSize"] = df_d["_MinutesSize"].fillna(pd.to_numeric(df_d[sc], errors="coerce"))

        # 5) Renombrar al español (asegúrate de que estas claves EXISTEN en tu CSV)
        RENAME_MAP = {
            # Volumen
            "Count Runs per 100 Runs": "Desmarques",
            "Count Dangerous Runs per 100 Runs": "Desmarques peligrosos",
            "Count Runs targeted per 100 Runs": "Desmarques intentados",
            "Count Runs received per 100 Runs": "Desmarques recibidos",            
   

            # Recepción / Peligro
            "Threat of Runs per 100 Runs": "Peligrosidad de Desmarques",
            "Threat of Runs targeted per 100 Runs": "Peligrosidad de Desmarques intentados",
            "Threat of Runs received per 100 Runs": "Peligrosidad de Desmarques recibidos",
            "Count dangerous Runs targeted per 100 Runs": "Desmarques peligrosos intentados", 
            "Count dangerous Runs received per 100 Runs": "Desmarques peligrosos recibidos", 


            # Finalización
            "Count Runs leading to goal per 100 Runs": "Desmarques que terminan en gol",
            "Count Runs leading to shot per 100 Runs": "Desmarques que terminan en remate",


            # Administrativas
            "Minutes played per match": "Minutos por partido",
            "Adjusted min TIP per match": "Min TIP ajustados por partido",
            "Count performances that pass the quality check": "Perf. que pasan quality",
            "Count performances that fail the quality check": "Perf. que fallan quality",
            "Count Runs in sample": "Desmarques (muestra)",
            "Count Runs per 100 Pass Opportunities": "Desmarques por 100 (conteo puro)",
        }
        df_d = df_d.rename(columns=RENAME_MAP)

        # 6) Ocultar columnas administrativas (NO mostrar en scatter/radar)
        NEVER_OFFER_ORIGINAL = {
            "Minutes played per match",
            "Adjusted min TIP per match",
            "Count performances that pass the quality check",
            "Count performances that fail the quality check",
            "Count Runs in sample",
            "Count Runs per 100 Pass Opportunities",
            "Count Runs per 100 Runs"
        }
        NEVER_OFFER_SPANISH = {
            "Minutos por partido",
            "Min TIP ajustados por partido",
            "Perf. que pasan quality",
            "Perf. que fallan quality",
            "Desmarques (muestra)",
            "Desmarques por 100 (conteo puro)",
            "Desmarques"
        }
        drop_cols = [c for c in df_d.columns if c in NEVER_OFFER_ORIGINAL or c in NEVER_OFFER_SPANISH or ("in sample" in c.lower())]
        df_d = df_d.drop(columns=drop_cols, errors="ignore")

        st.markdown("### Vista")
        modo = st.radio("Selecciona", ["Scatterplot", "Radares Mov. sin Balón"], index=0, horizontal=False)

        st.markdown("### Grupo de Posición")
        grupos_ok = ["Centrales","Carrileros/Laterales","Contenciones","Interiores","Volantes Ofensivos","Extremos","Delanteros"]
        grupo_sel = st.radio("Grupo", grupos_ok, index=0)

        st.markdown("### Filtros")
        if df_d["Age"].notna().any():
            age_min = int(np.nanmin(df_d["Age"])); age_max = int(np.nanmax(df_d["Age"]))
            edad_sel = st.slider("Edad", min_value=age_min, max_value=age_max, value=(max(17, age_min), age_max))
        else:
            edad_sel = None
            st.caption("No se pudo derivar 'Edad' desde Birthdate.")

    # -------- Subset + filtros --------
    df_view = df_d[df_d["Grupo"] == grupo_sel].copy()
    if edad_sel:
        df_view = df_view[df_view["Age"].between(edad_sel[0], edad_sel[1])]
    if df_view.empty:
        st.info("No hay jugadores tras aplicar los filtros seleccionados."); st.stop()

    # ========================= Scatter =========================
    if modo == "Scatterplot":
        st.markdown("#### Variables del gráfico (elige X e Y)")

        exclude_exact = {"Player","Short name","Player ID","Birthdate","Position","Grupo","third","channel","Age","_MinutesSize"}
        num_cols = [c for c in df_view.columns if c not in exclude_exact and not c.startswith("_") and pd.api.types.is_numeric_dtype(df_view[c])]
        if not num_cols:
            st.warning("No se encontraron métricas válidas para graficar."); st.stop()

        default_x = num_cols[0]
        default_y = num_cols[1] if len(num_cols) > 1 else num_cols[0]

        colx, coly = st.columns(2)
        with colx:
            x_var = st.selectbox("Eje X", options=num_cols, index=num_cols.index(default_x))
        with coly:
            y_var = st.selectbox("Eje Y", options=num_cols, index=num_cols.index(default_y))

        # Tamaño por minutos (usa _MinutesSize si existe; si no, fijo)
        SIZE_COL = "_MinutesSize" if ("_MinutesSize" in df_view.columns and pd.api.types.is_numeric_dtype(df_view["_MinutesSize"])) else None

        x_dom = _domain_with_pad(df_view[x_var]); y_dom = _domain_with_pad(df_view[y_var])
        x_scale = alt.Scale(domain=x_dom, nice=True, zero=False)
        y_scale = alt.Scale(domain=y_dom, nice=True, zero=False)

        jugadores = sorted(df_view["Player"].dropna().astype(str).unique())
        hi_sel = st.multiselect("Resalta jugadores", jugadores, default=[])

        d = df_view.copy()
        d["is_highlight"] = d["Player"].isin(hi_sel)

        sel = alt.selection_point(fields=["Player"], on="click", toggle=True, clear="dblclick", empty="none")

        base = alt.Chart(d).encode(
            x=alt.X(x_var, title=x_var, axis=alt.Axis(format="~s"), scale=x_scale),
            y=alt.Y(y_var, title=y_var, axis=alt.Axis(format="~s"), scale=y_scale),
            tooltip=[
                alt.Tooltip("Player:N", title="Jugador"),
                alt.Tooltip("Position:N", title="Posición"),
                alt.Tooltip("Grupo:N", title="Grupo"),
                alt.Tooltip(x_var, title=x_var, format=",.2f"),
                alt.Tooltip(y_var, title=y_var, format=",.2f"),
            ] + ([alt.Tooltip("_MinutesSize:Q", title="Min/partido (proxy)", format=",.1f")] if SIZE_COL else [])
        )

        size_enc = alt.Size("_MinutesSize", legend=None, scale=alt.Scale(range=[30, 500])) if SIZE_COL else alt.value(120)

        pts_base = base.mark_circle().encode(size=size_enc, color=alt.value(GRAY_BASE), opacity=alt.value(0.35))
        pts_sel  = base.transform_filter(sel).mark_circle().encode(size=size_enc, color=alt.value(ORANGE), opacity=alt.value(1.0)).add_params(sel)
        pts_list = base.transform_filter(alt.datum.is_highlight).mark_circle().encode(size=size_enc, color=alt.value(ORANGE), opacity=alt.value(1.0))

        labels_sel = base.transform_filter(sel).mark_text(dx=6, dy=-6, fontWeight="bold", color="#000000", clip=False).encode(text="Player:N")
        labels_list = base.transform_filter(alt.datum.is_highlight).mark_text(dx=6, dy=-6, fontWeight="bold", color="#000000", clip=False).encode(text="Player:N")

        x_mean = float(d[x_var].mean(skipna=True)); y_mean = float(d[y_var].mean(skipna=True))
        vline  = alt.Chart(pd.DataFrame({"v":[x_mean]})).mark_rule(strokeDash=[5,5], color="#9A9A9A", opacity=0.8).encode(x="v:Q")
        hline  = alt.Chart(pd.DataFrame({"h":[y_mean]})).mark_rule(strokeDash=[5,5], color="#9A9A9A", opacity=0.8).encode(y="h:Q")

        chart = (pts_base + pts_sel + pts_list + labels_sel + labels_list + vline + hline).properties(
            height=560, background="transparent",
            padding={"left": 10, "right": 160, "top": 40, "bottom": 30}
        ).configure_view(strokeWidth=0).configure_axis(
            grid=False, domain=False, tickColor=AXIS_COL, labelColor=AXIS_COL, titleColor=AXIS_COL
        )

        st.altair_chart(chart, use_container_width=True, theme=None)

    # ========================= Radar + KDE =========================
    else:
        st.markdown("#### Radares de Movimientos sin Balón")


        # Usa EXACTAMENTE los nombres tras el renombrado
        fases_desmarque = {
            "Volumen": [
                "Desmarques peligrosos",
                "Desmarques intentados",
                "Desmarques recibidos",
            ],
            "Peligrosidad": [
                "Peligrosidad de Desmarques",
                "Peligrosidad de Desmarques intentados",
                "Peligrosidad de Desmarques recibidos",
                "Desmarques peligrosos intentados",
                "Desmarques peligrosos recibidos"
            ],
            "Finalización": [
                "Desmarques que terminan en gol",
                "Desmarques que terminan en remate",
            ],
        }
        invertir_vars = {"Desmarques peligrosos recibidos", "Peligrosidad de Desmarques recibidos", "Desmarques recibidos"}  # menor=mejor

        jugadores = sorted(df_view["Player"].dropna().astype(str).unique())
        if not jugadores:
            st.warning("No hay jugadores tras aplicar filtros."); st.stop()
        jugador_sel = st.selectbox("Jugador", jugadores, index=0)

        left, mid, right = st.columns([0.05, 0.90, 0.05])
        with mid:
            fig = radar_barras_plotly_player(
                jugador=jugador_sel,
                df=df_view,
                fases_juego=fases_desmarque,
                id_col="Player",
                invertir_vars=invertir_vars,
                colores_fases=("rgba(59,130,246,0.90)", "rgba(245,158,11,0.90)", "rgba(16,185,129,0.90)"),
                chart_height=640
            )
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, theme=None)

        st.markdown("#### Distribuciones por métrica")
        charts = build_kde_charts(
            df=df_view,
            jugador=jugador_sel,
            fases_juego=fases_desmarque,
            id_col="Player",
            invertir_vars_kde=invertir_vars,
            height_each=120
        )
        if charts:
            for i in range(0, len(charts), 3):
                cols = st.columns(3, gap="large")
                for j in range(3):
                    if i + j < len(charts):
                        with cols[j]:
                            st.altair_chart(charts[i + j], use_container_width=True, theme=None)




##############################################################################################################
############################## Ligas Alternas ################################################################
##############################################################################################################

# =========================================
# LIGAS ALTERNAS — Base(s) alternas (sin depender de columnas internas)
# =========================================
if seleccion == "Ligas Alternas":
    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.decomposition import PCA

    st.markdown("<h3 style='margin-bottom: 15px; text-align: center;'>Ligas Alternas</h3>", unsafe_allow_html=True)

    # ========= LIGA / TEMPORADA controladas por ti =========
    st.sidebar.markdown("### Selecciona la Liga y Temporada (Ligas Alternas)")

    # 1) Define aquí las ligas y sus temporadas
    ligas_temporadas_la = {
        # EDITA/AGREGA AQUÍ
        "MLS Next Pro, USA": ["2025"],
        "Liga de Expansión, México": ["24/25", "25/26"],
        "Liga MX Sub-21, México": ["25/26"],
        "Liga MX Sub-23, México": ["24/25"],
        "Liga 1, Perú": ["2025"],
        "Copa Tigo, Bolivia": ["2025"],
        "Liga Futve, Venezuela": ["2025"],
        "Challenger Pro, Bélgica": ["24/25"],
        "Série B, Brasil": ["2025"],
        "Primera División, Costa Rica": ["24/25"],
        "Superleague, Croacia": ["24/25"],
        "Chance Liga, Rep. Checa": ["24/25"],
        "Superliga, Dinamarca": ["24/25"],
        "Championship, Inglaterra": ["24/25"],
        "Ligue 2, Francia": ["24/25"],
        "Bundesliga 2, Alemania": ["24/25"],
        "Super League, Grecia": ["24/25"],
        "J1 League, Japón": ["2025"],
        "K League, Korea": ["2025"],
        "Liga Profesional, Panamá": ["2025"],
        "Primera División, Polonia": ["24/25"],
        "Segunda Liga, Portugal": ["24/25"],
        "Pro League, Arabia": ["24/25"],
        "Premiership, Escocia": ["24/25"],
        "Primera RFEF, España": ["24/25"],
        "Segunda RFEF, España": ["24/25"],
        "Primera División, Turquía": ["24/25"],
        "Bundesliga, Austria": ["24/25"],
        "Super League, Suiza": ["24/25"],
        "Stars League, Qatar": ["24/25"],
        "Pro League, Emiratos Árabes": ["24/25"],

    }

    # 2) Mapea (liga, temporada) -> archivo CSV (ya filtrado como tú quieras)
    archivos_csv_la = {
        # EDITA/AGREGA AQUÍ
        ("MLS Next Pro, USA", "2025"): "nextpro2025.csv",
        ("Liga de Expansión, México", "24/25"): "expansion2425.csv",
        ("Liga de Expansión, México", "25/26"): "expansion2526.csv",
        ("Liga MX Sub-21, México", "25/26"): "sub212526.csv",
        ("Liga MX Sub-23, México", "24/25"): "sub232425.csv",
        ("Liga 1, Perú", "2025"): "peru2025.csv",
        ("Copa Tigo, Bolivia", "2025"): "bolivia2025.csv",
        ("Liga Futve, Venezuela", "2025"): "venezuela2025.csv",
        ("Challenger Pro, Bélgica", "24/25"): "challengerpro2425.csv",
        ("Série B, Brasil", "2025"): "serieb2025.csv",
        ("Primera División, Costa Rica", "24/25"): "costarica2425.csv",
        ("Superleague, Croacia", "24/25"): "croacia2425.csv",
        ("Chance Liga, Rep. Checa", "24/25"): "checa2425.csv",
        ("Superliga, Dinamarca", "24/25"): "denmark2425.csv",
        ("Championship, Inglaterra", "24/25"): "championship2425.csv",
        ("Ligue 2, Francia", "24/25"): "ligue22425.csv",
        ("Bundesliga 2, Alemania", "24/25"): "bundes22425.csv",
        ("Super League, Grecia", "24/25"): "grecia2425.csv",
        ("J1 League, Japón", "2025"): "japan2025.csv",
        ("K League, Korea", "2025"): "korea2025.csv",
        ("Liga Profesional, Panamá", "2025"): "panama2025.csv",
        ("Primera División, Polonia", "24/25"): "polonia2425.csv",
        ("Segunda Liga, Portugal", "24/25"): "portugal22425.csv",
        ("Pro League, Arabia", "24/25"): "arabia2425.csv",
        ("Premiership, Escocia", "24/25"): "escocia2425.csv",
        ("Primera RFEF, España", "24/25"): "primerarfef2425.csv",
        ("Segunda RFEF, España", "24/25"): "segundarfef2425.csv",
        ("Primera División, Turquía", "24/25"): "turquia2425.csv",
        ("Bundesliga, Austria", "24/25"): "austria2425.csv",
        ("Super League, Suiza", "24/25"): "suiza2425.csv",
        ("Stars League, Qatar", "24/25"): "qatar2425.csv",
        ("Pro League, Emiratos Árabes", "24/25"): "uae2425.csv",
       
    }


    # 3) Selectores
    ligas_disponibles_la = list(ligas_temporadas_la.keys())
    if not ligas_disponibles_la:
        st.error("Configura al menos una liga en 'ligas_temporadas_la'.")
        st.stop()

    liga_seleccionada = st.sidebar.selectbox("Liga (Ligas Alternas)", ligas_disponibles_la, index=0)

    temporadas_disponibles_la = ligas_temporadas_la.get(liga_seleccionada, [])
    if not temporadas_disponibles_la:
        st.error("Configura al menos una temporada para la liga seleccionada.")
        st.stop()

    temporada_seleccionada = st.sidebar.selectbox("Temporada", temporadas_disponibles_la, index=0)

    # 4) Carga del CSV exacto según el mapeo (SIN verificar columnas internas)
    archivo_la = archivos_csv_la.get((liga_seleccionada, temporada_seleccionada))
    if not archivo_la:
        st.error("No hay archivo CSV mapeado para esta liga/temporada.")
        st.stop()

    # Lectura robusta (coma o punto y coma)
    try:
        df_all = pd.read_csv(archivo_la)
    except Exception:
        df_all = pd.read_csv(archivo_la, sep=";")

    # Limpieza mínima de headers
    df_all.columns = df_all.columns.str.strip()

    # >>> SIN filtro por Competition/Season: usas todo el CSV seleccionado
    df_filtrado = df_all.copy()

    if df_filtrado.empty:
        st.warning("El CSV seleccionado no tiene datos.")
        st.stop()

    # ========== GRUPO DE POSICIÓN ==========
    st.sidebar.markdown("### Grupo de Posición")
    grupos_posicion = ["Porteros", "Centrales", "Carrileros/Laterales", "Contenciones",
                       "Interiores", "Volantes Ofensivos", "Extremos", "Delanteros"]

    slug_liga = str(liga_seleccionada).lower().replace(" ", "_")
    slug_temp = str(temporada_seleccionada).lower().replace(" ", "_").replace("/", "_")
    grupo_seleccionado = st.sidebar.radio(
        "Grupo",
        grupos_posicion,
        index=0,
        key=f"la_grupo_pos__{slug_liga}__{slug_temp}"
)


    st.markdown(
        f"Has seleccionado: <b>{grupo_seleccionado}</b> en <b>{liga_seleccionada}</b> – <i>{temporada_seleccionada}</i>",
        unsafe_allow_html=True
    )


    # ========================
    # Auxiliares
    # ========================
    def _as_num(df_, cols):
        X = df_[cols].copy()
        for c in cols:
            X[c] = pd.to_numeric(X[c], errors="coerce")
        return X.fillna(0.0)

    def _minmax_0_100(s):
        s = pd.to_numeric(s, errors="coerce")
        lo, hi = np.nanmin(s), np.nanmax(s)
        if not np.isfinite(lo) or not np.isfinite(hi) or hi == lo:
            return pd.Series([50.0]*len(s), index=s.index)
        return 100.0 * (s - lo) / (hi - lo)

    # ========================
    # PORTEROS
    # ========================
    def_vars_gk = [
        "Porterías imbatidas en los 90", "Paradas, %", "xG en contra", "Goles evitados", "Salidas/90", "Duelos aéreos en los 90"
    ]
    ball_vars_gk = [
        "Pases/90", "Pases recibidos /90", "Precisión pases, %", "Pases largos/90", "Precisión pases largos, %",
        "Pases progresivos/90", "Precisión pases progresivos, %"
    ]

    def perfil_porteros_la(df_in):
        dfp = df_in.copy()
        dfp = dfp[dfp["Posición específica"].astype(str).str.contains("GK", case=False)].copy()

        # Minutos
        dfp["Minutos jugados"] = pd.to_numeric(dfp["Minutos jugados"], errors="coerce")
        mins_validos = dfp["Minutos jugados"].dropna()
        if mins_validos.empty:
            st.warning("No hay datos válidos de minutos para porteros."); st.stop()
        min_val, max_val = int(mins_validos.min()), int(mins_validos.max())
        min_default = max(600, min_val)
        rango_mins = st.sidebar.slider("Rango de Minutos Jugados", min_val, max_val, (min_default, max_val), key="gk_mins")
        dfp = dfp[dfp["Minutos jugados"].between(rango_mins[0], rango_mins[1])]

        # Edad
        dfp["Edad"] = pd.to_numeric(dfp["Edad"], errors="coerce")
        edad_validos = dfp["Edad"].dropna()
        if edad_validos.empty:
            st.warning("No hay datos válidos de edad para porteros."); st.stop()
        amin, amax = int(edad_validos.min()), int(edad_validos.max())
        rango_edad = st.sidebar.slider("Rango de Edad", amin, amax, (17, 36), key="gk_age")
        dfp = dfp[dfp["Edad"].between(rango_edad[0], rango_edad[1])]

        # Nacionalidad
        nats = sorted(dfp["País de nacimiento"].dropna().unique())
        sel_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True, key="gk_nat_all")
        selected = nats if sel_all else st.sidebar.multiselect("Nacionalidades", nats, default=nats, key="gk_nat_list")
        dfp = dfp[dfp["País de nacimiento"].isin(selected)]

        # Rankings
        scaler = MinMaxScaler()
        def_cols = [c for c in def_vars_gk if c in dfp.columns]
        bal_cols = [c for c in ball_vars_gk if c in dfp.columns]

        if "xG en contra" in def_cols:
            dfp["xG en contra (inv)"] = -pd.to_numeric(dfp["xG en contra"], errors="coerce")
            def_cols = [c if c != "xG en contra" else "xG en contra (inv)" for c in def_cols]

        dfp["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(_as_num(dfp, def_cols))) if len(def_cols) >= 2 else 0.0
        dfp["_bal"] = PCA(n_components=1).fit_transform(scaler.fit_transform(_as_num(dfp, bal_cols))) if len(bal_cols) >= 2 else 0.0

        dfp["Ranking General Atajadas"] = _minmax_0_100(dfp["_def"])
        dfp["Ranking Juego de Pies"]    = _minmax_0_100(dfp["_bal"])

        # Variables (baseline: dos rankings distintos)
        grupos_variables = {
            "Con Balón": bal_cols if bal_cols else ["Ranking Juego de Pies"],
            "Defensivas": def_cols if def_cols else ["Ranking General Atajadas"],
            "Rankings": ["Ranking General Atajadas", "Ranking Juego de Pies"]
        }
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo X", list(grupos_variables.keys()), index=2, key="gk_tipo_x")
            var_x = st.selectbox("Variable X", grupos_variables[tipo_x], index=0, key="gk_var_x")
        with coly:
            tipo_y = st.selectbox("Grupo Y", list(grupos_variables.keys()), index=2, key="gk_tipo_y")
            default_idx_y = 1 if (tipo_y == "Rankings" and len(grupos_variables[tipo_y]) > 1) else 0
            var_y = st.selectbox("Variable Y", grupos_variables[tipo_y], index=default_idx_y, key="gk_var_y")

        # Highlight
        jugadores = sorted(dfp["Jugador"].dropna().unique())
        highlight_sel = st.multiselect("Highlight jugadores", jugadores, default=[], key="gk_highlight")

        # Alias para helper + preservar Equipo en tooltip
        dfp["Name"] = dfp["Jugador"]
        dfp["Team"] = dfp["Equipo"]

        scatter_interactivo_altair(
            dfp,
            x=var_x,
            y=var_y,
            size_col="Minutos jugados",
            tooltip_cols=["Jugador","Equipo","Posición específica","Edad","País de nacimiento","Minutos jugados","Ranking General Atajadas","Ranking Juego de Pies"],
            highlight_names=highlight_sel
        )

    # ========================
    # CENTRALES
    # ========================
    def_vars_cb = [
        "Acciones defensivas realizadas/90", "Duelos defensivos/90", "Duelos defensivos ganados, %", "Duelos aéreos en los 90",
        "Duelos aéreos ganados, %", "Entradas/90", "Posesión conquistada después de una entrada", "Tiros interceptados/90",
        "Interceptaciones/90", "Posesión conquistada después de una interceptación"
    ]
    ball_vars_cb = [
        "Carreras en progresión/90", "Aceleraciones/90", "Pases/90", "Precisión pases, %", "Pases hacia adelante/90",
        "Pases largos/90", "Precisión pases largos, %", "Pases en profundidad/90", "Pases progresivos/90"
    ]

    def perfil_centrales_la(df_in):
        dfc = df_in.copy()
        # Abreviaturas tipo "CB", "LCB", "RCB", combinaciones "RCB, CB", etc.
        dfc = dfc[dfc["Posición específica"].astype(str).str.contains("CB", na=False)].copy()

        # Minutos
        dfc["Minutos jugados"] = pd.to_numeric(dfc["Minutos jugados"], errors="coerce")
        mins_validos = dfc["Minutos jugados"].dropna()
        if mins_validos.empty:
            st.warning("No hay datos válidos de minutos para centrales."); st.stop()
        min_val, max_val = int(mins_validos.min()), int(mins_validos.max())
        min_default = max(600, min_val)
        rango_mins = st.sidebar.slider("Rango de Minutos Jugados", min_val, max_val, (min_default, max_val), key="cb_mins")
        dfc = dfc[dfc["Minutos jugados"].between(rango_mins[0], rango_mins[1])]

        # Edad
        dfc["Edad"] = pd.to_numeric(dfc["Edad"], errors="coerce")
        edad_validos = dfc["Edad"].dropna()
        if edad_validos.empty:
            st.warning("No hay datos válidos de edad para centrales."); st.stop()
        amin, amax = int(edad_validos.min()), int(edad_validos.max())
        rango_edad = st.sidebar.slider("Rango de Edad", amin, amax, (17, 36), key="cb_age")
        dfc = dfc[dfc["Edad"].between(rango_edad[0], rango_edad[1])]

        # Nacionalidad
        nats = sorted(dfc["País de nacimiento"].dropna().unique())
        sel_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True, key="cb_nat_all")
        selected = nats if sel_all else st.sidebar.multiselect("Nacionalidades", nats, default=nats, key="cb_nat_list")
        dfc = dfc[dfc["País de nacimiento"].isin(selected)]

        # Rankings
        scaler = MinMaxScaler()
        def_cols = [c for c in def_vars_cb if c in dfc.columns]
        bal_cols = [c for c in ball_vars_cb if c in dfc.columns]

        dfc["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(_as_num(dfc, def_cols))) if len(def_cols) >= 2 else 0.0
        dfc["_bal"] = PCA(n_components=1).fit_transform(scaler.fit_transform(_as_num(dfc, bal_cols))) if len(bal_cols) >= 2 else 0.0

        dfc["Ranking General Defensivo"] = _minmax_0_100(dfc["_def"])
        dfc["Ranking Con Balón"] = _minmax_0_100(dfc["_bal"])

        # Variables (baseline: dos rankings distintos)
        grupos_variables = {
            "Con Balón": bal_cols if bal_cols else ["Ranking Con Balón"],
            "Defensivas": def_cols if def_cols else ["Ranking General Defensivo"],
            "Rankings": ["Ranking General Defensivo", "Ranking Con Balón"]
        }
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo X", list(grupos_variables.keys()), index=2, key="cb_tipo_x")
            var_x = st.selectbox("Variable X", grupos_variables[tipo_x], index=0, key="cb_var_x")
        with coly:
            tipo_y = st.selectbox("Grupo Y", list(grupos_variables.keys()), index=2, key="cb_tipo_y")
            default_idx_y = 1 if (tipo_y == "Rankings" and len(grupos_variables[tipo_y]) > 1) else 0
            var_y = st.selectbox("Variable Y", grupos_variables[tipo_y], index=default_idx_y, key="cb_var_y")

        # Highlight
        jugadores = sorted(dfc["Jugador"].dropna().unique())
        highlight_sel = st.multiselect("Highlight jugadores", jugadores, default=[], key="cb_highlight")

        # Alias
        dfc["Name"] = dfc["Jugador"]
        dfc["Team"] = dfc["Equipo"]

        scatter_interactivo_altair(
            dfc,
            x=var_x,
            y=var_y,
            size_col="Minutos jugados",
            tooltip_cols=["Jugador","Equipo","Posición específica","Edad","País de nacimiento","Minutos jugados","Ranking General Defensivo","Ranking Con Balón"],
            highlight_names=highlight_sel
        )

    # ========================
    # CARRILEROS / LATERALES
    # ========================
    def_vars_wb = [
        "Acciones defensivas realizadas/90", "Duelos defensivos ganados, %", "Entradas/90",
        "Posesión conquistada después de una entrada", "Interceptaciones/90",
        "Posesión conquistada después de una interceptación", "Duelos defensivos/90", "Tiros interceptados/90"
    ]
    ball_vars_wb = [
        "Carreras en progresión/90", "Aceleraciones/90", "Acciones de ataque exitosas/90",
        "Goles (excepto los penaltis)", "xG/90", "Remates", "Remates/90", "Tiros a la portería, %",
        "Asistencias/90", "Centros/90", "Precisión centros, %", "Regates/90", "Duelos atacantes ganados, %",
        "Toques en el área de penalti/90", "Pases/90", "Pases hacia adelante/90", "xA/90",
        "Second assists/90", "Third assists/90", "Desmarques/90", "Precisión desmarques, %",
        "Jugadas claves/90", "Pases en el último tercio/90", "Centros desde el último tercio/90", "Pases progresivos/90"
    ]

    def perfil_laterales_la(df_in):
        dfl = df_in.copy()
        dfl = dfl[dfl["Posición específica"].astype(str).str.contains("RB|LB|RWB|LWB", na=False)].copy()

        # Minutos
        dfl["Minutos jugados"] = pd.to_numeric(dfl["Minutos jugados"], errors="coerce")
        mins_validos = dfl["Minutos jugados"].dropna()
        if mins_validos.empty:
            st.warning("No hay datos válidos de minutos para laterales."); st.stop()
        min_val, max_val = int(mins_validos.min()), int(mins_validos.max())
        min_default = max(600, min_val)
        rango_mins = st.sidebar.slider("Rango de Minutos Jugados", min_val, max_val, (min_default, max_val), key="wb_mins")
        dfl = dfl[dfl["Minutos jugados"].between(rango_mins[0], rango_mins[1])]

        # Edad
        dfl["Edad"] = pd.to_numeric(dfl["Edad"], errors="coerce")
        edad_validos = dfl["Edad"].dropna()
        if edad_validos.empty:
            st.warning("No hay datos válidos de edad para laterales."); st.stop()
        amin, amax = int(edad_validos.min()), int(edad_validos.max())
        rango_edad = st.sidebar.slider("Rango de Edad", amin, amax, (17, 36), key="wb_age")
        dfl = dfl[dfl["Edad"].between(rango_edad[0], rango_edad[1])]

        # Nacionalidad
        nats = sorted(dfl["País de nacimiento"].dropna().unique())
        sel_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True, key="wb_nat_all")
        selected = nats if sel_all else st.sidebar.multiselect("Nacionalidades", nats, default=nats, key="wb_nat_list")
        dfl = dfl[dfl["País de nacimiento"].isin(selected)]

        # Rankings
        scaler = MinMaxScaler()
        def_cols = [c for c in def_vars_wb if c in dfl.columns]
        bal_cols = [c for c in ball_vars_wb if c in dfl.columns]

        dfl["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(_as_num(dfl, def_cols))) if len(def_cols) >= 2 else 0.0
        dfl["_bal"] = PCA(n_components=1).fit_transform(scaler.fit_transform(_as_num(dfl, bal_cols))) if len(bal_cols) >= 2 else 0.0

        dfl["Ranking General Defensivo"] = _minmax_0_100(dfl["_def"])
        dfl["Ranking Con Balón"]         = _minmax_0_100(dfl["_bal"])

        # Variables (baseline: dos rankings distintos)
        grupos_variables = {
            "Con Balón": bal_cols if bal_cols else ["Ranking Con Balón"],
            "Defensivas": def_cols if def_cols else ["Ranking General Defensivo"],
            "Rankings": ["Ranking General Defensivo", "Ranking Con Balón"]
        }
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo X", list(grupos_variables.keys()), index=2, key="wb_tipo_x")
            var_x = st.selectbox("Variable X", grupos_variables[tipo_x], index=0, key="wb_var_x")
        with coly:
            tipo_y = st.selectbox("Grupo Y", list(grupos_variables.keys()), index=2, key="wb_tipo_y")
            default_idx_y = 1 if (tipo_y == "Rankings" and len(grupos_variables[tipo_y]) > 1) else 0
            var_y = st.selectbox("Variable Y", grupos_variables[tipo_y], index=default_idx_y, key="wb_var_y")

        # Highlight (definido ANTES de llamar al helper)
        jugadores = sorted(dfl["Jugador"].dropna().astype(str).unique())
        highlight_sel = st.multiselect("Highlight jugadores", jugadores, default=[], key="wb_highlight")

        # Alias
        dfl["Name"] = dfl["Jugador"]
        dfl["Team"] = dfl["Equipo"]

        scatter_interactivo_altair(
            dfl,
            x=var_x,
            y=var_y,
            size_col="Minutos jugados",
            tooltip_cols=["Jugador","Equipo","Posición específica","Edad","País de nacimiento","Minutos jugados","Ranking General Defensivo","Ranking Con Balón"],
            highlight_names=highlight_sel
        )

    def perfil_contenciones_la(df_in):
        dfd = df_in.copy()
        # Filtrar posiciones de contención (CDM, RDM, LDM, etc.)
        dfd = dfd[dfd["Posición específica"].astype(str).str.contains("DM", na=False)].copy()

        # Minutos
        dfd["Minutos jugados"] = pd.to_numeric(dfd["Minutos jugados"], errors="coerce")
        mins_validos = dfd["Minutos jugados"].dropna()
        if mins_validos.empty:
            st.warning("No hay datos válidos de minutos para contenciones."); st.stop()
        min_val, max_val = int(mins_validos.min()), int(mins_validos.max())
        min_default = max(600, min_val)
        rango_mins = st.sidebar.slider("Rango de Minutos Jugados", min_val, max_val, (min_default, max_val), key="dm_mins")
        dfd = dfd[dfd["Minutos jugados"].between(rango_mins[0], rango_mins[1])]

        # Edad
        dfd["Edad"] = pd.to_numeric(dfd["Edad"], errors="coerce")
        edad_validos = dfd["Edad"].dropna()
        if edad_validos.empty:
            st.warning("No hay datos válidos de edad para contenciones."); st.stop()
        amin, amax = int(edad_validos.min()), int(edad_validos.max())
        rango_edad = st.sidebar.slider("Rango de Edad", amin, amax, (17, 36), key="dm_age")
        dfd = dfd[dfd["Edad"].between(rango_edad[0], rango_edad[1])]

        # Nacionalidad
        nats = sorted(dfd["País de nacimiento"].dropna().unique())
        sel_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True, key="dm_nat_all")
        selected = nats if sel_all else st.sidebar.multiselect("Nacionalidades", nats, default=nats, key="dm_nat_list")
        dfd = dfd[dfd["País de nacimiento"].isin(selected)]

        # ------- VARIABLES (las que me diste) -------
        def_vars_dm = [
            "Acciones defensivas realizadas/90", "Duelos defensivos ganados, %", "Entradas/90",
            "Posesión conquistada después de una entrada", "Interceptaciones/90", "Posesión conquistada después de una interceptación"
        ]
        ball_vars_dm = [
            "Carreras en progresión/90", "Aceleraciones/90", "Pases/90", "Precisión pases, %", "Pases hacia adelante/90",
            "Pases largos/90", "Precisión pases largos, %", "Pases en profundidad/90", "Pases progresivos/90",
            "Acciones de ataque exitosas/90", "Remates/90", "Asistencias/90", "Pases recibidos /90", "Second assists/90",
            "Third assists/90", "Jugadas claves/90", "Pases en el último tercio/90", "Pases al área de penalti/90",
            "Precisión pases, %", "Pases recibidos /90", "Pases largos/90", "Precisión pases largos, %", "Longitud media pases, m"
        ]

        # ------- RANKINGS con deduplicación segura -------
        scaler = MinMaxScaler()

        # limpiar listas para evitar duplicados y sólo columnas existentes
        def_cols = [c for c in dict.fromkeys(def_vars_dm) if c in dfd.columns]
        bal_cols = [c for c in dict.fromkeys(ball_vars_dm) if c in dfd.columns]

        # matrices numéricas robustas (dedup y coerción)
        X_def = _as_num(dfd, def_cols)
        X_bal = _as_num(dfd, bal_cols)

        dfd["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(X_def)) if X_def.shape[1] >= 2 else 0.0
        dfd["_bal"] = PCA(n_components=1).fit_transform(scaler.fit_transform(X_bal)) if X_bal.shape[1] >= 2 else 0.0

        dfd["Ranking General Defensivo"] = _minmax_0_100(dfd["_def"])
        dfd["Ranking Con Balón"]         = _minmax_0_100(dfd["_bal"])

        # Variables (baseline: dos rankings distintos)
        grupos_variables = {
            "Con Balón": bal_cols if bal_cols else ["Ranking Con Balón"],
            "Defensivas": def_cols if def_cols else ["Ranking General Defensivo"],
            "Rankings": ["Ranking General Defensivo", "Ranking Con Balón"]
        }
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo X", list(grupos_variables.keys()), index=2, key="dm_tipo_x")
            var_x = st.selectbox("Variable X", grupos_variables[tipo_x], index=0, key="dm_var_x")
        with coly:
            tipo_y = st.selectbox("Grupo Y", list(grupos_variables.keys()), index=2, key="dm_tipo_y")
            default_idx_y = 1 if (tipo_y == "Rankings" and len(grupos_variables[tipo_y]) > 1) else 0
            var_y = st.selectbox("Variable Y", grupos_variables[tipo_y], index=default_idx_y, key="dm_var_y")

        # Highlight
        jugadores = sorted(dfd["Jugador"].dropna().unique())
        highlight_sel = st.multiselect("Highlight jugadores", jugadores, default=[], key="dm_highlight")

        # Alias
        dfd["Name"] = dfd["Jugador"]
        dfd["Team"] = dfd["Equipo"]

        scatter_interactivo_altair(
            dfd,
            x=var_x,
            y=var_y,
            size_col="Minutos jugados",
            tooltip_cols=["Jugador","Equipo","Posición específica","Edad","País de nacimiento","Minutos jugados","Ranking General Defensivo","Ranking Con Balón"],
            highlight_names=highlight_sel
        )


    # ========================
    # INTERIORES
    # ========================
    def_vars_cm = [
        "Acciones defensivas realizadas/90", "Duelos defensivos ganados, %", "Entradas/90",
        "Posesión conquistada después de una entrada", "Interceptaciones/90", "Posesión conquistada después de una interceptación"
    ]
    ball_vars_cm = [
        "Carreras en progresión/90", "Aceleraciones/90", "Pases/90", "Precisión pases, %", "Pases hacia adelante/90",
        "Pases largos/90", "Precisión pases largos, %", "Pases en profundidad/90", "Pases progresivos/90",
        "Acciones de ataque exitosas/90", "Remates/90", "Asistencias/90", "Pases recibidos /90", "Second assists/90",
        "Third assists/90", "Jugadas claves/90", "Pases en el último tercio/90", "Pases al área de penalti/90",
        "Precisión pases, %", "Pases recibidos /90", "Pases largos/90", "Precisión pases largos, %", "Longitud media pases, m"
    ]

    def perfil_interiores_la(df_in):
        dfi = df_in.copy()
        # Filtrar interiores (CM, RCM, LCM, etc.)
        dfi = dfi[dfi["Posición específica"].astype(str).str.contains("CM", na=False)].copy()

        # Minutos (robusto a NaN)
        dfi["Minutos jugados"] = pd.to_numeric(dfi["Minutos jugados"], errors="coerce")
        mins_validos = dfi["Minutos jugados"].dropna()
        if mins_validos.empty:
            st.warning("No hay datos válidos de minutos para interiores."); st.stop()
        min_val, max_val = int(mins_validos.min()), int(mins_validos.max())
        min_default = max(600, min_val)
        rango_mins = st.sidebar.slider("Rango de Minutos Jugados", min_val, max_val, (min_default, max_val), key="cm_mins")
        dfi = dfi[dfi["Minutos jugados"].between(rango_mins[0], rango_mins[1])]

        # Edad (robusto a NaN)
        dfi["Edad"] = pd.to_numeric(dfi["Edad"], errors="coerce")
        edad_validos = dfi["Edad"].dropna()
        if edad_validos.empty:
            st.warning("No hay datos válidos de edad para interiores."); st.stop()
        amin, amax = int(edad_validos.min()), int(edad_validos.max())
        rango_edad = st.sidebar.slider("Rango de Edad", amin, amax, (17, 36), key="cm_age")
        dfi = dfi[dfi["Edad"].between(rango_edad[0], rango_edad[1])]

        # Nacionalidad
        nats = sorted(dfi["País de nacimiento"].dropna().astype(str).unique())
        sel_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True, key="cm_nat_all")
        selected = nats if sel_all else st.sidebar.multiselect("Nacionalidades", nats, default=nats, key="cm_nat_list")
        dfi = dfi[dfi["País de nacimiento"].isin(selected)]

        # ===== Rankings (PCA → 0–100) con deduplicación segura =====
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.decomposition import PCA
        scaler = MinMaxScaler()

        # listas deduplicadas y solo columnas presentes
        def_cols = [c for c in dict.fromkeys(def_vars_cm) if c in dfi.columns]
        bal_cols = [c for c in dict.fromkeys(ball_vars_cm) if c in dfi.columns]

        X_def = _as_num(dfi, def_cols)
        X_bal = _as_num(dfi, bal_cols)

        dfi["_def"] = PCA(n_components=1).fit_transform(scaler.fit_transform(X_def)) if X_def.shape[1] >= 2 else 0.0
        dfi["_bal"] = PCA(n_components=1).fit_transform(scaler.fit_transform(X_bal)) if X_bal.shape[1] >= 2 else 0.0

        dfi["Ranking General Defensivo"] = _minmax_0_100(dfi["_def"])
        dfi["Ranking Con Balón"]         = _minmax_0_100(dfi["_bal"])

        # Variables (baseline: dos rankings distintos)
        grupos_variables = {
            "Con Balón": bal_cols if bal_cols else ["Ranking Con Balón"],
            "Defensivas": def_cols if def_cols else ["Ranking General Defensivo"],
            "Rankings": ["Ranking General Defensivo", "Ranking Con Balón"]
        }
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo X", list(grupos_variables.keys()), index=2, key="cm_tipo_x")
            var_x = st.selectbox("Variable X", grupos_variables[tipo_x], index=0, key="cm_var_x")
        with coly:
            tipo_y = st.selectbox("Grupo Y", list(grupos_variables.keys()), index=2, key="cm_tipo_y")
            default_idx_y = 1 if (tipo_y == "Rankings" and len(grupos_variables[tipo_y]) > 1) else 0
            var_y = st.selectbox("Variable Y", grupos_variables[tipo_y], index=default_idx_y, key="cm_var_y")

        # Highlight
        jugadores = sorted(dfi["Jugador"].dropna().astype(str).unique())
        highlight_sel = st.multiselect("Highlight jugadores", jugadores, default=[], key="cm_highlight")

        # Alias para tu helper y mantener 'Equipo' en tooltip
        dfi["Name"] = dfi["Jugador"]
        dfi["Team"] = dfi["Equipo"]

        # Tooltips
        tooltip_cols = [c for c in [
            "Jugador","Equipo","Posición específica","Edad","País de nacimiento","Minutos jugados",
            "Ranking General Defensivo","Ranking Con Balón"
        ] if c in dfi.columns]

        scatter_interactivo_altair(
            dfi,
            x=var_x,
            y=var_y,
            size_col="Minutos jugados",
            tooltip_cols=tooltip_cols,
            highlight_names=highlight_sel
        )
    

    # ========================
    # VOLANTES OFENSIVOS
    # ========================
    def_vars_am = [
        "Goles", "xG", "Asistencias", "xA", "Remates", "Tiros a la portería, %",
        "Goles hechos, %", "Second assists/90", "Third assists/90", "Jugadas claves/90"
    ]
    ball_vars_am = [
        "Carreras en progresión/90", "Aceleraciones/90", "Pases/90", "Precisión pases, %", "Pases hacia adelante/90",
        "Pases largos/90", "Precisión pases largos, %", "Pases en profundidad/90", "Pases progresivos/90",
        "Acciones de ataque exitosas/90", "Remates/90", "Asistencias/90", "Pases recibidos /90", "Second assists/90",
        "Third assists/90", "Jugadas claves/90", "Pases en el último tercio/90", "Pases al área de penalti/90",
        "Precisión pases, %", "Pases recibidos /90", "Pases largos/90", "Precisión pases largos, %", "Longitud media pases, m"
    ]

    def perfil_volantes_of_la(df_in):
        dfv = df_in.copy()
        # Filtrar volantes ofensivos (AM, CAM, LAM, RAM, etc.)
        dfv = dfv[dfv["Posición específica"].astype(str).str.contains("AM", na=False)].copy()

        # Minutos (robusto a NaN)
        dfv["Minutos jugados"] = pd.to_numeric(dfv["Minutos jugados"], errors="coerce")
        mins_validos = dfv["Minutos jugados"].dropna()
        if mins_validos.empty:
            st.warning("No hay datos válidos de minutos para volantes ofensivos."); st.stop()
        min_val, max_val = int(mins_validos.min()), int(mins_validos.max())
        min_default = max(600, min_val)
        rango_mins = st.sidebar.slider("Rango de Minutos Jugados", min_val, max_val, (min_default, max_val), key="am_mins")
        dfv = dfv[dfv["Minutos jugados"].between(rango_mins[0], rango_mins[1])]

        # Edad (robusto a NaN)
        dfv["Edad"] = pd.to_numeric(dfv["Edad"], errors="coerce")
        edad_validos = dfv["Edad"].dropna()
        if edad_validos.empty:
            st.warning("No hay datos válidos de edad para volantes ofensivos."); st.stop()
        amin, amax = int(edad_validos.min()), int(edad_validos.max())
        rango_edad = st.sidebar.slider("Rango de Edad", amin, amax, (17, 36), key="am_age")
        dfv = dfv[dfv["Edad"].between(rango_edad[0], rango_edad[1])]

        # Nacionalidad
        nats = sorted(dfv["País de nacimiento"].dropna().astype(str).unique())
        sel_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True, key="am_nat_all")
        selected = nats if sel_all else st.sidebar.multiselect("Nacionalidades", nats, default=nats, key="am_nat_list")
        dfv = dfv[dfv["País de nacimiento"].isin(selected)]

        # ===== Rankings (PCA → 0–100) con deduplicación segura =====
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.decomposition import PCA
        scaler = MinMaxScaler()

        # Dedup + sólo columnas presentes
        crea_cols = [c for c in dict.fromkeys(ball_vars_am) if c in dfv.columns]   # Creación
        defi_cols = [c for c in dict.fromkeys(def_vars_am) if c in dfv.columns]    # Definición

        X_crea = _as_num(dfv, crea_cols)
        X_defi = _as_num(dfv, defi_cols)

        # PCA (si hay al menos 2 columnas válidas)
        dfv["_crea"] = PCA(n_components=1).fit_transform(scaler.fit_transform(X_crea)) if X_crea.shape[1] >= 2 else 0.0
        dfv["_defi"] = PCA(n_components=1).fit_transform(scaler.fit_transform(X_defi)) if X_defi.shape[1] >= 2 else 0.0

        # 0–100
        dfv["Ranking Creación"]   = _minmax_0_100(dfv["_crea"])
        dfv["Ranking Definición"] = _minmax_0_100(dfv["_defi"])

        # Selector de variables (baseline: dos rankings distintos)
        grupos_variables = {
            "Creación": crea_cols if crea_cols else ["Ranking Creación"],
            "Definición": defi_cols if defi_cols else ["Ranking Definición"],
            "Rankings": ["Ranking Creación", "Ranking Definición"]
        }
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo X", list(grupos_variables.keys()), index=2, key="am_tipo_x")
            var_x = st.selectbox("Variable X", grupos_variables[tipo_x], index=0, key="am_var_x")
        with coly:
            tipo_y = st.selectbox("Grupo Y", list(grupos_variables.keys()), index=2, key="am_tipo_y")
            default_idx_y = 1 if (tipo_y == "Rankings" and len(grupos_variables[tipo_y]) > 1) else 0
            var_y = st.selectbox("Variable Y", grupos_variables[tipo_y], index=default_idx_y, key="am_var_y")

        # Highlight
        jugadores = sorted(dfv["Jugador"].dropna().astype(str).unique())
        highlight_sel = st.multiselect("Highlight jugadores", jugadores, default=[], key="am_highlight")

        # Alias para helper + mantener 'Equipo' en tooltip
        dfv["Name"] = dfv["Jugador"]
        dfv["Team"] = dfv["Equipo"]

        tooltip_cols = [c for c in [
            "Jugador","Equipo","Posición específica","Edad","País de nacimiento","Minutos jugados",
            "Ranking Creación","Ranking Definición"
        ] if c in dfv.columns]

        scatter_interactivo_altair(
            dfv,
            x=var_x,
            y=var_y,
            size_col="Minutos jugados",
            tooltip_cols=tooltip_cols,
            highlight_names=highlight_sel
        )


    # ========================
    # EXTREMOS (Creación / Definición)
    # ========================
    def_vars_w = [
        "Goles", "xG", "Asistencias", "xA", "Remates", "Tiros a la portería, %",
        "Goles hechos, %", "Second assists/90", "Third assists/90", "Jugadas claves/90",
        "Remates/90", "Centros/90", "Precisión centros, %", "Pases hacía el área pequeña, %"
    ]
    ball_vars_w = [
        "Carreras en progresión/90", "Aceleraciones/90", "Pases/90", "Precisión pases, %",
        "Pases en profundidad/90", "Pases progresivos/90", "Acciones de ataque exitosas/90",
        "Pases recibidos /90", "Pases en el último tercio/90", "Pases al área de penalti/90",
        "Regates/90", "Regates realizados, %", "Duelos atacantes ganados, %",
        "Desmarques/90", "Precisión desmarques, %"
    ]

    def perfil_extremos_la(df_in):
        dfx = df_in.copy()
        # Filtrar extremos: LW / RW (excluir WB para no mezclar con carrileros)
        pos = dfx["Posición específica"].astype(str)
        dfx = dfx[pos.str.contains(r"\bLW\b|\bRW\b", na=False) & ~pos.str.contains("WB", na=False)].copy()

        # ---- Minutos
        dfx["Minutos jugados"] = pd.to_numeric(dfx["Minutos jugados"], errors="coerce")
        mins_validos = dfx["Minutos jugados"].dropna()
        if mins_validos.empty:
            st.warning("No hay datos válidos de minutos para extremos."); st.stop()
        min_val, max_val = int(mins_validos.min()), int(mins_validos.max())
        min_default = max(600, min_val)
        rango_mins = st.sidebar.slider("Rango de Minutos Jugados", min_val, max_val,
                                    (min_default, max_val), key="w_mins")
        dfx = dfx[dfx["Minutos jugados"].between(rango_mins[0], rango_mins[1])]

        # ---- Edad
        dfx["Edad"] = pd.to_numeric(dfx["Edad"], errors="coerce")
        edad_validos = dfx["Edad"].dropna()
        if edad_validos.empty:
            st.warning("No hay datos válidos de edad para extremos."); st.stop()
        amin, amax = int(edad_validos.min()), int(edad_validos.max())
        rango_edad = st.sidebar.slider("Rango de Edad", amin, amax, (17, 36), key="w_age")
        dfx = dfx[dfx["Edad"].between(rango_edad[0], rango_edad[1])]

        # ---- Nacionalidad
        nats = sorted(dfx["País de nacimiento"].dropna().astype(str).unique())
        sel_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True, key="w_nat_all")
        selected = nats if sel_all else st.sidebar.multiselect("Nacionalidades", nats, default=nats, key="w_nat_list")
        dfx = dfx[dfx["País de nacimiento"].isin(selected)]

        # ===== Rankings (PCA → 0–100) deduplicando columnas =====
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.decomposition import PCA
        scaler = MinMaxScaler()

        crea_cols = [c for c in dict.fromkeys(ball_vars_w) if c in dfx.columns]   # Creación
        defi_cols = [c for c in dict.fromkeys(def_vars_w)  if c in dfx.columns]   # Definición

        X_crea = _as_num(dfx, crea_cols)
        X_defi = _as_num(dfx, defi_cols)

        dfx["_crea"] = PCA(n_components=1).fit_transform(scaler.fit_transform(X_crea)) if X_crea.shape[1] >= 2 else 0.0
        dfx["_defi"] = PCA(n_components=1).fit_transform(scaler.fit_transform(X_defi)) if X_defi.shape[1] >= 2 else 0.0

        dfx["Ranking Creación"]   = _minmax_0_100(dfx["_crea"])
        dfx["Ranking Definición"] = _minmax_0_100(dfx["_defi"])

        # ---- Variables (baseline: dos rankings distintos)
        grupos_variables = {
            "Creación": crea_cols if crea_cols else ["Ranking Creación"],
            "Definición": defi_cols if defi_cols else ["Ranking Definición"],
            "Rankings": ["Ranking Creación", "Ranking Definición"]
        }
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo X", list(grupos_variables.keys()), index=2, key="w_tipo_x")
            var_x = st.selectbox("Variable X", grupos_variables[tipo_x], index=0, key="w_var_x")
        with coly:
            tipo_y = st.selectbox("Grupo Y", list(grupos_variables.keys()), index=2, key="w_tipo_y")
            default_idx_y = 1 if (tipo_y == "Rankings" and len(grupos_variables[tipo_y]) > 1) else 0
            var_y = st.selectbox("Variable Y", grupos_variables[tipo_y], index=default_idx_y, key="w_var_y")

        # ---- Highlight
        jugadores = sorted(dfx["Jugador"].dropna().astype(str).unique())
        highlight_sel = st.multiselect("Highlight jugadores", jugadores, default=[], key="w_highlight")

        # ---- Alias helper y tooltips
        dfx["Name"] = dfx["Jugador"]
        dfx["Team"] = dfx["Equipo"]

        tooltip_cols = [c for c in [
            "Jugador","Equipo","Posición específica","Edad","País de nacimiento","Minutos jugados",
            "Ranking Creación","Ranking Definición"
        ] if c in dfx.columns]

        scatter_interactivo_altair(
            dfx,
            x=var_x,
            y=var_y,
            size_col="Minutos jugados",
            tooltip_cols=tooltip_cols,
            highlight_names=highlight_sel
        )

    # ========================
    # DELANTEROS (Creación / Definición)
    # ========================
    ball_vars_st = [
    "Goles", "xG", "Asistencias", "xA", "Remates", "Tiros a la portería, %",
    "Goles hechos, %", "Second assists/90", "Third assists/90", "Jugadas claves/90",
    "Remates/90", "Centros/90", "Precisión centros, %", "Pases hacía el área pequeña, %"
    ]
    def_vars_st = [
        "Carreras en progresión/90", "Aceleraciones/90", "Pases/90", "Precisión pases, %",
        "Pases en profundidad/90", "Pases progresivos/90", "Acciones de ataque exitosas/90", "Pases recibidos /90",
        "Pases en el último tercio/90", "Pases al área de penalti/90",
        "Regates/90", "Regates realizados, %", "Duelos atacantes ganados, %", "Desmarques/90", "Precisión desmarques, %"
    ]

    def perfil_delanteros_la(df_in):
        dff = df_in.copy()
        # Filtrar delanteros: ST / CF
        pos = dff["Posición específica"].astype(str)
        dff = dff[pos.str.contains(r"\bST\b|\bCF\b", na=False)].copy()

        # ---- Minutos
        dff["Minutos jugados"] = pd.to_numeric(dff["Minutos jugados"], errors="coerce")
        mins_validos = dff["Minutos jugados"].dropna()
        if mins_validos.empty:
            st.warning("No hay datos válidos de minutos para delanteros."); st.stop()
        min_val, max_val = int(mins_validos.min()), int(mins_validos.max())
        min_default = max(600, min_val)
        rango_mins = st.sidebar.slider("Rango de Minutos Jugados", min_val, max_val,
                                    (min_default, max_val), key="st_mins")
        dff = dff[dff["Minutos jugados"].between(rango_mins[0], rango_mins[1])]

        # ---- Edad
        dff["Edad"] = pd.to_numeric(dff["Edad"], errors="coerce")
        edad_validos = dff["Edad"].dropna()
        if edad_validos.empty:
            st.warning("No hay datos válidos de edad para delanteros."); st.stop()
        amin, amax = int(edad_validos.min()), int(edad_validos.max())
        rango_edad = st.sidebar.slider("Rango de Edad", amin, amax, (17, 36), key="st_age")
        dff = dff[dff["Edad"].between(rango_edad[0], rango_edad[1])]

        # ---- Nacionalidad
        nats = sorted(dff["País de nacimiento"].dropna().astype(str).unique())
        sel_all = st.sidebar.checkbox("Seleccionar todas las nacionalidades", value=True, key="st_nat_all")
        selected = nats if sel_all else st.sidebar.multiselect("Nacionalidades", nats, default=nats, key="st_nat_list")
        dff = dff[dff["País de nacimiento"].isin(selected)]

        # ===== Rankings (PCA → 0–100) deduplicando columnas =====
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.decomposition import PCA
        scaler = MinMaxScaler()

        # Definición (finishing): viene de ball_vars_st
        defi_cols = [c for c in dict.fromkeys(ball_vars_st) if c in dff.columns]
        # Creación (build-up): viene de def_vars_st
        crea_cols = [c for c in dict.fromkeys(def_vars_st)  if c in dff.columns]

        X_defi = _as_num(dff, defi_cols)
        X_crea = _as_num(dff, crea_cols)

        dff["_defi"] = PCA(n_components=1).fit_transform(scaler.fit_transform(X_defi)) if X_defi.shape[1] >= 2 else 0.0
        dff["_crea"] = PCA(n_components=1).fit_transform(scaler.fit_transform(X_crea)) if X_crea.shape[1] >= 2 else 0.0

        dff["Ranking Definición"] = _minmax_0_100(dff["_defi"])
        dff["Ranking Creación"]   = _minmax_0_100(dff["_crea"])

        # ---- Variables (baseline: dos rankings distintos)
        grupos_variables = {
            "Creación": crea_cols if crea_cols else ["Ranking Creación"],
            "Definición": defi_cols if defi_cols else ["Ranking Definición"],
            "Rankings": ["Ranking Creación", "Ranking Definición"]
        }
        colx, coly = st.columns(2)
        with colx:
            tipo_x = st.selectbox("Grupo X", list(grupos_variables.keys()), index=2, key="st_tipo_x")
            var_x = st.selectbox("Variable X", grupos_variables[tipo_x], index=0, key="st_var_x")
        with coly:
            tipo_y = st.selectbox("Grupo Y", list(grupos_variables.keys()), index=2, key="st_tipo_y")
            default_idx_y = 1 if (tipo_y == "Rankings" and len(grupos_variables[tipo_y]) > 1) else 0
            var_y = st.selectbox("Variable Y", grupos_variables[tipo_y], index=default_idx_y, key="st_var_y")

        # ---- Highlight
        jugadores = sorted(dff["Jugador"].dropna().astype(str).unique())
        highlight_sel = st.multiselect("Highlight jugadores", jugadores, default=[], key="st_highlight")

        # ---- Alias helper y tooltips
        dff["Name"] = dff["Jugador"]
        dff["Team"] = dff["Equipo"]

        tooltip_cols = [c for c in [
            "Jugador","Equipo","Posición específica","Edad","País de nacimiento","Minutos jugados",
            "Ranking Creación","Ranking Definición"
        ] if c in dff.columns]

        scatter_interactivo_altair(
            dff,
            x=var_x,
            y=var_y,
            size_col="Minutos jugados",
            tooltip_cols=tooltip_cols,
            highlight_names=highlight_sel
        )



    if grupo_seleccionado == "Porteros":
        perfil_porteros_la(df_filtrado)
    elif grupo_seleccionado == "Centrales":
        perfil_centrales_la(df_filtrado)
    elif grupo_seleccionado == "Carrileros/Laterales":
        perfil_laterales_la(df_filtrado)
    elif grupo_seleccionado == "Contenciones":
        perfil_contenciones_la(df_filtrado)
    elif grupo_seleccionado == "Interiores":
        perfil_interiores_la(df_filtrado)
    elif grupo_seleccionado == "Volantes Ofensivos":
        perfil_volantes_of_la(df_filtrado)
    elif grupo_seleccionado == "Extremos":
        perfil_extremos_la(df_filtrado)
    elif grupo_seleccionado == "Delanteros":
        perfil_delanteros_la(df_filtrado)




##############################################################################################################
############################## Radares Ligas Alternas ########################################################
##############################################################################################################

# ================================
# Radares Ligas Alternas (3 fases)
# ================================
if seleccion == "Radares Ligas Alternas":
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    import altair as alt

    st.markdown("<h3 style='margin-bottom: 15px;'>Radares Ligas Alternas</h3>", unsafe_allow_html=True)

    # --------- Colores / estilo ---------
    FILL_ORANGE = "#f9ae34"
    LINE_BLACK  = "#111111"
    FASE_COLORS = [
        "rgba(59,130,246,0.90)",  # azul
        "rgba(245,158,11,0.90)",  # naranja
        "rgba(16,185,129,0.90)",  # verde
    ]

    # --------- Utils ---------
    def _normalize_metrics(df, metrics, invert=None):
        """
        Normaliza 0–1 por métrica con coerción a numérico.
        Si está en 'invert', aplica 1 - z. NaN -> 0.5
        """
        invert = set(invert or [])
        out = df.copy()
        for m in metrics:
            if m not in out.columns:
                continue
            s = pd.to_numeric(out[m], errors="coerce")
            mn, mx = s.min(), s.max()
            if pd.isna(mn) or pd.isna(mx) or mx == mn:
                out[m] = 0.5
            else:
                z = (s - mn) / (mx - mn)
                out[m] = (1 - z) if m in invert else z
                out[m] = out[m].fillna(0.5)
        return out

    def radar_barras_plotly(
        jugador,
        df,
        fases_juego,         # dict: {fase: [vars]}
        invertir_vars=None,  # set de variables a invertir
        chart_height=640,
        show_silueta=False
    ):
        # Alias para trabajar con 'Name'
        if "Name" not in df.columns and "Jugador" in df.columns:
            df = df.copy()
            df["Name"] = df["Jugador"]

        if "Name" not in df.columns:
            st.warning("La base no tiene la columna 'Jugador'/'Name'."); return None
        if jugador not in df["Name"].values:
            st.warning(f"El jugador '{jugador}' no está en la base."); return None

        invertir = set(invertir_vars or [])

        # Variables presentes (en orden por fase)
        atributos, fase_idx = [], []
        fases_orden = list(fases_juego.keys())
        for i, (fase, vars_fase) in enumerate(fases_juego.items()):
            presentes = [v for v in vars_fase if v in df.columns]
            atributos.extend(presentes)
            fase_idx.extend([i] * len(presentes))
        if not atributos:
            st.warning("No hay variables presentes para construir el radar."); return None

        # Normalización a 0–100
        df_norm = _normalize_metrics(df, atributos, invert=invertir)
        row = df_norm.loc[df_norm["Name"] == jugador].iloc[0]
        r_vals = [float(row[a]) * 100 for a in atributos]

        # Ángulos
        n = len(atributos)
        thetas = np.linspace(0, 360, n, endpoint=False)

        fig = go.Figure()

        # Barras por fase
        for i, fase in enumerate(fases_orden):
            idxs = [k for k, fidx in enumerate(fase_idx) if fidx == i]
            if not idxs:
                continue
            color_i = FASE_COLORS[i % len(FASE_COLORS)]
            fig.add_trace(
                go.Barpolar(
                    r=[r_vals[k] for k in idxs],
                    theta=[thetas[k] for k in idxs],
                    width=[(360/n)*0.98]*len(idxs),
                    marker=dict(color=color_i, line=dict(width=0)),
                    name=fase,
                    hovertemplate="<b>%{customdata[0]}</b><br>Percentil: %{r:.1f}<extra></extra>",
                    customdata=[[atributos[k]] for k in idxs],
                    opacity=0.95,
                )
            )

        # (opcional) silueta poligonal
        if show_silueta:
            fig.add_trace(
                go.Scatterpolar(
                    r=r_vals + [r_vals[0]],
                    theta=thetas.tolist() + [thetas[0]],
                    mode="lines",
                    line=dict(color="rgba(0,0,0,0.35)", width=1),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

        # Etiquetas alrededor
        fig.add_trace(
            go.Scatterpolar(
                r=[110]*n,
                theta=thetas,
                mode="text",
                text=atributos,
                textfont=dict(size=11, color="#2B2B2B"),
                textposition="middle center",
                hoverinfo="skip",
                showlegend=False,
            )
        )

        fig.update_layout(
            template="plotly_white",
            height=chart_height,
            margin=dict(l=10, r=10, t=40, b=40),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    range=[0,112],
                    tickvals=[0,20,40,60,80,100],
                    ticktext=["0","20","40","60","80","100"],
                    showline=True, gridcolor="#E5E5E5", gridwidth=1,
                    tickfont=dict(size=11, color="#2B2B2B"),
                ),
                angularaxis=dict(
                    rotation=0, direction="clockwise", showline=False,
                    gridcolor="#F0F0F0", gridwidth=1,
                    tickfont=dict(size=10, color="#B3B3B3"),
                    ticks="",
                ),
            ),
            legend=dict(
                orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5,
                font=dict(size=12, color="#2B2B2B"), bgcolor="rgba(0,0,0,0)",
            ),
            title=dict(text=f"Radar · {jugador}", x=0.01, y=0.98, font=dict(size=18, color="#111111")),
        )
        return fig

    # --------- KDE (Altair) ---------
    def _kde_chart_altair(df, metric, jugador_val, fill_color=FILL_ORANGE, line_color=LINE_BLACK, height=120):
        if metric not in df.columns:
            return None
        serie = (
            pd.to_numeric(df[metric], errors="coerce")
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
            .astype(float)
        )
        if serie.empty or pd.isna(jugador_val):
            return None
        mn, mx = float(serie.min()), float(serie.max())
        if mn == mx:
            pad = max(abs(mn), 1.0) * 0.1
            mn, mx = mn - pad, mx + pad
        else:
            pad = (mx - mn) * 0.10
            mn, mx = mn - pad, mx + pad

        data_num = pd.DataFrame({"value": serie})
        base = alt.Chart(data_num).transform_density("value", as_=["x", "density"], extent=[mn, mx], steps=200)

        area = base.transform_filter(alt.datum.x <= float(jugador_val)).mark_area(opacity=0.22, color=fill_color).encode(
            x=alt.X("x:Q", title=None), y=alt.Y("density:Q", title=None)
        )
        line = base.mark_line(color=line_color, size=1.4).encode(x="x:Q", y="density:Q")
        rule = alt.Chart(pd.DataFrame({"x": [float(jugador_val)]})).mark_rule(color=line_color, strokeWidth=2).encode(
            x="x:Q", tooltip=[alt.Tooltip("x:Q", title="Valor", format=".3f")]
        )
        title = alt.TitleParams(metric, fontSize=12, anchor="middle", color="#1F2937")
        chart = (area + line + rule).properties(height=height, title=title).configure_axis(
            grid=False, domain=True, domainColor="#E6E6E6", labelColor="#2B2B2B"
        ).configure_view(strokeWidth=0).configure_title(font="Inter", color="#111111", anchor="middle")
        return chart

    def build_kde_charts(df, jugador, fases_juego, height_each=120):
        charts = []
        if "Name" not in df.columns and "Jugador" in df.columns:
            df = df.copy()
            df["Name"] = df["Jugador"]
        if "Name" not in df.columns or jugador not in df["Name"].values:
            return charts
        for _, vars_fase in fases_juego.items():
            presentes = [v for v in vars_fase if v in df.columns]
            for m in presentes:
                val = pd.to_numeric(df.loc[df["Name"] == jugador, m], errors="coerce").iloc[0]
                ch = _kde_chart_altair(df, m, val, fill_color=FILL_ORANGE, line_color=LINE_BLACK, height=height_each)
                if ch is not None:
                    charts.append(ch)
        return charts

    # =========================
    # Liga/Temporada -> CSV
    # =========================
    st.sidebar.markdown("### Selecciona la Liga y Temporada (Ligas Alternas)")

    ligas_temporadas_la = {
        "MLS Next Pro, USA": ["2025"],
        "Liga de Expansión, México": ["24/25", "25/26"],
        "Liga MX Sub-21, México": ["25/26"],
        "Liga MX Sub-23, México": ["24/25"],
        "Liga 1, Perú": ["2025"],
        "Copa Tigo, Bolivia": ["2025"],
        "Liga Futve, Venezuela": ["2025"],
        "Challenger Pro, Bélgica": ["24/25"],
        "Série B, Brasil": ["2025"],
        "Primera División, Costa Rica": ["24/25"],
        "Superleague, Croacia": ["24/25"],
        "Chance Liga, Rep. Checa": ["24/25"],
        "Superliga, Dinamarca": ["24/25"],
        "Championship, Inglaterra": ["24/25"],
        "Ligue 2, Francia": ["24/25"],
        "Bundesliga 2, Alemania": ["24/25"],
        "Super League, Grecia": ["24/25"],
        "J1 League, Japón": ["2025"],
        "K League, Korea": ["2025"],
        "Liga Profesional, Panamá": ["2025"],
        "Primera División, Polonia": ["24/25"],
        "Segunda Liga, Portugal": ["24/25"],
        "Pro League, Arabia": ["24/25"],
        "Premiership, Escocia": ["24/25"],
        "Primera RFEF, España": ["24/25"],
        "Segunda RFEF, España": ["24/25"],
        "Primera División, Turquía": ["24/25"],
        "Bundesliga, Austria": ["24/25"],
        "Super League, Suiza": ["24/25"],
        "Stars League, Qatar": ["24/25"],
        "Pro League, Emiratos Árabes": ["24/25"],


    }

    archivos_csv_la = {
        ("MLS Next Pro, USA", "2025"): "nextpro2025.csv",
        ("Liga de Expansión, México", "24/25"): "expansion2425.csv",
        ("Liga de Expansión, México", "25/26"): "expansion2526.csv",
        ("Liga MX Sub-21, México", "25/26"): "sub212526.csv",
        ("Liga MX Sub-23, México", "24/25"): "sub232425.csv",
        ("Liga 1, Perú", "2025"): "peru2025.csv",
        ("Copa Tigo, Bolivia", "2025"): "bolivia2025.csv",
        ("Liga Futve, Venezuela", "2025"): "venezuela2025.csv",
        ("Challenger Pro, Bélgica", "24/25"): "challengerpro2425.csv",
        ("Série B, Brasil", "2025"): "serieb2025.csv",
        ("Primera División, Costa Rica", "24/25"): "costarica2425.csv",
        ("Superleague, Croacia", "24/25"): "croacia2425.csv",
        ("Chance Liga, Rep. Checa", "24/25"): "checa2425.csv",
        ("Superliga, Dinamarca", "24/25"): "denmark2425.csv",
        ("Championship, Inglaterra", "24/25"): "championship2425.csv",
        ("Ligue 2, Francia", "24/25"): "ligue22425.csv",
        ("Bundesliga 2, Alemania", "24/25"): "bundes22425.csv",
        ("Super League, Grecia", "24/25"): "grecia2425.csv",
        ("J1 League, Japón", "2025"): "japan2025.csv",
        ("K League, Korea", "2025"): "korea2025.csv",
        ("Liga Profesional, Panamá", "2025"): "panama2025.csv",
        ("Primera División, Polonia", "24/25"): "polonia2425.csv",
        ("Segunda Liga, Portugal", "24/25"): "portugal22425.csv",
        ("Pro League, Arabia", "24/25"): "arabia2425.csv",
        ("Premiership, Escocia", "24/25"): "escocia2425.csv",
        ("Primera RFEF, España", "24/25"): "primerarfef2425.csv",
        ("Segunda RFEF, España", "24/25"): "segundarfef2425.csv",
        ("Primera División, Turquía", "24/25"): "turquia2425.csv",
        ("Bundesliga, Austria", "24/25"): "austria2425.csv",
        ("Super League, Suiza", "24/25"): "suiza2425.csv",
        ("Stars League, Qatar", "24/25"): "qatar2425.csv",
        ("Pro League, Emiratos Árabes", "24/25"): "uae2425.csv",


    }

    ligas_disponibles_la = list(ligas_temporadas_la.keys())
    liga_sel_la = st.sidebar.selectbox("Liga (Ligas Alternas)", ligas_disponibles_la, index=0)
    temporadas_disp_la = ligas_temporadas_la.get(liga_sel_la, [])
    temp_sel_la = st.sidebar.selectbox("Temporada", temporadas_disp_la, index=0)

    archivo_la = archivos_csv_la.get((liga_sel_la, temp_sel_la))
    if not archivo_la:
        st.error("No hay archivo CSV mapeado para esta liga/temporada."); st.stop()

    try:
        df_radar = pd.read_csv(archivo_la)
    except Exception:
        df_radar = pd.read_csv(archivo_la, sep=";")
    df_radar.columns = df_radar.columns.str.strip()

    # =========================
    # Grupo de posición + filtros
    # =========================
    st.sidebar.markdown("### Grupo de Posición")
    grupos_posicion = [
        "Porteros", "Centrales", "Carrileros/Laterales",
        "Contenciones", "Interiores", "Volantes Ofensivos",
        "Extremos", "Delanteros"
    ]
    slug_liga = str(liga_sel_la).lower().replace(" ", "_")
    slug_temp = str(temp_sel_la).lower().replace(" ", "_").replace("/", "_")
    grupo = st.sidebar.radio("Grupo", grupos_posicion, index=0, key=f"la_radar3_grupo__{slug_liga}__{slug_temp}")

    pos = df_radar["Posición específica"].astype(str)
    if grupo == "Porteros":
        df_radar = df_radar[pos.str.contains(r"\bGK\b", na=False)].copy()
    elif grupo == "Centrales":
        df_radar = df_radar[pos.str.contains("CB", na=False)].copy()
    elif grupo == "Carrileros/Laterales":
        df_radar = df_radar[pos.str.contains("RB|LB|RWB|LWB", na=False)].copy()
    elif grupo == "Contenciones":
        df_radar = df_radar[pos.str.contains("DM", na=False)].copy()
    elif grupo == "Interiores":
        df_radar = df_radar[pos.str.contains("CM", na=False)].copy()
    elif grupo == "Volantes Ofensivos":
        df_radar = df_radar[pos.str.contains("AM", na=False)].copy()
    elif grupo == "Extremos":
        df_radar = df_radar[pos.str.contains(r"\bLW\b|\bRW\b", na=False) & ~pos.str.contains("WB", na=False)].copy()
    else:  # Delanteros
        df_radar = df_radar[pos.str.contains(r"\bST\b|\bCF\b", na=False)].copy()

    # Minutos
    st.sidebar.markdown("### Minutos Jugados")
    if "Minutos jugados" in df_radar.columns:
        df_radar["Minutos jugados"] = pd.to_numeric(df_radar["Minutos jugados"], errors="coerce")
        mins = df_radar["Minutos jugados"].dropna()
        if mins.empty:
            st.warning("No hay datos válidos de minutos tras filtrar."); st.stop()
        mn, mx = int(mins.min()), int(mins.max())
        min_default = max(600, mn)
        if mn < mx:
            r_mins = st.sidebar.slider(
                "Rango de Minutos Jugados",
                mn, mx, (min_default, mx),
                key=f"la_radar3_mins__{slug_liga}__{slug_temp}"
            )
            df_radar = df_radar[df_radar["Minutos jugados"].between(r_mins[0], r_mins[1])]
    else:
        st.warning("La base no contiene 'Minutos jugados'."); st.stop()

    # Nacionalidad
    st.sidebar.markdown("### Filtrar por Nacionalidad")
    nats = sorted(df_radar["País de nacimiento"].dropna().astype(str).unique())
    sel_all = st.sidebar.checkbox(
        "Seleccionar todas las nacionalidades",
        value=True,
        key=f"la_radar3_natall__{slug_liga}__{slug_temp}"
    )
    selected_nats = nats if sel_all else st.sidebar.multiselect(
        "Nacionalidades", nats, default=nats,
        key=f"la_radar3_natlist__{slug_liga}__{slug_temp}"
    )
    df_radar = df_radar[df_radar["País de nacimiento"].isin(selected_nats)]
    if df_radar.empty:
        st.warning("No hay jugadores tras aplicar filtros."); st.stop()

    # =========================
    # Fases por grupo (3 fases) usando columnas en español
    # =========================
    fases_gk = {
        "Atajadas": [
            "Paradas, %", "Goles evitados", "Porterías imbatidas en los 90"
        ],
        "Juego aéreo y salidas": [
            "Salidas/90", "Duelos aéreos en los 90"
        ],
        "Juego de Pies": [
            "Pases/90", "Precisión pases, %", "Pases largos/90", "Precisión pases largos, %",
            "Pases progresivos/90", "Precisión pases progresivos, %", "Pases recibidos /90"
        ],
    }
    inv_gk = {"xG en contra"}

    fases_cb = {
        "Defensivas": [
            "Acciones defensivas realizadas/90", "Duelos defensivos/90", "Duelos defensivos ganados, %",
            "Duelos aéreos en los 90", "Duelos aéreos ganados, %",
            "Posesión conquistada después de una entrada", "Tiros interceptados/90", "Posesión conquistada después de una interceptación"
        ],
        "Construcción": [
            "Pases/90", "Precisión pases, %",
            "Pases largos/90", "Precisión pases largos, %", "Pases en profundidad/90",
            "Pases progresivos/90"
        ],
        "Ofensivas": [
            "Acciones de ataque exitosas/90", "Remates/90"
        ],
    }
    inv_cb = set()

    fases_wb = {
        "Defensivas": [
            "Acciones defensivas realizadas/90", "Duelos defensivos/90", "Duelos defensivos ganados, %", "Posesión conquistada después de una entrada",
            "Tiros interceptados/90", "Posesión conquistada después de una interceptación"
        ],
        "Construcción": [
            "Carreras en progresión/90", "Aceleraciones/90", "Pases/90", "Precisión pases, %",
            "Pases hacia adelante/90", "Pases en profundidad/90", "Pases progresivos/90"
        ],
        "Ofensivas": [
            "Remates/90", "Tiros a la portería, %",
            "Asistencias/90", "Centros/90", "Precisión centros, %", "Toques en el área de penalti/90",
            "xA/90", "Second assists/90", "Jugadas claves/90",
            "Pases en el último tercio/90", "Centros desde el último tercio/90", "Desmarques/90"
        ],
    }
    inv_wb = set()

    fases_dm = {
        "Defensivas": [
            "Acciones defensivas realizadas/90", "Duelos defensivos ganados, %",
            "Posesión conquistada después de una entrada", "Posesión conquistada después de una interceptación"
        ],
        "Construcción": [
            "Carreras en progresión/90", "Pases/90", "Precisión pases, %", "Pases largos/90", "Precisión pases largos, %",
            "Pases en profundidad/90", "Pases progresivos/90", "Pases en el último tercio/90",
            "Longitud media pases, m"
        ],
        "Ofensivas": [
            "Acciones de ataque exitosas/90", "Remates/90", "Asistencias/90", "Second assists/90", "Third assists/90",
            "Jugadas claves/90", "Pases al área de penalti/90"
        ],
    }
    inv_dm = set()

    fases_cm = {
        "Defensivas": [
            "Acciones defensivas realizadas/90", "Duelos defensivos ganados, %",
            "Posesión conquistada después de una entrada", "Posesión conquistada después de una interceptación"
        ],
        "Construcción": [
            "Carreras en progresión/90", "Pases/90", "Precisión pases, %",
            "Pases largos/90", "Precisión pases largos, %",
            "Pases en profundidad/90", "Pases progresivos/90", "Pases en el último tercio/90",
            "Longitud media pases, m"
        ],
        "Ofensivas": [
            "Acciones de ataque exitosas/90", "Remates/90", "Asistencias/90",
            "Second assists/90", "Third assists/90",
            "Jugadas claves/90", "Pases al área de penalti/90"
        ],
    }
    inv_cm = set()

    fases_am = {
        "Defensivas": [
            "Acciones defensivas realizadas/90", "Duelos defensivos ganados, %", "Entradas/90"
        ],
        "Construcción": [
            "Carreras en progresión/90", "Pases/90", "Precisión pases, %",
            "Pases largos/90", "Precisión pases largos, %",
            "Pases en profundidad/90", "Pases progresivos/90", "Pases en el último tercio/90",
            "Pases al área de penalti/90", "Jugadas claves/90", "Second assists/90", "Third assists/90",
            "Asistencias/90", "Longitud media pases, m"
        ],
        "Definición": [
            "Goles", "xG", "Asistencias", "xA", "Remates", "Remates/90",
            "Tiros a la portería, %"
        ],
    }
    inv_am = set()

    fases_w = {
        "Defensivas": [
            "Acciones defensivas realizadas/90", "Duelos defensivos ganados, %", "Entradas/90"
        ],
        "Construcción": [
            "Carreras en progresión/90",
            "Regates/90", "Regates realizados, %", "Duelos atacantes ganados, %",
            "Pases/90", "Precisión pases, %",
            "Pases en el último tercio/90", "Pases progresivos/90",
            "Desmarques/90"
        ],
        "Definición": [
            "Goles", "xG", "Asistencias", "xA",
            "Remates", "Remates/90", "Tiros a la portería, %", "Goles hechos, %",
            "Centros/90", "Precisión centros, %", "Pases hacía el área pequeña, %"
        ],
    }
    inv_w = set()

    fases_st = {
        "Defensivas": [
            "Acciones defensivas realizadas/90", "Duelos defensivos ganados, %"
        ],
        "Construcción": [
            "Carreras en progresión/90", "Pases/90", "Precisión pases, %",
            "Pases en profundidad/90", "Pases progresivos/90", "Pases recibidos /90",
            "Pases en el último tercio/90", "Pases al área de penalti/90",
            "Regates/90", "Regates realizados, %", "Duelos atacantes ganados, %",
            "Desmarques/90"
        ],
        "Definición": [
            "Goles", "xG", "Asistencias", "xA", "Remates", "Remates/90",
            "Tiros a la portería, %", "Centros/90"
        ],
    }
    inv_st = set()

    # Selección del set de fases según grupo (base)
    if grupo == "Porteros":
        fases_juego = {k: [c for c in v if c in df_radar.columns] for k, v in fases_gk.items()}
        invertir_vars = inv_gk & set(df_radar.columns)
    elif grupo == "Centrales":
        fases_juego = {k: [c for c in v if c in df_radar.columns] for k, v in fases_cb.items()}
        invertir_vars = inv_cb
    elif grupo == "Carrileros/Laterales":
        fases_juego = {k: [c for c in v if c in df_radar.columns] for k, v in fases_wb.items()}
        invertir_vars = inv_wb
    elif grupo == "Contenciones":
        fases_juego = {k: [c for c in v if c in df_radar.columns] for k, v in fases_dm.items()}
        invertir_vars = inv_dm
    elif grupo == "Interiores":
        fases_juego = {k: [c for c in v if c in df_radar.columns] for k, v in fases_cm.items()}
        invertir_vars = inv_cm
    elif grupo == "Volantes Ofensivos":
        fases_juego = {k: [c for c in v if c in df_radar.columns] for k, v in fases_am.items()}
        invertir_vars = inv_am
    elif grupo == "Extremos":
        fases_juego = {k: [c for c in v if c in df_radar.columns] for k, v in fases_w.items()}
        invertir_vars = inv_w
    else:
        fases_juego = {k: [c for c in v if c in df_radar.columns] for k, v in fases_st.items()}
        invertir_vars = inv_st

    # =========================
    # Selección de jugador
    # =========================
    st.markdown("### Jugador")
    jugadores_disp = sorted(df_radar["Jugador"].dropna().astype(str).unique())
    if not jugadores_disp:
        st.warning("No hay jugadores tras aplicar filtros."); st.stop()
    jugador_sel = st.selectbox("Jugador", jugadores_disp, index=0)

    df_radar = df_radar.copy()
    df_radar["Name"] = df_radar["Jugador"]

    # =========================
    # Modo de variables para el radar
    # =========================
    st.markdown("### Modo de variables para el radar")
    modo_radar_la = st.radio(
        "Elige cómo quieres armar el radar:",
        ["Radar predeterminado", "Seleccionar variables para el radar"],
        index=0,
        horizontal=True,
        key=f"la_radar3_modo__{slug_liga}__{slug_temp}"
    )

    fases_activas = {}

    if modo_radar_la == "Radar predeterminado":
        # Usamos todas las variables definidas para el grupo, filtrando vacías
        fases_activas = {fase: vars_f for fase, vars_f in fases_juego.items() if vars_f}
    else:
        # Modo personalizado: usuario elige variables por fase
        st.markdown("#### Selecciona las variables por fase de juego")
        st.caption("Solo se muestran variables que existen en la base filtrada.")

        for fase, vars_fase in fases_juego.items():
            disponibles = [v for v in vars_fase if v in df_radar.columns]
            if not disponibles:
                continue

            seleccionadas = st.multiselect(
                f"{fase}",
                options=disponibles,
                default=disponibles,  # si quieres obligar a elegir desde cero, pon default=[]
                key=f"la_ms_{fase}_{grupo}_{slug_liga}_{slug_temp}"
            )
            if seleccionadas:
                fases_activas[fase] = seleccionadas

        if not fases_activas:
            st.warning("No has seleccionado ninguna métrica para el radar."); st.stop()

    # =========================
    # Render
    # =========================
    if jugador_sel and fases_activas:
        # Radar centrado
        left, mid, right = st.columns([0.05, 0.90, 0.05])
        with mid:
            fig = radar_barras_plotly(
                jugador=jugador_sel,
                df=df_radar,
                fases_juego=fases_activas,
                invertir_vars=invertir_vars,
                chart_height=640,
                show_silueta=False
            )
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, theme=None)

        # Distribuciones 3×N
        st.markdown("#### Distribuciones por métrica")
        charts = build_kde_charts(df=df_radar, jugador=jugador_sel, fases_juego=fases_activas, height_each=120)
        if charts:
            for i in range(0, len(charts), 3):
                cols = st.columns(3, gap="large")
                for j in range(3):
                    if i + j < len(charts):
                        with cols[j]:
                            st.altair_chart(charts[i + j], use_container_width=True, theme=None)

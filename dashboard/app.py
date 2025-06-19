"""Streamlit COVID-19 Dashboard basado en datos transformados."""

# Page Setup with STREAMLIT
import streamlit as st
st.set_page_config(page_title="Dashboard COVID-19", layout="wide")

# Necessary libraries
import sqlite3
import requests
import pandas as pd
import pydeck as pdk
import altair as alt
import numpy as np
from zoneinfo import ZoneInfo

# Database directory
DB_PATH = "data/covid.db"

# Load data from DB
@st.cache_data
def load_data():
    """
    Carga los datos actuales e históricos de COVID-19 desde la base de datos SQLite.
    """
    conn = sqlite3.connect(DB_PATH)
    df_current = pd.read_sql_query("SELECT * FROM current_data", conn)
    df_historical = pd.read_sql_query("SELECT * FROM historical_data", conn)
    conn.close()
    return df_current, df_historical

df_current, df_historical = load_data()
df_historical["date"] = pd.to_datetime(df_historical["date"])
df_current["updated"] = pd.to_datetime(df_current["updated"], errors="coerce")

# Title and update
st.title("Dashboard COVID-19")
st.caption("Prueba técnica con ETL automatizado utilizando Airflow + SQLite + Streamlit")

latest_update = df_current["updated"].max()
if pd.notnull(latest_update):
    bogota_time = latest_update.tz_localize("UTC").astimezone(ZoneInfo("America/Bogota"))
    st.caption(f"Ultima actualización: {bogota_time.strftime('%Y-%m-%d %H:%M:%S')} (Hora Bogotá)")

# Globlas KPIs
st.markdown("### Indicadores globales")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Casos confirmados", f"{int(df_current['cases'].sum()):,}")
col2.metric("Muertes", f"{int(df_current['deaths'].sum()):,}")
col3.metric("Activos", f"{int(df_current['active'].sum()):,}")
col4.metric("Recuperados", f"{int(df_current['recovered'].sum()):,}")

# Evolution by date
st.markdown("### Evolución por fecha")

min_date = df_historical["date"].min().to_pydatetime()
max_date = df_historical["date"].max().to_pydatetime()

selected_date = st.slider(
    "Selecciona una fecha:",
    min_value=min_date,
    max_value=max_date,
    value=max_date,
    format="YYYY-MM-DD"
)

filtered_data = df_historical[df_historical["date"] <= pd.to_datetime(selected_date)]
grouped_data = filtered_data.groupby("date").sum().reset_index()

line_chart = alt.Chart(grouped_data).transform_fold(
    ["cases", "deaths"],
    as_=["Métrica", "Valor"]
).mark_line(strokeWidth=2.5).encode(
    x=alt.X("date:T", title="Fecha"),
    y=alt.Y("Valor:Q", title="Cantidad acumulada"),
    color=alt.Color("Métrica:N", scale=alt.Scale(domain=[
        "cases", "deaths"], range=["#1f77b4", "crimson"])),
    tooltip=[
        alt.Tooltip("date:T", title="Fecha"),
        alt.Tooltip("Métrica:N", title="Tipo"),
        alt.Tooltip("Valor:Q", title="Valor")
    ]
).properties(
    width=950,
    height=550,
    title="Tendencia acumulada global hasta la fecha seleccionada"
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_title(
    fontSize=18,
    anchor="start"
)

st.altair_chart(line_chart, use_container_width=True)

# World map of active cases
st.markdown("### Mapa mundial de casos activos")

@st.cache_data
def fetch_coordinates():
    """
    Fetches the current active COVID-19 case counts and geographic coordinates
        
        - IMPORTANT!: For consistency and maintainability of the initial database structure,
        add new parameters (lat, long)
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT country, active, lat, long 
        FROM current_data WHERE lat IS NOT NULL AND long IS NOT NULL
        """,
        conn
    )
    conn.close()

    df["scaled_radius"] = np.sqrt(df["active"]).fillna(0) * 100
    return df

df_map = fetch_coordinates()

st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=0,
        longitude=0,
        zoom=1,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=df_map,
            get_position='[long, lat]',
            get_radius='scaled_radius',
            get_fill_color='[255, 0, 0, 140]',
            pickable=True,
        ),
    ],
    tooltip={"text": "País: {country}\nActivos: {active}"}
))

# Comparison by country
st.markdown("### Comparativa por país")

# Sort by cases and select top 10
top_countries = df_current.sort_values("cases", ascending=False).head(10)

df_top = top_countries.melt(
    id_vars="country",
    value_vars=["cases", "active", "deaths", "recovered"],
    var_name="Tipo",
    value_name="Valor"
)

# Colors
color_scale = alt.Scale(
    domain=["cases", "active", "deaths", "recovered"],
    range=["#1f77b4", "#ff7f0e", "#d62728", "#2ca02c"]
)

# Graph
bar_chart = alt.Chart(df_top).mark_bar().encode(
    x=alt.X("country:N", title="País", axis=alt.Axis(labelAngle=-45)),
    xOffset="Tipo:N",
    y=alt.Y("Valor:Q", title="Cantidad"),
    color=alt.Color("Tipo:N", scale=color_scale, title="Categoría"),
    tooltip=["country:N", "Tipo:N", "Valor:Q"]
).properties(
    width=800,
    height=500,
    title="Top 10 países por categoría"
).configure_axis(
    labelFontSize=11,
    titleFontSize=13
)

st.altair_chart(bar_chart, use_container_width=True)

# Top 10 countries with the most accumulated cases
st.markdown("### Top 10 países con más casos acumulados")

top_10 = df_current.sort_values("cases", ascending=False).head(10).copy()
top_10 = top_10[["country", "cases", "deaths", "active", "recovered"]]
top_10.columns = ["País", "Casos Confirmados", "Muertes", "Activos", "Recuperados"]

# Format numbers
for col in ["Casos Confirmados", "Muertes", "Activos", "Recuperados"]:
    top_10[col] = top_10[col].apply(lambda x: f"{int(x):,}")

# Add "Position" column from 1 to 10
top_10.insert(0, "Puesto", range(1, 11))

# Display without index of DataFrame
st.dataframe(top_10, use_container_width=True, hide_index=True)

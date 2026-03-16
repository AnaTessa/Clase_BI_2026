import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from pywaffle import Waffle

# -----------------------------
# HEADER
# -----------------------------

def show_header(text_title: str):

    col1, col2 = st.columns([1,6])

    with col1:
        st.image("A95628AB-88C8-4FAA-A86D-A877C52152F0.jpg", width=200)

    with col2:
        st.title(text_title)
        st.caption("📘 Developed for: *Business Intelligence (Graduate Level)*")
        st.caption("Instructor: Edgar Avalos-Gauna (2025), Universidad Panamericana")


# -----------------------------
# LOAD DATA
# -----------------------------

@st.cache_data
def load_data():

    station_information = "https://gbfs.mex.lyftbikes.com/gbfs/es/station_information.json"
    response = requests.get(station_information)
    data = response.json()

    df = pd.DataFrame(data["data"]["stations"])

    df = df[["station_id","name","lat","lon","capacity"]]

    # status de estaciones
    url_station_status = "https://gbfs.mex.lyftbikes.com/gbfs/es/station_status.json"
    response = requests.get(url_station_status)
    status = response.json()

    df_status = pd.DataFrame(status["data"]["stations"])

    columnas = [
        "num_bikes_available",
        "num_bikes_disabled",
        "num_docks_available",
        "num_docks_disabled"
    ]

    df_status = df_status[["station_id"] + columnas]

    df = df.merge(df_status, on="station_id")

    return df


# -----------------------------
# MAPA
# -----------------------------

def plot_map(df):

    fig, ax = plt.subplots(figsize=(8,6))

    sns.scatterplot(
        data=df,
        x="lon",
        y="lat",
        ax=ax
    )

    ax.set_title("Ubicación de estaciones EcoBici")
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")

    return fig


# -----------------------------
# CAPACIDAD
# -----------------------------

def plot_capacity(df):

    top_capacity = df.sort_values("capacity", ascending=False).head(15)

    fig, ax = plt.subplots(figsize=(10,6))

    sns.barplot(
        data=top_capacity,
        y="name",
        x="capacity",
        ax=ax
    )

    ax.set_title("Top 15 estaciones con mayor capacidad")
    ax.set_xlabel("Capacidad")
    ax.set_ylabel("Estación")

    return fig


# -----------------------------
# WAFFLE ESTACIÓN
# -----------------------------

def plot_station(df, station_id):

    df_filtrado = df[df["station_id"] == station_id]

    if df_filtrado.empty:
        return None

    fila = df_filtrado.iloc[0]

    values = [
        fila["num_bikes_available"],
        fila["num_bikes_disabled"],
        fila["num_docks_available"],
        fila["num_docks_disabled"]
    ]

    fig = plt.figure(
        FigureClass=Waffle,
        rows=5,
        values=values,
        labels=[
            "Bikes available",
            "Bikes disabled",
            "Docks available",
            "Docks disabled"
        ],
        legend={'loc': 'upper left', 'bbox_to_anchor': (1, 1)}
    )

    return fig


# -----------------------------
# APP
# -----------------------------

show_header("Análisis del sistema EcoBici CDMX")

st.write(
"""
Esta aplicación analiza el sistema **EcoBici de la Ciudad de México**
utilizando datos oficiales del sistema **GBFS (General Bikeshare Feed Specification)**.
"""
)

# cargar datos
df = load_data()

# -----------------------------
# MAPA
# -----------------------------

st.header("Mapa de estaciones")

fig_map = plot_map(df)
st.pyplot(fig_map)


# -----------------------------
# NUEVA GRÁFICA
# -----------------------------

st.header("Estaciones con mayor capacidad")

fig_capacity = plot_capacity(df)
st.pyplot(fig_capacity)


# -----------------------------
# SELECTOR
# -----------------------------

st.header("Disponibilidad de bicicletas por estación")

station = st.selectbox(
    "Selecciona una estación",
    df["station_id"]
)

fig_station = plot_station(df, station)

if fig_station:
    st.pyplot(fig_station)
else:
    st.warning("No hay datos para esta estación")

import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from pywaffle import Waffle

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

import streamlit as st

# ESTA DEBE SER LA LÍNEA 1 (después de los imports de librerías base)
st.set_page_config(layout="wide", page_title="Ecobici Dashboard UP")

# Inyección de CSS corregida y segura
st.markdown("""
    <style>
        /* Reducir el espacio superior sin ocultar los botones de control */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
        }
        
        /* En lugar de ocultar el header completo, solo quitamos el fondo */
        header {
            background-color: rgba(0,0,0,0) !important;
        }

        /* Forzar que el botón del Sidebar sea visible (flecha >) */
        .css-6q9sum.edgvb6w4 {
            visibility: visible !important;
            background-color: white !important;
            border-radius: 50%;
        }
    </style>
    """, unsafe_allow_html=True)

# Ahora sí, el resto de las importaciones de tus módulos
try:
    from Modules.UI.header import show_header
    from Modules.Data.ecobici_service import EcobiciService
    from Modules.Viz.viz_service import EcobiciViz
except Exception as e:
    st.error(f"Error al importar módulos: {e}")

# --- EJECUCIÓN DEL TABLERO ---

def main():
    # Encabezado
    show_header("Análisis de Movilidad: Ecobici CDMX")
    
    # Instanciar servicios
    service = EcobiciService()
    viz = EcobiciViz()
    
    # Carga de datos
    with st.spinner('Cargando datos de la API de Ecobici...'):
        df = service.get_full_data()
    
    if df is not None and not df.empty:
        # Ejecutar la visualización que creamos en viz_service.py
        viz.render_map_and_waffle(df)
    else:
        st.error("No se pudieron obtener datos. Verifica tu conexión o la API de Ecobici.")

if __name__ == "__main__":
    main()


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

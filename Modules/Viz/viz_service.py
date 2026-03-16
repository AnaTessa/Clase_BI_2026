import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt
from pywaffle import Waffle
import pandas as pd

class EcobiciViz:
    def render_map_and_waffle(self, df):
        """
        Renderiza un mapa interactivo de Plotly y un gráfico de Waffle 
        lado a lado, con márgenes ajustados y controles en el sidebar.
        """

        tab1, tab2 = st.tabs(["Mapa y disponibilidad", "Capacidad de estaciones"])
        with tab1:
        # --- 1. CONTROLES EN SIDEBAR ---
            st.sidebar.markdown("### Configuración de Visualización")
        
        # Selector de Estación
            estaciones = ["Todas"] + sorted(df['name'].unique().tolist())
            seleccion = st.sidebar.selectbox("Selecciona una estación:", estaciones)
        
        # Slider de Zoom (Niveles 1 a 4)
            nivel_slider = st.sidebar.slider("Nivel de Zoom", 1, 4, 1)
            zoom_map_dict = {1: 12, 2: 13.5, 3: 15, 4: 16.5}
        
        # Slider de Tamaño de marcadores
            tamanio_puntos = st.sidebar.slider("Tamaño de puntos en mapa", 10, 40, 18)
        
        # --- 2. PREPARACIÓN DE DATOS Y LÓGICA DE CENTRADO ---
            columnas_status = [
                'num_bikes_available', 'num_bikes_disabled', 
                'num_docks_available', 'num_docks_disabled'
            ]
        
            if seleccion != "Todas":
            # Caso: Estación específica
                fila = df[df['name'] == seleccion].iloc[0]
                valores_waffle = fila[columnas_status].values.astype(int)
                lat_center, lon_center = fila['lat'], fila['lon']
                n_rows_waffle = 6  # Más filas para que crezca verticalmente
                font_waffle = 32   # Iconos grandes para llenar el espacio
                leyenda_escala = "1 icono = 1 unidad"
                df['resaltado'] = df['name'].apply(lambda x: 'Seleccionada' if x == seleccion else 'Normal')
            else:
            # Caso: Vista Global de la Ciudad
            # Escalado para evitar lentitud (1 icono ≈ 100 unidades)
                factor_escala = 100
                valores_reales = df[columnas_status].sum().values
                valores_waffle = (valores_reales / factor_escala).astype(int)
            
                lat_center, lon_center = df['lat'].mean(), df['lon'].mean()
                n_rows_waffle = 15 # Proporción vertical para el total de la ciudad
                font_waffle = 24
                leyenda_escala = f"1 icono ≈ {factor_escala} unidades"
                df['resaltado'] = 'Normal'

        # --- 3. DISEÑO DE INTERFAZ EN COLUMNAS ---
        # Proporción 2.5 a 1 para dar protagonismo al mapa pero espacio al Waffle
            col_mapa, col_waffle = st.columns([2.5, 1], gap="medium")

            with col_mapa:
                st.markdown(f"#### Ubicación de Estaciones")
            
            # Mapa Base con Plotly Express
                fig_map = px.scatter_mapbox(
                    df, 
                    lat="lat", 
                    lon="lon", 
                    size=[tamanio_puntos] * len(df), 
                    size_max=tamanio_puntos,
                    color="resaltado", 
                    color_discrete_map={"Seleccionada": "red", "Normal": "#1f77b4"},
                    hover_name="name",
                    zoom=zoom_map_dict[nivel_slider],
                    center={"lat": lat_center, "lon": lon_center},
                    mapbox_style="carto-positron", 
                    height=650
                )
            
            # Añadir marcador de "Pin" rojo si hay una estación seleccionada
                if seleccion != "Todas":
                    fig_map.add_trace(go.Scattermapbox(
                        lat=[lat_center], 
                        lon=[lon_center], 
                        mode='markers',
                        marker=go.scattermapbox.Marker(
                            size=tamanio_puntos + 15, 
                            color='red', 
                            symbol='marker'
                        ),
                        showlegend=False
                    ))
            
                fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, showlegend=False)
                st.plotly_chart(fig_map, use_container_width=True)

            with col_waffle:
                st.markdown(f"#### Disponibilidad: {seleccion if seleccion != 'Todas' else 'CDMX'}")
            
                if sum(valores_waffle) > 0:
                # Creación del gráfico de Waffle
                    fig_waffle = plt.figure(
                        FigureClass=Waffle,
                        rows=n_rows_waffle,
                        values=valores_waffle,
                        colors=["#2ecc71", "#e74c3c", "#3498db", "#95a5a6"],
                        icons='bicycle', 
                        font_size=font_waffle, 
                        figsize=(8, 11), # Ajuste de alto para ocupar la columna
                        legend={
                            'labels': ['Disponible', 'Dañada', 'Puerto Libre', 'Puerto Dañado'], 
                            'loc': 'lower center', 
                            'bbox_to_anchor': (0.5, -0.15), 
                            'ncol': 2, 
                            'fontsize': 11, 
                            'frameon': False
                        }
                    )
                
                # Ajuste de márgenes para dar el "respiro" solicitado
                # left=0.05 y right=0.95 evitan que pegue totalmente a los bordes
                    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.2)
                
                    st.pyplot(fig_waffle, use_container_width=True, clear_figure=True)
                    st.caption(f"**Escala:** {leyenda_escala}")
                else:
                    st.info("No hay datos suficientes para generar el gráfico de disponibilidad.")

        with tab2:
        # --- 4. GRÁFICA EXTRA: TOP ESTACIONES POR CAPACIDAD ---
            st.markdown("---")
            st.markdown("### Top estaciones con mayor capacidad")

            if "capacity" in df.columns:

                top_capacity = (
                    df[['name','capacity']]
                    .drop_duplicates()
                    .sort_values("capacity", ascending=False)
                    .head(15)
                )

                fig_top = px.bar(
                    top_capacity,
                    x="capacity",
                    y="name",
                    orientation="h",
                    title="Top 15 estaciones con mayor capacidad",
                    labels={
                        "capacity":"Capacidad de bicicletas",
                        "name":"Estación"
                    }
                )

                fig_top.update_layout(
                    height=500,
                    yaxis={'categoryorder':'total ascending'}
                )

                st.plotly_chart(fig_top, use_container_width=True)

            else:
                st.warning("La columna 'capacity' no está disponible en los datos.")

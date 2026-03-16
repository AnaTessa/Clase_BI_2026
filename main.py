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

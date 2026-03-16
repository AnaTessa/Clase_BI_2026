import requests
import pandas as pd
import streamlit as st

class EcobiciService:
    def __init__(self):
        self.url_info = 'https://gbfs.mex.lyftbikes.com/gbfs/es/station_information.json'
        self.url_status = 'https://gbfs.mex.lyftbikes.com/gbfs/es/station_status.json'

    @st.cache_data(ttl=300) # Cache por 5 minutos para datos en tiempo real
    def get_full_data(_self):
        """
        Obtiene, limpia y combina los datos de información y estatus de estaciones.
        """
        try:
            # 1. Obtener Información de Estaciones
            resp_info = requests.get(_self.url_info)
            data_info = resp_info.json()['data']['stations']
            df_info = pd.DataFrame(data_info)
            
            # Filtramos columnas base
            df_info = df_info[['station_id', 'name', 'lat', 'lon', 'capacity']]

            # 2. Obtener Estatus en Tiempo Real
            resp_status = requests.get(_self.url_status)
            data_status = resp_status.json()['data']['stations']
            df_status = pd.DataFrame(data_status)
            
            # Columnas de interés según tu análisis
            cols_status = ['station_id', 'num_bikes_available', 'num_bikes_disabled', 
                           'num_docks_available', 'num_docks_disabled', 'is_renting']
            df_status = df_status[cols_status]

            # 3. Merge de datos (Usamos merge por station_id para mayor seguridad que concat)
            df_final = pd.merge(df_info, df_status, on='station_id')
            
            return df_final

        except Exception as e:
            st.error(f"Error al conectar con la API de Ecobici: {e}")
            return pd.DataFrame()

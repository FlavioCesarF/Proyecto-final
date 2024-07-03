import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
import numpy as np

# Configuración de la página de Streamlit
st.set_page_config(page_title="Dashboard de Aeropuertos", page_icon="✈️", layout="wide")

# Función para cargar los datos
@st.cache_data
def cargar_datos(file_path, delimiter, column_names=None):
    return pd.read_csv(file_path, delimiter=delimiter, on_bad_lines='skip', names=column_names, header=0 if column_names is None else None)

# Cargar archivos CSV
aeropuertos_detalle_path = 'database/aeropuertos_detalle.csv'
informe_ministerio_paths = [
    'database/202405_informe-ministerio.csv',
    'database/202312_informe-ministerio-actualizado-dic.csv',
    'database/202212_informe-ministerio.csv',
    'database/202112_informe_ministerio.csv',
    'database/2020_informe_ministerio.csv',
    'database/2019_informe_ministerio.csv'
]

aeropuertos_detalle = cargar_datos(aeropuertos_detalle_path, delimiter=';')

# Columnas para los informes del ministerio
columnas_informe_ministerio = ["Fecha UTC", "Hora UTC", "Clase de Vuelo (todos los vuelos)", "Clasificación Vuelo", "Tipo de Movimiento", "Aeropuerto", "Origen / Destino", "Aerolinea Nombre", "Aeronave", "Pasajeros", "PAX", "Calidad dato"]

# Cargar y combinar informes del ministerio
informes_ministerio = []
for path in informe_ministerio_paths:
    informes_ministerio.append(cargar_datos(path, delimiter=',', column_names=columnas_informe_ministerio))

informe_ministerio = pd.concat(informes_ministerio, ignore_index=True)

# Imprimir columnas para depuración
st.write("Columnas del DataFrame 'informe_ministerio':")
st.write(informe_ministerio.columns)

# Convertir la columna 'Fecha UTC' a formato de fecha
informe_ministerio['Fecha UTC'] = pd.to_datetime(informe_ministerio['Fecha UTC'], format='%d/%m/%Y', errors='coerce')

# Limpiar datos nulos en el informe del ministerio
informe_ministerio = informe_ministerio.dropna(subset=['Fecha UTC', 'Aeropuerto', 'Aerolinea Nombre'])

# Convertir columna 'PAX' a numérica, limpiando errores
informe_ministerio['PAX'] = pd.to_numeric(informe_ministerio['PAX'], errors='coerce')
informe_ministerio = informe_ministerio.dropna(subset=['PAX'])

# Título del Dashboard
st.title('✈️ Dashboard Aeropuertos')

# Muestra de datos
st.header('📋 Vista Previa de Datos')
col1, col2 = st.columns(2)

with col1:
    st.subheader('Detalle de Aeropuertos')
    st.write(aeropuertos_detalle.head())

with col2:
    st.subheader('Informe del Ministerio')
    st.write(informe_ministerio.head())

# Análisis Descriptivo
st.header('📊 Análisis Descriptivo')
col3, col4 = st.columns(2)

with col3:
    st.subheader('Estadísticas Descriptivas de Aeropuertos')
    st.write(aeropuertos_detalle.describe())

with col4:
    st.subheader('Estadísticas Descriptivas del Informe del Ministerio')
    st.write(informe_ministerio.describe())

# Filtros en el sidebar
st.sidebar.header('🔎 Filtros Interactivos')

# Filtro por provincia
provincia_seleccionada = st.sidebar.selectbox('Selecciona una provincia', aeropuertos_detalle['provincia'].unique())
aeropuertos_filtrados = aeropuertos_detalle[aeropuertos_detalle['provincia'] == provincia_seleccionada]

# Filtro por tipo de aeródromo
tipo_seleccionado = st.sidebar.selectbox('Selecciona un tipo de aeródromo', aeropuertos_detalle['tipo'].unique())
aeropuertos_filtrados = aeropuertos_filtrados[aeropuertos_filtrados['tipo'] == tipo_seleccionado]

# Filtro por control
control_seleccionado = st.sidebar.selectbox('Selecciona el tipo de control', aeropuertos_detalle['control'].unique())
aeropuertos_filtrados = aeropuertos_filtrados[aeropuertos_filtrados['control'] == control_seleccionado]

# Filtro por rango de fechas en el informe del ministerio
fecha_min, fecha_max = st.sidebar.slider('Selecciona un rango de fechas', 
                                         min_value=informe_ministerio['Fecha UTC'].min().to_pydatetime(), 
                                         max_value=informe_ministerio['Fecha UTC'].max().to_pydatetime(), 
                                         value=(informe_ministerio['Fecha UTC'].min().to_pydatetime(), 
                                                informe_ministerio['Fecha UTC'].max().to_pydatetime()))
informe_filtrado = informe_ministerio[(informe_ministerio['Fecha UTC'] >= fecha_min) & (informe_ministerio['Fecha UTC'] <= fecha_max)]

# Filtro por Aeropuerto
aeropuerto_seleccionado = st.sidebar.selectbox('Selecciona un Aeropuerto', informe_ministerio['Aeropuerto'].unique())
informe_filtrado = informe_filtrado[informe_filtrado['Aeropuerto'] == aeropuerto_seleccionado]

# Filtro por Aerolínea
aerolinea_seleccionada = st.sidebar.selectbox('Selecciona una Aerolínea', informe_ministerio['Aerolinea Nombre'].unique())
informe_filtrado = informe_filtrado[informe_filtrado['Aerolinea Nombre'] == aerolinea_seleccionada]

# Filtro por Clase de Vuelo
clase_vuelo_seleccionada = st.sidebar.selectbox('Selecciona la Clase de Vuelo', informe_ministerio['Clase de Vuelo (todos los vuelos)'].unique())
informe_filtrado = informe_filtrado[informe_filtrado['Clase de Vuelo (todos los vuelos)'] == clase_vuelo_seleccionada]

# Filtro por Clasificación de Vuelo
clasificacion_vuelo_seleccionada = st.sidebar.selectbox('Selecciona la Clasificación de Vuelo', informe_ministerio['Clasificación Vuelo'].unique())
informe_filtrado = informe_filtrado[informe_filtrado['Clasificación Vuelo'] == clasificacion_vuelo_seleccionada]

# Visualizaciones
st.header('📈 Visualizaciones')

# Gráfico de barras
st.subheader('Cantidad de Aeropuertos por Provincia')
if 'provincia' in aeropuertos_filtrados.columns:
    aeropuertos_por_provincia = aeropuertos_filtrados['provincia'].value_counts()
    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    aeropuertos_por_provincia.plot(kind='bar', ax=ax)
    ax.set_title('Cantidad de Aeropuertos por Provincia')
    ax.set_xlabel('Provincia')
    ax.set_ylabel('Cantidad de Aeropuertos')
    st.pyplot(fig)
else:
    st.write("La columna 'provincia' no existe en el DataFrame de aeropuertos.")

# Gráfico de dispersión
st.subheader('Distribución de Aeropuertos por Latitud y Longitud')
if 'longitud' in aeropuertos_filtrados.columns and 'latitud' in aeropuertos_filtrados.columns:
    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    sns.scatterplot(data=aeropuertos_filtrados, x='longitud', y='latitud', ax=ax)
    ax.set_title('Distribución de Aeropuertos')
    ax.set_xlabel('Longitud')
    ax.set_ylabel('Latitud')
    st.pyplot(fig)
else:
    st.write("Las columnas 'longitud' y/o 'latitud' no existen en el DataFrame de aeropuertos.")

# Gráfico de líneas
st.subheader('Tendencias en el Informe del Ministerio')
if 'Fecha UTC' in informe_filtrado.columns and 'PAX' in informe_filtrado.columns:
    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    sns.lineplot(data=informe_filtrado, x='Fecha UTC', y='PAX', ax=ax)
    ax.set_title('Tendencias de PAX en el Tiempo')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('PAX')
    st.pyplot(fig)
else:
    st.write("Las columnas 'Fecha UTC' y/o 'PAX' no existen en el DataFrame del informe del ministerio.")

# Conclusiones
st.header('📌 Conclusiones')
st.write('Aquí puedes incluir algunas conclusiones basadas en los datos analizados y las visualizaciones.')

# Tema oscuro
st.sidebar.header('🌓 Tema')
dark_mode = st.sidebar.checkbox('Activar modo oscuro')
if dark_mode:
    st.markdown(
        """
        <style>
        body {
            background-color: #333;
            color: #fff;
        }
        .stButton>button {
            color: #fff !important;
            background-color: #333 !important;
        }
        .stHeader, .stSidebar, .stMain, .stFooter {
            background-color: #000 !important;
            color: #fff !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Resumen del Tráfico Aéreo
st.header('✈️ Resumen del Tráfico Aéreo')
st.markdown('#### Resumen de Llegadas y Salidas por Aeropuerto')
aeropuerto_trafico = informe_ministerio.groupby(['Aeropuerto', 'Tipo de Movimiento']).size().unstack(fill_value=0)
st.write(aeropuerto_trafico)

df = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(df)

# Visualización 3D
st.header('📊 Visualización 3D')
st.markdown('#### Visualización 3D del Tráfico Aéreo')

if 'longitud' in aeropuertos_detalle.columns and 'latitud' in aeropuertos_detalle.columns and 'elevacion' in aeropuertos_detalle.columns:
    fig_3d = px.scatter_3d(
        aeropuertos_detalle,
        x='longitud',
        y='latitud',
        z='elevacion',
        color='provincia',
        hover_name='denominacion'
    )
    st.plotly_chart(fig_3d, use_container_width=True)
else:
    st.write("Las columnas 'longitud', 'latitud' y/o 'elevacion' no existen en el DataFrame de aeropuertos.")

# Footer con Copyright
st.markdown("""
<hr style="border:2px solid gray"> </hr>
<center>
<p style="font-size:12px; color:gray;">&copy; 2024 Flavio Cesar Flores</p>
</center>
""", unsafe_allow_html=True)

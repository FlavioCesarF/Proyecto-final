import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium

# Configuración de la página de Streamlit
st.set_page_config(page_title="Dashboard de Aeropuertos", page_icon="✈️", layout="wide")

# Función para cargar los datos
@st.cache_data
def cargar_datos(file_path, delimiter, column_names=None):
    return pd.read_csv(file_path, delimiter=delimiter, on_bad_lines='skip', names=column_names, header=0 if column_names is None else None)

# Cargar archivos CSV
aeropuertos_detalle_path = 'database/aeropuertos_detalle.csv'
informe_ministerio_paths = [
    'database/202405-informe-ministerio.csv',
    'database/202312-informe-ministerio-actualizado-dic.csv',
    'database/2019_informe_ministerio.csv',
    'database/202112_informe_ministerio.csv',
    'database/2020_informe_ministerio.csv'
]

aeropuertos_detalle = cargar_datos(aeropuertos_detalle_path, delimiter=';')

# Columnas para los informes del ministerio
columnas_informe_ministerio = ["Fecha UTC", "Hora UTC", "Clase de Vuelo (todos los vuelos)", "Clasificación Vuelo", "Tipo de Movimiento", "Aeropuerto", "Origen / Destino", "Aerolinea Nombre", "Aeronave", "Pasajeros", "PAX", "Calidad dato"]

# Cargar y combinar informes del ministerio
informes_ministerio = []
for path in informe_ministerio_paths:
    informes_ministerio.append(cargar_datos(path, delimiter=',', column_names=columnas_informe_ministerio))

informe_ministerio = pd.concat(informes_ministerio, ignore_index=True)

# Convertir la columna 'Fecha UTC' a formato de fecha
informe_ministerio['Fecha UTC'] = pd.to_datetime(informe_ministerio['Fecha UTC'], format='%d/%m/%Y', errors='coerce')

# Título del Dashboard
st.title('✈️ Dashboard de Análisis de Aeropuertos')

# Agregar iconos y descripción
st.markdown("""
<div style="text-align: center;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/e/e1/Airport_icon.png" alt="icon" width="100">
    <h3>Análisis detallado del tráfico aéreo y la gestión de aeropuertos</h3>
</div>
""", unsafe_allow_html=True)

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

# Visualizaciones
st.header('📈 Visualizaciones')

# Gráfico de barras
st.subheader('Cantidad de Aeropuertos por Provincia')
if 'provincia' in aeropuertos_filtrados.columns:
    aeropuertos_por_provincia = aeropuertos_filtrados['provincia'].value_counts()
    fig, ax = plt.subplots()
    aeropuertos_por_provincia.plot(kind='bar', ax=ax)
    ax.set_title('Cantidad de Aeropuertos por Provincia')
    st.pyplot(fig)
else:
    st.write("La columna 'provincia' no existe en el DataFrame de aeropuertos.")

# Gráfico de dispersión
st.subheader('Distribución de Aeropuertos por Latitud y Longitud')
if 'longitud' in aeropuertos_filtrados.columns and 'latitud' in aeropuertos_filtrados.columns:
    fig, ax = plt.subplots()
    sns.scatterplot(data=aeropuertos_filtrados, x='longitud', y='latitud', ax=ax)
    ax.set_title('Distribución de Aeropuertos')
    st.pyplot(fig)
else:
    st.write("Las columnas 'longitud' y/o 'latitud' no existen en el DataFrame de aeropuertos.")

# Gráfico de líneas
st.subheader('Tendencias en el Informe del Ministerio')
if 'Fecha UTC' in informe_filtrado.columns and 'PAX' in informe_filtrado.columns:
    fig, ax = plt.subplots()
    sns.lineplot(data=informe_filtrado, x='Fecha UTC', y='PAX', ax=ax)
    ax.set_title('Tendencias de PAX en el Tiempo')
    st.pyplot(fig)
else:
    st.write("Las columnas 'Fecha UTC' y/o 'PAX' no existen en el DataFrame del informe del ministerio.")

# Mapa interactivo
st.header('🗺️ Mapa Interactivo de Aeropuertos')
if 'latitud' in aeropuertos_filtrados.columns and 'longitud' in aeropuertos_filtrados.columns:
    m = folium.Map(location=[aeropuertos_filtrados['latitud'].mean(), aeropuertos_filtrados['longitud'].mean()], zoom_start=5)
    for _, row in aeropuertos_filtrados.iterrows():
        folium.Marker(
            location=[row['latitud'], row['longitud']],
            popup=row['denominacion'],
            icon=folium.Icon(icon='plane', prefix='fa')
        ).add_to(m)
    st_folium(m, width=700, height=500)
else:
    st.write("Las columnas 'latitud' y/o 'longitud' no existen en el DataFrame de aeropuertos.")

# Conclusiones
st.header('📌 Conclusiones')
st.write('Aquí puedes incluir algunas conclusiones basadas en los datos analizados y las visualizaciones.')

import pandas as pd

# Cargar los archivos CSV
aeropuertos_detalle = pd.read_csv('/mnt/data/aeropuertos_detalle.csv')
informe_ministerio = pd.read_csv('/mnt/data/202405-informe-ministerio.csv')

# Mostrar las primeras filas de cada DataFrame
print(aeropuertos_detalle.head())
print(informe_ministerio.head())

# Verificar valores nulos y tipos de datos
print(aeropuertos_detalle.info())
print(informe_ministerio.info())

# Limpieza de datos si es necesario
# Ejemplo de eliminación de valores nulos
aeropuertos_detalle.dropna(inplace=True)
informe_ministerio.dropna(inplace=True)

import matplotlib.pyplot as plt
import seaborn as sns

# Ejemplo de un gráfico
plt.figure(figsize=(10, 6))
sns.countplot(data=aeropuertos_detalle, x='estado')
plt.title('Distribución de Aeropuertos por Estado')
plt.show()

import streamlit as st

# Título del Dashboard
st.title('Dashboard de Aeropuertos')

# Carga de datos
@st.cache
def load_data():
    aeropuertos_detalle = pd.read_csv('/mnt/data/aeropuertos_detalle.csv')
    informe_ministerio = pd.read_csv('/mnt/data/202405-informe-ministerio.csv')
    return aeropuertos_detalle, informe_ministerio

aeropuertos_detalle, informe_ministerio = load_data()

# Sidebar para filtros
st.sidebar.header('Filtros')
estado = st.sidebar.multiselect('Estado', aeropuertos_detalle['estado'].unique())
categoria = st.sidebar.multiselect('Categoría', informe_ministerio['categoria'].unique())

# Filtrar datos
if estado:
    aeropuertos_detalle = aeropuertos_detalle[aeropuertos_detalle['estado'].isin(estado)]
if categoria:
    informe_ministerio = informe_ministerio[informe_ministerio['categoria'].isin(categoria)]

# Mostrar datos filtrados
st.write('### Datos Filtrados de Aeropuertos')
st.dataframe(aeropuertos_detalle)

st.write('### Datos Filtrados del Informe Ministerio')
st.dataframe(informe_ministerio)

# Gráfico interactivo
st.write('### Distribución de Aeropuertos por Estado')
fig, ax = plt.subplots()
sns.countplot(data=aeropuertos_detalle, x='estado', ax=ax)
st.pyplot(fig)

# Visualizar las primeras líneas de los archivos CSV
with open('/mnt/data/aeropuertos_detalle.csv', 'r') as file:
    aeropuertos_detalle_preview = file.readlines()[:10]

with open('/mnt/data/202405-informe-ministerio.csv', 'r') as file:
    informe_ministerio_preview = file.readlines()[:10]

aeropuertos_detalle_preview, informe_ministerio_preview

import pandas as pd

# Cargar los archivos CSV con el delimitador correcto
aeropuertos_detalle = pd.read_csv('/mnt/data/aeropuertos_detalle.csv', delimiter=';')
informe_ministerio = pd.read_csv('/mnt/data/202405-informe-ministerio.csv', delimiter=';')

# Mostrar las primeras filas de cada DataFrame
print(aeropuertos_detalle.head())
print(informe_ministerio.head())

# Obtener información de los DataFrames
print(aeropuertos_detalle.info())
print(informe_ministerio.info())

# Tratamiento de valores nulos en aeropuertos_detalle
aeropuertos_detalle.fillna('No disponible', inplace=True)

# Convertir columnas de fechas en informe_ministerio
informe_ministerio['Fecha UTC'] = pd.to_datetime(informe_ministerio['Fecha UTC'], format='%d/%m/%Y')
informe_ministerio['Hora UTC'] = pd.to_datetime(informe_ministerio['Hora UTC'], format='%H:%M').dt.time

# Revisar valores nulos en informe_ministerio
informe_ministerio.fillna(0, inplace=True)


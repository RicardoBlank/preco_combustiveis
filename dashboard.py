import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import folium
import streamlit as st

df = pd.read_csv('/home/ricardoblank/projects/preco_combustiveis/ca-2022-02.csv', sep=';')

# Valor de compra é uma coluna vazia
df = df.drop('Valor de Compra', axis=1)

# Transforma o preço em tipo numérico float
df['Valor de Venda'] = df['Valor de Venda'].apply(lambda x: float(x.replace(',', '.')))

# Renomeia algumas colunas por conveniência
df = df.rename(columns={'Regiao - Sigla': 'Regiao', 'Estado - Sigla': 'Estado'})

lista_estados = np.sort(df['Estado'].unique())

# Add a selectbox to the sidebar:
selectbox_estado = st.sidebar.selectbox(
    'Escolha o estado:',
    lista_estados
)

lista_municipios = np.sort(df[df['Estado'] == selectbox_estado]['Municipio'].unique())

# Add a selectbox to the sidebar:
selectbox_municipio = st.sidebar.selectbox(
    'Escolha o municipio:',
    lista_municipios
)

def menor_preco(cidade, combustivel):
    """ Função que retorna os dados do posto com o menor preço de acordo com a cidade escolhida"""
    dados = df.iloc[df[(df['Municipio'] == cidade.upper()) & 
                        (df['Produto'] == combustivel.upper())]['Valor de Venda'].idxmin(), :]
    return dados

dados = menor_preco(selectbox_municipio, 'gasolina')

# Junta os dados de endereço em uma string única
endereco_completo = f"{dados['Nome da Rua']}, {dados['Numero Rua']}, {dados['Bairro']}, {dados['Municipio']}, {dados['Estado']}, {dados['Cep']}"

# É utilizado o Nominatim (OpenStreetMap) como backend por ser open_source
geolocator = Nominatim(user_agent="preco_combustivel")

# Obter as coordenadas a partir do endereço
location = geolocator.geocode(endereco_completo)
coords = location.point[0:2]
coords = pd.DataFrame({
    'lat': [coords[0]],
    'lon': [coords[1]]
})

st.map(coords)


import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import folium
import streamlit as st
from streamlit_folium import folium_static

APP_TITLE = "Preço dos combustíveis no Brasil"
APP_SUBTITLE = "Fonte de dados: ANP 2º semestre de 2022"


def clean_df(df):
    # Valor de compra é uma coluna vazia
    df_cleaned = df.drop('Valor de Compra', axis=1)

    # Transforma o preço em tipo numérico float
    df_cleaned['Valor de Venda'] = df_cleaned['Valor de Venda'].str.replace(',', '.').astype(float)

    # Renomeia algumas colunas por conveniência
    df_cleaned = df_cleaned.rename(columns={'Regiao - Sigla': 'Regiao', 'Estado - Sigla': 'Estado'})

    return df_cleaned

def menores_precos(df, municipio, combustivel):
    """ Função que retorna os dados dos postos com os menores preços em ordem crescente de acordo com a cidade e combustivel escolhida"""
    df_menores_precos = df.loc[(df['Municipio'] == municipio.upper()) & (df['Produto'] == combustivel.upper())] \
                        .sort_values(by='Valor de Venda')
    return df_menores_precos

def display_filters(df):
    lista_estados = np.sort(df['Estado'].unique())

    # Add a selectbox to the sidebar:
    estado = st.sidebar.selectbox('Escolha o estado:', lista_estados)

    lista_municipios = np.sort(df[df['Estado'] == estado]['Municipio'].unique())

    # Add a selectbox to the sidebar:
    municipio = st.sidebar.selectbox('Escolha o município:', lista_municipios)

    return municipio

def plot_map(locations):

    for _, location in locations.iterrows():
        # Junta os dados de endereço em uma string única
        endereco_completo = f"{location['Nome da Rua']}, {location['Numero Rua']}, \
                            {location['Bairro']}, {location['Municipio']}, {location['Estado']}, {location['Cep']}"

        # É utilizado o Nominatim (OpenStreetMap) como backend por ser open_source
        geolocator = Nominatim(user_agent="preco_combustivel")

        # Obter as coordenadas a partir do endereço
        geocode = geolocator.geocode(endereco_completo)

        if geocode:
            coords = {'lat': geocode.point[0], 'lon': geocode.point[1]}

            # Dados para popup no mapa
            revenda = f"<strong>Revenda:</strong> {location['Revenda']}"
            bandeira = f"<strong>Bandeira:</strong> {location['Bandeira']}"
            preco = f"<strong>Preço/Litro:</strong> R$ {str(location['Valor de Venda']).replace('.', ',')}"
            data_atualizacao = f"<strong>Data da última atualização:</strong> {location['Data da Coleta']}"
            endereco = f"<strong>Endereço:</strong> {endereco_completo}"

            # Plotar o mapa com o marker no endereço obtido
            m = folium.Map(location=[coords['lat'], coords['lon']], zoom_start=15)

            # Popup com dados do posto
            popup_text = f"{revenda}<br>{bandeira}<br>{preco}<br>{data_atualizacao}<br>{endereco}"

            folium.Marker(
                location=[coords['lat'], coords['lon']],
                popup=folium.map.Popup(popup_text, max_width=300),
                icon=folium.Icon(icon="gas-pump", prefix='fa'),
            ).add_to(m)

            break

    st_map = folium_static(m, width=725)

    return st_map

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon=':fuelpump:')
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    # Load Data
    df = pd.read_csv('/home/ricardoblank/projects/preco_combustiveis/ca-2022-02.csv', sep=';')
    df = clean_df(df)

    # Display Filters and Get Filtered Locations
    municipio = display_filters(df)
    combustivel = 'gasolina'
    locations = menores_precos(df, municipio, combustivel)

    # Plot Map with Filtered Locations
    plot_map(locations)

if __name__ == "__main__":
    main()
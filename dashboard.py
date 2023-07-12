import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import folium
import streamlit as st
from streamlit_folium import folium_static

plt.style.use('ggplot')

def clean_df(df):
    # Valor de compra é uma coluna vazia
    df_cleaned = df.drop('Valor de Compra', axis=1)

    # Transforma o preço em tipo numérico float
    df_cleaned['Valor de Venda'] = df_cleaned['Valor de Venda'].str.replace(',', '.').astype(float)

    # Renomeia algumas colunas por conveniência
    df_cleaned = df_cleaned.rename(columns={'Regiao - Sigla': 'Regiao', 'Estado - Sigla': 'Estado'})

    return df_cleaned

def menores_precos(df, municipio, combustivel):
    #Função que retorna os dados dos postos com os menores preços em ordem crescente de acordo com a cidade e combustivel escolhido
    df_menores_precos = df.loc[(df['Municipio'] == municipio.upper()) & (df['Produto'] == combustivel.upper())] \
                        .sort_values(by='Valor de Venda')
    return df_menores_precos

def display_filters(df):
    # Função para adicionar os filtros na aba lateral do app
    st.sidebar.subheader("Filtros")

    lista_estados = np.sort(df['Estado'].unique())

    # Add a selectbox to the sidebar:
    estado = st.sidebar.selectbox('Escolha o estado:', lista_estados)

    lista_municipios = np.sort(df[df['Estado'] == estado]['Municipio'].unique())

    # Add a selectbox to the sidebar:
    municipio = st.sidebar.selectbox('Escolha o município:', lista_municipios)

    lista_combustiveis = np.sort(df[df['Municipio'] == municipio]['Produto'].unique())

    # Add a selectbox to the sidebar:
    combustivel = st.sidebar.selectbox('Escolha o combustível:', lista_combustiveis)

    return municipio, combustivel

def plot_map(locations):
    # Plota o mapa através do geocode para obter coordenadas e folium para plotagem
    try:
        for _, location in locations.iterrows():
            # Junta os dados de endereço em uma string única
            endereco_completo = f"{location['Nome da Rua']}, {location['Numero Rua']}, \
                                {location['Bairro']}, {location['Municipio']}, {location['Estado']}, {location['Cep']}"

            # É utilizado o Nominatim (OpenStreetMap) como backend por ser open_source
            geolocator = Nominatim(user_agent="preco_combustivel")

            # Obter as coordenadas a partir do endereço
            geocode = geolocator.geocode(endereco_completo)

            # Verifica se geocode retonna um valor diferende de None, ou seja, se encontrou as coordenadas do endereço
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

        # Utiliza o streamlit folium para plotar o mapa no app
        st_map = folium_static(m, width=725)

    except UnboundLocalError:
        return st.error("Erro: não foi possível carregar o mapa")

    return st_map

def plot_hist_prices(df, municipio, combustivel):
    # Plota o histograma da distribuição dos preços

    hist_prices = df[(df['Municipio'] == municipio) & (df['Produto'] == combustivel)]['Valor de Venda']

    fig, ax = plt.subplots()
    ax.hist(x=hist_prices, bins=10)

    ax.set_title(f"Distribuição dos preços de {combustivel} em {municipio}")
    ax.set_xlabel("Preço [R$]")

    # indicação do preço médio no Municipio
    ax.axvline(x=hist_prices.mean(), linestyle='--', color='b')
    ax.text(x=hist_prices.mean()+0.05, y=5, s='Média = {}'.format(round(hist_prices.mean(), 2)), rotation='vertical')

    # ajustes dos ticks
    ax.set_xticks(np.arange(round(hist_prices.min(), 0) - 0.5, round(hist_prices.max(), 0) + 0.5, 0.5))
    ax.minorticks_on()
    ax.tick_params(axis='y', which='minor', left=False)

    return st.pyplot(fig)

def main():

    APP_TITLE = "Preço dos combustíveis no Brasil"
    APP_SUBTITLE = "Fonte de dados: ANP 2º semestre de 2022"

    st.set_page_config(page_title=APP_TITLE, page_icon=':fuelpump:')
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    st.markdown("<h3 style='text-align: center; color: grey;'>Localização do estabelecimento com o preço mais baixo</h3>", unsafe_allow_html=True)

    # Carrega e limpa os dados
    df = pd.read_csv('/home/ricardoblank/projects/preco_combustiveis/ca-2022-02.csv', sep=';')
    df = clean_df(df)

    # Mostra os filtro e filtra o df
    municipio, combustivel = display_filters(df)
    locations = menores_precos(df, municipio, combustivel)

    # Plota o mapa indicando o estabelecimento com o menor preço
    plot_map(locations)

    # Plota o histograma de acordo com os filtros
    plot_hist_prices(df, municipio, combustivel)

if __name__ == "__main__":
    main()
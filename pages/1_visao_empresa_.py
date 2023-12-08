#bibliotecas necessárias
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide' )

#=========================================
# Funções 
#=========================================
def Clean_data(df):
    """ 
    Essa função tem a responsabilidade de limpar o dataframe
    1. Remoção dos dados NaN
    2. mudança do tipo da coluna de dados
    3. Remoção dos espaços das variaveis de Textos 
    4. Formataçao da coluna de data
    5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )
        
    Input: Dataframe
    Output: Dataframe
    """
    
    #removendo os spaces
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Weatherconditions'] = df.loc[:, 'Weatherconditions'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
    df.loc[:, 'Delivery_person_Age'] = df.loc[:, 'Delivery_person_Age'].str.strip()

    #drop variaveis 'nan' e 'NaN'
    linhas_limpas = df['Weatherconditions'] != 'nan' 
    df = df.loc[linhas_limpas, :]    
    linhas_limpas = df['City'] != 'NaN' 
    df = df.loc[linhas_limpas, :]
    linhas_limpas = df['Road_traffic_density'] != 'NaN' 
    df = df.loc[linhas_limpas, :]
    linhas_limpas = df['Festival'] != 'NaN' 
    df = df.loc[linhas_limpas, :]
    linhas_v = df['Delivery_person_Age'] != 'NaN'
    df = df.loc[linhas_v, : ].copy()
    linhas_v = df['multiple_deliveries'] != 'NaN'
    df = df.loc[linhas_v, : ]
    df['Time_taken(min)'] = df['Time_taken(min)'].astype('str') #transformando o Time_take(min) em string para retirar o valor NaN
    linhas_limpas = df['Time_taken(min)'] != 'NaN' 
    df = df.loc[linhas_limpas, :]
    linhas_limpas = df['Time_taken(min)'] != 'nan' 
    df = df.loc[linhas_limpas, :]

    #1. convertendo as linhas com a idade dos entregadores de object para int
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)

    #2. convertendo as linhas com a avaliaçao dos entregadores de object para int
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)

    #3. convertendo as linhas com a order_date de object para data
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y' )

    #4. convertendo as linhas com a condiçoes do veiculo de object para int
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(float).astype('Int64')

    #5. covertendo o Time_taken(min) para string
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    #transfomando em inteiro
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    #reiniciando a contagem do index
    #dropando a linha index antiga
    df = df.reset_index(drop=True)
    return df 


def Pedidos_by_Day(df):
    """ 
    Essa função tem a responsabilidade de plotar um grafico de barras com a Quantidade de pedidos por dia 
    1. Agrupar as entregas pela datas 
    2. Contar a quantidade de entregas por datas
    3. Cria um grafico de barras com a visualização quantide de entregas por dia 
        
    Input: Dataframe
    Output: Grafico de barras 
    """
    
    cols = ['ID','Order_Date']
    df_axc = (df.loc[:,cols]
                .groupby(['Order_Date'])
                .count()
                .reset_index())
    fig = px.bar(df_axc, x='Order_Date', y ='ID')
    return fig

def Perct_entrega_por_trafego(df):
    """ 
    Essa função tem a responsabilidade de plotar o gráfico de pizza com a porcentagem dos pedidos por tipo de tráfego.
    1. Agrupar as entregas pela densidades de traficos
    2. Contar a quantidade de entregas por densidade de trafico
    3. Cálcular a porcentagem de entregas por densidade de trafico
    4. Cria um grafico de pizza com a porcentagem das entregas por densidade de tráfego 
        
    Input: Dataframe
    Output: Gráfico de Pizza
    """
    df_axc = (df.loc[:,['ID','Road_traffic_density']]
                .groupby(['Road_traffic_density'])
                .count()
                .reset_index())
    df_axc['entrega_perc'] = df_axc['ID'] / df_axc['ID'].sum()
    fig = px.pie(df_axc, values='entrega_perc', names= 'Road_traffic_density')
    return fig

def conparacao_entreg_city_trafeg(df):
    """ 
    Essa função tem a responsabilidade de plotar o gráfico de dispersão(scatter) com a Comparação do volume de pedidos por cidade e tipo de tráfego.
    1. Agrupar as entregas pela cidades e densidades de traficos
    2. Contar a quantidade de entregas por densidade de trafico e cidades
    3. Cria um grafico de Dispersão(scatter) com a comparação das entregas por densidades de tráfegos e cidades. 
        
    Input: Dataframe
    Output: Gráfico de Dispersão(scatter) 
    """
    df_axc= (df.loc[:,['ID','City','Road_traffic_density']]
               .groupby(['City','Road_traffic_density'])
               .count()
               .reset_index())
    fig = px.scatter(df_axc, x= 'City', y='Road_traffic_density', size='ID', color='City')
    return fig

def quantid_entrega_semana(df):
    """ 
    Essa função tem a responsabilidade de plotar o gráfico de linha com a Quantidade de pedidos por semana.
    1. Criando a coluna de semana por ano
    2. Agrupar as entregas pela semanas
    3. Contar a quantidade de entregas por semanas no ano
    4. Cria um grafico de linha com a quantidade de entregas por semanas. 
        
    Input: Dataframe
    Output: Gráfico de linha
    """
    df['wenk_of_year'] = df['Order_Date'].dt.strftime('%U')
    cols = ['ID','wenk_of_year']
    df_axc = (df.loc[:,['ID','wenk_of_year']]
                .groupby(['wenk_of_year'])
                .count()
                .reset_index())
    fig = px.line(df_axc, x='wenk_of_year', y='ID' )
    return fig

def quantid_entrega_entregador_semana(df):
    """ 
    Essa função tem a responsabilidade de plotar o gráfico de linha com a quantidade de pedidos por entregador por semana.
    1. Agrupar as entregas pela semanas e pegar a quatidade de entregas por semana o dataframe
    2. Agrupar os entregadores pelas semanas e pegar a quntidade unica de entregadores por semana e fazer um dataframe
    3. Mesclar os dataframes dos agrupamentos acimas 
    4. Criar uma coluna com a quantidade de entrega por entregador por semana
    5. Cria um grafico de linha com a quantidade de entregas por entregadores por semanas. 
        
    Input: Dataframe
    Output: Gráfico de linha
    """
    df_axc1 = df.loc[:,['ID','wenk_of_year']].groupby(['wenk_of_year']).count().reset_index()
    df_axc2 = df.loc[:,['Delivery_person_ID','wenk_of_year']].groupby(['wenk_of_year']).nunique().reset_index()
    df_axc = pd.merge(df_axc1, df_axc2, how= 'inner')
    df_axc['order_by_delivery'] =df_axc['ID'] / df_axc['Delivery_person_ID']
    fig = px.line(df_axc, x='wenk_of_year', y='order_by_delivery')
    return fig

def Local_entrega(df):
    """ 
    Essa função tem a responsabilidade de plotar um mapa com a localização central de 10 cidade por tipo de tráfego.
    1. Agrupar as latitude e longitude pelas cidade e dencidades de trafegos a calcular a media
    2. pegar as primeiras 10 linhas do dataframe
    3. cronstruir um loop for para inplantar os 10 pontos em cada local do mapa
   
    Input: Dataframe
    Output: mapa
    """
    df_axc = (df.loc[:,['City','Road_traffic_density',
                        'Delivery_location_latitude',
                        'Delivery_location_longitude']]
                .groupby(['City','Road_traffic_density'])
                .median()
                .reset_index())

    df_axc = df_axc.head(10)
    map = folium.Map()

    for index ,location_info in df_axc.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], 
                       location_info['Delivery_location_longitude']],
                       popup=location_info[['City', 'Road_traffic_density']] ).add_to(map)
    return map

#___________________________________________ Inicio da Estrutura Lógica do código __________________________________________

#-----------------------------------------
# Import dataset
#-----------------------------------------
df_ = pd.read_csv('../dataset/train.csv')

#-----------------------------------------
# Limpendo os dados
#-----------------------------------------
df = Clean_data(df_)


#=========================================
#Barra lateral
#=========================================
st.header('Marketplace - Visão Empresa')

#image_path = r'C:\Users\User\comunidade_DS\FTC_Analisando_dados_Python'
image = Image.open( 'logo.png' )
st.sidebar.image(image, width=120)


st.sidebar.markdown('# cury company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
data_slider = st.sidebar.slider('Até qual valor?',
                                value= pd.datetime(2022, 4, 13),
                                min_value = pd.datetime(2022, 2, 11),
                                max_value= pd.datetime(2022, 4, 6),
                                format='DD-MM-YY')

st.sidebar.markdown("""___""")

traffic_options=st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

clima_options = st.sidebar.multiselect('Quais as condições climaticas',['conditions Sunny', 
                                        'conditions Stormy', 'conditions Sandstorms',
                                        'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
                                        default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
                                        'conditions Cloudy', 'conditions Fog', 'conditions Windy'] )

linhas_selecionadas = df['Order_Date'] < data_slider
df = df.loc[ linhas_selecionadas, :]
#isin quer dizier (esta em) e uma forma de filtrar a tabela e so trazer variaveis dessa coluna que correspoda com o valor detro do isin()
linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[linhas_selecionadas, :]

linhas_selecionadas = df['Weatherconditions'].isin( clima_options )
df = df.loc[linhas_selecionadas, :]

st.sidebar.markdown("""___""")
st.sidebar.markdown('Powered by Comunidade DS')



#=========================================
#Layout no Streamlit
#=========================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 
                             'Visão Tática ',
                             'Visão Geográfica'] )
with tab1:
    with st.container():
        #order metric
        fig = Pedidos_by_Day(df)
        st.markdown('# Orders by Day')
        st.plotly_chart(fig,use_container_width=True )
        
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.header('Traffic Order Share')
            fig = Perct_entrega_por_trafego(df)
            st.plotly_chart(fig,use_container_width=True )
            
        with col2:
            st.header('Traffic Order City')
            fig = conparacao_entreg_city_trafeg(df)
            st.plotly_chart( fig, use_container_width=True )
            
    
with tab2:
    with st.container():
        st.header('Delivery per Week')
        fig = quantid_entrega_semana(df)
        st.plotly_chart( fig, use_container_width=True )
    
    with st.container():
        st.header('Delivery of each Delivery Person per Week')

        fig = quantid_entrega_entregador_semana(df)
        st.plotly_chart( fig, use_container_width=True )
        

with tab3:
    st.header('Country Maps')

    map = Local_entrega(df)
    folium_static(map, width=1024, height=600)
    
#a forma de rodar o python no terminal
#python visao_empresa.py
#a forma de rodar o streanlit no terminal
###streamlit run visao_emperesa.py###

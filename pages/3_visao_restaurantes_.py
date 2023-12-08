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

st.set_page_config( page_title='Visão Restaurante', page_icon='🧂', layout='wide' )


#=========================================
# Funções 
#=========================================

def time_avg_STD_entreg_city_trafego(df):
    """
    Esta funçao calcula o tempo medio e o desvio padrão do tempo de entrega por cada cidade e pelo trafego.
    1. primeiro eu localizar as coluna de tempo, cidades e trafego depois agrupar por cidades e os tipos de trafegos
    depois calcular o tempo medio e o desvio padrao das entregas por cada cidade e tipo de trafego.
    
    2. colocando o nome em cada coluna do novo dataframe
    3. criando um grafico de raio do sol(sunburst) com o tempo medio e o desvio padrao por cidades e os tipos de trafegos
    Parâmetros:
        Input:
             -df: Dataframe
        Output:
              -sunburst: um grafico de raio do sol(sunburst) com o tempo medio  e o desvio padrão em cima do tempo de entrega em cada cidade e em cada tipo de trafego
    """
    df_axc = (df.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density'] ]
                .groupby(['City', 'Road_traffic_density'])
                .agg( {'Time_taken(min)' : ['mean','std'] } ).reset_index())

    df_axc.columns = ['City','Road_traffic_density','avg_time', 'std_time']
    df_axc =df_axc.reset_index(drop=True)
                
    fig = px.sunburst( df_axc, path =['City', 'Road_traffic_density'], values= 'avg_time',
                       color= 'std_time', color_continuous_scale= 'amp',
                       color_continuous_midpoint=np.average(df_axc['std_time']))
    return fig


def Tempo_medio_STD_tipo_entrega_e_cidade(df):
    """
    Esta funçao calcula o tempo medio e o desvio padrão do tempo de entrega por cada cidade e tipo de entrega.
    1. primeiro eu localizar as coluna de tempo, cidades e tipo de entregas depois agrupar por cidades e tipos de entregas
    depois calcular o tempo medio e o desvio padrao das entregas por cada cidade e tipo de entrega.
    
    2. colocando o nome em cada coluna do novo dataframe.
    3. criando um Dataframe com o tempo medio e o desvio padrao por cada cidade e tipo de entrega. 
    Parâmetros:
        Input:
             -df: Dataframe
        Output:
              -df: Dataframe
    """
    df_axc = (df.loc[:, ['City', 'Time_taken(min)', 'Type_of_order'] ]
                .groupby(['City', 'Type_of_order'])
                .agg( {'Time_taken(min)' : ['mean','std'] } )
                .reset_index())

    df_axc.columns = ['City','Type_of_order','avg_time', 'std_time']
    df_axc = df_axc.reset_index(drop=True)
    
    return df_axc 


def dristrib_tempo_medio_STD_cidade(df):
    """
    Esta funçao calcula o tempo medio e o desvio padrão do tempo de entrega por cada cidade.
    1. primeiro eu localizar as coluna de tempo e cidades depois agrupar por cidades depois calcular o tempo medio e o desvio padrao das entregas por cada cidade 
    2. colocando o nome em cada coluna do novo dataframe
    3. criando um grafico de barra com o tempo medio sendo as barras e linhas sendo o desvio padrao 
    Parâmetros:
        Input:
             -df: Dataframe
        Output:
              -Bar: um Gráfico de barras com o tempo medio sendo a barras e o desvio padrão sendo a marcação em linha e isso sendo em cima do tempo de entrega em cada cidade
    """
    df_axc = (df.loc[:,['City','Time_taken(min)']]
                .groupby(['City'])
                .agg( {'Time_taken(min)' : ['mean','std'] } )
                .reset_index())

    df_axc.columns = ['City','avg_time', 'std_time']
    df_axc =df_axc.reset_index(drop=True)
    
    fig = go.Figure()
    fig.add_trace(go.Bar( name='Control',
                          x=df_axc['City'],
                          y=df_axc['avg_time'],
                          error_y = dict( type='data', array=df_axc['std_time'])))
    return fig

            
def time_delivery_avg_std(df, metric=[], festival=[]):
    """
    Esta funçao calcula o tempo medio e o desvio padrão do tempo medio de entrega durante ou nao o festival.
    Parâmetros:
        Input:
             -df: Dataframe com os dados necessário para calcular.
             -metric: tipo de operação que vai ser calculado.
                    'avg_time': calcula o tempo medio
                    'std_time': calcula o desvio padrão 
             -festival: Se esta ou nao durante o festival
                    'Yes': esta durante o festival
                    'No': nao esta durante o fetival
        Output:
              -Int: um valor ou do tempo medio ou desvio padrao do tempo durante ou nao o festival
             
    """
    df_axc = (df.loc[:, ['Time_taken(min)', 'Festival'] ]
                 .groupby(['Festival'])
                 .agg( {'Time_taken(min)' : ['mean','std'] } )
                 .reset_index())

    df_axc.columns = ['Festival', 'avg_time', 'std_time']
    df_axc =df_axc.reset_index(drop=True)

    linhas_selecionadas = df_axc['Festival'] == festival
    df_axc = df_axc.loc[linhas_selecionadas, :]
    df_axc = np.round(df_axc[metric], 2)
    return df_axc


def dictance(df,fig):
    """
    Parâmetros:
        Input: 
             -df: Datafarme
              fig: um if com true e false para plotar um grafico de pizza ou um dataframe 
              True:
                   Esta funçao calcula a distância media entre os restaurantes e o local de entrega por cada cidade.
                   1. Pegando a latitude e longitude dos locais de entregas e restaurantes e calculando as distâncias e implementando em uma nova coluna 
                   2. Reduzindo as fraçoes da media da distância para 2 frações 
                   Output: 
                         -Int: um valor com a distancia media 
              False:
                   Esta funçao calcula a distância media entre os restaurantes e o local de entrega e visualizado em um grafico de pizza com porcentagem por cada cidade.
                   1. Pegando a latitude e longitude dos locais de entregas e restaurantes e calculando as distâncias e implementando em uma nova coluna 
                   2. Calculando a media da distancia por cada cidade 
                   3. Criando o Grafico de pizza com a porcentagem da distancia media em cada cidade e disatcando a fatia com a menor distancia 
                   Output: 
                         Pie- um grafico de pizza com a porcentagem da distancia media em cada cidade e disatcando a fatia com a menor distancia 
    """
    if fig == False:
        
        col = ['Restaurant_latitude','Restaurant_longitude',
              'Delivery_location_latitude','Delivery_location_longitude'] 
        df['distance'] = df.loc[:, col].apply( lambda x:
                                               haversine( (x['Delivery_location_latitude'], x['Delivery_location_longitude']),
                                                          (x['Restaurant_latitude'], x['Restaurant_longitude']) ), axis=1)
        distan_mean = np.round(df['distance'].mean(), 2)
        return distan_mean
    else:
        
        col = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude'] 
        df['distance'] = df.loc[:, col].apply( lambda x: 
                                                    haversine( (x['Delivery_location_latitude'], x['Delivery_location_longitude']),
                                                                (x['Restaurant_latitude'], x['Restaurant_longitude']) ), axis=1)

        av_distance = df.loc[:, ['City', 'distance']].groupby(['City']).mean().reset_index()

        fig =go.Figure( data = [ go.Pie( labels = av_distance['City'], values=av_distance['distance'],
                        pull = [0, 0.1, 0]) ]) 
        return fig
        


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


#___________________________________________ Inicio da Estrutura Lógica do código __________________________________________
#-----------------------------------------
# Import dataset
#-----------------------------------------
df_ = pd.read_csv('dataset\train.csv')

#-----------------------------------------
# Limpendo os dados
#-----------------------------------------
df = Clean_data(df_)

#=========================================
#Barra lateral
#=========================================

st.header('Marketplace - Visão Restaurantes')

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

st.sidebar.markdown("""___""")


clima_options = st.sidebar.multiselect('Quais as condições climaticas',['conditions Sunny', 
                                        'conditions Stormy', 'conditions Sandstorms',
                                        'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
                                        default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
                                        'conditions Cloudy', 'conditions Fog', 'conditions Windy'] )


st.sidebar.markdown("""___""")
st.sidebar.markdown('Powered by Comunidade DS')


linhas_selecionadas = df['Order_Date'] < data_slider
df = df.loc[ linhas_selecionadas, :]

#isin quer dizier (esta em) e uma forma de filtrar a tabela e so trazer variaveis dessa coluna que correspoda com o valor detro do isin()
linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[linhas_selecionadas, :]


linhas_selecionadas = df['Weatherconditions'].isin( clima_options )
df = df.loc[linhas_selecionadas, :]

#=========================================
#Layout no Streamlit
#=========================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 
                             '_',
                             '_'] )
with tab1:
    with st.container():
        st.title( 'Overall Metrics' )
        col1, col2, col3, col4, col5, col6 = st.columns(6)
       
        with col1:
            quant_entregadores = df['Delivery_person_ID'].nunique()
            col1.metric('Entregadores únicos',quant_entregadores)
            
        with col2:
            distan_mean = dictance(df,fig=False)
            col2.metric('Distância media', distan_mean)

        with col3:
            df_axc =time_delivery_avg_std(df,'avg_time','Yes')
            col3.metric('tempo de entrega media c/ festival', df_axc)
            
        with col4:
            df_axc =time_delivery_avg_std(df,'std_time','Yes')
            col4.metric('STD de entrega c/ festival', df_axc)
            
        with col5:
            df_axc =time_delivery_avg_std(df,'avg_time','No')
            col5.metric('tempo de entrega media s/ festival', df_axc)
            
        with col6:
            df_axc =time_delivery_avg_std(df,'std_time','No')
            col6.metric('STD de entrega s/ festival', df_axc)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""___""")
            st.markdown( 'Distribuição de tempo medio e STD por cidade' )
            fig = dristrib_tempo_medio_STD_cidade(df)
            st.plotly_chart(fig)
            
        with col2:       
            st.markdown( 'Tempo médio e STD por tipo de entrega e cidade' )
            df_axc = Tempo_medio_STD_tipo_entrega_e_cidade(df)
            st.dataframe(df_axc)  
            
    with st.container():
        st.markdown("""___""")
        col1 , col2 = st.columns(2, gap= 'large')
        
        with col1:
            st.markdown( 'O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego' )
            fig = time_avg_STD_entreg_city_trafego(df)
            st.plotly_chart(fig)

        with col2:    
            st.markdown( 'distancia medio de entrega por cidade' )
            fig = dictance(df,fig=True)
            st.plotly_chart(fig)      

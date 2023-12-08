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

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide' )
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

def top_entregas(df,top_asc):
    """ 
    Essa função tem a responsabilidade de encontrar os 10 entregadores mais rapidos e lentos
    1. Pegando as 10 primeiras linhas de cada cidade do dataframe que vão ser os entregadores mas rapidas ou lentas dependo do top_asc
    2. Agrupando os dataframes de cada cidade e criando um unico dataframe  
    3. alterando para int a coluna de tempo de entrega de float para int
    Parâmetros: 
        Input: 
            -df: Dataframe
            -top_asc: modificando o tipo de orde crente ou decrecente para sintetizar se eu que os maiores ou menores valores primeiro 
                    -True: vai trazer os menores valores primeiros que vao ser os entregadore mais rapidos 
                    -False: vai trazer os maiores valores primeiros que vao ser os entregadore mais lentos  
        Output: Dataframe
    """
    df_entreg= (df.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
                        .groupby(['City','Delivery_person_ID'])
                        .mean()
                        .sort_values(['City','Time_taken(min)'],ascending=top_asc)
                        .reset_index())

    df_Met = df_entreg.loc[df_entreg['City'] == 'Metropolitian'].head(10)
    df_Ur = df_entreg.loc[df_entreg['City'] == 'Urban'].head(10)
    df_Semi = df_entreg.loc[df_entreg['City'] == 'Semi-Urban'].head(10)

    df_entreg = pd.concat([df_Met,df_Ur,df_Semi]).reset_index(drop = True)
    df_entreg['Time_taken(min)'] =  df_entreg['Time_taken(min)'].astype(int)
    return df_entreg

def avaliação_media(df,col1=[],group=[],col2=[]):
    """ 
    Essa função tem a responsabilidade de encontrar A avaliação média e o desvio padrão por tipo de tráfego e tambem encontrar as condições climáticas.
    Parâmetros: 
        Input: 
            -df: Dataframe
            -col1: as colunas qua se utiliza nessa funçao
                 ['Delivery_person_Ratings','Road_traffic_density'] utiliza essa colunas se quiser a avaliação media por transito 
                 ['Delivery_person_Ratings','Weatherconditions'] e essa colunas se quiser a avaliação media por clima
            -group: as colunas que serao agrupadas
                 'Road_traffic_density' essa coluna faz a avaliaçao mdia por trânsito
                 'Weatherconditions' e essa coluna faz avaliaçao mdia por clima
            -col2: esses sao os nomes que cada coluna vai ter
                 ['Road_traffic_density','delivery_mean','delivery_std']esse nomes sao para o transito 
                 ['Weatherconditions','delivery_mean','delivery_std']e esses para o clima   
    
        Output: Dataframe
    """
    df_axc= (df.loc[:,col1]
               .groupby(group)
               .agg({'Delivery_person_Ratings':['mean','std']})
               .reset_index())
    df_axc.columns = col2
    return df_axc

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
st.header('Marketplace - Visão Entregadores')

#image_path = r'C:\Users\User\comunidade_DS\FTC_Analisando_dados_Python'
image = Image.open('logo.png' )
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
        
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
            # A maior idade dos entregadores
            maior_idade = df.loc[:,'Delivery_person_Age'].max()
            col1.metric( 'A Maior Idade', maior_idade )
            
        with col2:
            # A menor idade dos entregadores
            menor_idade = df.loc[:,'Delivery_person_Age'].min()
            col2.metric( 'A Menor Idade', menor_idade)
            
        with col3:
            #A Melhor condições de veiculos
            melhor_veiculo = df.loc[:,'Vehicle_condition'].max()
            col3.metric( 'Melhor condicao', int(melhor_veiculo))

            
        with col4:
            #A Pior condições de veiculos
            pior_veiculo = df.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condicao', int(pior_veiculo))
    
    with st.container():
        st.markdown("""___""")
        st.title( 'Avaliacoes' )
        
        col1, col2= st.columns(2, gap='large')
        with col1:
            st.markdown( '##### avaliação media por entregador' )
            df_av_por_entreg_mean = (df.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                                       .groupby('Delivery_person_ID')
                                       .mean()
                                       .reset_index())
            st.dataframe(df_av_por_entreg_mean)

        with col2:
            st.markdown( '##### avaliação media por transito' )
            col1=['Delivery_person_Ratings','Road_traffic_density']
            group = ['Road_traffic_density']
            col2 = ['Road_traffic_density','delivery_mean','delivery_std']
            st.dataframe(avaliação_media(df,col1,group,col2))
            
            
            st.markdown( '##### avaliação media por clima' )
            col1=['Delivery_person_Ratings','Weatherconditions']
            group = ['Weatherconditions']
            col2 = ['Weatherconditions','delivery_mean','delivery_std']
            st.dataframe(avaliação_media(df,col1,group,col2))
    
    with st.container():
        st.markdown("""___""")           
        st.title( 'Velocidade de Entrega' )
        
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.markdown( '##### top entregadores mais rapidos' )
            st.dataframe(top_entregas(df, True))
            
        with col2:
            st.markdown( '##### top entregadores mais lentos' )
            st.dataframe(top_entregas(df, False))

#a forma de rodar o python no terminal
#python visao_empresa.py
#a forma de rodar o streanlit no terminal
###streamlit run visao_emperesa.py###

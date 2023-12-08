import streamlit as st
from PIL import Image

st.set_page_config(
        page_title='Home',
        page_icon='☝🏻')


#image_path = r'C:\Users\User\comunidade_DS\FTC_Analisando_dados_Python'
image = Image.open('logo.png' )

st.sidebar.image(image, width=120)
st.sidebar.markdown('# cury company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write('# cury company Growth Dashboard')
st.markdown(
    """
    Growth Dashboard foi construido para acopanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Isights de geolocalização.
    - visão Entregador:
        - Acompanhamento dos indicadores semanais de crecimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos Restaurantes.
    ### Ask for Help
    - Meu perfil no LinkedIn
        - www.linkedin.com/in/gustavohenriquedossantoss
    
""")

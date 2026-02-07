# app.py
import streamlit as st
import pandas as pd
from bd import inserir_jogo,inserir_desempenho


jogadores = ['Peteka', 'Villa', 'Lucas', 'Chape', 'Arthur', 'Amauri', 'Fabinho','Paulinho', 'Henry']




# Configuração da página
st.set_page_config(
    page_title="Soccer Beer Club",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #1E3A8A; }
    .metric-card { background: #f0f2f6; padding: 20px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:

    st.markdown(
        """
        <style>
        [data-testid="stForm"]{
        border: 2px solid red;
        border-radius: 10px;
        box-shadow: 5px 5px 5px pink;
        color
        }
        </style>
        """, unsafe_allow_html=True
    )
    jogadores = ['Paulinho', 'Felipe', 'Arthur', 'Amauri', 'Lucas', 'Fabinho', 'Guh', 'Baiak', 'Andry', 'Chape', 'Villa', 'Henry', 'Peteka', 'Murilo']
    jogadores_keys = {'Paulinho': 1, 'Felipe': 2, 'Arthur': 3, 'Amauri': 4, 'Lucas': 5, 'Fabinho': 6, 'Guh': 7, 'Baiak': 8, 'Andry': 9, 'Chape': 10, 'Villa': 11, 'Henry': 12, 'Peteka': 13, 'Murilo': 14}

    with st.form("my_form"):
        st.columns([1, 3, 1, 1])  # header visual

        dados = []

        df = pd.DataFrame({
            "Presença": [False] * len(jogadores),
            "Jogador": jogadores,
            "Gols": [0] * len(jogadores),
            "Assistências": [0] * len(jogadores)
        })

        edited_df = st.data_editor(
            df,
            column_config={
                "Presença": st.column_config.CheckboxColumn(label="Presença", default=False),
                "Jogador": st.column_config.TextColumn(disabled=True),
                "Gols": st.column_config.NumberColumn(min_value=0, step=1),
                "Assistências": st.column_config.NumberColumn(min_value=0, step=1)
            },
            hide_index=True,
            use_container_width=True
        )
        so_presentes = edited_df[edited_df['Presença']==True]
        dados = so_presentes.to_dict('records')

        # inserir_desempenho(id_jogador, id_jogo, gols, assistencias,presenca)
 

##########################################################################################################
        cols = st.columns(4)
        dados_jogo = {'data': '', 'scb_gols': '', 'adv_gols': '', 'adv_nome': ''}
        with cols[0]:
            txt_input_1 = st.text_input("Data")
            dados_jogo['data'] = txt_input_1
        with cols[1]:
            txt_input_2 = st.text_input("Placar SBC")
            dados_jogo['scb_gols'] = txt_input_2
        with cols[2]:
            txt_input_1 = st.text_input("Placar Adversário")
            dados_jogo['adv_gols'] = txt_input_1
        with cols[3]:
            txt_input_1 = st.text_input("Nome Adversario")
            dados_jogo['adv_nome'] = txt_input_1
        
        
        submitted = st.form_submit_button("Submit!", width='stretch', type="primary")

        if submitted:

            scb_gols = int(dados_jogo['scb_gols'])
            adv_gols = int(dados_jogo['adv_gols'])
            id_jogo = inserir_jogo(
            dados_jogo['data'],
            scb_gols,
            adv_gols,
            dados_jogo['adv_nome']
            )
            for x in dados:
                inserir_desempenho(
                    jogadores_keys[x['Jogador']],
                    id_jogo,
                    x['Gols'],
                    x['Assistências'],
                    True
                    )
            st.success(f"Jogo inserido com sucesso! ID: {id_jogo}")
        
##################################################################################################

        

# Conteúdo principal
st.markdown('<h1 class="main-header"> Soccer Beer Club</h1>', unsafe_allow_html=True)

# Abas
tab1, tab2, tab3, tab4 = st.tabs(["📈 Visão Geral", "💸 Despesas", "💰 Receitas", "📊 Análises"])

# with tab1:
#     # Seu código para visão geral
#     st.header('teste')
    
# with tab2:
#     # Seu código para despesas
#     st.header('teste')
# with tab3:
#     # Seu código para receitas
#     st.header('teste')
# with tab4:

#     st.header('teste')
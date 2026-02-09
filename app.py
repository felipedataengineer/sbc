# app.py
import streamlit as st
import pandas as pd
from bd import inserir_jogo,inserir_desempenho, atualizar_ranking_historico, get_estatisticas, get_ranking_jogadores,get_ranking_trios_completo,get_ranks_por_rodada
import altair as alt

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

    jogadores = ['Amauri', 'Andry', 'Arthur', 'Baiak', 'Chape', 'Fabinho', 'Felipe', 'Guh', 'Henry', 'Lucas', 'Murilo', 'Paulinho', 'Peteka', 'Villa']
    # jogadores = ['Paulinho', 'Felipe', 'Arthur', 'Amauri', 'Lucas', 'Fabinho', 'Guh', 'Baiak', 'Andry', 'Chape', 'Villa', 'Henry', 'Peteka', 'Murilo']
    jogadores_keys = {'Amauri': 4, 'Andry': 9, 'Arthur': 3, 'Baiak': 8, 'Chape': 10, 'Fabinho': 6, 'Felipe': 2, 'Guh': 7, 'Henry': 12, 'Lucas': 5, 'Murilo': 14, 'Paulinho': 1, 'Peteka': 13, 'Villa': 11}
    # jogadores_keys = {'Paulinho': 1, 'Felipe': 2, 'Arthur': 3, 'Amauri': 4, 'Lucas': 5, 'Fabinho': 6, 'Guh': 7, 'Baiak': 8, 'Andry': 9, 'Chape': 10, 'Villa': 11, 'Henry': 12, 'Peteka': 13, 'Murilo': 14}

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
            
            atualizar_ranking_historico(id_jogo)
            st.success(f"Jogo inserido com sucesso! ID: {id_jogo}")
        
##################################################################################################

        

# Conteúdo principal
st.markdown('<h1 class="main-header"> Soccer Beer Club</h1>', unsafe_allow_html=True)

# Abas
tab1, tab2, tab3 = st.tabs(["📈 Visão Geral", "⚽ Desempenho Individual", "🥉Rank Trio"])

with tab1:
    st.markdown("""
    <style>
    div[data-testid="stMetricValue"] {
        background-color: #2b2b2b;
        border: 3px solid #ff4b4b;
        border-radius: 15px;
        padding: 25px;
        max-width: 800px;
        margin: auto;
        box-shadow: 5px 5px 15px black;
    }
    </style>
    """, unsafe_allow_html=True)
    
    stats = get_estatisticas()

    pct= (((stats['vitorias'] *3) + stats['empates']) /((stats['num_jogos'])*3)) * 100
    gols_media = stats['gols_scb']/ stats['num_jogos']
    gols_media_adv = stats['gols_adv']/ stats['num_jogos']

    with st.container(border=True):
        st.title("Estatísticas SCB")
        col1, col2, col3, col4, col5= st.columns(5)
        col1.metric("Jogos", stats['num_jogos'])
        col2.metric("Vitórias", stats['vitorias'])
        col3.metric("Derrotas", stats['derrotas'])
        col4.metric("Empates", stats['empates'])
        col5.metric("Aproveitamento", f'{pct:.0f}%')
        col1.metric("Media Gols", f'{gols_media}')
        col2.metric("Media Gols Tomados", f'{gols_media_adv}')
        col3.metric("Maior Sequência De Vitórias", stats['maior_seq_vit'])
        col4.metric("Maior Sequência Invicto", stats['maior_seq_invicto'])
        col5.metric("Maior Sequência De Derrota", stats['maior_seq_der'])




with tab2:

    cols = st.columns(3)
    with cols[0]:
        rank = get_ranking_jogadores()
        print(type(rank[0]['var_gols']))
        # Tabela Artilheiro
        df_art = pd.DataFrame([
            {
                'Nome': r['nome'], 
                'Gols': r['gols'], 
                'Rank': r['rank_gols'], 
                'Variação': f'🟢 {r["var_gols"]}' if (r['var_gols'] or 0) > 0 else f'🔴{r["var_gols"]}' if (r['var_gols'] or 0) < 0 else '⚪'
            }
            for r in rank
        ]).sort_values('Rank')
        df_art = df_art.drop(columns=['Rank'])
        df_art.index = range(1, len(df_art) + 1)
        st.subheader("Artilheiros")
        st.dataframe(df_art.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border': '1px solid black'}))

    with cols[1]:
        # Tabela Assistências
        df_ass = pd.DataFrame([
            {'Nome': r['nome'], 'Assistências': r['assistencias'], 'Rank': r['rank_ass'], 'Variação': f'🟢 {r["var_ass"]}' if (r['var_ass'] or 0) > 0 else f'🔴{r["var_ass"]}' if (r['var_ass'] or 0) < 0 else '⚪'}
            for r in rank
        ]).sort_values('Rank')
        df_ass = df_ass.drop(columns=['Rank'])
        df_ass.index = range(1, len(df_ass) + 1)
        st.subheader("Assistências")
        st.dataframe(df_ass.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border': '1px solid black'}))
    with cols[2]:
        # Tabela Presenças
        df_pres = pd.DataFrame([
            {'Nome': r['nome'], 'Presenças': r['presencas'], 'Rank': r['rank_pres'], 'Variação': f'🟢 {r["var_pres"]}' if (r['var_pres'] or 0) > 0 else f'🔴{r["var_pres"]}' if (r['var_pres'] or 0) < 0 else '⚪'}
            for r in rank
        ]).sort_values('Rank')
        df_pres = df_pres.drop(columns=['Rank'])
        df_pres.index = range(1, len(df_pres) + 1)
        st.subheader("Presenças")
        st.dataframe(df_pres.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border': '1px solid black'}))    
    # st.table(product_data, border="horizontal")

    
    def plot_evolucao_ranks(data):
        
        df = pd.DataFrame(data)
        jogadores = df['nome'].unique()
        metricas = ['Gols (Rank)', 'Assistências (Rank)', 'Presenças (Rank)']
        
        jogadores_sel = st.multiselect("Selecione Jogadores", jogadores)
        metrica = st.selectbox("Selecione a Métrica", metricas)
        
        df_jog = df[df['nome'].isin(jogadores_sel)]
        col_map = {'Gols (Rank)': 'rank_gols', 'Assistências (Rank)': 'rank_ass', 'Presenças (Rank)': 'rank_pres'}
        col = col_map[metrica]
        
        chart = alt.Chart(df_jog).mark_line().encode(
            x=alt.X('rodada:O', title='Rodada'),  # Usar :O (ordinal) força valores discretos
            y=alt.Y(f'{col}:Q', 
                title='Posição no Ranking',
                scale=alt.Scale(reverse=True,domain=[1, 14]),
                axis=alt.Axis(tickMinStep=1, format='d')),  # tickMinStep=1 e format='d' para inteiros
            color=alt.Color('nome:N', legend=alt.Legend(title="Jogadores")),
            # color='nome:N',
            tooltip=['rodada:O', 'nome:N', f'{col}:Q']
        )
        
        st.altair_chart(chart, use_container_width=True)

    data2= get_ranks_por_rodada()
    plot_evolucao_ranks(data2)

    
with tab3:

    # Buscar dados completos
    dados_completos = get_ranking_trios_completo()
    df = pd.DataFrame(dados_completos)

    # Converter lista de nomes para string
    df['Trio'] = df['Trio'].apply(lambda x: ', '.join(x))

    # Top 3 vitórias (por taxa)
    top_vitorias = df.sort_values('taxa_vitorias', ascending=False).head(5)
    top_vitorias = top_vitorias[['Trio', 'taxa_vitorias', 'vitorias', 'jogos']]
    # print(top_vitorias)
    # Top 3 derrotas (por taxa) 
    top_derrotas = df[df['jogos'] >= 3].sort_values('taxa_derrotas', ascending=False).head(5)
    top_derrotas = top_derrotas[['Trio', 'taxa_derrotas','derrotas','jogos']]
    print(top_derrotas)
    
    cols = st.columns(2)
    with cols[0]:
          
        df_art = pd.DataFrame(top_vitorias)
        st.subheader("Trio Vitória Certa")
        st.dataframe(df_art.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border': '1px solid black'}))
    
    with cols[1]:
        df_art = pd.DataFrame(top_derrotas)
        st.subheader("Trio Sofrido")
        st.dataframe(df_art.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border': '1px solid black'}))
        

    # with tab4:
# pd.DataFrame()
#     st.header('teste')
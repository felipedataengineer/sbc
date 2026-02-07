from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

load_dotenv()
DB_USERNAME = os.getenv('BD_USER')
encoded_password = os.getenv('BD_PASSWORD')
DB_HOST = os.getenv('BD_HOST')
DB_PORT = os.getenv('BD_PORT')
DB_NAME = os.getenv('BD_NAME')

engine = create_engine(f'postgresql+psycopg2://{DB_USERNAME}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}', pool_pre_ping=True,pool_recycle=300)

#inserir dados jogos
def inserir_jogo(data, scb_gols, adv_gols, adv_nome):
    result = []
    if scb_gols > adv_gols:
        result = 'v'
    elif scb_gols < adv_gols:
        result = 'd'
    else:
        result = 'e'  
        
    sql = text("""INSERT INTO jogos (data, scb_gols, adv_gols, adv_nome, result)
                VALUES(:data, :scb_gols, :adv_gols, :adv_nome, :result)
                RETURNING id_jogo""")
    with engine.begin() as conn:
        # conn.execute(sql, {"data": data, "scb_gols": scb_gols, "adv_gols": adv_gols, "adv_nome": adv_nome, "result": result})
        id_jogo = conn.execute(sql, {"data": data, "scb_gols": scb_gols, "adv_gols": adv_gols, "adv_nome": adv_nome, "result": result}).scalar()
    return id_jogo

# print(inserir_jogo('17/01/2026', 10, 3, 'vino'))

# #inserir performance
def inserir_desempenho(id_jogador, id_jogo, gols, assistencias,presenca):

    sql = text(f"""INSERT INTO desempenho (id_jogador, id_jogo, gols, assistencias, presenca)
                    VALUES(:id_jogador, :id_jogo, :gols, :assistencias, :presenca)
                    """)
    with engine.begin() as conn:
        conn.execute(sql, {'id_jogador':id_jogador, 'id_jogo':id_jogo, 'gols':gols, 'assistencias':assistencias, 'presenca':presenca})
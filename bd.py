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


# funcao para criar snapshot ranking


def atualizar_ranking_historico(id_jogo):
    sql = text("""
        INSERT INTO ranking_historico (
            id_jogo, id_jogador,
            total_gols, pos_gols,
            total_assist, pos_assist,
            total_presenca, pos_presenca
        )
        SELECT
            :id_jogo AS id_jogo,
            d.id_jogador,

            SUM(d.gols) AS total_gols,
            DENSE_RANK() OVER (ORDER BY SUM(d.gols) DESC) AS pos_gols,

            SUM(d.assistencias) AS total_assist,
            DENSE_RANK() OVER (ORDER BY SUM(d.assistencias) DESC) AS pos_assist,

            SUM(CASE WHEN d.presenca = true THEN 1 ELSE 0 END) AS total_presenca,
            DENSE_RANK() OVER (ORDER BY SUM(CASE WHEN d.presenca = true THEN 1 ELSE 0 END) DESC) AS pos_presenca

        FROM desempenho d
        WHERE d.id_jogo <= :id_jogo
        GROUP BY d.id_jogador

        ON CONFLICT (id_jogo, id_jogador)
        DO UPDATE SET
            total_gols = EXCLUDED.total_gols,
            pos_gols = EXCLUDED.pos_gols,
            total_assist = EXCLUDED.total_assist,
            pos_assist = EXCLUDED.pos_assist,
            total_presenca = EXCLUDED.total_presenca,
            pos_presenca = EXCLUDED.pos_presenca;
    """)

    with engine.begin() as conn:
        conn.execute(sql, {"id_jogo": id_jogo})





#visualizar o artilheiro
query = text("""SELECT 
    j.nome,
    SUM(d.gols) AS total_gols
FROM desempenho d
JOIN jogadores j ON j.id_jogador = d.id_jogador
GROUP BY j.nome
ORDER BY total_gols DESC;""")


###############################################
#tudo em uma

def get_estatisticas():
    query = text("""WITH 
    stats_basic AS (
        SELECT 
            COUNT(*) AS num_jogos,
            COUNT(*) FILTER (WHERE result = 'v') AS vitorias,
            COUNT(*) FILTER (WHERE result = 'e') AS empates,
            COUNT(*) FILTER (WHERE result = 'd') AS derrotas,
            SUM(scb_gols) AS gols_scb,
            SUM(adv_gols) AS gols_adv
        FROM jogos
    ),
    max_vit AS (
        SELECT COALESCE(MAX(cnt), 0) AS max_vit
        FROM (
            SELECT COUNT(*) AS cnt
            FROM (
                SELECT rn - ROW_NUMBER() OVER (ORDER BY rn) AS grp
                FROM (
                    SELECT ROW_NUMBER() OVER (ORDER BY data) AS rn
                    FROM jogos WHERE result = 'v'
                ) t
            ) g
            GROUP BY grp
        ) s
    ),
    max_invicto AS (
        SELECT COALESCE(MAX(cnt), 0) AS max_invicto
        FROM (
            SELECT COUNT(*) AS cnt
            FROM (
                SELECT rn - ROW_NUMBER() OVER (ORDER BY rn) AS grp
                FROM (
                    SELECT ROW_NUMBER() OVER (ORDER BY data) AS rn
                    FROM jogos WHERE result != 'd'
                ) t
            ) g
            GROUP BY grp
        ) s
    ),
    max_der AS (
        SELECT COALESCE(MAX(cnt), 0) AS max_der
        FROM (
            SELECT COUNT(*) AS cnt
            FROM (
                SELECT rn - ROW_NUMBER() OVER (ORDER BY rn) AS grp
                FROM (
                    SELECT ROW_NUMBER() OVER (ORDER BY data) AS rn
                    FROM jogos WHERE result = 'd'
                ) t
            ) g
            GROUP BY grp
        ) s
    )
    SELECT 
        sb.num_jogos,
        sb.vitorias,
        sb.empates,
        sb.derrotas,
        sb.gols_scb,
        sb.gols_adv,
        mv.max_vit AS maior_sequencia_vitorias,
        mi.max_invicto AS maior_sequencia_invicto,
        md.max_der AS maior_sequencia_derrotas
    FROM stats_basic sb
    CROSS JOIN max_vit mv
    CROSS JOIN max_invicto mi
    CROSS JOIN max_der md;""")

    with engine.connect() as conn:
        result = conn.execute(query).fetchone()
        return {
            "num_jogos": result.num_jogos,
            "vitorias": result.vitorias,
            "empates": result.empates,
            "derrotas": result.derrotas,
            "gols_scb": result.gols_scb,
            "gols_adv": result.gols_adv,
            "maior_seq_vit": result.maior_sequencia_vitorias,
            "maior_seq_invicto": result.maior_sequencia_invicto,
            "maior_seq_der": result.maior_sequencia_derrotas,
        }


###################################################
#desempenho jogadores

def get_ranking_jogadores():
    sql = text("""-- IDs das rodadas (jogos ordenados por data)
WITH rodadas AS (
    SELECT id_jogo, ROW_NUMBER() OVER (ORDER BY data) AS rodada_num
    FROM jogos
),
ultima_rodada AS (SELECT MAX(id_jogo) AS id FROM jogos),
penultima_rodada AS (
    SELECT id_jogo AS id
    FROM rodadas
    WHERE rodada_num = (SELECT MAX(rodada_num) - 1 FROM rodadas)
)

-- Totais cumulativos e ranks
, cumuls AS (
    SELECT 
        j.id_jogador, jo.id_jogo,
        SUM(d.gols) OVER (PARTITION BY j.id_jogador ORDER BY jo.data ROWS UNBOUNDED PRECEDING) AS gols_tot,
        SUM(d.assistencias) OVER (PARTITION BY j.id_jogador ORDER BY jo.data ROWS UNBOUNDED PRECEDING) AS ass_tot,
        SUM(CASE WHEN d.presenca THEN 1 ELSE 0 END) OVER (PARTITION BY j.id_jogador ORDER BY jo.data ROWS UNBOUNDED PRECEDING) AS pres_tot
    FROM desempenho d
    JOIN jogadores j ON d.id_jogador = j.id_jogador
    JOIN jogos jo ON d.id_jogo = jo.id_jogo
)

-- Ranks por métrica até rodada específica (usando DENSE_RANK para evitar buracos)
, ranks_ultima AS (
    SELECT 
        id_jogador,
        DENSE_RANK() OVER (ORDER BY gols_tot DESC) AS rank_gols,
        DENSE_RANK() OVER (ORDER BY ass_tot DESC) AS rank_ass,
        DENSE_RANK() OVER (ORDER BY pres_tot DESC) AS rank_pres
    FROM cumuls
    WHERE id_jogo = (SELECT id FROM ultima_rodada)
)

, ranks_penultima AS (
    SELECT 
        id_jogador,
        DENSE_RANK() OVER (ORDER BY gols_tot DESC) AS rank_gols_ant,
        DENSE_RANK() OVER (ORDER BY ass_tot DESC) AS rank_ass_ant,
        DENSE_RANK() OVER (ORDER BY pres_tot DESC) AS rank_pres_ant
    FROM cumuls
    WHERE id_jogo = (SELECT id FROM penultima_rodada)
)

-- Resultado final: totais atuais, ranks atuais e variações (positivo = subiu posições)
SELECT 
    j.nome,
    c.gols_tot AS gols,
    c.ass_tot AS assistencias,
    c.pres_tot AS presencas,
    ru.rank_gols,
    COALESCE(rp.rank_gols_ant - ru.rank_gols, 0) AS var_gols,  -- Variação gols
    ru.rank_ass,
    COALESCE(rp.rank_ass_ant - ru.rank_ass, 0) AS var_ass,     -- Variação assist
    ru.rank_pres,
    COALESCE(rp.rank_pres_ant - ru.rank_pres, 0) AS var_pres   -- Variação pres
FROM cumuls c
JOIN jogadores j ON c.id_jogador = j.id_jogador
JOIN ranks_ultima ru ON c.id_jogador = ru.id_jogador
LEFT JOIN ranks_penultima rp ON c.id_jogador = rp.id_jogador
WHERE c.id_jogo = (SELECT id FROM ultima_rodada)
ORDER BY ru.rank_gols, ru.rank_ass, ru.rank_pres;""")
    
    with engine.connect() as conn:
        results = conn.execute(sql).fetchall()
        return [
            {
                "nome": row.nome,
                "gols": row.gols,
                "assistencias": row.assistencias,
                "presencas": row.presencas,
                "rank_gols": row.rank_gols,
                "var_gols": row.var_gols,
                "rank_ass": row.rank_ass,
                "var_ass": row.var_ass,
                "rank_pres": row.rank_pres,
                "var_pres": row.var_pres
            } for row in results
        ]
    


############################################################################
#trio
def get_ranking_trios_completo():
    sql = text("""
        WITH presentes AS (
            SELECT id_jogo, id_jogador
            FROM desempenho
            WHERE presenca = true
        ),
        trios AS (
            SELECT 
                p1.id_jogo,
                p1.id_jogador AS j1,
                p2.id_jogador AS j2,
                p3.id_jogador AS j3
            FROM presentes p1
            JOIN presentes p2 
                ON p1.id_jogo = p2.id_jogo 
               AND p1.id_jogador < p2.id_jogador
            JOIN presentes p3 
                ON p1.id_jogador < p3.id_jogador
               AND p2.id_jogador < p3.id_jogador
               AND p1.id_jogo = p3.id_jogo
        ),
        contagem AS (
            SELECT 
                t.j1, t.j2, t.j3,
                COUNT(*) FILTER (WHERE j.result = 'v') AS vitorias,
                COUNT(*) FILTER (WHERE j.result = 'd') AS derrotas,
                COUNT(*) AS jogos
            FROM trios t
            JOIN jogos j ON j.id_jogo = t.id_jogo
            GROUP BY t.j1, t.j2, t.j3
        )
        SELECT 
            jg1.nome AS jogador1,
            jg2.nome AS jogador2,
            jg3.nome AS jogador3,
            vitorias,
            derrotas,
            jogos,
            ROUND(vitorias::DECIMAL / NULLIF(jogos, 0), 3) AS taxa_vitorias,
            ROUND(derrotas::DECIMAL / NULLIF(jogos, 0), 3) AS taxa_derrotas
        FROM contagem c
        JOIN jogadores jg1 ON jg1.id_jogador = c.j1
        JOIN jogadores jg2 ON jg2.id_jogador = c.j2
        JOIN jogadores jg3 ON jg3.id_jogador = c.j3
        WHERE jogos > 0
    """)
    
    with engine.connect() as conn:
        results = conn.execute(sql).fetchall()

    return [
        {
            "Trio": [row.jogador1, row.jogador2, row.jogador3],
            "vitorias": row.vitorias,
            "derrotas": row.derrotas,
            "jogos": row.jogos,
            "taxa_vitorias": row.taxa_vitorias,
            "taxa_derrotas": row.taxa_derrotas
        }
        for row in results
    ]


def get_ranks_por_rodada():
    sql = text("""
WITH rodadas AS (
    SELECT id_jogo, data, ROW_NUMBER() OVER (ORDER BY data) AS rodada
    FROM jogos
),
cumulativos AS (
    SELECT 
        r.rodada,
        d.id_jogador,
        SUM(d.gols) OVER (PARTITION BY d.id_jogador ORDER BY r.data ROWS UNBOUNDED PRECEDING) AS gols_cum,
        SUM(d.assistencias) OVER (PARTITION BY d.id_jogador ORDER BY r.data ROWS UNBOUNDED PRECEDING) AS ass_cum,
        SUM(CASE WHEN d.presenca THEN 1 ELSE 0 END) OVER (PARTITION BY d.id_jogador ORDER BY r.data ROWS UNBOUNDED PRECEDING) AS pres_cum
    FROM desempenho d
    JOIN rodadas r ON d.id_jogo = r.id_jogo
),
ranks AS (
    SELECT 
        rodada,
        id_jogador,
        DENSE_RANK() OVER (PARTITION BY rodada ORDER BY gols_cum DESC) AS rank_gols,
        DENSE_RANK() OVER (PARTITION BY rodada ORDER BY ass_cum DESC) AS rank_ass,
        DENSE_RANK() OVER (PARTITION BY rodada ORDER BY pres_cum DESC) AS rank_pres
    FROM cumulativos
)
SELECT 
    ranks.rodada,
    j.nome,
    ranks.rank_gols,
    ranks.rank_ass,
    ranks.rank_pres
FROM ranks
JOIN jogadores j ON ranks.id_jogador = j.id_jogador
ORDER BY ranks.rodada, j.nome;
    """)
    with engine.connect() as conn:
        results = conn.execute(sql).fetchall()
        return [
            {
                "rodada": row.rodada,
                "nome": row.nome,
                "rank_gols": row.rank_gols,
                "rank_ass": row.rank_ass,
                "rank_pres": row.rank_pres
            } for row in results
        ]





def teste():
    sql = text("""SELECT 
    j.id_jogo, j.data, j.scb_gols, j.adv_gols, j.adv_nome, j.result,
    jo.nome AS jogador_nome,
    d.gols, d.assistencias, d.presenca
FROM jogos j
LEFT JOIN desempenho d ON j.id_jogo = d.id_jogo
LEFT JOIN jogadores jo ON d.id_jogador = jo.id_jogador
ORDER BY j.data, jo.nome;""")
    with engine.connect() as conn:
            results = conn.execute(sql).fetchall()
            return [
                {
                    "rodada": row.rodada,
                    "nome": row.nome,
                    "rank_gols": row.rank_gols,
                    "rank_ass": row.rank_ass,
                    "rank_pres": row.rank_pres
                } for row in results
            ]
import streamlit as st
import pandas as pd
import psycopg2
from src.bd_conection import get_postgres_connection



def obter_rotas_evacuacao():
    """Obtém todas as rotas de evacuação do banco de dados."""
    conn = get_postgres_connection()
    df_rotas = pd.DataFrame()
    if conn:
        try:
            query = """
            SELECT
                rota_id,
                nome_rota,
                descricao,
                pontos_chave,
                status_rota,
                risco_associado
            FROM rotas_evacuacao
            ORDER BY rota_id;
            """
            df_rotas = pd.read_sql(query, conn)
            # Renomear colunas para melhor exibição no Streamlit
            df_rotas.columns = ['ID', 'Nome da Rota', 'Descrição', 'Pontos Chave', 'Status', 'Risco Associado']
        except psycopg2.Error as e:
            st.error(f"Erro ao obter rotas de evacuação: {e}")
        finally:
            conn.close()
    return df_rotas

def obter_abrigos():
    """Obtém todos os abrigos de emergência do banco de dados."""
    conn = get_postgres_connection()
    df_abrigos = pd.DataFrame()
    if conn:
        try:
            query = """
            SELECT
                abrigo_id,
                nome_abrigo,
                localizacao_geo,
                capacidade_maxima,
                capacidade_atual,
                endereco,
                contato_abrigo,
                status_abrigo
            FROM abrigos
            ORDER BY abrigo_id;
            """
            df_abrigos = pd.read_sql(query, conn)
            df_abrigos.columns = ['ID', 'Nome do Abrigo', 'Localização Geo', 'Capacidade Máxima', 'Capacidade Atual', 'Endereço', 'Contato', 'Status']

            # Extrair Latitude e Longitude para o mapa (se Localização Geo for formatada como "Lat:X, Lon:Y")
            # Isso é uma simplificação. Em um sistema real, você teria colunas separadas para lat/lon ou tipo de dado geográfico.
            df_abrigos['Latitude'] = df_abrigos['Localização Geo'].apply(
                lambda x: float(x.split(',')[0].replace('Lat:', '').strip()) if x and 'Lat:' in x else None
            )
            df_abrigos['Longitude'] = df_abrigos['Localização Geo'].apply(
                lambda x: float(x.split(',')[1].replace('Lon:', '').strip()) if x and 'Lon:' in x else None
            )

        except psycopg2.Error as e:
            st.error(f"Erro ao obter abrigos: {e}")
        finally:
            conn.close()
    return df_abrigos

def obter_dados_mobilidade():
    """Obtém os dados de mobilidade mais recentes do banco de dados."""
    conn = get_postgres_connection()
    df_mobilidade = pd.DataFrame()
    if conn:
        try:
            query = """
            SELECT
                dado_id,
                localizacao_geo,
                nivel_trafego,
                tempo_viagem_estimado,
                timestamp_dado
            FROM dados_mobilidade
            ORDER BY timestamp_dado DESC
            LIMIT 10; -- Pega os 10 dados mais recentes
            """
            df_mobilidade = pd.read_sql(query, conn)
            df_mobilidade.columns = ['ID', 'Localização Geo', 'Nível de Tráfego', 'Tempo Viagem Est.', 'Timestamp']
        except psycopg2.Error as e:
            st.error(f"Erro ao obter dados de mobilidade: {e}")
        finally:
            conn.close()
    return df_mobilidade

# --- Função Principal do Módulo Streamlit ---
def evacuation_system():
    st.header("🗺️ Análise e Tomada de Decisão para Evacuação")
    st.write("Visualize informações críticas para planejar e executar evacuações preventivas.")

    st.subheader("Informações sobre Rotas de Evacuação")
    df_rotas = obter_rotas_evacuacao()
    if not df_rotas.empty:
        st.dataframe(df_rotas)
    else:
        st.info("Nenhuma rota de evacuação cadastrada.")

    st.markdown("---")

    st.subheader("Status dos Abrigos de Emergência")
    df_abrigos = obter_abrigos()
    if not df_abrigos.empty:
        # Exibir tabelas com status
        st.dataframe(df_abrigos[['Nome do Abrigo', 'Capacidade Máxima', 'Capacidade Atual', 'Status', 'Endereço', 'Contato']])

        # Adicionar mapa dos abrigos
        st.write("#### Localização dos Abrigos")
        # Filtrar abrigos com coordenadas válidas para o mapa
        df_map_abrigos = df_abrigos.dropna(subset=['Latitude', 'Longitude'])
        if not df_map_abrigos.empty:
            # st.map espera colunas 'lat' e 'lon' por padrão
            df_map_abrigos = df_map_abrigos.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})
            st.map(df_map_abrigos, zoom=10) # Ajuste o zoom conforme a área da sua cidade
        else:
            st.warning("Não há abrigos com coordenadas geográficas válidas para exibir no mapa.")

    else:
        st.info("Nenhum abrigo de emergência cadastrado.")

    st.markdown("---")

    st.subheader("Condições de Tráfego e Mobilidade Recente")
    df_mobilidade = obter_dados_mobilidade()
    if not df_mobilidade.empty:
        st.dataframe(df_mobilidade)
        # Exemplo de visualização de tráfego no mapa (simplificado)
        st.write("#### Pontos de Tráfego Recentes")
        df_map_mobilidade = df_mobilidade.copy()
        # Extrair Latitude e Longitude para o mapa (se Localização Geo for formatada como "Lat:X, Lon:Y")
        df_map_mobilidade['lat'] = df_map_mobilidade['Localização Geo'].apply(
            lambda x: float(x.split(',')[0].replace('Lat:', '').strip()) if x and 'Lat:' in x else None
        )
        df_map_mobilidade['lon'] = df_map_mobilidade['Localização Geo'].apply(
            lambda x: float(x.split(',')[1].replace('Lon:', '').strip()) if x and 'Lon:' in x else None
        )
        df_map_mobilidade = df_map_mobilidade.dropna(subset=['lat', 'lon'])
        if not df_map_mobilidade.empty:
            st.map(df_map_mobilidade, zoom=10)
        else:
            st.info("Não há dados de mobilidade com coordenadas geográficas válidas para exibir no mapa.")

    else:
        st.info("Nenhum dado de mobilidade recente disponível.")

    st.markdown("---")
    st.caption("Esta interface auxilia na decisão de evacuação, fornecendo um panorama das rotas, abrigos e condições de tráfego.")
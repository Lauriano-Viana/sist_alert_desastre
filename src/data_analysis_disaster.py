import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px # Para gráficos mais interativos e sofisticados
import datetime
from src.bd_conection import get_postgres_connection


# --- Funções para obter dados específicos para análise ---

def obter_dados_leituras_sensores(periodo_dias=30):
    """Obtém leituras de sensores para um período específico."""
    conn = get_postgres_connection()
    df_leituras = pd.DataFrame()
    if conn:
        try:
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=periodo_dias)

            query = f"""
            SELECT
                l.timestamp_leitura,
                s.tipo_sensor,
                s.localizacao_geo,
                l.valor_lido,
                l.unidade_medida
            FROM leituras_sensores l
            JOIN sensores_ambientais s ON l.sensor_id = s.sensor_id
            WHERE l.timestamp_leitura BETWEEN %s AND %s
            ORDER BY l.timestamp_leitura ASC;
            """
            df_leituras = pd.read_sql(query, conn, params=(start_date, end_date))
            df_leituras.columns = ['Timestamp', 'Tipo Sensor', 'Localização', 'Valor Lido', 'Unidade']
            df_leituras['Timestamp'] = pd.to_datetime(df_leituras['Timestamp'])
        except psycopg2.Error as e:
            st.error(f"Erro ao obter dados de leituras de sensores: {e}")
        finally:
            conn.close()
    return df_leituras

def obter_dados_alertas(periodo_dias=30):
    """Obtém dados de alertas para um período específico."""
    conn = get_postgres_connection()
    df_alertas = pd.DataFrame()
    if conn:
        try:
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=periodo_dias)

            query = f"""
            SELECT
                timestamp_alerta,
                tipo_alerta,
                nivel_alerta,
                area_afetada,
                status_alerta
            FROM alertas_desastre
            WHERE timestamp_alerta BETWEEN %s AND %s
            ORDER BY timestamp_alerta ASC;
            """
            df_alertas = pd.read_sql(query, conn, params=(start_date, end_date))
            df_alertas.columns = ['Timestamp', 'Tipo Alerta', 'Nível Alerta', 'Área Afetada', 'Status']
            df_alertas['Timestamp'] = pd.to_datetime(df_alertas['Timestamp'])
        except psycopg2.Error as e:
            st.error(f"Erro ao obter dados de alertas: {e}")
        finally:
            conn.close()
    return df_alertas

def obter_dados_solicitacoes_alocacoes(periodo_dias=30):
    """Obtém dados de solicitações de ajuda e suas alocações para um período específico."""
    conn = get_postgres_connection()
    df_solicitacoes_alocacoes = pd.DataFrame()
    if conn:
        try:
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=periodo_dias)

            query = f"""
            SELECT
                sa.timestamp_solicitacao,
                c.nome_comunidade,
                sa.tipo_ajuda,
                sa.status_solicitacao,
                ar.timestamp_alocacao,
                r.nome_recurso,
                ar.quantidade_alocada,
                ar.status_alocacao AS status_alocacao_recurso
            FROM solicitacoes_ajuda sa
            JOIN comunidades c ON sa.comunidade_id = c.comunidade_id
            LEFT JOIN alocacao_recursos ar ON sa.solicitacao_id = ar.solicitacao_id
            LEFT JOIN recursos r ON ar.recurso_id = r.recurso_id
            WHERE sa.timestamp_solicitacao BETWEEN %s AND %s
            ORDER BY sa.timestamp_solicitacao ASC;
            """
            df_solicitacoes_alocacoes = pd.read_sql(query, conn, params=(start_date, end_date))
            df_solicitacoes_alocacoes.columns = [
                'Data Solicitação', 'Comunidade', 'Tipo Ajuda', 'Status Solicitação',
                'Data Alocação', 'Recurso Alocado', 'Qtd. Alocada', 'Status Alocação Recurso'
            ]
            df_solicitacoes_alocacoes['Data Solicitação'] = pd.to_datetime(df_solicitacoes_alocacoes['Data Solicitação'])
            df_solicitacoes_alocacoes['Data Alocação'] = pd.to_datetime(df_solicitacoes_alocacoes['Data Alocação'])
        except psycopg2.Error as e:
            st.error(f"Erro ao obter dados de solicitações/alocações: {e}")
        finally:
            conn.close()
    return df_solicitacoes_alocacoes

# --- Função Principal do Módulo Streamlit ---
def disaster_data_analysis():
    st.header("📈 Análise de Dados Pós-Desastre")
    st.write("Obtenha insights e visualize tendências a partir dos dados coletados durante e após os eventos de desastre.")

    # Opção de filtro de período
    periodo_dias = st.slider("Selecione o período de análise (dias):", min_value=7, max_value=365, value=30)
    st.markdown("---")

    # --- Análise de Leituras de Sensores ---
    st.subheader("Sensor Data Trends")
    df_leituras = obter_dados_leituras_sensores(periodo_dias)

    if not df_leituras.empty:
        st.write("#### Nível de Água (Leituras ao Longo do Tempo)")
        df_nivel_agua = df_leituras[df_leituras['Tipo Sensor'] == 'Nível de Água']
        if not df_nivel_agua.empty:
            fig_nivel = px.line(df_nivel_agua, x='Timestamp', y='Valor Lido', color='Localização',
                                title='Variação do Nível de Água ao Longo do Tempo',
                                labels={'Valor Lido': 'Nível (m)', 'Timestamp': 'Data/Hora'})
            st.plotly_chart(fig_nivel, use_container_width=True)
        else:
            st.info("Nenhum dado de nível de água disponível para o período selecionado.")

        st.write("#### Volume de Chuva (Leituras ao Longo do Tempo)")
        df_pluviometro = df_leituras[df_leituras['Tipo Sensor'] == 'Pluviômetro']
        if not df_pluviometro.empty:
            fig_chuva = px.bar(df_pluviometro, x='Timestamp', y='Valor Lido', color='Localização',
                               title='Volume de Chuva ao Longo do Tempo',
                               labels={'Valor Lido': 'Chuva (mm/h)', 'Timestamp': 'Data/Hora'})
            st.plotly_chart(fig_chuva, use_container_width=True)
        else:
            st.info("Nenhum dado de pluviômetro disponível para o período selecionado.")
    else:
        st.info("Nenhuma leitura de sensor disponível para o período selecionado.")

    st.markdown("---")

    # --- Análise de Alertas ---
    st.subheader("Alerts Analysis")
    df_alertas = obter_dados_alertas(periodo_dias)

    if not df_alertas.empty:
        st.write("#### Distribuição de Alertas por Nível")
        # Conta a ocorrência de cada nível de alerta
        alert_level_counts = df_alertas['Nível Alerta'].value_counts().reset_index()
        alert_level_counts.columns = ['Nível de Alerta', 'Contagem']
        fig_alert_level = px.bar(alert_level_counts, x='Nível de Alerta', y='Contagem',
                                 title='Número de Alertas por Nível',
                                 color='Nível de Alerta',
                                 category_orders={"Nível de Alerta": ["SEGURO", "BAIXO", "MEDIO", "ALTO", "CRITICO"]})
        st.plotly_chart(fig_alert_level, use_container_width=True)

        st.write("#### Alertas ao Longo do Tempo")
        # Agrupa alertas por dia para visualização de linha
        df_alertas['Data'] = df_alertas['Timestamp'].dt.date
        alerts_daily = df_alertas.groupby(['Data', 'Nível Alerta']).size().reset_index(name='Contagem')
        fig_alerts_time = px.line(alerts_daily, x='Data', y='Contagem', color='Nível Alerta',
                                  title='Alertas Emitidos por Dia',
                                  labels={'Contagem': 'Número de Alertas', 'Data': 'Data'})
        st.plotly_chart(fig_alerts_time, use_container_width=True)
    else:
        st.info("Nenhum alerta disponível para o período selecionado.")

    st.markdown("---")

    # --- Análise de Solicitações de Ajuda e Alocações ---
    st.subheader("Aid Requests and Resource Allocation Analysis")
    df_solicitacoes_alocacoes = obter_dados_solicitacoes_alocacoes(periodo_dias)

    if not df_solicitacoes_alocacoes.empty:
        st.write("#### Status das Solicitações de Ajuda")
        # Conta o status das solicitações
        request_status_counts = df_solicitacoes_alocacoes['Status Solicitação'].value_counts().reset_index()
        request_status_counts.columns = ['Status', 'Contagem']
        fig_request_status = px.pie(request_status_counts, values='Contagem', names='Status',
                                    title='Distribuição de Solicitações por Status')
        st.plotly_chart(fig_request_status, use_container_width=True)

        st.write("#### Tipos de Ajuda Mais Solicitados")
        # Conta os tipos de ajuda mais solicitados
        top_aid_types = df_solicitacoes_alocacoes['Tipo Ajuda'].value_counts().reset_index()
        top_aid_types.columns = ['Tipo de Ajuda', 'Contagem']
        fig_top_aid = px.bar(top_aid_types.head(5), x='Tipo de Ajuda', y='Contagem',
                             title='Top 5 Tipos de Ajuda Solicitados')
        st.plotly_chart(fig_top_aid, use_container_width=True)

        st.write("#### Alocação de Recursos ao Longo do Tempo")
        # Filtra para alocações concretas e agrupa por data
        df_alocacoes_validas = df_solicitacoes_alocacoes.dropna(subset=['Data Alocação', 'Recurso Alocado'])
        if not df_alocacoes_validas.empty:
            df_alocacoes_validas['Data Alocacao Dia'] = df_alocacoes_validas['Data Alocação'].dt.date
            daily_allocations = df_alocacoes_validas.groupby(['Data Alocacao Dia', 'Recurso Alocado'])['Qtd. Alocada'].sum().reset_index()
            fig_alloc_time = px.line(daily_allocations, x='Data Alocacao Dia', y='Qtd. Alocada', color='Recurso Alocado',
                                     title='Recursos Alocados por Dia',
                                     labels={'Qtd. Alocada': 'Quantidade Alocada', 'Data Alocacao Dia': 'Data'})
            st.plotly_chart(fig_alloc_time, use_container_width=True)
        else:
            st.info("Nenhum dado de alocação de recursos disponível para o período selecionado.")

    else:
        st.info("Nenhuma solicitação de ajuda ou alocação de recursos disponível para o período selecionado.")

    st.markdown("---")
    st.caption("Esta análise fornece informações valiosas para avaliação pós-desastre e planejamento futuro.")
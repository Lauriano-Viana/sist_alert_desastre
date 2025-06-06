import psycopg2
import pandas as pd
import streamlit as st
import datetime

from src.bd_conection import get_postgres_connection

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
            if conn: conn.close()
    return df_leituras
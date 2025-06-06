import psycopg2
import pandas as pd
import streamlit as st


# Conexão com o PostgreSQL
def get_postgres_connection():
    # --- Configurações do Banco de Dados PostgreSQL ---
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = "lcv123"
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = 5433
    POSTGRES_DB = "postgres"  
    try:
        connection = psycopg2.connect(
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB
        )
        return connection
    except psycopg2.Error as e:
        st.error(f"Erro ao conectar ao PostgreSQL: {e}")
        return None
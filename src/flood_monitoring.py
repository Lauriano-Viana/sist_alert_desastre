import streamlit as st
import pandas as pd
import random
import datetime
import psycopg2  
from src.bd_conection import get_postgres_connection  # Importando a função de conexão com o banco de dados

# --- Funções de Simulação e Lógica de Monitoramento ---

# Limiares de alerta para nível de água (em metros)
LIMIARES_NIVEL_AGUA = {
    'BAIXO': 2.0,
    'MEDIO': 3.5,
    'ALTO': 5.0,
    'CRITICO': 6.5
}

# Limiares de alerta para volume de chuva (em mm/h)
LIMIARES_CHUVA = {
    'BAIXO': 5,
    'MEDIO': 20,
    'ALTO': 40,
    'CRITICO': 60
}

def simular_leitura_sensor(tipo_sensor):
    """Simula a leitura de um sensor."""
    if tipo_sensor == "Nível de Água":
        leitura = random.uniform(2.5, 6.0)
        return round(leitura, 2)
    elif tipo_sensor == "Pluviômetro":
        leitura = random.uniform(0, 50)
        if random.random() < 0.1:
            leitura = random.uniform(50, 80)
        return round(leitura, 2)
    else:
        return 0.0

def determinar_nivel_alerta(leitura, limiares):
    """Determina o nível de alerta com base na leitura e limiares."""
    if leitura >= limiares['CRITICO']:
        return 'CRITICO'
    elif leitura >= limiares['ALTO']:
        return 'ALTO'
    elif leitura >= limiares['MEDIO']:
        return 'MEDIO'
    elif leitura >= limiares['BAIXO']:
        return 'BAIXO'
    else:
        return 'SEGURO'

def gerar_alerta(tipo_alerta, nivel, valor_lido, unidade, localizacao):
    """Gera uma descrição de alerta."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    descricao = f"Alerta de {tipo_alerta} - Nível {nivel}: {valor_lido} {unidade} detectado em {localizacao}. "

    recomendacao = ""
    if nivel == 'BAIXO':
        recomendacao = "Monitorar a situação e manter-se informado."
    elif nivel == 'MEDIO':
        recomendacao = "Atenção em áreas de risco. Preparar-se para possível evacuação."
    elif nivel == 'ALTO':
        recomendacao = "Evacuação imediata de áreas ribeirinhas e de risco de alagamento. Procure abrigos seguros."
    elif nivel == 'CRITICO':
        recomendacao = "Situação de emergência grave. Evacuação urgente. Siga as orientações das autoridades."
    
    descricao += recomendacao
    return {
        "Tipo": tipo_alerta,
        "Nível": nivel,
        "Valor Lido": f"{valor_lido} {unidade}",
        "Localização": localizacao,
        "Timestamp": timestamp,
        "Recomendação": recomendacao,
        "DescricaoCompleta": descricao
    }

def salvar_leitura_no_bd(sensor_id, valor_lido, unidade_medida, timestamp_leitura):
    """Salva a leitura de um sensor no banco de dados PostgreSQL."""
    conn = get_postgres_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            INSERT INTO LEITURAS_SENSORES (SENSOR_ID, VALOR_LIDO, UNIDADE_MEDIDA, TIMESTAMP_LEITURA)
            VALUES (%s, %s, %s, %s)
            RETURNING LEITURA_ID
            """
            cursor.execute(query, (sensor_id, valor_lido, unidade_medida, timestamp_leitura))
            conn.commit()
            return True
        except psycopg2.Error as e:
            st.error(f"Erro ao salvar leitura no BD: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def salvar_alerta_no_bd(tipo_alerta, nivel_alerta, descricao_alerta, area_afetada, recomendacao):
    """Salva um alerta no banco de dados PostgreSQL."""
    conn = get_postgres_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            INSERT INTO ALERTAS_DESASTRE (TIPO_ALERTA, NIVEL_ALERTA, DESCRICAO_ALERTA, AREA_AFETADA, RECOMENDACAO, TIMESTAMP_ALERTA, STATUS_ALERTA)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, 'ATIVO')
            RETURNING ALERTA_ID
            """
            cursor.execute(query, (tipo_alerta, nivel_alerta, descricao_alerta, area_afetada, recomendacao))
            conn.commit()
            return True
        except psycopg2.Error as e:
            st.error(f"Erro ao salvar alerta no BD: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def obter_sensores_cadastrados():
    """Obtém os sensores cadastrados no banco de dados."""
    conn = get_postgres_connection()
    sensores = []
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT SENSOR_ID, TIPO_SENSOR, DESCRICAO, LOCALIZACAO_GEO FROM SENSORES_AMBIENTAIS ORDER BY SENSOR_ID")
            for row in cursor:
                sensores.append({
                    "SENSOR_ID": row[0],
                    "TIPO_SENSOR": row[1],
                    "DESCRICAO": row[2],
                    "LOCALIZACAO_GEO": row[3]
                })
        except psycopg2.Error as e:
            st.error(f"Erro ao obter sensores do BD: {e}")
        finally:
            cursor.close()
            conn.close()
    return sensores

def cadastrar_novo_sensor(tipo, descricao, localizacao):
    """Cadastra um novo sensor no banco de dados."""
    conn = get_postgres_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            INSERT INTO SENSORES_AMBIENTAIS (TIPO_SENSOR, DESCRICAO, LOCALIZACAO_GEO, STATUS_OPERACIONAL, DATA_INSTALACAO)
            VALUES (%s, %s, %s, 'ATIVO', CURRENT_TIMESTAMP)
            RETURNING SENSOR_ID
            """
            cursor.execute(query, (tipo, descricao, localizacao))
            conn.commit()
            st.success("Sensor cadastrado com sucesso!")
            return True
        except psycopg2.Error as e:
            st.error(f"Erro ao cadastrar sensor: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def obter_historico_leituras():
    """Obtém o histórico de leituras do banco de dados."""
    conn = get_postgres_connection()
    if conn:
        try:
            query = """
            SELECT
                L.TIMESTAMP_LEITURA,
                S.TIPO_SENSOR,
                S.LOCALIZACAO_GEO,
                L.VALOR_LIDO,
                L.UNIDADE_MEDIDA
            FROM LEITURAS_SENSORES L
            JOIN SENSORES_AMBIENTAIS S ON L.SENSOR_ID = S.SENSOR_ID
            ORDER BY L.TIMESTAMP_LEITURA DESC
            LIMIT 100
            """
            df_leituras = pd.read_sql(query, conn)
            df_leituras.columns = ['Timestamp', 'Tipo Sensor', 'Localização', 'Valor Lido', 'Unidade']
            return df_leituras
        except psycopg2.Error as e:
            st.error(f"Erro ao obter histórico de leituras do BD: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()

def obter_historico_alertas():
    """Obtém o histórico de alertas do banco de dados."""
    conn = get_postgres_connection()
    if conn:
        try:
            query = """
            SELECT
                TIMESTAMP_ALERTA,
                TIPO_ALERTA,
                NIVEL_ALERTA,
                AREA_AFETADA,
                RECOMENDACAO,
                STATUS_ALERTA
            FROM ALERTAS_DESASTRE
            ORDER BY TIMESTAMP_ALERTA DESC
            LIMIT 50
            """
            df_alertas = pd.read_sql(query, conn)
            df_alertas.columns = ['Timestamp', 'Tipo', 'Nível', 'Área Afetada', 'Recomendação', 'Status']
            return df_alertas
        except psycopg2.Error as e:
            st.error(f"Erro ao obter histórico de alertas do BD: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()

# --- Função Principal do Módulo Streamlit ---
def monitor_environmental_conditions():
    st.header("💧 Monitoramento Ambiental e Alerta de Inundação")
    st.write("Acompanhe as condições ambientais e receba alertas de inundação em tempo real.")

    # --- Seção para Cadastrar Novos Sensores ---
    st.subheader("➕ Cadastrar Novo Sensor")
    with st.expander("Clique para expandir o formulário de cadastro de sensor"):
        with st.form("form_novo_sensor", clear_on_submit=True):
            tipo_sensor_novo = st.selectbox("Tipo de Sensor:", ["Nível de Água", "Pluviômetro", "Umidade do Solo", "Vento", "Temperatura"])
            localizacao_sensor_novo = st.text_input("Localização Geográfica (ex: Lat:-5.09, Lon:-42.81, Rio Poti - Centro):")
            descricao_sensor_novo = st.text_area("Descrição do Sensor (opcional):")
            submit_button = st.form_submit_button("Cadastrar Sensor")
            if submit_button:
                if tipo_sensor_novo and localizacao_sensor_novo:
                    cadastrar_novo_sensor(tipo_sensor_novo, descricao_sensor_novo, localizacao_sensor_novo)
                else:
                    st.warning("Por favor, preencha o Tipo de Sensor e a Localização.")
    st.markdown("---")

    # --- Obter sensores cadastrados no BD ---
    sensores_cadastrados = obter_sensores_cadastrados()
    if not sensores_cadastrados:
        st.warning("Nenhum sensor cadastrado. Por favor, cadastre um sensor para iniciar o monitoramento.")
        return

    st.subheader("📊 Dados Atuais dos Sensores e Alertas")

    # Layout em colunas para os dados dos sensores
    cols = st.columns(len(sensores_cadastrados))
    alertas_gerados = []

    for i, sensor_info in enumerate(sensores_cadastrados):
        with cols[i]:
            st.metric(label=f"Sensor: {sensor_info['TIPO_SENSOR']} ({sensor_info['LOCALIZACAO_GEO']})", value="Aguardando...")

            # Simular leitura do sensor
            leitura_atual = simular_leitura_sensor(sensor_info['TIPO_SENSOR'])
            unidade = "m" if sensor_info['TIPO_SENSOR'] == "Nível de Água" else "mm/h" if sensor_info['TIPO_SENSOR'] == "Pluviômetro" else ""
            st.metric(label="Valor Atual", value=f"{leitura_atual} {unidade}")

            # Salvar leitura no banco de dados
            if salvar_leitura_no_bd(sensor_info['SENSOR_ID'], leitura_atual, unidade, datetime.datetime.now()):
                st.success(f"Leitura de {sensor_info['TIPO_SENSOR']} salva no BD!")

            # Determinar nível de alerta e gerar alerta se aplicável
            nivel_alerta = 'SEGURO'
            if sensor_info['TIPO_SENSOR'] == "Nível de Água":
                nivel_alerta = determinar_nivel_alerta(leitura_atual, LIMIARES_NIVEL_AGUA)
            elif sensor_info['TIPO_SENSOR'] == "Pluviômetro":
                nivel_alerta = determinar_nivel_alerta(leitura_atual, LIMIARES_CHUVA)

            if nivel_alerta != 'SEGURO':
                alerta = gerar_alerta(sensor_info['TIPO_SENSOR'], nivel_alerta, leitura_atual, unidade, sensor_info['LOCALIZACAO_GEO'])
                st.error(f"🚨 ALERTA: {alerta['Nível']} - {alerta['Tipo']} - {alerta['Recomendação']}")
                alertas_gerados.append(alerta)

                # Salvar alerta no banco de dados
                if salvar_alerta_no_bd(alerta['Tipo'], alerta['Nível'], alerta['DescricaoCompleta'], alerta['Localização'], alerta['Recomendação']):
                    st.success(f"Alerta de {alerta['Tipo']} salvo no BD!")
            else:
                st.info(f"Status: {nivel_alerta}")

    st.markdown("---")

    # --- Histórico de Leituras ---
    st.subheader("🕰️ Histórico Recente de Leituras dos Sensores")
    df_leituras = obter_historico_leituras()
    if not df_leituras.empty:
        st.dataframe(df_leituras)
    else:
        st.info("Nenhuma leitura de sensor registrada ainda.")

    st.markdown("---")

    # --- Histórico de Alertas ---
    st.subheader("🚨 Histórico de Alertas de Desastre")
    df_alertas = obter_historico_alertas()
    if not df_alertas.empty:
        st.dataframe(df_alertas)
    else:
        st.info("Nenhum alerta de desastre registrado ainda.")

    st.markdown("---")
    st.info("As leituras dos sensores e os alertas são atualizados cada vez que a página é recarregada. Para um monitoramento contínuo, considere usar `st.rerun()` ou automatizar a atualização.")
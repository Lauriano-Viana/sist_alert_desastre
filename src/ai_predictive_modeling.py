import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import random
import os
import unidecode
from fpdf import FPDF

# Importações de Machine Learning
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib

# Importar funções de utilidade do novo módulo utils.py
from src.utils import obter_dados_leituras_sensores
from scripts.python.analise_ndwi import analisar_ndwi_com_ml




def obter_dados_historicos_para_ml(periodo_dias=90, intervalo_horas=1):
    """
    Obtém dados históricos de sensores e os prepara para modelagem ML.
    Cria features de chuva acumulada e valores defasados.
    NÃO usa mais dados de CSVs.
    """
    # Usa a função reutilizada de src.utils
    df_raw = obter_dados_leituras_sensores(periodo_dias)
    
    if df_raw.empty:
        st.warning("Não há leituras de sensores disponíveis para o período selecionado.")
        return pd.DataFrame(), None, None, None, None, None

    try:
        # Pivota a tabela para ter tipos de sensor como colunas
        # Combinamos Tipo Sensor e Localização para chaves únicas
        df_raw['Sensor_Key'] = df_raw['Tipo Sensor'] + '_' + df_raw['Localização'].str.replace(' ', '_').str.replace(':', '').str.replace(',', '_').str.replace('-', '_').str.replace('/', '_')

        df_pivot = df_raw.pivot_table(index='Timestamp', columns='Sensor_Key', values='Valor Lido')
        df_pivot = df_pivot.sort_index()

        # Resample para um intervalo regular (ex: 1 hora) e preenche valores ausentes
        df_resampled = df_pivot.resample(f'{intervalo_horas}h').mean()
        df_resampled = df_resampled.ffill().bfill() # Preenche NaNs de resample

        # Engenharia de Features
        # target_col = None
        # for col in df_resampled.columns:
        #     if 'Nível_de_Água' in col: # Procurar por Nível_de_Água em qualquer Sensor_Key
        #         target_col = col
        #         break
        
        target_col = None
        for col in df_resampled.columns:
            col_sem_acento = unidecode.unidecode(col.lower())
            if 'nivel' in col_sem_acento and 'agua' in col_sem_acento:
                target_col = col
                break

        if target_col is None:
            st.warning("Não foram encontrados sensores de 'Nível de Água' para treinar o modelo.")
            return pd.DataFrame(), None, None, None, None, None

        features = []
        for col in df_resampled.columns:
            # Features defasadas de sensores
            if 'Nível_de_Água' in col:
                df_resampled[f'{col}_lag1'] = df_resampled[col].shift(1)
                df_resampled[f'{col}_lag3'] = df_resampled[col].shift(3)
                df_resampled[f'{col}_lag6'] = df_resampled[col].shift(6)
                features.extend([f'{col}_lag1', f'{col}_lag3', f'{col}_lag6'])
            elif 'Pluviômetro' in col:
                df_resampled[f'{col}_acc3h'] = df_resampled[col].rolling(window=3, min_periods=1).sum().shift(1)
                df_resampled[f'{col}_acc6h'] = df_resampled[col].rolling(window=6, min_periods=1).sum().shift(1)
                df_resampled[f'{col}_acc12h'] = df_resampled[col].rolling(window=12, min_periods=1).sum().shift(1)
                features.extend([f'{col}_acc3h', f'{col}_acc6h', f'{col}_acc12h'])
            elif 'Umidade_do_Solo' in col:
                df_resampled[f'{col}_lag1'] = df_resampled[col].shift(1)
                features.append(f'{col}_lag1')
            
        # Definir o TARGET: Nível de água 1 hora no futuro
        horizonte_previsao = 1 
        df_resampled['TARGET_Nivel_Agua_Futuro'] = df_resampled[target_col].shift(-horizonte_previsao)
        
        # Remover linhas com valores NaN que surgiram devido ao shift e preenchimento inicial
        df_final = df_resampled.dropna(subset=['TARGET_Nivel_Agua_Futuro'] + features)

        if df_final.empty:
            st.warning("Dados insuficientes após engenharia de features. Tente aumentar o período de análise ou garantir mais dados nos sensores.")
            return pd.DataFrame(), None, None, None, None, None

        X = df_final[features]
        y = df_final['TARGET_Nivel_Agua_Futuro']
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return X_scaled, y, features, scaler, target_col, df_final 
        
    except Exception as e: # Captura outros erros de Pandas/processamento
        st.error(f"Erro inesperado durante a preparação de dados: {e}")
        return pd.DataFrame(), None, None, None, None, None


# --- Funções para Treinar e Avaliar Modelos (Sem alteração significativa aqui) ---
def treinar_e_avaliar_modelos(X, y):
    """
    Treina e avalia modelos de regressão.
    Retorna os modelos treinados e suas métricas.
    """
    if X is None or y is None or X.shape[0] < 2:
        st.warning("Dados insuficientes para treinamento de modelos.")
        return {}, {}

    test_size_val = 0.2 if X.shape[0] * 0.2 >= 1 else (1 if X.shape[0] > 1 else 0)
    if test_size_val == 0:
        st.warning("Conjunto de dados muito pequeno para dividir em treino/teste. Não é possível avaliar adequadamente.")
        return {}, {}
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size_val, random_state=42)

    models = {
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='mae'),
        'SVM': SVR(kernel='rbf') 
    }

    results = {}
    trained_models = {}

    st.write("Iniciando treinamento e avaliação dos modelos...")
    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            results[name] = {'MAE': round(mae, 2), 'R2': round(r2, 2)}
            trained_models[name] = model
            st.success(f"Modelo {name} treinado e avaliado.")
        except Exception as e:
            st.error(f"Erro ao treinar/avaliar {name}: {e}")
            results[name] = {'MAE': 'Erro', 'R2': 'Erro'}

    return trained_models, results

def gerar_relatorio_pdf(df_resultado):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Relatório de Risco de Inundação", ln=True, align='C')
    pdf.ln(10)

    for coluna in df_resultado.columns:
        valor = df_resultado[coluna].values[0]
        linha = f"{coluna}: {valor}"
        pdf.multi_cell(0, 10, linha)

    output_path = "relatorio_inundacao.pdf"
    pdf.output(output_path)
    return output_path


# --- Função Principal do Módulo Streamlit ---
def predictive_ml():
    st.header("🧠 Modelagem Preditiva e Cenários")
    st.write("Utilize inteligência artificial para prever riscos e simular cenários de desastre.")

    st.info("⚠️ **Aviso:** Os modelos são treinados com dados de sensores históricos. Os resultados são para fins **demonstrativos** e não devem ser usados para decisões reais. Modelos robustos exigem grande volume de dados históricos, validação e otimização rigorosas.")

    # --- Configurações de Dados para Treinamento ---
    st.subheader("⚙️ Configuração de Dados para Treinamento")
    periodo_dias = st.slider("Período de dados históricos para treinamento (dias):", min_value=7, max_value=365, value=90)
    intervalo_horas = st.selectbox("Intervalo de amostragem de dados (horas):", [1, 3, 6, 12], index=0)

    # Botão para carregar e preparar dados
    if st.button("Preparar Dados e Treinar Modelos"):
        with st.spinner("Preparando dados e treinando modelos..."):
            X_scaled, y, features, scaler, target_col, df_final_features = obter_dados_historicos_para_ml(periodo_dias, intervalo_horas)
            
            if X_scaled is not None and y is not None and len(X_scaled) > 0:
                st.session_state['X_scaled'] = X_scaled
                st.session_state['y'] = y
                st.session_state['features'] = features
                st.session_state['scaler'] = scaler
                st.session_state['target_water_level_col'] = target_col
                st.session_state['df_final_features'] = df_final_features

                trained_models, model_results = treinar_e_avaliar_modelos(X_scaled, y)
                st.session_state['trained_models'] = trained_models
                st.session_state['model_results'] = model_results
                
                st.success("Dados preparados e modelos treinados com sucesso!")
                
                st.write("### Desempenho dos Modelos (Dados de Teste)")
                st.dataframe(pd.DataFrame(model_results).T) 
                st.markdown("""
                * **MAE (Mean Absolute Error):** Média da diferença absoluta entre os valores previstos e os reais. Um MAE menor é melhor.
                * **R2 (Coefficient of Determination):** Mede a proporção da variância na variável dependente que é previsível a partir das variáveis independentes. Varia de 0 a 1, onde 1 é um ajuste perfeito.
                """)
                st.write("### Exemplo das Features Utilizadas (Primeiras 5 Linhas):")
                st.dataframe(pd.DataFrame(X_scaled, columns=features).head())

            else:
                st.error("Não foi possível preparar os dados para treinamento. Verifique se há dados suficientes e sensores de nível de água.")
                for key in ['X_scaled', 'y', 'features', 'scaler', 'target_water_level_col', 'trained_models', 'model_results', 'df_final_features']:
                    if key in st.session_state:
                        del st.session_state[key]


    st.markdown("---")

    # --- Seção de Previsão em Tempo Real (usando o último dado disponível) ---
    st.subheader("💧 Previsão de Nível de Água (com Modelo Treinado)")
    
    if 'trained_models' in st.session_state and st.session_state['trained_models']:
        
        st.write("Selecione um modelo treinado para gerar uma previsão com os dados mais recentes.")
        
        model_choice = st.selectbox("Escolha o Modelo para Previsão:", list(st.session_state['trained_models'].keys()))
        selected_model = st.session_state['trained_models'][model_choice]
        scaler = st.session_state['scaler']
        features = st.session_state['features']
        
        df_final_features = st.session_state['df_final_features'] 

        st.write("#### Entrada para Previsão (Últimos Valores Conhecidos)")
        st.info("Os valores padrão são os últimos do conjunto de dados de treinamento. Ajuste para simular condições atuais.")

        last_known_features = df_final_features.iloc[-1][features].to_dict()

        current_features_input = {}
        for feature_name in features:
            default_val = last_known_features.get(feature_name, 0.0) 
            current_features_input[feature_name] = st.number_input(
                f"{feature_name}:",
                value=float(default_val),
                step=0.1,
                key=f"input_pred_{feature_name}"
            )

        input_data_for_prediction = pd.DataFrame([current_features_input])
        input_scaled = scaler.transform(input_data_for_prediction)

        if st.button("Gerar Previsão com Modelo Selecionado"):
            try:
                prediction = selected_model.predict(input_scaled)[0]
                st.success(f"**Previsão de Nível de Água (Modelo {model_choice}):**")
                st.metric(label="Nível de Água Previsto", value=f"{prediction:.2f} m")

                nivel_alerta_previsto = ""
                if prediction >= 6.5: nivel_alerta_previsto = "CRÍTICO - Perigo Iminente!"
                elif prediction >= 5.0: nivel_alerta_previsto = "ALTO - Risco de Inundação Grave!"
                elif prediction >= 3.5: nivel_alerta_previsto = "MÉDIO - Atenção para Alagamentos!"
                elif prediction >= 2.0: nivel_alerta_previsto = "BAIXO - Monitoramento Necessário."
                else: nivel_alerta_previsto = "SEGURO - Nível Normal."
                st.write(f"Contexto de Risco Previsto: **{nivel_alerta_previsto}**")
            except Exception as e:
                st.error(f"Erro ao gerar previsão: {e}")
        
    else:
        st.info("Por favor, clique em 'Preparar Dados e Treinar Modelos' acima para carregar e treinar os modelos.")
    
    st.markdown("---")

    # --- Seção de Simulação com Modelo de ML ---
    st.subheader("🌧️ Simulação de Cenários de Chuva/Inundação com Modelo ML")
    st.markdown("Explore o impacto de diferentes volumes de chuva usando o modelo de previsão treinado.")

    nivel_inicial_cenario = st.number_input("Nível de Água Inicial (m) para o Cenário:", min_value=0.5, max_value=10.0, value=2.0, step=0.1, key="cen_nivel_inicial")
    chuva_total_cenario = st.slider("Volume Total de Chuva no Cenário (mm):", min_value=0, max_value=200, value=50, key="cen_chuva")
    duracao_cenario = st.slider("Duração da Chuva no Cenário (horas):", min_value=1, max_value=48, value=12, key="cen_duracao")

    if st.button("Simular Cenário de Inundação", key="btn_simular_cenario"):
        if 'trained_models' in st.session_state and st.session_state['trained_models']:
            model_choice = list(st.session_state['trained_models'].keys())[0]
            modelo = st.session_state['trained_models'][model_choice]
            scaler = st.session_state['scaler']
            features = st.session_state['features']
            df_final = st.session_state['df_final_features']
            base_features = df_final.iloc[-1][features].to_dict()

            nivel_simulado, risco_simulado, recomendacao_simulada = simular_cenario_inundacao_ml(
                chuva_total_cenario, duracao_cenario, nivel_inicial_cenario,
                modelo, scaler, features, base_features
            )
            st.success(f"**Resultado da Simulação com Modelo {model_choice}:**")
            st.metric(label="Nível de Água Previsto", value=f"{nivel_simulado} m")
            st.write(f"**Risco Previsto:** {risco_simulado}")
            st.info(f"**Recomendação:** {recomendacao_simulada}")
        else:
            st.warning("Treine um modelo primeiro para usar a simulação com ML.")


        
    
    # --- Nova seção: análise de NDWI externo ---
    st.markdown("---")
    st.subheader("🌊 Análise de Imagem NDWI Exportada do GEE")
    st.markdown("Faça upload da imagem NDWI exportada do Google Earth Engine para prever o risco de inundação.")

    if 'trained_models' in st.session_state and st.session_state['trained_models']:
        uploaded_ndwi = st.file_uploader("Faça upload da imagem NDWI (.tif):", type=['tif', 'tiff'])

        if uploaded_ndwi is not None:
            model_choice = list(st.session_state['trained_models'].keys())[0]
            modelo = st.session_state['trained_models'][model_choice]
            scaler = st.session_state['scaler']
            features_base = st.session_state['df_final_features'].iloc[-1][st.session_state['features']].to_dict()

            with open("ndwi_temp.tif", "wb") as f:
                f.write(uploaded_ndwi.read())

            resultado_ndwi = analisar_ndwi_com_ml("ndwi_temp.tif", modelo, scaler, features_base)

            st.success("Análise da imagem NDWI realizada com sucesso!")
            st.dataframe(resultado_ndwi)

            caminho_pdf = gerar_relatorio_pdf(resultado_ndwi)
            with open(caminho_pdf, "rb") as pdf_file:
                st.download_button(
                    label="📄 Baixar Relatório em PDF",
                    data=pdf_file,
                    file_name="relatorio_inundacao.pdf",
                    mime="application/pdf"
                )
    else:
        st.info("Você precisa treinar um modelo primeiro antes de usar a imagem NDWI.")        
        

def simular_cenario_inundacao_ml(chuva_total_mm, duracao_horas, nivel_agua_inicial, modelo, scaler, features, base_features):
    """
    Simula um cenário de inundação usando o modelo de ML treinado.
    Ajusta variáveis de entrada e prevê o nível de água.
    """
    entrada = base_features.copy()

    for f in entrada:
        if 'nivel' in f.lower():
            entrada[f] = nivel_agua_inicial
        elif 'pluvio' in f.lower():
            if 'acc3h' in f:
                entrada[f] = chuva_total_mm * 0.25
            elif 'acc6h' in f:
                entrada[f] = chuva_total_mm * 0.5
            elif 'acc12h' in f:
                entrada[f] = chuva_total_mm

    df_input = pd.DataFrame([entrada])
    input_scaled = scaler.transform(df_input)
    pred = modelo.predict(input_scaled)[0]

    if pred >= 6.5:
        risco = "Desastre Catastrófico"
        recomendacao = "Evacuação total imediata da região."
    elif pred >= 5.0:
        risco = "Inundação Severa"
        recomendacao = "Evacuação de áreas de risco."
    elif pred >= 3.5:
        risco = "Inundação Moderada"
        recomendacao = "Monitoramento contínuo. Atenção às autoridades."
    else:
        risco = "Risco Baixo"
        recomendacao = "Situação normal. Continuar monitoramento."
    return round(pred, 2), risco, recomendacao

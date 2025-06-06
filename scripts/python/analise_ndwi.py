import rasterio
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO

def analisar_ndwi_com_ml(ndwi_path, modelo, scaler, features_base):
    """
    Lê uma imagem NDWI exportada do Google Earth Engine,
    extrai estatísticas e usa modelo ML treinado para estimar risco de inundação.
    
    Parâmetros:
        ndwi_path: caminho do arquivo .tif da imagem NDWI
        modelo: modelo de ML já treinado
        scaler: objeto de normalização (StandardScaler)
        features_base: dicionário com base de features para simulação (última linha de sensores)
    
    Retorna:
        DataFrame com estatísticas e previsão
    """

    # 1. Carregar imagem NDWI (GeoTIFF)
    with rasterio.open(ndwi_path) as src:
        ndwi_array = src.read(1).astype(float)
        ndwi_array[ndwi_array == src.nodata] = np.nan

    # 2. Gerar estatísticas básicas do NDWI
    ndwi_mean = np.nanmean(ndwi_array)
    ndwi_max = np.nanmax(ndwi_array)
    ndwi_min = np.nanmin(ndwi_array)
    ndwi_std = np.nanstd(ndwi_array)

    # Plot NDWI
    plt.figure(figsize=(8, 6))
    plt.imshow(ndwi_array, cmap='Blues')
    plt.colorbar(label='NDWI')
    plt.title('Mapa de NDWI')
    plt.show()

    # 3. Criar entrada para modelo ML (usando features base + NDWI como ajuste)
    entrada = features_base.copy()

    # Exemplo: ajuste de variáveis com base no NDWI
    for f in entrada:
        if 'nivel' in f.lower():
            entrada[f] = ndwi_mean * 10  # arbitrário — pode calibrar com base em dados reais
        elif 'pluvio' in f.lower():
            entrada[f] = ndwi_mean * 50  # aproximação de chuva baseada no NDWI

    # 4. Previsão com ML
    df_input = pd.DataFrame([entrada])
    input_scaled = scaler.transform(df_input)
    pred = modelo.predict(input_scaled)[0]

    # 5. Avaliação do risco
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

    resultado_df = pd.DataFrame({
        'NDWI Médio': [ndwi_mean],
        'Previsão Nível Água (m)': [round(pred, 2)],
        'Classificação de Risco': [risco],
        'Recomendação': [recomendacao]
    })

    return resultado_df

# --- Função para gerar relatório em CSV ---
def gerar_relatorio_csv(df_resultado):
    buffer = BytesIO()
    df_resultado.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer
# 🚨 Sistema Inteligente de Alerta e Apoio a Desastres

Este projeto é um Dashboard interativo desenvolvido em Streamlit, focado na prevenção e resposta a desastres naturais, com ênfase inicial em inundações. Ele integra monitoramento ambiental, tomada de decisão para evacuação, apoio a comunidades isoladas, análise de dados pós-desastre e modelagem preditiva, tudo isso apoiado por um banco de dados PostgreSQL. A aplicação foi concebida para auxiliar autoridades e a população de Teresina, Piauí, Brasil, na gestão de crises.

## ✨ Funcionalidades

O dashboard é dividido em módulos, cada um abordando uma etapa crucial na gestão de desastres:

1.  **Monitoramento Ambiental e Alerta de Inundação (`flood_monitoring.py`)**:
    * Monitora (via simulação e leitura de BD) dados de sensores de nível de água, pluviômetros e umidade do solo.
    * Gera alertas automáticos com base em limiares predefinidos (seguro, baixo, médio, alto, crítico) para chuvas e níveis de água.
    * Permite o cadastro de novos sensores e visualiza o histórico de leituras e alertas.
    * Os dados de leituras e alertas são persistidos em um banco de dados PostgreSQL.

2.  **Análise e Tomada de Decisão para Evacuação (`evacuation_decision.py`)**:
    * Exibe rotas de evacuação predefinidas e seu status (aberta, fechada, bloqueada).
    * Apresenta informações detalhadas sobre abrigos de emergência, incluindo capacidade máxima, capacidade atual e status de ocupação.
    * Visualiza a localização de abrigos e pontos críticos no mapa.
    * Mostra dados recentes de mobilidade e tráfego, auxiliando na escolha das melhores rotas.

3.  **Plataforma de Apoio a Comunidades Isoladas (`community_support.py`)**:
    * Interface para comunidades afetadas registrarem solicitações de ajuda (alimentos, água, resgate, médico, etc.).
    * Permite a visualização e filtragem de todas as solicitações de ajuda por status (pendente, em andamento, concluído, cancelado) e prioridade.
    * Funcionalidade para autoridades atualizarem o status das solicitações e alocarem recursos disponíveis (cestas básicas, barcos de resgate, equipes).
    * Gerencia o estoque de recursos e a alocação para cada solicitação.

4.  **Análise de Dados Pós-Desastre (`data_analysis_disaster.py`)**:
    * Fornece dashboards e gráficos para analisar dados históricos de sensores, alertas, solicitações de ajuda e alocações de recursos.
    * Visualiza tendências de nível de água e volume de chuva ao longo do tempo.
    * Apresenta a distribuição e frequência de alertas emitidos.
    * Analisa os tipos de ajuda mais solicitados e a eficiência da alocação de recursos.
    * Permite filtrar a análise por período (últimos 7 a 365 dias).

5.  **Modelagem Preditiva e Cenários (`ai_predictive_modeling.py`)**:
    * **Treinamento e Avaliação de Modelos de Regressão:** Permite treinar modelos como Random Forest, XGBoost e SVM para prever níveis de água.
    * As variáveis de entrada para os modelos são baseadas em dados históricos de sensores (nível de água defasado, chuva acumulada, umidade do solo defasada).
    * Exibe métricas de desempenho (MAE, R2) para comparar a performance dos modelos treinados.
    * **Previsão Interativa:** Após o treinamento, o usuário pode selecionar um modelo e fornecer entradas (ou usar os últimos dados conhecidos) para obter uma previsão do nível de água futuro e seu contexto de risco.
    * **Simulação de Cenários:** Permite simular o impacto de diferentes volumes e durações de chuva em potenciais níveis de inundação, oferecendo recomendações de risco.

## 🛠️ Tecnologias Utilizadas

* **Python 3.x**
* **Streamlit:** Para a criação da interface do dashboard.
* **Pandas:** Para manipulação e análise de dados.
* **Psycopg2:** Driver Python para conexão com banco de dados PostgreSQL.
* **Scikit-learn:** Biblioteca de Machine Learning (Random Forest, SVM, StandardScaler, etc.).
* **XGBoost:** Biblioteca de Machine Learning para modelos de árvores de decisão impulsionadas.
* **Plotly Express:** Para a geração de gráficos interativos e visualizações de dados.
* **PostgreSQL:** Sistema de Gerenciamento de Banco de Dados Relacional para persistência de dados.

## 🗃️ Estrutura do Banco de Dados

### Principais tabelas:

* **SENSORES_AMBIENTAIS**: Registro de sensores e suas localizações

* **LEITURAS_SENSORES**: Histórico de leituras dos sensores

* **ALERTAS_DESASTRE**: Alertas gerados pelo sistema

* **COMUNIDADES**: Comunidades cadastradas

* **SOLICITACOES_AJUDA**: Pedidos de ajuda das comunidades

* **RECURSOS**: Recursos disponíveis para alocação

* **ALOCACAO_RECURSOS**: Histórico de alocações

## 🤖 Modelos de Machine Learning

### Implementados em ai_predictive_modeling.py:

* **Random Forest**: Para previsão de níveis de água

* **XGBoost**: Alternativa de alto desempenho

* **SVM**: Para comparação de resultados

### Features utilizadas:

* Valores defasados de nível de água

* Chuva acumulada (3h, 6h, 12h)

* Umidade do solo

## ⚙️ Configuração do Ambiente

Siga os passos abaixo para configurar e rodar o projeto em sua máquina local.

### Pré-requisitos

* **Python 3.8+**
* **PostgreSQL** (instalado e rodando)
* **DBeaver** (ou qualquer outro cliente SQL para gerenciar o banco de dados)
* **Bibliotecas listadas** (em requirements.txt)

### 1. Clonar o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd sis_alerta_desastre # ou o nome da pasta do projeto
```

### 2. Configurar o Ambiente Virtual

É altamente recomendável usar um ambiente virtual para gerenciar as dependências do projeto.

```bash
python -m venv venv
source venv/bin/activate # No Linux/macOS
# venv\Scripts\activate # No Windows
```

### 3. Instalar Dependências Python

```bash
pip install -r requirements.txt
```

### 4. Configurar o Banco de Dados PostgreSQL

a.  **Criar o Banco de Dados e Usuário (Opcional, mas recomendado)**:
    Conecte-se ao seu PostgreSQL (como `postgres` ou outro superusuário) e execute os comandos para criar um novo banco de dados e um usuário dedicado, se ainda não tiver:

    ```sql
    CREATE DATABASE seu_banco_de_dados;
    CREATE USER seu_usuario WITH PASSWORD 'sua_senha';
    GRANT ALL PRIVILEGES ON DATABASE seu_banco_de_dados TO seu_usuario;
    ```
    Substitua `seu_banco_de_dados`, `seu_usuario` e `sua_senha` por valores de sua preferência.

b.  **Criar as Tabelas**:
    * No DBeaver, conecte-se ao `seu_banco_de_dados` usando as credenciais do `seu_usuario`.
    * Abra o arquivo `criar_tabelas.sql` (localizado na raiz do projeto ou na pasta `src/`).
    * **Importante:** Se você estiver reexecutando, considere **descomentar as linhas `DROP TABLE ... CASCADE CONSTRAINTS;`** no início do script para limpar quaisquer tabelas existentes e garantir uma recriação limpa.
    * Execute o script `criar_tabelas.sql` por completo.

c.  **Popular as Tabelas com Dados de Exemplo**:
    * Abra o script SQL para população de dados (`popular_tabelas.sql`).
    * **Importante:** Este script insere dados simulados para diversos sensores. Certifique-se de que os `SENSOR_ID`s e seus tipos correspondem aos seus dados na tabela `SENSORES_AMBIENTAIS` (IDs 1, 2, 3 e 4 para Nível de Água, Pluviômetro, Nível de Água e Umidade do Solo, respectivamente).
    

d.  **Configurar Credenciais no Código Python**:
    * Abra o arquivo `src/utils.py`.
    * Atualize as variáveis de conexão com as credenciais do seu banco de dados PostgreSQL:

    ```python
    # src/utils.py
    PG_HOST = "localhost" # ou o IP do seu servidor PostgreSQL
    PG_PORT = 5432
    PG_DATABASE = "seu_banco_de_dados"
    PG_USER = "seu_usuario"
    PG_PASSWORD = "sua_senha"
    ```
    * **É fundamental que essas configurações estejam corretas e sejam consistentes em `src/utils.py`, pois todos os outros módulos (e.g., `flood_monitoring.py`, `community_support.py`, `evacuation_decision.py`, `data_analysis_disaster.py`, `ai_predictive_modeling.py`) reutilizam essas configurações através da importação de `src/utils.py`**.

### 5. Executar a Aplicação Streamlit

Com todas as configurações e banco de dados prontos, execute o dashboard:

```bash
streamlit run dash-gestao-desastres.py # Assumindo que este é seu arquivo principal
```

Isso abrirá a aplicação em seu navegador web padrão (geralmente em `http://localhost:8501`).

## 📂 Estrutura do Projeto

```
.
├── dash-gestao-desastres.py   # Arquivo principal do Streamlit
├── src/
│   |
│   ├── utils.py                  # Funções utilitárias e configuração do BD.
│   ├── flood_monitoring.py       # Módulo de Monitoramento e Alerta.
│   ├── evacuation_decision.py    # Módulo de Tomada de Decisão para Evacuação.
│   ├── community_support.py      # Módulo de Apoio a Comunidades Isoladas.
│   ├── data_analysis_disaster.py # Módulo de Análise de Dados Pós-Desastre
│   └── ai_predictive_modeling.py # Módulo de Modelagem Preditiva e Cenários de IA.
│       
├── scripts/
│   |
│   ├── python/                  
│   |     └── analise_ndwi.py           
│   ├── sql/                    
|         ├── criar_tabelas.sql  
|         └── preencher_bd.sql
|
├── requirements.txt
└── README.md                  
```

🔗 Links


[YOUTUBE](https://youtu.be/MUkx9XVdjXI)


---

## 👨‍💻 Desenvolvido por

Lauriano – Estudante FIAP | Engenharia de Machine Learning  
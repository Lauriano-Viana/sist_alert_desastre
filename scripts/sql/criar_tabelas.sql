-- SQL Script para criação de base de dados PostgreSQL para Sistema de Alerta e Apoio a Desastres
-- COMPATÍVEL COM POSTGRESQL 16

-- 1. Tabela para registrar dados de sensores ambientais (Monitoramento Ambiental)
CREATE TABLE SENSORES_AMBIENTAIS (
    SENSOR_ID         SERIAL PRIMARY KEY,
    TIPO_SENSOR       VARCHAR(50) NOT NULL, -- Ex: "Nível de Água", "Pluviômetro", "Umidade do Solo"
    LOCALIZACAO_GEO   VARCHAR(255),          -- Coordenadas geográficas (latitude, longitude) ou descrição do local
    DESCRICAO         VARCHAR(500),
    STATUS_OPERACIONAL VARCHAR(20) DEFAULT 'ATIVO' NOT NULL CHECK (STATUS_OPERACIONAL IN ('ATIVO', 'INATIVO', 'MANUTENCAO')),
    DATA_INSTALACAO   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela para armazenar leituras dos sensores (Monitoramento Ambiental)
CREATE TABLE LEITURAS_SENSORES (
    LEITURA_ID        SERIAL PRIMARY KEY,
    SENSOR_ID         INTEGER NOT NULL,
    VALOR_LIDO        NUMERIC NOT NULL,
    UNIDADE_MEDIDA    VARCHAR(20),           -- Ex: "m", "mm", "%"
    TIMESTAMP_LEITURA TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT FK_LEITURAS_SENSOR FOREIGN KEY (SENSOR_ID) REFERENCES SENSORES_AMBIENTAIS(SENSOR_ID)
);

-- 3. Tabela para registrar alertas de desastre (Monitoramento Ambiental e Evacuação)
CREATE TABLE ALERTAS_DESASTRE (
    ALERTA_ID         SERIAL PRIMARY KEY,
    TIPO_ALERTA       VARCHAR(50) NOT NULL, -- Ex: "INUNDACAO_MODERADA", "INUNDACAO_GRAVE", "ALERTA_CHUVA_FORTE"
    NIVEL_ALERTA      VARCHAR(20) NOT NULL CHECK (NIVEL_ALERTA IN ('BAIXO', 'MEDIO', 'ALTO', 'CRITICO')),
    DESCRICAO_ALERTA  VARCHAR(1000),
    AREA_AFETADA      VARCHAR(500),          -- Descrição da área ou coordenadas
    RECOMENDACAO      VARCHAR(1000),         -- Ex: "Evacuar áreas de risco", "Procurar abrigo"
    TIMESTAMP_ALERTA  TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    STATUS_ALERTA     VARCHAR(20) DEFAULT 'ATIVO' NOT NULL CHECK (STATUS_ALERTA IN ('ATIVO', 'RESOLVIDO', 'CANCELADO'))
);

-- 4. Tabela para gerenciar comunidades (Plataforma de Apoio a Comunidades Isoladas)
CREATE TABLE COMUNIDADES (
    COMUNIDADE_ID     SERIAL PRIMARY KEY,
    NOME_COMUNIDADE   VARCHAR(100) NOT NULL,
    LOCALIZACAO_GEO   VARCHAR(255),
    POPULACAO_ESTIMADA INTEGER,
    DESCRICAO         VARCHAR(500),
    CONTATO_PRINCIPAL VARCHAR(100)           -- Nome de uma pessoa de contato
);

-- 5. Tabela para registrar solicitações de ajuda de comunidades (Plataforma de Apoio a Comunidades Isoladas)
CREATE TABLE SOLICITACOES_AJUDA (
    SOLICITACAO_ID    SERIAL PRIMARY KEY,
    COMUNIDADE_ID     INTEGER NOT NULL,
    TIPO_AJUDA        VARCHAR(100) NOT NULL, -- Ex: "Alimentos", "Água Potável", "Atendimento Médico", "Resgate"
    DESCRICAO_SOLICITACAO VARCHAR(1000),
    STATUS_SOLICITACAO VARCHAR(20) DEFAULT 'PENDENTE' NOT NULL CHECK (STATUS_SOLICITACAO IN ('PENDENTE', 'EM_ANDAMENTO', 'CONCLUIDO', 'CANCELADO')),
    TIMESTAMP_SOLICITACAO TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    TIMESTAMP_ATUALIZACAO TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIORIDADE        VARCHAR(20) DEFAULT 'MEDIA' NOT NULL CHECK (PRIORIDADE IN ('BAIXA', 'MEDIA', 'ALTA', 'URGENTE')),
    CONSTRAINT FK_SOLICITACAO_COMUNIDADE FOREIGN KEY (COMUNIDADE_ID) REFERENCES COMUNIDADES(COMUNIDADE_ID)
);

-- 6. Tabela para registrar recursos e sua alocação (Apoio a Comunidades Isoladas)
CREATE TABLE RECURSOS (
    RECURSO_ID        SERIAL PRIMARY KEY,
    NOME_RECURSO      VARCHAR(100) NOT NULL, -- Ex: "Kit de Primeiros Socorros", "Barco de Resgate", "Alimentos Enlatados"
    TIPO_RECURSO      VARCHAR(50),           -- Ex: "Equipamento", "Alimento", "Medicamento", "Humano"
    QUANTIDADE_DISPONIVEL INTEGER DEFAULT 0 NOT NULL,
    UNIDADE           VARCHAR(20),           -- Ex: "unidades", "litros", "kg", "pessoas"
    LOCAL_ARMAZENAMENTO VARCHAR(255)
);

-- 7. Tabela para vincular recursos a solicitações de ajuda
CREATE TABLE ALOCACAO_RECURSOS (
    ALOCACAO_ID       SERIAL PRIMARY KEY,
    SOLICITACAO_ID    INTEGER NOT NULL,
    RECURSO_ID        INTEGER NOT NULL,
    QUANTIDADE_ALOCADA INTEGER NOT NULL,
    TIMESTAMP_ALOCACAO TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    STATUS_ALOCACAO   VARCHAR(20) DEFAULT 'PENDENTE' NOT NULL CHECK (STATUS_ALOCACAO IN ('PENDENTE', 'ENVIADO', 'ENTREGUE', 'CANCELADO')),
    CONSTRAINT FK_ALOCACAO_SOLICITACAO FOREIGN KEY (SOLICITACAO_ID) REFERENCES SOLICITACOES_AJUDA(SOLICITACAO_ID),
    CONSTRAINT FK_ALOCACAO_RECURSO FOREIGN KEY (RECURSO_ID) REFERENCES RECURSOS(RECURSO_ID)
);

-- 8. Tabela para informações de evacuação (Análise e Tomada de Decisão para Evacuação)
CREATE TABLE ROTAS_EVACUACAO (
    ROTA_ID           SERIAL PRIMARY KEY,
    NOME_ROTA         VARCHAR(255) NOT NULL,
    DESCRICAO         VARCHAR(1000),
    PONTOS_CHAVE      VARCHAR(2000),         -- Descrição textual ou JSON de pontos de passagem
    STATUS_ROTA       VARCHAR(20) DEFAULT 'ABERTA' NOT NULL CHECK (STATUS_ROTA IN ('ABERTA', 'FECHADA', 'BLOQUEADA')),
    RISCO_ASSOCIADO   VARCHAR(50)            -- Ex: "BAIXO", "MEDIO", "ALTO"
);

-- 9. Tabela para abrigos de emergência (Análise e Tomada de Decisão para Evacuação)
CREATE TABLE ABRIGOS (
    ABRIGO_ID         SERIAL PRIMARY KEY,
    NOME_ABRIGO       VARCHAR(100) NOT NULL,
    LOCALIZACAO_GEO   VARCHAR(255),
    CAPACIDADE_MAXIMA INTEGER,
    CAPACIDADE_ATUAL  INTEGER DEFAULT 0,
    ENDERECO          VARCHAR(255),
    CONTATO_ABRIGO    VARCHAR(100),
    STATUS_ABRIGO     VARCHAR(20) DEFAULT 'DISPONIVEL' NOT NULL CHECK (STATUS_ABRIGO IN ('DISPONIVEL', 'CHEIO', 'FECHADO'))
);

-- 10. Tabela para dados de monitoramento de tráfego/mobilidade (para evacuação)
-- Pode ser alimentada por APIs externas ou simulações
CREATE TABLE DADOS_MOBILIDADE (
    DADO_ID           SERIAL PRIMARY KEY,
    LOCALIZACAO_GEO   VARCHAR(255),
    NIVEL_TRAFEGO     VARCHAR(50),           -- Ex: "BAIXO", "MODERADO", "ALTO", "ENGARRAFADO"
    TEMPO_VIAGEM_ESTIMADO INTEGER,           -- Em minutos
    TIMESTAMP_DADO    TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Índices para melhor desempenho (opcional, mas recomendado para grandes volumes de dados)
CREATE INDEX IDX_LEITURAS_SENSOR_ID ON LEITURAS_SENSORES (SENSOR_ID);
CREATE INDEX IDX_LEITURAS_TIMESTAMP ON LEITURAS_SENSORES (TIMESTAMP_LEITURA);
CREATE INDEX IDX_ALERTAS_TIMESTAMP ON ALERTAS_DESASTRE (TIMESTAMP_ALERTA);
CREATE INDEX IDX_SOLICITACOES_COMUNIDADE ON SOLICITACOES_AJUDA (COMUNIDADE_ID);
CREATE INDEX IDX_SOLICITACOES_STATUS ON SOLICITACOES_AJUDA (STATUS_SOLICITACAO);
CREATE INDEX IDX_ALOCACAO_SOLICITACAO ON ALOCACAO_RECURSOS (SOLICITACAO_ID);
CREATE INDEX IDX_ALOCACAO_RECURSO ON ALOCACAO_RECURSOS (RECURSO_ID);

-- Comentários para as tabelas e colunas (boas práticas)
COMMENT ON TABLE SENSORES_AMBIENTAIS IS 'Armazena informações sobre os sensores ambientais utilizados para monitoramento.';
COMMENT ON COLUMN SENSORES_AMBIENTAIS.TIPO_SENSOR IS 'Tipo do sensor, ex: Nível de Água, Pluviômetro.';
COMMENT ON TABLE LEITURAS_SENSORES IS 'Registra as leituras coletadas pelos sensores ambientais.';
COMMENT ON COLUMN LEITURAS_SENSORES.VALOR_LIDO IS 'Valor da leitura do sensor.';
COMMENT ON TABLE ALERTAS_DESASTRE IS 'Armazena informações sobre os alertas de desastre emitidos.';
COMMENT ON COLUMN ALERTAS_DESASTRE.NIVEL_ALERTA IS 'Nível de severidade do alerta: BAIXO, MEDIO, ALTO, CRITICO.';
COMMENT ON TABLE COMUNIDADES IS 'Detalhes sobre as comunidades que podem ser afetadas ou precisar de apoio.';
COMMENT ON TABLE SOLICITACOES_AJUDA IS 'Registra as solicitações de ajuda feitas pelas comunidades.';
COMMENT ON TABLE RECURSOS IS 'Informações sobre os recursos disponíveis para resposta a desastres.';
COMMENT ON TABLE ALOCACAO_RECURSOS IS 'Associa recursos específicos a solicitações de ajuda.';
COMMENT ON TABLE ROTAS_EVACUACAO IS 'Detalhes sobre rotas de evacuação seguras.';
COMMENT ON TABLE ABRIGOS IS 'Informações sobre abrigos de emergência.';
COMMENT ON TABLE DADOS_MOBILIDADE IS 'Dados sobre o tráfego e mobilidade em áreas afetadas ou rotas de evacuação.';

-- Opcional: Criação de um usuário específico para o aplicativo
/*
CREATE USER disaster_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO disaster_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO disaster_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO disaster_user;
*/
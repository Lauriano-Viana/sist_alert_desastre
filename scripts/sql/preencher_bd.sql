-- SQL Script para popular as tabelas do PostgreSQL para Sistema de Alerta e Apoio a Desastres

-- Inserção de dados em SENSORES_AMBIENTAIS
INSERT INTO SENSORES_AMBIENTAIS (TIPO_SENSOR, LOCALIZACAO_GEO, DESCRICAO, STATUS_OPERACIONAL, DATA_INSTALACAO) VALUES
('Nível de Água', 'Lat:-5.08, Lon:-42.82, Rio Poti - Ponte Estaiada', 'Sensor de nível do Rio Poti próximo à Ponte Estaiada.', 'ATIVO', '2023-01-15 10:00:00'),
('Pluviômetro', 'Lat:-5.07, Lon:-42.79, Bairro São João', 'Pluviômetro na zona leste de Teresina.', 'ATIVO', '2023-02-01 08:30:00'),
('Nível de Água', 'Lat:-5.12, Lon:-42.84, Rio Parnaíba - Centro', 'Sensor de nível do Rio Parnaíba na região central.', 'ATIVO', '2023-03-10 14:00:00'),
('Umidade do Solo', 'Lat:-5.09, Lon:-42.81, Zona Rural - Norte', 'Sensor de umidade do solo em área agrícola.', 'ATIVO', '2023-04-05 09:15:00'),
('Pluviômetro', 'Lat:-5.15, Lon:-42.85, Bairro Esplanada', 'Pluviômetro na zona sul de Teresina.', 'ATIVO', '2023-05-20 11:45:00');

-- Inserção de dados em COMUNIDADES
INSERT INTO COMUNIDADES (NOME_COMUNIDADE, LOCALIZACAO_GEO, POPULACAO_ESTIMADA, DESCRICAO, CONTATO_PRINCIPAL) VALUES
('Comunidade Beira Rio', 'Lat:-5.08, Lon:-42.83', 1500, 'Comunidade residencial às margens do Rio Poti.', 'Maria Silva'),
('Vila Esperança', 'Lat:-5.10, Lon:-42.80', 800, 'Pequena vila em área de risco de alagamento.', 'João Santos'),
('Assentamento Boa Vista', 'Lat:-5.18, Lon:-42.90', 2500, 'Assentamento rural isolado durante inundações.', 'Ana Costa'),
('Residencial Alvorada', 'Lat:-5.05, Lon:-42.75', 1200, 'Novo residencial próximo a córregos sazonais.', 'Pedro Oliveira');

-- Inserção de dados em RECURSOS
INSERT INTO RECURSOS (NOME_RECURSO, TIPO_RECURSO, QUANTIDADE_DISPONIVEL, UNIDADE, LOCAL_ARMAZENAMENTO) VALUES
('Cestas Básicas', 'Alimento', 500, 'unidades', 'Centro de Apoio Municipal'),
('Água Potável (5L)', 'Alimento', 1000, 'litros', 'Depósito Central'),
('Barcos de Resgate', 'Equipamento', 10, 'unidades', 'Base da Defesa Civil'),
('Kits de Primeiros Socorros', 'Medicamento', 200, 'unidades', 'Unidade de Saúde Central'),
('Equipes de Resgate', 'Humano', 5, 'pessoas', 'Corpo de Bombeiros');


-- Inserção de dados em LEITURAS_SENSORES (simulando algumas leituras)
-- Para SENSOR_ID = 1 (Nível de Água - Ponte Estaiada)
INSERT INTO LEITURAS_SENSORES (SENSOR_ID, VALOR_LIDO, UNIDADE_MEDIDA, TIMESTAMP_LEITURA) VALUES
(1, 2.8, 'm', '2024-05-30 08:00:00'),
(1, 3.2, 'm', '2024-05-30 12:00:00'),
(1, 3.8, 'm', '2024-05-30 18:00:00'), -- Nível médio
(1, 4.5, 'm', '2024-05-31 00:00:00'), -- Nível médio/alto
(1, 5.2, 'm', '2024-05-31 06:00:00'); -- Nível alto

-- Para SENSOR_ID = 2 (Pluviômetro - Bairro São João)
INSERT INTO LEITURAS_SENSORES (SENSOR_ID, VALOR_LIDO, UNIDADE_MEDIDA, TIMESTAMP_LEITURA) VALUES
(2, 8.5, 'mm/h', '2024-05-30 09:00:00'),
(2, 25.0, 'mm/h', '2024-05-30 15:00:00'), -- Chuva forte
(2, 45.3, 'mm/h', '2024-05-31 03:00:00'); -- Chuva muito forte

-- Para SENSOR_ID = 3 (Nível de Água - Rio Parnaíba)
INSERT INTO LEITURAS_SENSORES (SENSOR_ID, VALOR_LIDO, UNIDADE_MEDIDA, TIMESTAMP_LEITURA) VALUES
(3, 1.9, 'm', '2024-05-30 07:30:00'),
(3, 2.1, 'm', '2024-05-30 13:00:00');

-- Inserção de dados em ALERTAS_DESASTRE (com base nas leituras simuladas)
INSERT INTO ALERTAS_DESASTRE (TIPO_ALERTA, NIVEL_ALERTA, DESCRICAO_ALERTA, AREA_AFETADA, RECOMENDACAO, TIMESTAMP_ALERTA, STATUS_ALERTA) VALUES
('INUNDACAO_MODERADA', 'MEDIO', 'Nível da água do Rio Poti atingiu limiar de atenção.', 'Lat:-5.08, Lon:-42.82, Região da Ponte Estaiada', 'Atenção em áreas de risco. Preparar-se para possível evacuação.', '2024-05-30 18:05:00', 'ATIVO'),
('ALERTA_CHUVA_FORTE', 'MEDIO', 'Chuva intensa no Bairro São João. Risco de alagamentos.', 'Lat:-5.07, Lon:-42.79, Bairro São João', 'Evitar áreas baixas e passagens alagadas.', '2024-05-30 15:05:00', 'ATIVO'),
('INUNDACAO_GRAVE', 'ALTO', 'Nível crítico do Rio Poti. Áreas ribeirinhas com alto risco.', 'Lat:-5.08, Lon:-42.83, Comunidade Beira Rio', 'Evacuação imediata de áreas ribeirinhas e de risco de alagamento. Procure abrigos seguros.', '2024-05-31 06:10:00', 'ATIVO');

-- Inserção de dados em SOLICITACOES_AJUDA
INSERT INTO SOLICITACOES_AJUDA (COMUNIDADE_ID, TIPO_AJUDA, DESCRICAO_SOLICITACAO, STATUS_SOLICITACAO, TIMESTAMP_SOLICITACAO, TIMESTAMP_ATUALIZACAO, PRIORIDADE) VALUES
(1, 'Água Potável', 'Necessidade urgente de água potável para 500 pessoas.', 'PENDENTE', '2024-05-31 07:00:00', '2024-05-31 07:00:00', 'URGENTE'),
(2, 'Resgate', 'Famílias ilhadas na Vila Esperança, necessitam de resgate imediato.', 'PENDENTE', '2024-05-31 07:30:00', '2024-05-31 07:30:00', 'URGENTE'),
(1, 'Cestas Básicas', 'Solicitação de 100 cestas básicas para a comunidade.', 'EM_ANDAMENTO', '2024-05-31 08:15:00', '2024-06-01 10:00:00', 'ALTA'),
(3, 'Atendimento Médico', 'Pessoas com doenças crônicas no assentamento, acesso difícil.', 'PENDENTE', '2024-05-31 09:00:00', '2024-05-31 09:00:00', 'ALTA');

-- Inserção de dados em ALOCACAO_RECURSOS (alocando recursos para as solicitações)
INSERT INTO ALOCACAO_RECURSOS (SOLICITACAO_ID, RECURSO_ID, QUANTIDADE_ALOCADA, TIMESTAMP_ALOCACAO, STATUS_ALOCACAO) VALUES
(1, 2, 500, '2024-05-31 09:30:00', 'ENVIADO'), -- 500 litros de água para solicitação 1
(2, 3, 2, '2024-05-31 10:00:00', 'PENDENTE'), -- 2 barcos de resgate para solicitação 2
(3, 1, 50, '2024-06-01 10:15:00', 'ENTREGUE'); -- 50 cestas básicas para solicitação 3

-- Inserção de dados em ROTAS_EVACUACAO
INSERT INTO ROTAS_EVACUACAO (NOME_ROTA, DESCRICAO, PONTOS_CHAVE, STATUS_ROTA, RISCO_ASSOCIADO) VALUES
('Rota Rio Poti Norte (Para Abrigo A)', 'Rota principal para evacuação da margem norte do Rio Poti.', 'Ponte Estaiada, Av. Raul Lopes, Abrigo Central', 'ABERTA', 'BAIXO'),
('Rota Vila Esperança (Para Abrigo B)', 'Caminho alternativo para evacuação de áreas de risco.', 'Rua Principal da Vila, BR-343, Ginásio Municipal', 'ABERTA', 'MEDIO'),
('Rota de Contingência Sul', 'Rota de emergência para a zona sul, em caso de bloqueio da rota principal.', 'Estrada Vicinal X, Ponto de Encontro Y', 'FECHADA', 'ALTO');

-- Inserção de dados em ABRIGOS
INSERT INTO ABRIGOS (NOME_ABRIGO, LOCALIZACAO_GEO, CAPACIDADE_MAXIMA, CAPACIDADE_ATUAL, ENDERECO, CONTATO_ABRIGO, STATUS_ABRIGO) VALUES
('Abrigo Central Teresina', 'Lat:-5.09, Lon:-42.81', 1000, 350, 'Rua da Cidadania, 123, Centro', '(86) 99123-4567', 'DISPONIVEL'),
('Ginásio Municipal Sul', 'Lat:-5.11, Lon:-42.86', 500, 100, 'Av. Principal, 456, Esplanada', '(86) 99876-5432', 'DISPONIVEL'),
('Escola Dona Clotilde', 'Lat:-5.07, Lon:-42.78', 200, 0, 'Rua da Educação, 789, São João', '(86) 99345-6789', 'DISPONIVEL');

-- Inserção de dados em DADOS_MOBILIDADE (exemplos hipotéticos)
INSERT INTO DADOS_MOBILIDADE (LOCALIZACAO_GEO, NIVEL_TRAFEGO, TEMPO_VIAGEM_ESTIMADO, TIMESTAMP_DADO) VALUES
('Lat:-5.08, Lon:-42.82, Ponte Estaiada', 'MODERADO', 15, '2024-06-02 10:00:00'),
('Lat:-5.10, Lon:-42.80, Acesso à Vila Esperança', 'ALTO', 45, '2024-06-02 10:15:00'),
('Lat:-5.09, Lon:-42.81, Centro da Cidade', 'BAIXO', 5, '2024-06-02 10:30:00');
-- SQL Script para popular a tabela LEITURAS_SENSORES com dados suficientes para ML
-- Este script irá inserir dados para os últimos 90 dias, a cada hora, para SENSOR_ID 1, 2 e 3.
-- Garanta que os SENSOR_ID 1, 2 e 3 já existam na tabela SENSORES_AMBIENTAIS.

-- Deleta leituras antigas para evitar duplicidade ou conflito, se for rodar múltiplas vezes para teste
-- CUIDADO: Isso apagará todas as leituras existentes!
DELETE FROM LEITURAS_SENSORES WHERE SENSOR_ID IN (1, 2, 3, 4); -- Inclui sensor 4 se ele for de umidade do solo

-- Declaração de variáveis para controle do loop (específico para PL/pgSQL ou DBeaver com script)
-- Para rodar isso no DBeaver, selecione o bloco DO $$...$$ e execute como um único script.
DO $$
DECLARE
    loop_timestamp TIMESTAMP; -- Renomeado para evitar conflito com palavra-chave
    start_time TIMESTAMP := (NOW() - INTERVAL '90 days');
    end_time TIMESTAMP := NOW();
    level_val_1 NUMERIC;
    level_val_3 NUMERIC;
    rain_val_2 NUMERIC;
    soil_humidity_val_4 NUMERIC; -- Assumindo SENSOR_ID 4 é umidade do solo
    last_rain_sum NUMERIC; -- Declarada aqui para ser acessível
BEGIN
    -- Loop para SENSOR_ID = 1 (Nível de Água - Rio Poti - Ponte Estaiada)
    -- Simula flutuações, com alguns picos e descidas.
    loop_timestamp := start_time;
    WHILE loop_timestamp <= end_time LOOP
        -- Simula um padrão de nível de água que oscila, com eventos de pico
        -- Nível base: 2.0 a 3.0
        level_val_1 := 2.0 + (RANDOM() * 1.0);

        -- Adiciona picos simulados de inundação
        IF (EXTRACT(EPOCH FROM (loop_timestamp - start_time)) / 3600)::INT % 100 < 10 THEN -- Pico a cada 100 horas (10% do tempo)
            level_val_1 := level_val_1 + (RANDOM() * 3.5); -- Aumenta para até 5.5-6.5m
        END IF;
        
        -- Garante que não vá abaixo de um mínimo realista
        level_val_1 := GREATEST(level_val_1, 1.5);

        INSERT INTO LEITURAS_SENSORES (SENSOR_ID, VALOR_LIDO, UNIDADE_MEDIDA, TIMESTAMP_LEITURA)
        VALUES (1, ROUND(level_val_1, 2), 'm', loop_timestamp); -- Usando a variável do loop

        loop_timestamp := loop_timestamp + INTERVAL '1 hour';
    END LOOP;

    -- Loop para SENSOR_ID = 2 (Pluviômetro - Bairro São João)
    -- Simula volume de chuva, com períodos de seca e chuvas intensas.
    loop_timestamp := start_time;
    WHILE loop_timestamp <= end_time LOOP
        rain_val_2 := 0.0;
        -- 70% de chance de não chover
        IF RANDOM() > 0.7 THEN
            -- Pequena chance de chuva leve
            IF RANDOM() < 0.8 THEN
                rain_val_2 := RANDOM() * 5.0; -- Chuva leve (0-5 mm/h)
            ELSE
                -- Pequena chance de chuva forte
                rain_val_2 := (RANDOM() * 20.0) + 5.0; -- Chuva moderada a forte (5-25 mm/h)
                IF RANDOM() < 0.1 THEN
                    rain_val_2 := (RANDOM() * 30.0) + 25.0; -- Chuva muito forte (25-55 mm/h)
                END IF;
            END IF;
        END IF;
        
        INSERT INTO LEITURAS_SENSORES (SENSOR_ID, VALOR_LIDO, UNIDADE_MEDIDA, TIMESTAMP_LEITURA)
        VALUES (2, ROUND(rain_val_2, 2), 'mm/h', loop_timestamp); -- Usando a variável do loop

        loop_timestamp := loop_timestamp + INTERVAL '1 hour';
    END LOOP;

    -- Loop para SENSOR_ID = 3 (Nível de Água - Rio Parnaíba - Centro)
    -- Simula um padrão semelhante, mas com níveis ligeiramente diferentes.
    loop_timestamp := start_time;
    WHILE loop_timestamp <= end_time LOOP
        level_val_3 := 1.8 + (RANDOM() * 0.8); -- Nível base: 1.8 a 2.6

        -- Adiciona picos simulados de inundação (menos frequentes ou menos intensos que o sensor 1)
        IF (EXTRACT(EPOCH FROM (loop_timestamp - start_time)) / 3600)::INT % 150 < 5 THEN -- Pico a cada 150 horas
            level_val_3 := level_val_3 + (RANDOM() * 2.0); -- Aumenta para até 3.8-4.6m
        END IF;

        level_val_3 := GREATEST(level_val_3, 1.0);

        INSERT INTO LEITURAS_SENSORES (SENSOR_ID, VALOR_LIDO, UNIDADE_MEDIDA, TIMESTAMP_LEITURA)
        VALUES (3, ROUND(level_val_3, 2), 'm', loop_timestamp); -- Usando a variável do loop

        loop_timestamp := loop_timestamp + INTERVAL '1 hour';
    END LOOP;

    -- Loop para SENSOR_ID = 4 (Umidade do Solo - Zona Rural - Norte)
    -- Simula umidade do solo, que pode variar com a chuva.
    -- (Assumindo que o sensor 4 é umidade do solo, caso contrário, ajuste o ID e o tipo)
    loop_timestamp := start_time;
    WHILE loop_timestamp <= end_time LOOP
        -- Umidade base: 30-60%
        soil_humidity_val_4 := 30.0 + (RANDOM() * 30.0);

        -- Aumenta a umidade se choveu muito recentemente (simplificação)
        -- Busca a chuva das últimas 3 horas (apenas para a simulação, não é uma query complexa)
        -- A variável last_rain_sum já foi declarada no bloco DECLARE principal
        last_rain_sum := 0; -- Inicializa para cada iteração do loop
        
        -- Adicionado um bloco BEGIN/END para garantir que a subconsulta funcione corretamente.
        SELECT COALESCE(SUM(valor_lido), 0) INTO last_rain_sum
        FROM LEITURAS_SENSORES
        WHERE SENSOR_ID = 2
          AND TIMESTAMP_LEITURA BETWEEN (loop_timestamp - INTERVAL '3 hour') AND loop_timestamp;
            
        soil_humidity_val_4 := soil_humidity_val_4 + (last_rain_sum * 0.5); -- Mais chuva = mais umidade
        soil_humidity_val_4 := LEAST(soil_humidity_val_4, 95.0); -- Umidade máxima de 95%
        soil_humidity_val_4 := GREATEST(soil_humidity_val_4, 20.0); -- Umidade mínima de 20%


        INSERT INTO LEITURAS_SENSORES (SENSOR_ID, VALOR_LIDO, UNIDADE_MEDIDA, TIMESTAMP_LEITURA)
        VALUES (4, ROUND(soil_humidity_val_4, 2), '%', loop_timestamp); -- Usando a variável do loop

        loop_timestamp := loop_timestamp + INTERVAL '1 hour';
    END LOOP;

END $$;
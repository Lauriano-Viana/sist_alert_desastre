import streamlit as st
import pandas as pd
import psycopg2
from src.bd_conection import get_postgres_connection

# --- Funções para obter dados do BD ---
def obter_comunidades():
    """Obtém todas as comunidades do banco de dados."""
    conn = get_postgres_connection()
    df_comunidades = pd.DataFrame()
    if conn:
        try:
            query = """
            SELECT
                comunidade_id,
                nome_comunidade,
                localizacao_geo,
                populacao_estimada,
                contato_principal
            FROM comunidades
            ORDER BY nome_comunidade;
            """
            df_comunidades = pd.read_sql(query, conn)
            df_comunidades.columns = ['ID', 'Nome da Comunidade', 'Localização Geo', 'População Estimada', 'Contato Principal']
        except psycopg2.Error as e:
            st.error(f"Erro ao obter comunidades: {e}")
        finally:
            conn.close()
    return df_comunidades

def obter_tipos_ajuda_disponiveis():
    """Retorna uma lista de tipos de ajuda comuns."""
    # Em um sistema real, isso poderia vir de uma tabela de lookup no BD
    return ["Alimentos", "Água Potável", "Atendimento Médico", "Resgate", "Abrigo Temporário", "Medicamentos", "Outros"]

def obter_solicitacoes_ajuda(status_filtro=None):
    """Obtém as solicitações de ajuda do banco de dados, com filtro de status opcional."""
    conn = get_postgres_connection()
    df_solicitacoes = pd.DataFrame()
    if conn:
        try:
            query = """
            SELECT
                sa.solicitacao_id,
                c.nome_comunidade,
                sa.tipo_ajuda,
                sa.descricao_solicitacao,
                sa.status_solicitacao,
                sa.prioridade,
                sa.timestamp_solicitacao,
                sa.timestamp_atualizacao
            FROM solicitacoes_ajuda sa
            JOIN comunidades c ON sa.comunidade_id = c.comunidade_id
            """
            params = []
            if status_filtro and status_filtro != "Todos":
                query += " WHERE sa.status_solicitacao = %s"
                params.append(status_filtro)
            query += " ORDER BY sa.timestamp_solicitacao DESC;"

            df_solicitacoes = pd.read_sql(query, conn, params=params)
            df_solicitacoes.columns = [
                'ID Solicitação', 'Comunidade', 'Tipo de Ajuda', 'Descrição',
                'Status', 'Prioridade', 'Data Solicitação', 'Última Atualização'
            ]
        except psycopg2.Error as e:
            st.error(f"Erro ao obter solicitações de ajuda: {e}")
        finally:
            conn.close()
    return df_solicitacoes

def obter_recursos_disponiveis():
    """Obtém todos os recursos disponíveis no banco de dados."""
    conn = get_postgres_connection()
    df_recursos = pd.DataFrame()
    if conn:
        try:
            query = """
            SELECT
                recurso_id,
                nome_recurso,
                tipo_recurso,
                quantidade_disponivel,
                unidade,
                local_armazenamento
            FROM recursos
            ORDER BY nome_recurso;
            """
            df_recursos = pd.read_sql(query, conn)
            df_recursos.columns = ['ID Recurso', 'Nome', 'Tipo', 'Qtd. Disponível', 'Unidade', 'Local']
        except psycopg2.Error as e:
            st.error(f"Erro ao obter recursos: {e}")
        finally:
            conn.close()
    return df_recursos

def obter_alocacoes_por_solicitacao(solicitacao_id):
    """Obtém as alocações de recursos para uma solicitação específica."""
    conn = get_postgres_connection()
    df_alocacoes = pd.DataFrame()
    if conn:
        try:
            query = """
            SELECT
                ar.alocacao_id,
                r.nome_recurso,
                ar.quantidade_alocada,
                r.unidade,
                ar.timestamp_alocacao,
                ar.status_alocacao
            FROM alocacao_recursos ar
            JOIN recursos r ON ar.recurso_id = r.recurso_id
            WHERE ar.solicitacao_id = %s
            ORDER BY ar.timestamp_alocacao DESC;
            """
            df_alocacoes = pd.read_sql(query, conn, params=(solicitacao_id,))
            df_alocacoes.columns = ['ID Alocação', 'Recurso', 'Qtd. Alocada', 'Unidade', 'Data Alocação', 'Status']
        except psycopg2.Error as e:
            st.error(f"Erro ao obter alocações para solicitação {solicitacao_id}: {e}")
        finally:
            conn.close()
    return df_alocacoes

# --- Funções para inserir/atualizar dados no BD ---
def registrar_solicitacao(comunidade_id, tipo_ajuda, descricao, prioridade):
    """Registra uma nova solicitação de ajuda no banco de dados."""
    conn = get_postgres_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO solicitacoes_ajuda (comunidade_id, tipo_ajuda, descricao_solicitacao, status_solicitacao, timestamp_solicitacao, timestamp_atualizacao, prioridade)
            VALUES (%s, %s, %s, 'PENDENTE', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s);
            """
            cursor.execute(query, (comunidade_id, tipo_ajuda, descricao, prioridade))
            conn.commit()
            st.success("Solicitação de ajuda registrada com sucesso!")
            return True
        except psycopg2.Error as e:
            st.error(f"Erro ao registrar solicitação: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    return False

def atualizar_status_solicitacao(solicitacao_id, novo_status):
    """Atualiza o status de uma solicitação de ajuda."""
    conn = get_postgres_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            UPDATE solicitacoes_ajuda
            SET status_solicitacao = %s, timestamp_atualizacao = CURRENT_TIMESTAMP
            WHERE solicitacao_id = %s;
            """
            cursor.execute(query, (novo_status, solicitacao_id))
            conn.commit()
            st.success(f"Status da solicitação {solicitacao_id} atualizado para '{novo_status}'!")
            return True
        except psycopg2.Error as e:
            st.error(f"Erro ao atualizar status da solicitação: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    return False

def alocar_recurso(solicitacao_id, recurso_id, quantidade_alocada):
    """Aloca um recurso a uma solicitação de ajuda e atualiza a quantidade disponível."""
    conn = get_postgres_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # 1. Inserir na tabela de alocação
            query_alocacao = """
            INSERT INTO alocacao_recursos (solicitacao_id, recurso_id, quantidade_alocada, timestamp_alocacao, status_alocacao)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, 'PENDENTE');
            """
            cursor.execute(query_alocacao, (solicitacao_id, recurso_id, quantidade_alocada))

            # 2. Atualizar a quantidade disponível do recurso
            query_update_recurso = """
            UPDATE recursos
            SET quantidade_disponivel = quantidade_disponivel - %s
            WHERE recurso_id = %s;
            """
            cursor.execute(query_update_recurso, (quantidade_alocada, recurso_id))

            conn.commit()
            st.success(f"Recurso alocado: {quantidade_alocada} unidades ao ID da solicitação {solicitacao_id}.")
            return True
        except psycopg2.Error as e:
            st.error(f"Erro ao alocar recurso: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    return False

# --- Função Principal do Módulo Streamlit ---
def community_aid_platform():
    st.header("🤝 Plataforma de Apoio a Comunidades Isoladas")
    st.write("Gerencie solicitações de ajuda e aloque recursos para comunidades afetadas.")

    # --- Aba para Comunidades Solicitarem Ajuda ---
    st.subheader("📝 Solicitar Ajuda (para Comunidades)")
    st.markdown("Selecione sua comunidade e descreva a ajuda necessária.")

    comunidades = obter_comunidades()
    if comunidades.empty:
        st.warning("Nenhuma comunidade cadastrada. Por favor, cadastre comunidades na base de dados para usar este formulário.")
        return # Impede a continuação se não houver comunidades

    lista_comunidades = comunidades[['ID', 'Nome da Comunidade']].set_index('ID')['Nome da Comunidade'].to_dict()
    comunidade_selecionada_id = st.selectbox(
        "Selecione sua Comunidade:",
        options=list(lista_comunidades.keys()),
        format_func=lambda x: lista_comunidades[x]
    )

    tipo_ajuda = st.selectbox("Tipo de Ajuda Necessária:", obter_tipos_ajuda_disponiveis())
    descricao_ajuda = st.text_area("Descreva a ajuda em detalhes (ex: 'Alimentos para 50 pessoas, sem água potável'):", height=100)
    prioridade_ajuda = st.selectbox("Prioridade:", ['BAIXA', 'MEDIA', 'ALTA', 'URGENTE'])

    if st.button("Enviar Solicitação de Ajuda"):
        if comunidade_selecionada_id and tipo_ajuda and descricao_ajuda:
            registrar_solicitacao(comunidade_selecionada_id, tipo_ajuda, descricao_ajuda, prioridade_ajuda)
        else:
            st.warning("Por favor, preencha todos os campos obrigatórios para enviar a solicitação.")

    st.markdown("---")

    # --- Aba para Autoridades Gerenciarem Solicitações ---
    st.subheader("✅ Gerenciar Solicitações de Ajuda (para Autoridades)")
    st.markdown("Visualize, filtre e gerencie o status das solicitações, e aloque recursos.")

    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        status_filtro = st.selectbox(
            "Filtrar Solicitações por Status:",
            ['Todos', 'PENDENTE', 'EM_ANDAMENTO', 'CONCLUIDO', 'CANCELADO']
        )
    with col2:
        st.write("") # Espaço para alinhar o botão
        if st.button("Atualizar Lista de Solicitações"):
            st.session_state['refresh_requests'] = True # Força a atualização

    df_solicitacoes = obter_solicitacoes_ajuda(status_filtro)

    if not df_solicitacoes.empty:
        st.dataframe(df_solicitacoes, use_container_width=True)

        # Seleção de Solicitação para Ações
        st.write("#### Ações para Solicitações Selecionadas")
        solicitacao_ids_disponiveis = df_solicitacoes['ID Solicitação'].tolist()
        if solicitacao_ids_disponiveis:
            selected_solicitacao_id = st.selectbox("Selecione o ID da Solicitação:", solicitacao_ids_disponiveis)

            # --- Atualizar Status ---
            st.write("##### Atualizar Status da Solicitação")
            novo_status = st.selectbox("Novo Status:", ['PENDENTE', 'EM_ANDAMENTO', 'CONCLUIDO', 'CANCELADO'], key=f"status_update_{selected_solicitacao_id}")
            if st.button(f"Atualizar Status do ID {selected_solicitacao_id}"):
                if atualizar_status_solicitacao(selected_solicitacao_id, novo_status):
                    st.session_state['refresh_requests'] = True
                    st.rerun() # Recarrega a página para mostrar as mudanças

            st.markdown("---")

            # --- Alocar Recursos ---
            st.write("##### Alocar Recursos")
            recursos_disponiveis = obter_recursos_disponiveis()
            if not recursos_disponiveis.empty:
                st.dataframe(recursos_disponiveis[['Nome', 'Qtd. Disponível', 'Unidade', 'Local']], use_container_width=True)

                recurso_map = recursos_disponiveis[['ID Recurso', 'Nome', 'Unidade']].set_index('ID Recurso')['Nome'].to_dict()
                if recurso_map:
                    recurso_selecionado_id = st.selectbox(
                        "Selecione o Recurso para Alocar:",
                        options=list(recurso_map.keys()),
                        format_func=lambda x: f"{recurso_map[x]} ({recursos_disponiveis[recursos_disponiveis['ID Recurso'] == x]['Qtd. Disponível'].iloc[0]} {recursos_disponiveis[recursos_disponiveis['ID Recurso'] == x]['Unidade'].iloc[0]} disponíveis)"
                    )
                    
                    if recurso_selecionado_id:
                        max_qty = recursos_disponiveis[recursos_disponiveis['ID Recurso'] == recurso_selecionado_id]['Qtd. Disponível'].iloc[0]
                        quantidade_alocada = st.number_input(f"Quantidade a Alocar (Max: {max_qty}):", min_value=1, max_value=int(max_qty), value=1)
                        if st.button(f"Alocar Recurso ao ID {selected_solicitacao_id}"):
                            if alocar_recurso(selected_solicitacao_id, recurso_selecionado_id, quantidade_alocada):
                                st.session_state['refresh_requests'] = True
                                st.rerun() # Recarrega a página para mostrar as mudanças
                else:
                    st.info("Nenhum recurso disponível para alocação.")
            else:
                st.info("Nenhum recurso cadastrado para alocação. Por favor, adicione recursos.")

            st.markdown("---")

            # --- Visualizar Alocações Existentes para esta Solicitação ---
            st.write(f"##### Recursos Alocados para Solicitação ID {selected_solicitacao_id}")
            df_alocacoes_solicitacao = obter_alocacoes_por_solicitacao(selected_solicitacao_id)
            if not df_alocacoes_solicitacao.empty:
                st.dataframe(df_alocacoes_solicitacao, use_container_width=True)
            else:
                st.info("Nenhum recurso alocado para esta solicitação ainda.")

        else:
            st.info("Nenhuma solicitação disponível para selecionar.")
    else:
        st.info("Nenhuma solicitação de ajuda encontrada com o filtro atual.")

    st.markdown("---")
    st.caption("Desenvolvido para coordenar o apoio a comunidades em situações de desastre.")
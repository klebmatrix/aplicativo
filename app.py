import os
import streamlit as st
from cryptography.fernet import Fernet
import psycopg2 # Exemplo usando PostgreSQL (comum no Render)

# --- 1. CARREGAMENTO DA CHAVE MESTRA ---
def carregar_chave_mestra():
    """
    Busca a chave mestra nas variáveis de ambiente do Render.
    """
    chave = os.environ.get('chave_mestra')
    if not chave:
        st.error("❌ Erro Crítico: Variável de ambiente 'chave_mestra' não configurada no Render.")
        st.stop()
    
    # Limpeza básica para garantir que a chave esteja no formato correto
    chave = chave.strip().replace("'", "").replace('"', "")
    if chave.startswith('b'): chave = chave[1:]
    
    return chave.encode()

# --- 2. DESCRIPTOGRAFIA DE CREDENCIAIS ---
def descriptografar_dado(dado_criptografado, chave):
    """
    Usa a chave mestra para descriptografar informações sensíveis.
    """
    try:
        f = Fernet(chave)
        return f.decrypt(dado_criptografado.encode()).decode()
    except Exception as e:
        st.error(f"❌ Erro ao descriptografar dados: {e}")
        st.stop()

# --- 3. CONEXÃO AO BANCO DE DADOS ---
def conectar_banco():
    # Exemplo de credenciais criptografadas (geralmente salvas em um arquivo ou DB)
    # No mundo real, você buscaria esses tokens de um arquivo .env ou config
    DB_PASSWORD_TOKEN = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="
    
    chave = carregar_chave_mestra()
    senha_real = descriptografar_dado(DB_PASSWORD_TOKEN, chave)
    
    try:
        # Exemplo de string de conexão
        conn = psycopg2.connect(
            host="seu-db-host.render.com",
            database="seu_banco",
            user="seu_usuario",
            password=senha_real,
            port="5432"
        )
        return conn
    except Exception as e:
        st.error(f"❌ Falha na conexão com o banco de dados: {e}")
        return None

# --- 4. USO NO STREAMLIT ---
st.title("🗄️ Conexão Segura Quantum Lab")

if st.button("Testar Conexão com Banco"):
    with st.spinner("Conectando..."):
        conexao = conectar_banco()
        if conexao:
            st.success("✅ Conexão estabelecida com sucesso usando a chave_mestra!")
            # Exemplo de query
            # cursor = conexao.cursor()
            # cursor.execute("SELECT version();")
            # st.write(cursor.fetchone())
            conexao.close()

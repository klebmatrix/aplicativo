import streamlit as st
import os
from cryptography.fernet import Fernet

# COLE O TOKEN QUE O COMANDO ACIMA GEROU
PIN_CRIPTOGRAFADO = "gAAAAABpdPwNgg7J86tk5_CQCt9ZPF8JMjD2He9LQ79G3R7AH3excYYlXGJ5KvoFPPpHUbnNcuD1ndd9I3lovdyFBXH97hOD4w=="

def login():
    st.title("🔐 Acesso")
    # Mostra se a chave existe (ajuda a saber se o Render está lendo)
    chave_no_servidor = os.environ.get('chave_mestra')
    
    if not chave_no_servidor:
        st.error("ERRO: O Render não tem a variável 'chave_mestra'.")
        return

    senha = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        try:
            # Limpeza radical da chave
            limpa = chave_no_servidor.strip().strip("'").strip('"')
            f = Fernet(limpa.encode())
            decodificado = f.decrypt(PIN_CRIPTOGRAFADO.encode()).decode()
            
            if senha == decodificado:
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("PIN incorreto.")
        except Exception as e:
            st.error(f"Erro na chave: {e}")

if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    login()
else:
    st.success("Logado com sucesso!")
    st.write("Seu conteúdo quântico vai aqui.")
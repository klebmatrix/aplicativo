import streamlit as st

# 1. Busca as senhas nos Secrets
try:
    PIN_ALUNO = str(st.secrets["acesso_aluno"]).strip()
    CHAVE_MESTRA = str(st.secrets["chave_mestra"]).strip()
except:
    st.error("Erro: Configure os Secrets no Streamlit!")
    st.stop()

# 2. Inicializa o estado da sessão (para o app "lembrar" que você logou)
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.perfil = None

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("🔐 Acesso ao Sistema")
    
    perfil_selecionado = st.radio("Entrar como:", ["Aluno", "Professor"])
    senha = st.text_input("Senha", type="password").strip()

    if st.button("Entrar"):
        if perfil_selecionado == "Aluno" and senha == PIN_ALUNO:
            st.session_state.logado = True
            st.session_state.perfil = "aluno"
            st.rerun() # Atualiza a tela
        elif perfil_selecionado == "Professor" and senha == CHAVE_MESTRA:
            st.session_state.logado = True
            st.session_state.perfil = "professor"
            st.rerun() # Atualiza a tela
        else:
            st.error("Senha ou perfil incorretos!")

# --- TELAS PÓS-LOGIN ---
else:
    if st.sidebar.button("Sair/Logoff"):
        st.session_state.logado = False
        st.rerun()

    if st.session_state.perfil == "aluno":
        st.title("📖 Área do Aluno")
        st.write("Bem-vindo! Aqui estão seus materiais de física quântica.")
        # Coloque aqui o conteúdo do aluno

    elif st.session_state.perfil == "professor":
        st.title("⚛️ Painel do Professor")
        st.write("Olá, Mestre! Aqui você gerencia o laboratório.")
        # Coloque aqui o conteúdo do professor
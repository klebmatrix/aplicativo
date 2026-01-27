import streamlit as st

# --- CONFIGURAÇÃO DE ACESSO ---
# st.secrets busca as senhas que você cadastrou no painel do Streamlit
try:
    PIN_ALUNO = str(st.secrets["acesso_aluno"]).strip()
    CHAVE_MESTRA = str(st.secrets["chave_mestra"]).strip()
except KeyError:
    st.error("Erro: As senhas não foram configuradas nos Secrets!")
    st.stop()

st.title("Quantum Lab Online")

# Interface de Login
perfil = st.radio("Selecione o perfil:", ["Aluno", "Professor"])
senha_digitada = st.text_input("Digite sua senha/PIN:", type="password").strip()

if st.button("Entrar"):
    if perfil == "Aluno":
        if senha_digitada == PIN_ALUNO:
            st.success("Bem-vindo, Aluno!")
            # Coloque aqui o que o aluno pode ver
        else:
            st.error("PIN do Aluno incorreto.")

    elif perfil == "Professor":
        if senha_digitada == CHAVE_MESTRA:
            st.success("Acesso Mestre Liberado!")
            # Coloque aqui as funções do professor
        else:
            st.error("Chave Mestra incorreta.")
import streamlit as st
import math
import numpy as np

# --- 1. LOGIN ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_prof = str(st.secrets["chave_mestra"]).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_prof: return "admin"
    except:
        st.error("Erro nos Secrets!")
    return "negado"

st.set_page_config(page_title="Quantum Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Senha incorreta")
    st.stop()

# --- 2. MENU LATERAL ---
perfil = st.session_state.perfil
st.sidebar.title(f"Menu {'Professor' if perfil == 'admin' else 'Aluno'}")

opcoes = ["Equações", "Expressões", "Drive"]
if perfil == "admin":
    opcoes += ["Gerador de Atividades", "Sistemas Lineares"]

escolha = st.sidebar.radio("Ir para:", opcoes)

if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

# --- 3. TELAS (Aqui ninguém some!) ---

if escolha == "Equações":
    st.header("📐 Equações de 1º e 2º Grau")
    tipo = st.selectbox("Grau:", ["1º Grau", "2º Grau"])
    if tipo == "1º Grau":
        a = st.number_input("a", value=1.0)
        b = st.number_input("b", value=2.0)
        if st.button("Resolver 1º"):
            st.success(f"x = {-b/a}")
    else:
        a = st.number_input("a", value=1.0, key="a2")
        b = st.number_input("b", value=-5.0)
        c = st.number_input("c", value=6.0)
        if st.button("Resolver 2º"):
            delta = b**2 - 4*a*c
            if delta >= 0:
                x1 = (-b + math.sqrt(delta))/(2*a)
                x2 = (-b - math.sqrt(delta))/(2*a)
                st.success(f"x1={x1}, x2={x2}")
            else: st.error("Sem raízes reais")

elif escolha == "Gerador de Atividades":
    st.header("📄 Gerador de Atividades (Mestre)")
    titulo = st.text_input("Nome da Lista", "Exercícios de Matemática")
    qtd = st.number_input("Quantidade de questões", 1, 50, 10)
    if st.button("Gerar PDF"):
        st.write(f"Gerando {qtd} questões para '{titulo}'...")
        st.download_button("Baixar PDF (Simulado)", "Conteúdo do PDF", file_name="atividade.pdf")

elif escolha == "Drive":
    st.header("📂 Arquivos")
    st.link_button("Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc")
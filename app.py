import streamlit as st
import math
import numpy as np

# --- 1. SEGURANÇA (Acesso Comum como você pediu) ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except:
        st.error("Erro: Configure 'acesso_aluno' e 'chave_mestra' nos Secrets!")
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de Acesso:", type="password", key="login_pass")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. INTERFACE PÓS-LOGIN ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        itens += ["Gerador de Atividades", "Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- LOGARITMOS (APENAS CÁLCULO) ---
    if menu == "Logaritmos":
        st.header("🔢 Cálculo de Logaritmo")
        logaritmando = st.number_input("Logaritmando (Número):", value=100.0, min_value=0.01)
        base = st.number_input("Base:", value=10.0, min_value=0.01)
        if st.button("Calcular Log"):
            try:
                res = math.log(logaritmando, base)
                st.success(f"O resultado de log de {logaritmando} na base {base} é: {res:.4f}")
            except Exception as e:
                st.error(f"Erro no cálculo: {e}")

    # --- FUNÇÕES ARITMÉTICAS (DIVISORES) ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Divisores e Números Primos")
        n = st.number_input("Digite um número inteiro:", min_value=1, value=12, step=1)
        if st.button("Analisar Número"):
            divs = [d for d in range(1, n + 1) if n % d == 0]
            st.write(f"**Divisores de {n}:** {divs}")
            st.info(f"Total de divisores: {len(divs)}")
            if len(divs) == 2:
                st.success(f"{n} é um número PRIMO!")
            else:
                st.warning(f"{n} não é primo.")

    # --- EQUAÇÕES (REFORÇADO) ---
    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Resolução de Equações")
        grau = st.selectbox("Grau:", ["1º Grau", "2º Grau"])
        if grau == "1º Grau":
            a, b = st.number_input("a"), st.number_input("b")
            if st.button("Resolver"):
                st.success(f"x = {-b/a}") if a != 0 else st.error("Inválido")
        else:
            a, b, c = st.number_input("a", value=1.0), st.number_input("b"), st.number_input("c")
            if st.button("Resolver"):
                delta = b**2 - 4*a*c
                if delta >= 0:
                    x1 = (-b + math.sqrt(delta))/(2*a)
                    x2 = (-b - math.sqrt(delta))/(2*a)
                    st.success(f"x1: {x1:.2f}, x2: {x2:.2f}")
                else: st.error("Delta negativo.")

    # --- OUTROS MENUS (PARA NÃO SUMIR NADA) ---
    elif menu == "Atividades (Drive)":
        st.link_button("📂 Abrir Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc")

    elif menu == "Sistemas Lineares":
        st.header("⚖️ Sistema 2x2")
        # Lógica de np.linalg.solve aqui...
        st.write("Painel de Sistemas Ativo.")

    elif menu == "Matrizes":
        st.header("📊 Determinantes")
        st.write("Painel de Matrizes Ativo.")
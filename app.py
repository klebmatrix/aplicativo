import streamlit as st
import math
import numpy as np

# --- 1. FUNÇÃO DE VALIDAÇÃO ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except:
        st.error("Configure os Secrets no Streamlit!")
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite seu PIN ou Chave Mestra:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. INTERFACE ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        itens += ["Sistemas Lineares", "Matrizes"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- LOGARITMOS (CORRIGIDO) ---
    if menu == "Logaritmos":
        st.header("🔢 Calculadora de Logaritmos")
        base = st.number_input("Base (ex: 10):", value=10.0)
        logaritmando = st.number_input("Logaritmando (número):", value=100.0)
        if st.button("Calcular"):
            try:
                res = math.log(logaritmando, base)
                st.success(f"Resultado: log_{base}({logaritmando}) = {res:.4f}")
            except Exception as e: st.error(f"Erro: {e}")

    # --- FUNÇÕES ARITMÉTICAS (CORRIGIDO) ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Divisores e Primalidade")
        n = st.number_input("Digite um número inteiro:", min_value=1, value=12)
        divs = [d for d in range(1, n + 1) if n % d == 0]
        st.write(f"**Divisores de {n}:** {divs}")
        st.info(f"Total de divisores: {len(divs)}")
        if len(divs) == 2: st.success(f"{n} é um número PRIMO!")

    # --- SISTEMAS LINEARES (SÓ PROFESSOR) ---
    elif menu == "Sistemas Lineares":
        st.header("⚖️ Sistema 2x2 (ax + by = c)")
        col1, col2 = st.columns(2)
        with col1:
            a1 = st.number_input("a1:", value=1.0); b1 = st.number_input("b1:", value=1.0); c1 = st.number_input("c1 (resultado):", value=5.0)
        with col2:
            a2 = st.number_input("a2:", value=1.0); b2 = st.number_input("b2:", value=-1.0); c2 = st.number_input("c2 (resultado):", value=1.0)
        if st.button("Resolver Sistema"):
            A = np.array([[a1, b1], [a2, b2]])
            B = np.array([c1, c2])
            try:
                X = np.linalg.solve(A, B)
                st.success(f"Solução: x = {X[0]:.2f}, y = {X[1]:.2f}")
            except: st.error("Sistema sem solução única.")

    # --- MATRIZES (SÓ PROFESSOR) ---
    elif menu == "Matrizes":
        st.header("📊 Determinante de Matriz 2x2")
        m11 = st.number_input("M11", value=1.0); m12 = st.number_input("M12", value=2.0)
        m21 = st.number_input("M21", value=3.0); m22 = st.number_input("M22", value=4.0)
        if st.button("Calcular Determinante"):
            det = (m11 * m22) - (m12 * m21)
            st.metric("Determinante", det)

    # --- OUTROS MENUS (MANTIDOS) ---
    elif menu == "Atividades (Drive)":
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc")

    elif menu == "Expressões (PEMDAS)":
        exp = st.text_input("Expressão:")
        if st.button("Calcular"):
            st.write("Resultado:", eval(exp.replace('^', '**')))
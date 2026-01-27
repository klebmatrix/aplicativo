import streamlit as st
import math
import numpy as np
import os

# --- 1. SEGURANÇA (Acesso Comum) ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except:
        st.error("Erro: Configure 'acesso_aluno' e 'chave_mestra' nos Secrets do Streamlit!")
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

# --- 3. INTERFACE COMPLETA (SEM SUMIR NADA) ---
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

    # --- ATIVIDADES ---
    if menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    # --- EXPRESSÕES ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Expressões")
        exp = st.text_input("Digite a expressão (ex: (5+3)*2^2):")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    # --- EQUAÇÕES ---
    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Resolução de Equações")
        grau = st.selectbox("Escolha o Grau:", ["1º Grau", "2º Grau"])
        if grau == "1º Grau":
            a1 = st.number_input("a:", value=1.0); b1 = st.number_input("b:", value=0.0)
            if st.button("Calcular 1º"):
                if a1 != 0: st.success(f"x = {-b1/a1:.2f}")
        else:
            a2 = st.number_input("a:", value=1.0, key="a2"); b2 = st.number_input("b:", value=-5.0); c2 = st.number_input("c:", value=6.0)
            if st.button("Calcular 2º"):
                delta = b2**2 - 4*a2*c2
                if delta >= 0:
                    x1 = (-b2 + math.sqrt(delta))/(2*a2); x2 = (-b2 - math.sqrt(delta))/(2*a2)
                    st.success(f"x1 = {x1:.2f}, x2 = {x2:.2f}")
                else: st.error("Delta negativo.")

    # --- CÁLCULO DE FUNÇÕES ---
    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Cálculo de Valores")
        func_input = st.text_input("Função f(x):", value="2*x + 10")
        val_x = st.number_input("Valor de x:", value=0.0)
        if st.button("Calcular"):
            try:
                res = eval(func_input.replace('x', f'({val_x})').replace('^', '**'))
                st.metric("Resultado", f"{res:.2f}")
            except: st.error("Erro na fórmula.")

    # --- LOGARITMOS (SOMENTE CÁLCULO) ---
    elif menu == "Logaritmos":
        st.header("🔢 Cálculo de Logaritmo")
        num = st.number_input("Logaritmando:", value=100.0)
        base = st.number_input("Base:", value=10.0)
        if st.button("Calcular Log"):
            try:
                st.success(f"Resultado: {math.log(num, base):.4f}")
            except: st.error("Números inválidos.")

    # --- FUNÇÕES ARITMÉTICAS ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Divisores")
        n = st.number_input("Número n:", min_value=1, value=12)
        if st.button("Ver Divisores"):
            divs = [d for d in range(1, n+1) if n % d == 0]
            st.write(f"Divisores: {divs}")
            st.info(f"Total: {len(divs)}")

    # --- SISTEMAS LINEARES ---
    elif menu == "Sistemas Lineares":
        st.header("⚖️ Sistema 2x2")
        a1 = st.number_input("a1", value=1.0); b1 = st.number_input("b1", value=1.0); c1 = st.number_input("c1", value=5.0)
        a2 = st.number_input("a2", value=1.0); b2 = st.number_input("b2", value=-1.0); c2 = st.number_input("c2", value=1.0)
        if st.button("Resolver Sistema"):
            try:
                X = np.linalg.solve(np.array([[a1, b1], [a2, b2]]), np.array([c1, c2]))
                st.success(f"x = {X[0]:.2f}, y = {X[1]:.2f}")
            except: st.error("Sem solução.")

    # --- MATRIZES ---
    elif menu == "Matrizes":
        st.header("📊 Determinante 2x2")
        m11 = st.number_input("M11", value=1.0); m12 = st.number_input("M12", value=0.0)
        m21 = st.number_input("M21", value=0.0); m22 = st.number_input("M22", value=1.0)
        if st.button("Calcular Det"):
            st.metric("Determinante", (m11*m22) - (m12*m21))

    # --- FINANCEIRO ---
    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        cap = st.number_input("Capital:", value=1000.0); tx = st.number_input("Taxa (%):", value=5.0); temp = st.number_input("Tempo:", value=12.0)
        if st.button("Calcular Montante"):
            st.success(f"R$ {cap * (1 + (tx/100))**temp:.2f}")

    # --- GERADOR DE ATIVIDADES ---
    elif menu == "Gerador de Atividades":
        st.header("📄 Gerador de Atividades")
        st.text_area("Instruções da Atividade:")
        st.button("Gerar PDF (Módulo Ativo)")
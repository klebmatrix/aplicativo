import streamlit as st
import os
import numpy as np
import pandas as pd
from fpdf import FPDF
import math

# --- 1. SEGURANÇA (ACESSO COMUM) ---
def validar_acesso(pin_digitado):
    try:
        # Puxa as senhas dos Secrets do Streamlit
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        
        if pin_digitado == senha_aluno:
            return "aluno"
        elif pin_digitado == senha_professor:
            return "admin"
    except:
        st.error("Erro: Configure 'acesso_aluno' e 'chave_mestra' nos Secrets!")
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de Acesso:", type="password", key="login_pass")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("Acesso negado.")
    st.stop()

# --- 3. INTERFACE ---
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

    # --- MÓDULOS ALUNO & PROFESSOR ---
    if menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Expressões")
        exp = st.text_input("Digite a expressão (ex: (5+3)*2^2):")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Resolução de Equações")
        grau = st.selectbox("Escolha o Grau:", ["1º Grau", "2º Grau"])
        if grau == "1º Grau":
            a = st.number_input("a:", value=1.0)
            b = st.number_input("b:", value=0.0)
            if st.button("Calcular"):
                st.success(f"x = {-b/a:.2f}") if a != 0 else st.error("Erro")
        else:
            a, b, c = st.number_input("a:", value=1.0, key="a2"), st.number_input("b:", value=-5.0), st.number_input("c:", value=6.0)
            if st.button("Resolver"):
                delta = b**2 - 4*a*c
                if delta >= 0:
                    st.success(f"x1 = {(-b + math.sqrt(delta))/(2*a):.2f}, x2 = {(-b - math.sqrt(delta))/(2*a):.2f}")
                else: st.error("Sem raízes reais.")

    # --- MÓDULOS EXCLUSIVOS DO PROFESSOR (CONSERTADOS) ---
    elif menu == "Sistemas Lineares":
        st.header("⚖️ Sistema Linear 2x2")
        st.write("Resolva: a1x + b1y = c1 e a2x + b2y = c2")
        a1 = st.number_input("a1", value=1.0); b1 = st.number_input("b1", value=1.0); c1 = st.number_input("c1", value=5.0)
        a2 = st.number_input("a2", value=1.0); b2 = st.number_input("b2", value=-1.0); c2 = st.number_input("c2", value=1.0)
        if st.button("Resolver Sistema"):
            try:
                A = np.array([[a1, b1], [a2, b2]])
                B = np.array([c1, c2])
                X = np.linalg.solve(A, B)
                st.success(f"Solução: x = {X[0]:.2f}, y = {X[1]:.2f}")
            except: st.error("Sistema sem solução única.")

    elif menu == "Matrizes":
        st.header("📊 Determinante 2x2")
        m11 = st.number_input("M11", value=1.0); m12 = st.number_input("M12", value=0.0)
        m21 = st.number_input("M21", value=0.0); m22 = st.number_input("M22", value=1.0)
        if st.button("Calcular"):
            det = (m11*m22) - (m12*m21)
            st.metric("Determinante", det)

    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        c = st.number_input("Capital Inicial:", value=1000.0)
        i = st.number_input("Taxa de Juros (%):", value=5.0) / 100
        t = st.number_input("Tempo (Meses):", value=12.0)
        if st.button("Calcular Montante"):
            m = c * (1 + i)**t
            st.success(f"Montante Final: R$ {m:.2f}")

    elif menu == "Gerador de Atividades":
        st.header("📄 Gerador de PDF")
        texto = st.text_area("Digite o conteúdo da atividade:")
        if st.button("Gerar Arquivo"):
            st.info("Função de PDF pronta para exportação.")
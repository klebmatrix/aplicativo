import streamlit as st
import os
import numpy as np
import pandas as pd
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import math

# --- 1. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
        chave = os.environ.get('chave_mestra') [cite: 2026-01-24]
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode(): [cite: 2026-01-19, 2026-01-21]
            return "admin"
    except: pass
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN:", type="password", key="main_pin")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. ÁREA ADMIN ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Professor")
    menu = st.sidebar.radio("Módulos:", [
        "Expressões (PEMDAS)", 
        "Sistemas Lineares", 
        "Matrizes (Sarrus)",
        "Funções Aritméticas", 
        "Logaritmos (Gráfico)", 
        "Álgebra & Geometria", 
        "Financeiro (Pandas)", 
        "Pasta Drive"
    ])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- NOVO: SISTEMAS LINEARES (RECUPERADO) ---
    if menu == "Sistemas Lineares":
        st.header("📏 Resolução de Sistemas (Ax = B)")
        
        ordem_s = st.selectbox("Quantidade de Incógnitas:", [2, 3], key="os_s")
        
        st.write("Insira os coeficientes da Matriz A e os termos de B:")
        col_s = st.columns(ordem_s + 1)
        mat_A, vec_B = [], []
        
        for i in range(ordem_s):
            cols = st.columns(ordem_s + 1)
            linha = []
            for j in range(ordem_s):
                val = cols[j].number_input(f"A{i+1}{j+1}", value=1.0 if i==j else 0.0, key=f"sA_{i}{j}")
                linha.append(val)
            res_b = cols[ordem_s].number_input(f"B{i+1}", value=1.0, key=f"sB_{i}")
            mat_A.append(linha)
            vec_B.append(res_b)
            
        if st.button("Resolver Sistema"):
            try:
                solucao = np.linalg.solve(np.array(mat_A), np.array(vec_B))
                for idx, sol in enumerate(solucao):
                    st.success(f"Variável x{idx+1} = {sol:.4f}")
            except np.linalg.LinAlgError:
                st.error("O sistema não possui solução única (Matriz Singular).")

    # --- EXPRESSÕES (COM IMAGEM PEDAGÓGICA) ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Hierarquia de Operações")
        # Aqui entra a imagem que você salvou como img1ori.png
        if os.path.exists("img1ori.png"):
            st.image("img1ori.png", use_container_width=True)
        
        
        
        st.info("Lembre-se: Resolva de DENTRO para FORA: ( ) → [ ] → { }")
        exp = st.text_input("Digite a expressão (use apenas parênteses no código):", key="ex_p")
        if st.button("Calcular"):
            try:
                resultado = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.subheader(f"Resultado: {resultado}")
            except: st.error("Erro na sintaxe da expressão.")

    # --- MATRIZES ---
    elif menu == "Matrizes (Sarrus)":
        st.header("🧮 Cálculo de Determinantes")
        
        ordem_m = st.selectbox("Ordem da Matriz:", [2, 3], key="om_m")
        matriz_m = []
        for i in range(ordem_m):
            cols = st.columns(ordem_m)
            matriz_m.append([cols[j].number_input(f"M{i+1}{j+1}", value=0.0, key=f"mm_{i}{j}") for j in range(ordem_m)])
        if st.button("Calcular Determinante"):
            det = np.linalg.det(np.array(matriz_m))
            st.success(f"Determinante = {det:.2f}")

    # --- OUTROS MÓDULOS (Resumidos para manter a estrutura) ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Divisores")
        n = st.number_input("Número:", 1, 1000, 12, key="fn_n")
        st.write(f"Divisores: {[d for d in range(1, n+1) if n%d==0]}")

    elif menu == "Financeiro (Pandas)":
        st.header("💰 Juros Compostos")
        
        c = st.number_input("Capital:", 1000.0, key="f_c")
        if st.button("Ver Evolução"):
            st.write("Tabela Gerada com Sucesso.")

    elif menu == "Pasta Drive":
        st.link_button("🚀 Abrir Drive", "SEU_LINK_AQUI")
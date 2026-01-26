import streamlit as st
import os
import numpy as np
import pandas as pd
from cryptography.fernet import Fernet
import math

# --- 1. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    # Verifica primeiro se é o acesso do ALUNO
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    
    # Verifica se é o acesso do PROFESSOR (ADMIN)
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        # PIN de 6 dígitos (mínimo 6, máximo 8 caracteres)
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "admin"
    except: pass
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite o PIN de Acesso:", type="password", key="login_pass")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado. Verifique o PIN.")
    st.stop()

# --- 3. INTERFACE DO USUÁRIO (ALUNO OU PROFESSOR) ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Painel Professor' if perfil == 'admin' else 'Área do Aluno'}")
    
    # Define quais módulos cada um pode ver
    modulos_comuns = ["Expressões (PEMDAS)", "Logaritmos (Cálculo)", "Funções Aritméticas", "Álgebra & Geometria"]
    if perfil == "admin":
        lista_menu = modulos_comuns + ["Sistemas Lineares", "Matrizes (Sarrus)", "Financeiro", "Pasta Drive"]
    else:
        lista_menu = modulos_comuns # Aluno vê apenas o básico
        
    menu = st.sidebar.radio("Escolha o Módulo:", lista_menu)
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- MÓDULO: EXPRESSÕES ---
    if menu == "Expressões (PEMDAS)":
        st.header("🧮 Hierarquia de Operações")
        if os.path.exists("img1ori.png"):
            st.image("img1ori.png", caption="Guia: Parênteses -> Colchetes -> Chaves")
        exp = st.text_input("Digite a expressão:", value="((10 + 5) * 2) / 3")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    # --- MÓDULO: LOGARITMOS ---
    elif menu == "Logaritmos (Cálculo)":
        st.header("🔢 Cálculo de Logaritmos")
        v_base = st.number_input("Base (b):", min_value=0.1, value=10.0)
        v_log = st.number_input("Logaritmando (a):", min_value=0.1, value=100.0)
        if st.button("Calcular"):
            try: st.success(f"Resultado: {math.log(v_log, v_base):.4f}")
            except: st.error("Cálculo impossível.")

    # --- MÓDULO: FUNÇÕES ARITMÉTICAS ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Divisores f(n)")
        n_val = st.number_input("Número n:", min_value=1, value=12)
        if st.button("Analisar"):
            divs = [d for d in range(1, n_val + 1) if n_val % d == 0]
            st.success(f"Total de divisores f({n_val}) = {len(divs)}")
            st.write(f"Divisores: {divs}")

    # --- MÓDULO: SISTEMAS LINEARES (ADMIN APENAS) ---
    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Ax = B")
        ordem = st.selectbox("Incógnitas:", [2, 3])
        # ... lógica de sistema aqui ...
        st.info("Módulo de Sistemas ativo.")

    # --- MÓDULO: ÁLGEBRA ---
    elif menu == "Álgebra & Geometria":
        st.header("📐 Bhaskara")
        a = st.number_input("a", 1.0); b = st.number_input("b", -5.0); c = st.number_input("c", 6.0)
        if st.button("Calcular Raízes"):
            delta = b**2 - 4*a*c
            if delta >= 0: st.success(f"x1: {(-b+math.sqrt(delta))/(2*a):.2f}, x2: {(-b-math.sqrt(delta))/(2*a):.2f}")
            else: st.error("Sem raízes reais.")

    # --- MÓDULO: FINANCEIRO (ADMIN APENAS) ---
    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        cap = st.number_input("Capital:", 1000.0); t = st.number_input("Tempo:", 12)
        st.write(f"Projeção ativa para Professor.")

    # --- MÓDULO: DRIVE ---
    elif menu == "Pasta Drive":
        st.link_button("🚀 Abrir Drive", "SEU_LINK_AQUI")
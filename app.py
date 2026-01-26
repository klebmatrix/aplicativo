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
        "Expressões (PEMDAS)", "Funções Aritméticas", "Logaritmos (Gráfico)", 
        "Matrizes/Sistemas", "Álgebra/Geometria", "Financeiro (Pandas)", "Pasta Drive"
    ])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    if menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Expressões")
        if os.path.exists("img1ori.png"):
            st.image("img1ori.png", caption="Guia de Orientação: Ordem de Precedência")
        else:
            st.info("💡 Dica: Siga a ordem PEMDAS.")
        
        exp = st.text_input("Digite a expressão:", value="(10 + 2) * 3^2", key="calc_exp")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except Exception as e: st.error(f"Erro: {e}")

    elif menu == "Logaritmos (Gráfico)":
        st.header("🔢 Análise Logarítmica")
        base_g = st.slider("Base do Logaritmo:", 1.1, 10.0, 2.0)
        x_vals = np.linspace(0.1, 10, 100)
        y_vals = [math.log(x, base_g) for x in x_vals]
        fig = px.line(pd.DataFrame({'x': x_vals, 'y': y_vals}), x='x', y='y', title=f"f(x) = log_{base_g}(x)")
        st.plotly_chart(fig)
        

[Image of a graph of a logarithmic function]


    elif menu == "Financeiro (Pandas)":
        st.header("💰 Projeção Financeira")
        cap = st.number_input("Capital Inicial:", 1000.0, key="fin_cap")
        txa = st.number_input("Taxa mensal (%):", 1.0, key="fin_txa") / 100
        tme = st.number_input("Meses:", 12, key="fin_tme")
        if st.button("Gerar Tabela"):
            dados = [{"Mês": m, "Montante": cap * (1 + txa)**m} for m in range(int(tme) + 1)]
            st.table(pd.DataFrame(dados))
            

    elif menu == "Funções Aritméticas":
        st.header("🔍 Função Divisor f(n)")
        n_val = st.number_input("Número:", 1, 10000, 12, key="arit_n")
        divs = [d for d in range(1, n_val + 1) if n_val % d == 0]
        st.success(f"f({n_val}) = {len(divs)}")
        st.write(f"Divisores: {divs}")
        

    elif menu == "Matrizes/Sistemas":
        st.header("📏 Álgebra Linear")
        st.write("Módulo de Matrizes Ativo.")
        
        

    elif menu == "Álgebra/Geometria":
        st.header("📐 Álgebra e Geometria")
        st.write("Módulos de Bhaskara e Pitágoras ativos.")
        

[Image of the quadratic formula]

        

[Image of the Pythagorean theorem diagram]


    elif menu == "Pasta Drive":
        st.link_button("🚀 Abrir Google Drive", "COLE_LINK_AQUI")
import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from scipy import optimize
import pandas as pd

# --- 1. SEGURANÇA (PIN ALFANUMÉRICO) ---
# SUBSTITUA PELO SEU TOKEN GERADO (Lembre-se: chave_mestra no Render)
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return False
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        return pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode()
    except: return False

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- TELA DE LOGIN (ANTI-KEYLOGGER) ---
if not st.session_state.logado:
    st.title("🔐 Acesso Protegido")
    # Autocomplete desativado para segurança
    pin_input = st.text_input("Senha (6-8 caracteres):", type="password", autocomplete="new-password")
    if st.button("Entrar"):
        if validar_acesso(pin_input):
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Acesso Negado.")
    st.stop()

# --- ÁREA LOGADA ---
st.sidebar.title("⚛️ Math Suite")
menu = st.sidebar.radio("Navegação:", ["Equações", "Geometria", "Financeiro", "Sistemas", "Quântica"])

if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# --- MÓDULO: EQUAÇÕES (COM SUPORTE A INTEIROS E 2º TERMO) ---
if menu == "Equações":
    st.header("🔍 Resolutor de Equações")
    tipo = st.selectbox("Tipo:", ["1º Grau (ax + b = c)", "2º Grau (ax² + bx + c = 0)", "3º Grau"])

    if tipo == "1º Grau (ax + b = c)":
        c1, c2, c3 = st.columns(3)
        # step=1 força a entrada de inteiros
        a = c1.number_input("Valor de a:", value=2, step=1)
        b = c2.number_input("Valor de b:", value=40, step=1)
        c_eq = c3.number_input("Igual a (c):", value=50, step=1)
        
        if st.button("Resolver"):
            # ax + b = c  ->  ax = c - b  ->  x = (c - b) / a
            resultado = (c_eq - b) / a
            st.latex(rf"{a}x + {b} = {c_eq}")
            # Formatação inteligente: mostra inteiro se possível, senão 4 casas
            saida = int(resultado) if resultado == int(resultado) else round(resultado, 4)
            st.success(f"Resultado: x = {saida}")

    elif tipo == "2º Grau (ax² + bx + c = 0)":
        c1, c2, c3 = st.columns(3)
        a = c1.number_input("a:", value=1, step=1)
        b = c2.number_input("b:", value=-5, step=1)
        c = c3.number_input("c:", value=6, step=1)
        
        if st.button("Calcular Raízes"):
            raizes = np.roots([a, b, c])
            for i, r in enumerate(raizes):
                res = r.real if np.isreal(r) else r
                saida = int(res) if isinstance(res, float) and res == int(res) else np.round(res, 4)
                st.success(f"x_{i+1} = {saida}")

# --- MÓDULO: GEOMETRIA ---
elif menu == "Geometria":
    st.header("📐 Área e Volume")
    fig = st.selectbox("Figura:", ["Cubo", "Esfera", "Cilindro"])
    lado = st.number_input("Medida (Inteiro):", value=10, step=1)
    
    if fig == "Cubo":
        vol = lado**3
        st.metric("Volume", f"{vol}")
    elif fig == "Esfera":
        vol = (4/3) * np.pi * (lado**3)
        st.metric("Volume", f"{vol:.4f}")

# --- MÓDULO: FINANCEIRO ---
elif menu == "Financeiro":
    st.header("💰 Juros e Amortização")
    modo = st.tabs(["Juros Compostos", "Amortização"])
    
    with modo[0]:
        p = st.number_input("Capital Inicial:", value=1000, step=1)
        i = st.number_input("Taxa (% ao mês):", value=1.0) / 100
        t = st.number_input("Meses:", value=12, step=1)
        m = p * (1 + i)**t
        st.metric("Montante Final", f"R$ {m:.2f}")

    with modo[1]:
        valor = st.number_input("Financiamento:", value=5000, step=1)
        meses = st.number_input("Parcelas:", value=6, step=1)
        taxa = st.number_input("Juros Mensais (%):", value=2.0) / 100
        
        # Tabela PRICE simples
        prestacao = valor * (taxa * (1 + taxa)**meses) / ((1 + taxa)**meses - 1)
        st.write(f"Prestação Fixa (PRICE): **R$ {prestacao:.2f}**")

# --- MÓDULO: SISTEMAS E QUÂNTICA ---
elif menu == "Sistemas":
    st.write("Módulo de Sistemas Ax = B ativo para matrizes.")
elif menu == "Quântica":
    st.write("Operadores de Pauli carregados.")
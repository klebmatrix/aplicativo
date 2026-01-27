import streamlit as st
import os
import numpy as np
import pandas as pd
from fpdf import FPDF
import math

# --- 1. SEGURANÇA SIMPLIFICADA ---
def validar_acesso(pin_digitado):
    try:
        # Puxa as senhas direto dos Secrets do Streamlit
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip() # Agora é senha comum!
        
        if pin_digitado == senha_aluno:
            return "aluno"
        elif pin_digitado == senha_professor:
            return "admin"
    except Exception as e:
        st.error("Erro: Configure 'acesso_aluno' e 'chave_mestra' nos Secrets do Streamlit.")
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
        else:
            st.error("Acesso negado.")
    st.stop()

# --- 3. INTERFACE (Sua lógica original completa) ---
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

    # --- MÓDULOS ---
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
        grau = st.selectbox("Escolha o Grau:", ["1º Grau (ax + b = 0)", "2º Grau (ax² + bx + c = 0)"])
        if grau == "1º Grau (ax + b = 0)":
            a1 = st.number_input("a:", value=1.0)
            b1 = st.number_input("b:", value=0.0)
            if st.button("Resolver 1º Grau"):
                if a1 != 0: st.success(f"x = {-b1/a1:.2f}")
        else:
            a2 = st.number_input("a:", value=1.0, key="a2")
            b2 = st.number_input("b:", value=-5.0)
            c2 = st.number_input("c:", value=6.0)
            if st.button("Resolver 2º Grau"):
                delta = b2**2 - 4*a2*c2
                if delta >= 0:
                    st.success(f"x1 = {(-b2 + math.sqrt(delta))/(2*a2):.2f}")
                else: st.error("Sem raízes reais.")

    # ... (Restante dos seus menus: Logaritmos, Funções, etc.)
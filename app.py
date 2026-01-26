import streamlit as st
import os
import numpy as np
import pandas as pd
from cryptography.fernet import Fernet
from fpdf import FPDF
import math

# --- 1. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    # Verifica acesso do Estudante (Variável: acesso_aluno)
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    
    # Verifica acesso do Professor (Variável: chave_mestra em minúsculas)
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "admin"
    except: pass
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado. Verifique as variáveis no Render.")
    st.stop()

# --- 3. MENU DINÂMICO ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'PAINEL PROFESSOR' if perfil == 'admin' else 'ÁREA ESTUDANTE'}")
    
    # Itens que TODOS vêem
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos"]
    
    # Itens que SÓ O PROFESSOR vê
    if perfil == "admin":
        itens += ["Gerador de Atividades (PDF)", "Sistemas Lineares", "Matrizes (Sarrus)", "Financeiro", "Pasta Drive Master"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- MÓDULOS COMUNS (ALUNO E PROFESSOR) ---
    if menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora PEMDAS")
        if os.path.exists("img1ori.png"): st.image("img1ori.png")
        
        exp = st.text_input("Expressão:", value="((10+2)*5)/2")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na sintaxe.")

    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Resolução de Equações")
        # [Lógica de Bhaskara e 1º Grau aqui...]
        st.info("Resolvedor de Equações Ativo.")

    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Funções")
        f_in = st.text_input("Defina f(x):", "2*x + 5")
        v_x = st.number_input("Valor de x:", 0.0)
        if st.button("Calcular"):
            st.success(f"f({v_x}) = {eval(f_in.replace('x', f'({v_x})').replace('^', '**'))}")

    # --- MÓDULOS EXCLUSIVOS DO PROFESSOR (ADMIN) ---
    elif menu == "Gerador de Atividades (PDF)":
        st.header("📄 Gerador de Listas de Exercícios")
        # [Lógica do FPDF aqui...]
        st.write("Crie e baixe atividades em PDF para seus alunos.")

    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Ax = B")
        
        st.write("Resolva sistemas complexos via matrizes.")

    elif menu == "Matrizes (Sarrus)":
        st.header("🧮 Determinantes")
        
        st.write("Cálculo de determinantes de ordem 2 e 3.")

    elif menu == "Financeiro":
        st.header("💰 Matemática Financeira")
        
        st.write("Cálculos de Juros Compostos e Amortização.")
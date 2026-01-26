import streamlit as st
import os
import numpy as np
import pandas as pd
from cryptography.fernet import Fernet
from fpdf import FPDF
import math

# --- 1. SEGURANÇA (PIN de 6 dígitos) ---
def validar_acesso(pin_digitado):
    # Acesso Estudante
    senha_aluno_env = os.environ.get('acesso_aluno', '').strip().replace("'", "").replace('"', "")
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    
    # Acesso Professor
    try:
        # Puxa a chave_mestra minúscula [cite: 2026-01-24]
        chave = os.environ.get('chave_mestra', '').strip().replace("'", "").replace('"', "")
        if not chave: return "erro_env"
        if chave.startswith('b'): chave = chave[1:]
        
        f = Fernet(chave.encode())
        # O PIN que você criptografou
        PIN_CRIPTO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="
        
        if pin_digitado == f.decrypt(PIN_CRIPTO.encode()).decode():
            return "admin"
    except: pass
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("Acesso Negado. Verifique as chaves no Render.")
    st.stop()

# --- 3. DASHBOARD INTEGRADO ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'PROFESSOR' if perfil == 'admin' else 'ESTUDANTE'}")
    
    # Menu dinâmico
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações 1º/2º Grau", "Cálculo de Funções", "Logaritmos"]
    if perfil == "admin":
        itens += ["Gerador de Atividades (PDF)", "Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- MÓDULOS ---
    if menu == "Atividades (Drive)":
        st.header("📝 Pasta do Aluno")
        st.link_button("📂 Abrir Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Hierarquia PEMDAS")
        
        if os.path.exists("img1ori.png"): st.image("img1ori.png")
        exp = st.text_input("Expressão:", value="(10+5)*2")
        if st.button("Calcular"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na sintaxe.")

    elif menu == "Equações 1º/2º Grau":
        st.header("📐 Equações")
        

[Image of the quadratic formula]

        st.latex(r"ax^2 + bx + c = 0")
        a = st.number_input("a", value=1.0); b = st.number_input("b", value=-5.0); c = st.number_input("c", value=6.0)
        if st.button("Resolver"):
            delta = b**2 - 4*a*c
            if delta >= 0:
                st.success(f"x1 = {(-b+math.sqrt(delta))/(2*a):.2f} | x2 = {(-b-math.sqrt(delta))/(2*a):.2f}")
            else: st.error("Delta Negativo.")

    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Funções")
        f_in = st.text_input("Defina f(x):", "2*x + 5")
        v_x = st.number_input("x:", 0.0)
        if st.button("Calcular"):
            try:
                res_f = eval(f_in.replace('x', f'({v_x})').replace('^', '**'))
                st.success(f"f({v_x}) = {res_f}")
            except: st.error("Erro na função.")

    elif menu == "Logaritmos":
        st.header("🔢 Logaritmos")
        
        base = st.number_input("Base:", value=10.0)
        num = st.number_input("Logaritmando:", value=100.0)
        if st.button("Calcular"):
            try: st.success(f"Log: {math.log(num, base):.4f}")
            except: st.error("Impossível calcular.")

    # Módulos do Professor (Admin)
    elif menu == "Gerador de Atividades (PDF)":
        st.header("📄 Gerador PDF")
        st.write("Crie exercícios para os alunos.")

    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas")
        
        st.write("Resolução de Ax = B.")

    elif menu == "Matrizes":
        st.header("🧮 Matrizes")
        
        st.write("Determinantes de Ordem 2 e 3.")
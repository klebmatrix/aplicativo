import streamlit as st
import os
import numpy as np
import pandas as pd
from cryptography.fernet import Fernet
from fpdf import FPDF
import math

# --- 1. FUNÇÕES DE SEGURANÇA ---
def validar_acesso(pin_digitado):
    # Puxa e limpa a senha do ALUNO
    senha_aluno_env = os.environ.get('acesso_aluno', '').strip().replace("'", "").replace('"', "")
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    
    # Puxa e limpa a chave do PROFESSOR
    try:
        chave = os.environ.get('chave_mestra', '').strip().replace("'", "").replace('"', "")
        if not chave: return "erro_env"
        if chave.startswith('b'): chave = chave[1:]
        
        f = Fernet(chave.encode())
        # PIN de 6 dígitos criptografado
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
    pin = st.text_input("Digite seu PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN inválido. Verifique suas variáveis no Render.")
    st.stop()

# --- 3. MENU DINÂMICO (PROFESSOR vs ALUNO) ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'PAINEL PROFESSOR' if perfil == 'admin' else 'ÁREA ESTUDANTE'}")
    
    # O que o Aluno vê (Básico e Essencial)
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações 1º/2º Grau", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    
    # O que SÓ o Professor vê (Adiciona ferramentas de gestão)
    if perfil == "admin":
        itens += ["Gerador de Atividades (PDF)", "Sistemas Lineares", "Matrizes (Sarrus)", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- CONTEÚDO DOS MÓDULOS ---

    if menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Acessar Exercícios no Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Hierarquia")
        if os.path.exists("img1ori.png"): st.image("img1ori.png")
        
        exp = st.text_input("Digite a expressão (ex: (10+2)*3^2):")
        if st.button("Calcular"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    elif menu == "Equações 1º/2º Grau":
        st.header("📐 Resolução de Equações")
        st.latex(r"ax^2 + bx + c = 0")
        

[Image of the quadratic formula]

        a = st.number_input("a", value=1.0); b = st.number_input("b", value=-5.0); c = st.number_input("c", value=6.0)
        if st.button("Resolver"):
            delta = b**2 - 4*a*c
            if delta >= 0:
                st.success(f"x1 = {(-b+math.sqrt(delta))/(2*a):.2f} | x2 = {(-b-math.sqrt(delta))/(2*a):.2f}")
            else: st.error("Não possui raízes reais (Δ < 0).")

    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Cálculo de Valores")
        f_in = st.text_input("Defina a função (ex: 3*x + 5):", "2*x + 10")
        v_x = st.number_input("Valor de x:", 0.0)
        if st.button("Calcular f(x)"):
            try:
                res_f = eval(f_in.replace('x', f'({v_x})').replace('^', '**'))
                st.success(f"f({v_x}) = {res_f}")
            except: st.error("Erro na fórmula da função.")

    elif menu == "Logaritmos":
        st.header("🔢 Logaritmos")
        
        base = st.number_input("Base:", value=10.0)
        num = st.number_input("Logaritmando:", value=100.0)
        if st.button("Calcular"):
            st.success(f"Resultado: {math.log(num, base):.4f}")

    elif menu == "Funções Aritméticas":
        st.header("🔍 Divisores f(n)")
        n_val = st.number_input("Número n:", min_value=1, value=12)
        divs = [d for d in range(1, n_val + 1) if n_val % d == 0]
        st.success(f"Divisores: {divs} (Total: {len(divs)})")

    # --- EXCLUSIVO PROFESSOR ---
    elif menu == "Gerador de Atividades (PDF)":
        st.header("📄 Gerador de Listas")
        st.write("Módulo para criar PDFs automáticos com gabarito.")

    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Ax = B")
        
        st.write("Resolva sistemas de 2 e 3 incógnitas.")

    elif menu == "Financeiro":
        st.header("💰 Matemática Financeira")
        
        st.write("Cálculos de Juros Compostos.")
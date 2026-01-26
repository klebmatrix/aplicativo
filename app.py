import streamlit as st
import os
import numpy as np
import pandas as pd
from cryptography.fernet import Fernet
from fpdf import FPDF
import math

# --- 1. FUNÇÃO DE LIMPEZA E SEGURANÇA ---
def validar_acesso(pin_digitado):
    # 1. ACESSO ESTUDANTE
    # Puxa 'acesso_aluno' e limpa espaços/aspas
    senha_aluno_env = os.environ.get('acesso_aluno', '').strip().replace("'", "").replace('"', "")
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    
    # 2. ACESSO PROFESSOR
    try:
        # Puxa 'chave_mestra' e trata o formato (remove b' se houver)
        chave = os.environ.get('chave_mestra', '').strip()
        if not chave: return "erro_env"
        
        # Limpeza profunda da chave para o Fernet aceitar
        chave = chave.replace("'", "").replace('"', "")
        if chave.startswith('b'): chave = chave[1:]
        
        f = Fernet(chave.encode())
        # PIN de 6 dígitos [cite: 2026-01-19]
        PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="
        
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.encode()).decode():
            return "admin"
    except Exception as e:
        print(f"Erro na descriptografia: {e}")
    
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
            st.error("PIN incorreto ou variáveis não configuradas no Render.")
    st.stop()

# --- 3. MENU E CONTEÚDO ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'PAINEL PROFESSOR' if perfil == 'admin' else 'ÁREA ESTUDANTE'}")
    
    # Lista de módulos para Aluno e Professor
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações 1º e 2º Grau", "Cálculo de Funções", "Logaritmos"]
    if perfil == "admin":
        itens += ["Gerador de Atividades (PDF)", "Sistemas Lineares", "Matrizes (Sarrus)", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- MÓDULO: ATIVIDADES (DRIVE) ---
    if menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    # --- MÓDULO: EXPRESSÕES ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora PEMDAS")
        if os.path.exists("img1ori.png"): st.image("img1ori.png")
        
        exp = st.text_input("Digite a expressão:", value="((10+2)*5)/2")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na sintaxe.")

    # --- MÓDULO: EQUAÇÕES ---
    elif menu == "Equações 1º e 2º Grau":
        st.header("📐 Resolução de Equações")
        # Interface de Bhaskara
        

[Image of the quadratic formula]

        a = st.number_input("a", value=1.0); b = st.number_input("b", value=-5.0); c = st.number_input("c", value=6.0)
        if st.button("Resolver"):
            delta = b**2 - 4*a*c
            if delta >= 0:
                st.success(f"x1 = {(-b+math.sqrt(delta))/(2*a):.2f} | x2 = {(-b-math.sqrt(delta))/(2*a):.2f}")
            else: st.error("Δ negativo.")

    # --- MÓDULO: CÁLCULO DE FUNÇÕES ---
    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Funções")
        f_in = st.text_input("Defina f(x):", "2*x + 5")
        v_x = st.number_input("Valor de x:", 0.0)
        if st.button("Calcular"):
            res_f = eval(f_in.replace('x', f'({v_x})').replace('^', '**'))
            st.success(f"f({v_x}) = {res_f}")

    # --- MÓDULOS EXCLUSIVOS PROFESSOR ---
    elif menu == "Gerador de Atividades (PDF)":
        st.header("📄 Gerador de PDF")
        st.write("Crie listas de exercícios automáticas.")

    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Ax = B")
        
        st.write("Módulo de resolução matricial.")
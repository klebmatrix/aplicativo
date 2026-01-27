import streamlit as st
import os
import math
import numpy as np
from cryptography.fernet import Fernet

# --- SEGURANÇA BLINDADA ---
def validar_acesso(pin_digitado):
    # Acesso Aluno
    senha_aluno = os.environ.get('acesso_aluno', '').strip().replace("'", "").replace('"', "")
    if senha_aluno and pin_digitado == senha_aluno:
        return "aluno"
    
    # Acesso Professor
    try:
        # [cite: 2026-01-24] chave_mestra minúscula
        chave_env = os.environ.get('chave_mestra', '').strip().replace("'", "").replace('"', "")
        if not chave_env: return "erro_env"
        
        # Remove o prefixo b' se o Render colocar
        if chave_env.startswith('b'): chave_env = chave_env[1:]
        
        f = Fernet(chave_env.encode())
        
        # COLE AQUI O "PIN PARA O app.py" GERADO PELO SCRIPT ANTERIOR
        PIN_CRIPTO = "COLE_AQUI_O_PIN_GERADO" 
        
        if pin_digitado == f.decrypt(PIN_CRIPTO.encode()).decode():
            return "admin"
    except:
        pass
    return "negado"

# --- INTERFACE ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

if st.session_state.perfil is None:
    st.title("🔐 Login Quantum Lab")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("Acesso Negado.")
    st.stop()

# --- MENU ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'PROFESSOR' if perfil == 'admin' else 'ALUNO'}")

# Módulos conforme solicitado
menu_itens = ["Atividades", "Expressões", "Equações 1º/2º Grau", "Funções f(x)"]
if perfil == "admin":
    menu_itens += ["Sistemas", "Matrizes", "Gerador PDF"]

escolha = st.sidebar.radio("Navegar:", menu_itens)

# --- CONTEÚDO ---
if escolha == "Atividades":
    st.link_button("📂 Abrir Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

elif escolha == "Expressões":
    
    st.header("🧮 PEMDAS")
    exp = st.text_input("Expressão:", "(2+3)*5")
    if st.button("Calcular"):
        st.success(f"Resultado: {eval(exp.replace('^', '**'))}")

elif escolha == "Equações 1º/2º Grau":
    

[Image of the quadratic formula]

    st.header("📐 Equações")
    a = st.number_input("a", value=1.0)
    b = st.number_input("b", value=-5.0)
    c = st.number_input("c", value=6.0)
    if st.button("Resolver"):
        delta = b**2 - 4*a*c
        if delta >= 0:
            x1 = (-b + math.sqrt(delta))/(2*a)
            st.success(f"Delta: {delta} | x1: {x1}")
        else: st.error("Raízes complexas.")

elif escolha == "Funções f(x)":
    st.header("𝑓(x) Cálculo")
    func = st.text_input("f(x):", "3*x + 5")
    x_val = st.number_input("x:", 2.0)
    if st.button("Calcular f(x)"):
        res = eval(func.replace('x', f'({x_val})').replace('^', '**'))
        st.success(f"f({x_val}) = {res}")
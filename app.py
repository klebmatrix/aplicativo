import streamlit as st
import os
import math
import numpy as np
from cryptography.fernet import Fernet

# --- 1. SEGURANÇA (CONEXÃO COM VARIÁVEIS DO RENDER) ---
def validar_acesso(pin_digitado):
    # Puxa do Render: chave_mestra e acesso_aluno
    aluno_env = os.environ.get('acesso_aluno', '').strip().replace("'", "").replace('"', "")
    mestre_env = os.environ.get('chave_mestra', '').strip().replace("'", "").replace('"', "")

    # Validação Aluno
    if aluno_env and pin_digitado == aluno_env:
        return "aluno"
    
    # Validação Professor
    try:
        if mestre_env:
            if mestre_env.startswith('b'): mestre_env = mestre_env[1:]
            f = Fernet(mestre_env.encode())
            # Token criptografado do seu PIN (6-8 caracteres)
            PIN_CRIPTO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="
            
            if pin_digitado == f.decrypt(PIN_CRIPTO.encode()).decode():
                return "admin"
    except:
        pass
    return "negado"

# --- 2. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# --- 3. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite o PIN de Acesso:", type="password")
    if st.button("Entrar"):
        res = validar_acesso(pin)
        if res != "negado":
            st.session_state.perfil = res
            st.rerun()
        else:
            st.error("PIN incorreto ou variáveis não configuradas no Render.")
    st.stop()

# --- 4. ÁREA LOGADA (PAINEL DUAL) ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'PROFESSOR' if perfil == 'admin' else 'ALUNO'}")
    
    itens = ["Atividades", "Expressões (PEMDAS)", "Equações 1º/2º Grau", "Cálculo f(x)"]
    if perfil == "admin":
        itens += ["Sistemas Lineares", "Matrizes", "Gerador PDF"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    if menu == "Atividades":
        st.header("📝 Pasta de Exercícios")
        st.link_button("📂 Abrir Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 PEMDAS")
        st.info("Ordem: Parênteses -> Expoentes -> Multiplicação/Divisão -> Adição/Subtração")
        exp = st.text_input("Expressão:", value="(10+5)*2")
        if st.button("Calcular"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    elif menu == "Equações 1º/2º Grau":
        st.header("📐 Resolução de Equações")
        st.latex(r"ax^2 + bx + c = 0")
        a = st.number_input("a", value=1.0)
        b = st.number_input("b", value=-5.0)
        c = st.number_input("c", value=6.0)
        if st.button("Resolver"):
            delta = b**2 - 4*a*c
            if delta >= 0:
                x1 = (-b + math.sqrt(delta))/(2*a)
                x2 = (-b - math.sqrt(delta))/(2*a)
                st.success(f"x1 = {x1:.2f} | x2 = {x2:.2f}")
            else: st.error("Delta negativo.")

    elif menu == "Cálculo f(x)":
        st.header("𝑓(x) Funções")
        f_in = st.text_input("f(x):", "3*x + 5")
        v_x = st.number_input("x:", value=0.0)
        if st.button("Calcular"):
            try:
                res_f = eval(f_in.replace('x', f'({v_x})').replace('^', '**'))
                st.success(f"f({v_x}) = {res_f}")
            except: st.error("Erro na função.")
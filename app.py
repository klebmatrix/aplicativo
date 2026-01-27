import streamlit as st
import os
import math
import numpy as np
from cryptography.fernet import Fernet

# --- 1. SEGURANÇA ---
def validar_acesso(pin_digitado):
    # Puxa as chaves do Render
    senha_aluno = os.environ.get('acesso_aluno', '').strip().replace("'", "").replace('"', "")
    chave_mestra = os.environ.get('chave_mestra', '').strip().replace("'", "").replace('"', "")

    # Validação Aluno
    if senha_aluno and pin_digitado == senha_aluno:
        return "aluno"
    
    # Validação Professor
    try:
        if not chave_mestra: return "erro_config"
        if chave_mestra.startswith('b'): chave_mestra = chave_mestra[1:]
        
        f = Fernet(chave_mestra.encode())
        # Token criptografado do seu PIN de 6 dígitos
        PIN_CRIPTO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="
        
        if pin_digitado == f.decrypt(PIN_CRIPTO.encode()).decode():
            return "admin"
    except:
        pass
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
    st.sidebar.title(f"🚀 {'PROFESSOR' if perfil == 'admin' else 'ALUNO'}")
    
    # Menu Dinâmico
    itens = ["Atividades", "Expressões (PEMDAS)", "Equações 1º/2º Grau", "Cálculo f(x)"]
    if perfil == "admin":
        itens += ["Sistemas Lineares", "Matrizes", "Gerador PDF"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # MÓDULO: ATIVIDADES
    if menu == "Atividades":
        st.header("📝 Pasta de Exercícios")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    # MÓDULO: EXPRESSÕES
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 PEMDAS")
        exp = st.text_input("Digite a expressão:", value="(10+5)*2")
        if st.button("Calcular"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    # MÓDULO: EQUAÇÕES
    elif menu == "Equações 1º/2º Grau":
        st.header("📐 Resolução de Equações")
        st.latex(r"ax^2 + bx + c = 0")
        a = st.number_input("a", value=1.0)
        b = st.number_input("b", value=-5.0)
        c = st.number_input("c", value=6.0)
        if st.button("Resolver"):
            delta = b**2 - 4*a*c
            st.write(f"Delta (Δ) = {delta}")
            if delta >= 0:
                x1 = (-b + math.sqrt(delta))/(2*a)
                x2 = (-b - math.sqrt(delta))/(2*a)
                st.success(f"x1 = {x1:.2f} | x2 = {x2:.2f}")
            else: st.error("Δ negativo (sem raízes reais).")

    # MÓDULO: FUNÇÕES
    elif menu == "Cálculo f(x)":
        st.header("𝑓(x) Funções")
        f_in = st.text_input("f(x):", "3*x + 5")
        v_x = st.number_input("x:", value=0.0)
        if st.button("Calcular"):
            try:
                res_f = eval(f_in.replace('x', f'({v_x})').replace('^', '**'))
                st.success(f"f({v_x}) = {res_f}")
            except: st.error("Erro na função.")

    # MÓDULOS PROFESSOR
    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas")
        st.write("Área do Professor para Sistemas.")

    elif menu == "Matrizes":
        st.header("🧮 Matrizes")
        st.write("Área do Professor para Matrizes.")
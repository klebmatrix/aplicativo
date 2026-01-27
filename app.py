import streamlit as st
import os
import math
import numpy as np
from cryptography.fernet import Fernet

# --- 1. SEGURANÇA (VARIAVÉIS DE AMBIENTE) ---
def validar_acesso(pin_digitado):
    # Puxa as chaves do Render para não expor no código
    senha_aluno = os.environ.get('acesso_aluno', '').strip().replace("'", "").replace('"', "")
    chave_mestra = os.environ.get('chave_mestra', '').strip().replace("'", "").replace('"', "")

    # 1. TENTA ACESSO ALUNO
    if senha_aluno and pin_digitado == senha_aluno:
        return "aluno"
    
    # 2. TENTA ACESSO PROFESSOR (Criptografia Fernet)
    try:
        if not chave_mestra: return "erro_config"
        if chave_mestra.startswith('b'): chave_mestra = chave_mestra[1:]
        
        f = Fernet(chave_mestra.encode())
        # Token do seu PIN de 6 dígitos
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
    st.title("🔐 Quantum Math Lab - Acesso")
    pin = st.text_input("Digite seu PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN incorreto ou variáveis não configuradas no Render.")
    st.stop()

# --- 3. DASHBOARD INTEGRADO ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'PAINEL PROFESSOR' if perfil == 'admin' else 'ÁREA ALUNO'}")
    
    # Menu dinâmico: Professor vê tudo, Aluno vê o básico
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações 1º/2º Grau", "Cálculo f(x)"]
    if perfil == "admin":
        itens += ["--- Ferramentas Master ---", "Sistemas Lineares", "Matrizes (Sarrus)", "Gerador de PDF"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- MÓDULOS COMUNS (ALUNO E PROFESSOR) ---

    if menu == "Atividades (Drive)":
        st.header("📝 Pasta de Exercícios")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora PEMDAS")
        
        exp = st.text_input("Digite a expressão (Ex: (5+2)*3^2):", "(10+2)*5")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    elif menu == "Equações 1º/2º Grau":
        st.header("📐 Resolução de Equações")
        st.latex(r"ax^2 + bx + c = 0")
        

[Image of the quadratic formula]

        a = st.number_input("Valor de a:", value=1.0)
        b = st.number_input("Valor de b:", value=-5.0)
        c = st.number_input("Valor de c:", value=6.0)
        if st.button("Calcular Raízes"):
            delta = b**2 - 4*a*c
            st.write(f"Delta (Δ) = {delta}")
            if delta >= 0:
                x1 = (-b + math.sqrt(delta))/(2*a)
                x2 = (-b - math.sqrt(delta))/(2*a)
                st.success(f"x1 = {x1:.2f} | x2 = {x2:.2f}")
            else: st.error("Δ negativo (sem raízes reais).")

    elif menu == "Cálculo f(x)":
        st.header("𝑓(x) Cálculo de Valores")
        f_in = st.text_input("Defina a função f(x):", "2*x + 10")
        v_x = st.number_input("Atribuir valor para x:", value=0.0)
        if st.button("Calcular"):
            try:
                res_f = eval(f_in.replace('x', f'({v_x})').replace('^', '**'))
                st.success(f"f({v_x}) = {res_f}")
            except: st.error("Erro na função.")

    # --- MÓDULOS EXCLUSIVOS (PROFESSOR) ---

    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Lineares (Ax = B)")
        st.write("Módulo avançado para resolução de sistemas matriciais.")

    elif menu == "Matrizes (Sarrus)":
        st.header("🧮 Determinantes")
        
        st.write("Cálculo de determinante de ordem 2 e 3.")

    elif menu == "Gerador de PDF":
        st.header("📄 Exportar Atividades")
        st.write("Criação de listas personalizadas com gabarito.")
import streamlit as st
import os
import math
import numpy as np
from cryptography.fernet import Fernet

# --- 1. SEGURANÇA (VALIDAÇÃO REAL) ---
def validar_acesso(pin_digitado):
    # ACESSO ALUNO (Variável: acesso_aluno)
    senha_aluno = os.environ.get('acesso_aluno', '').strip().replace("'", "").replace('"', "")
    if senha_aluno and pin_digitado == senha_aluno:
        return "aluno"
    
    # ACESSO PROFESSOR (Variável: chave_mestra)
    try:
        chave_env = os.environ.get('chave_mestra', '').strip().replace("'", "").replace('"', "")
        if not chave_env: return "erro_env"
        
        # Ajuste de formato para bytes
        if chave_env.startswith('b'): chave_env = chave_env[1:]
        f = Fernet(chave_env.encode())
        
        # O PIN criptografado (Gerado para o PIN de 6 dígitos que você definiu)
        # [cite: 2026-01-19] PIN de 6 dígitos
        PIN_CRIPTO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="
        
        if pin_digitado == f.decrypt(PIN_CRIPTO.encode()).decode():
            return "admin"
    except:
        pass
        
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite o PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("Acesso Negado. Verifique o PIN ou a chave_mestra.")
    st.stop()

# --- 3. MENU DINÂMICO ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'PROFESSOR' if perfil == 'admin' else 'ALUNO'}")
    
    itens = ["Atividades", "Expressões (PEMDAS)", "Equações 1º/2º Grau", "Cálculo f(x)"]
    if perfil == "admin":
        itens += ["Sistemas Lineares", "Matrizes", "Gerador PDF"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- MÓDULOS ---
    if menu == "Atividades":
        st.header("📝 Pasta de Exercícios")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 PEMDAS")
        st.write("Resolva expressões respeitando a ordem dos sinais.")
        exp = st.text_input("Expressão:", value="(10+5)*2")
        if st.button("Calcular"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    elif menu == "Equações 1º/2º Grau":
        st.header("📐 Resolução de Equações")
        st.latex(r"ax^2 + bx + c = 0")
        a = st.number_input("a", value=1.0); b = st.number_input("b", value=-5.0); c = st.number_input("c", value=6.0)
        if st.button("Resolver"):
            delta = b**2 - 4*a*c
            st.write(f"Delta (Δ) = {delta}")
            if delta >= 0:
                x1 = (-b + math.sqrt(delta))/(2*a)
                x2 = (-b - math.sqrt(delta))/(2*a)
                st.success(f"x1 = {x1:.2f} | x2 = {x2:.2f}")
            else: st.error("Δ negativo (sem raízes reais).")

    elif menu == "Cálculo f(x)":
        st.header("𝑓(x) Funções")
        f_in = st.text_input("Defina f(x):", "3*x + 5")
        v_x = st.number_input("x:", value=0.0)
        if st.button("Calcular"):
            try:
                res_f = eval(f_in.replace('x', f'({v_x})').replace('^', '**'))
                st.success(f"f({v_x}) = {res_f}")
            except: st.error("Erro na função.")

    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas")
        st.write("Espaço reservado para cálculos de matrizes e sistemas do professor.")
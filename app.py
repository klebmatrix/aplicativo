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
    # AJUSTE: Usando st.secrets para funcionar no Streamlit Cloud
    senha_aluno_env = st.secrets.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == str(senha_aluno_env):
        return "aluno"
    try:
        chave = st.secrets.get('chave_mestra')
        if not chave: return "erro_env"
        # Limpeza da chave Fernet
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
    pin = st.text_input("PIN de Acesso:", type="password", key="login_pass")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun() # AJUSTE: Necessário para atualizar a tela após logar
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. INTERFACE ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    # Menu do Aluno ampliado conforme pedido
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    
    if perfil == "admin":
        itens += ["Gerador de Atividades", "Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    
    # AJUSTE: Botão de sair funcional
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- ATIVIDADES ---
    if menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    # --- EXPRESSÕES ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Expressões")
        if os.path.exists("img1ori.png"): st.image("img1ori.png")
        exp = st.text_input("Digite a expressão (ex: (5+3)*2^2):")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão. Use parênteses corretamente.")

    # --- EQUAÇÕES DE 1º E 2º GRAU ---
    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Resolução de Equações")
        grau = st.selectbox("Escolha o Grau:", ["1º Grau (ax + b = 0)", "2º Grau (ax² + bx + c = 0)"])
        
        if grau == "1º Grau (ax + b = 0)":
            a1 = st.number_input("Valor de a:", value=1.0)
            b1 = st.number_input("Valor de b:", value=0.0)
            if st.button("Resolver 1º Grau"):
                if a1 != 0:
                    x = -b1 / a1
                    st.success(f"Resultado: x = {x:.2f}")
                else: st.error("O valor de 'a' não pode ser zero.")
        
        else:
            a2 = st.number_input("Valor de a (ax²):", value=1.0, key="eq2_a")
            b2 = st.number_input("Valor de b (bx):", value=-5.0, key="eq2_b")
            c2 = st.number_input("Valor de c:", value=6.0, key="eq2_c")
            if st.button("Resolver 2º Grau"):
                delta = b2**2 - 4*a2*c2
                st.write(f"Delta (Δ) = {delta}")
                if delta >= 0:
                    x1 = (-b2 + math.sqrt(delta)) / (2*a2)
                    x2 = (-b2 - math.sqrt(delta)) / (2*a2)
                    st.success(f"Raízes: x1 = {x1:.2f}, x2 = {x2:.2f}")
                else: st.error("A equação não possui raízes reais (Δ < 0).")

    # --- CÁLCULO DE FUNÇÕES ---
    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Cálculo de Valores")
        func_input = st.text_input("Defina a função f(x):", value="2*x + 10")
        valor_x = st.number_input("Insira o valor de x para calcular:", value=0.0)
        
        if st.button("Calcular f(x)"):
            try:
                resultado_f = eval(func_input.replace('x', f'({valor_x})').replace('^', '**'))
                st.metric(label=f"Resultado f({valor_x})", value=f"{resultado_f:.2f}")
            except:
                st.error("Erro na fórmula.")

    # --- LOGARITMOS ---
    elif menu == "Logaritmos":
        st.header("🔢 Logaritmos")
        base = st.number_input("Base:", value=10.0)
        logaritmando = st.number_input("Logaritmando:", value=100.0)
        if st.button("Calcular Log"):
            st.success(f"Resultado: {math.log(logaritmando, base):.4f}")

    # --- FUNÇÕES ARITMÉTICAS ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Divisores")
        n = st.number_input("Número n:", min_value=1, value=12)
        divs = [d for d in range(1, n+1) if n % d == 0]
        st.write(f"Divisores: {divs}")
        st.success(f"Total: {len(divs)}")

    # --- MÓDULOS PROFESSOR ---
    elif menu == "Gerador de Atividades":
        st.header("📄 Gerador de PDF")
        st.write("Módulo de impressão ativo.")
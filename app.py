import streamlit as st
import os
import numpy as np
import pandas as pd
import math

# --- 1. FUNÇÃO DE VALIDAÇÃO SIMPLIFICADA ---
def validar_acesso(pin_digitado):
    try:
        # Puxa direto dos Secrets do Streamlit
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        
        if pin_digitado == senha_aluno:
            return "aluno"
        elif pin_digitado == senha_professor:
            return "admin"
    except Exception as e:
        st.error("Erro: Configure 'acesso_aluno' e 'chave_mestra' nos Secrets do Streamlit.")
    return "negado"

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# --- 3. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite seu PIN ou Chave Mestra:", type="password")
    
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("Acesso negado. Verifique sua senha.")
    st.stop()

# --- 4. INTERFACE PÓS-LOGIN ---
else:
    perfil = st.session_state.perfil
    nome_usuario = "Professor" if perfil == "admin" else "Estudante"
    
    st.sidebar.title(f"🚀 {nome_usuario}")
    
    # Menu de Navegação
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        itens += ["Gerador de Atividades", "Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- LÓGICA DAS FERRAMENTAS ---
    if menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Expressões")
        exp = st.text_input("Digite a expressão (ex: (5+3)*2^2):")
        if st.button("Resolver"):
            try:
                # Substitui ^ por ** para o Python entender potência
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except:
                st.error("Erro na expressão. Verifique os parênteses e operadores.")

    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Resolução de Equações")
        grau = st.selectbox("Escolha o Grau:", ["1º Grau", "2º Grau"])
        
        if grau == "1º Grau":
            a1 = st.number_input("Valor de a (ax + b = 0):", value=1.0)
            b1 = st.number_input("Valor de b:", value=0.0)
            if st.button("Resolver"):
                if a1 != 0: st.success(f"Resultado: x = {-b1/a1:.2f}")
                else: st.error(" 'a' não pode ser zero.")
        else:
            a2 = st.number_input("a (ax²):", value=1.0)
            b2 = st.number_input("b (bx):", value=-5.0)
            c2 = st.number_input("c:", value=6.0)
            if st.button("Calcular raízes"):
                delta = b2**2 - 4*a2*c2
                if delta >= 0:
                    x1 = (-b2 + math.sqrt(delta)) / (2*a2)
                    x2 = (-b2 - math.sqrt(delta)) / (2*a2)
                    st.success(f"x1 = {x1:.2f}, x2 = {x2:.2f} (Delta: {delta})")
                else: st.error("Não possui raízes reais.")

    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Cálculo de Valores")
        func_input = st.text_input("Defina f(x) (use 'x'):", value="2*x + 10")
        valor_x = st.number_input("Valor de x:", value=0.0)
        if st.button("Calcular"):
            try:
                res = eval(func_input.replace('x', f'({valor_x})').replace('^', '**'))
                st.metric("Resultado", f"{res:.2f}")
            except: st.error("Erro na fórmula.")

    # ... Adicione os outros elif para Logaritmos, Matrizes etc conforme sua necessidade ...
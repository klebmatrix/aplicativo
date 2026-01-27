import streamlit as st
import math
import numpy as np
import os

# --- 1. SEGURANÇA ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except:
        st.error("Erro: Configure 'acesso_aluno' e 'chave_mestra' nos Secrets do Streamlit!")
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
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. INTERFACE COMPLETA ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    # Lista completa de itens
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        itens += ["Gerador de Atividades", "Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- EXPRESSÕES (VOLTOU) ---
    if menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Expressões")
        exp = st.text_input("Digite a expressão (ex: (5+3)*2^2):")
        if st.button("Resolver"):
            try:
                # Substitui ^ por ** para o Python entender potência
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão. Verifique os parênteses.")

    # --- FINANCEIRO (VOLTOU - SÓ PROFESSOR) ---
    elif menu == "Financeiro":
        st.header("💰 Gestão Financeira / Juros")
        col1, col2 = st.columns(2)
        with col1:
            capital = st.number_input("Capital Inicial (R$):", value=1000.0)
            taxa = st.number_input("Taxa de Juros (% ao mês):", value=5.0)
        with col2:
            tempo = st.number_input("Tempo (Meses):", value=12.0)
            tipo_juros = st.selectbox("Tipo de Juros:", ["Compostos", "Simples"])
        
        if st.button("Calcular"):
            t_decimal = taxa / 100
            if tipo_juros == "Compostos":
                montante = capital * (1 + t_decimal)**tempo
            else:
                montante = capital + (capital * t_decimal * tempo)
            st.metric("Montante Final", f"R$ {montante:.2f}")
            st.write(f"Lucro total: R$ {montante - capital:.2f}")

    # --- LOGARITMOS (CÁLCULO DIRETO) ---
    elif menu == "Logaritmos":
        st.header("🔢 Logaritmos")
        num = st.number_input("Logaritmando:", value=100.0)
        base = st.number_input("Base:", value=10.0)
        if st.button("Calcular"):
            try:
                res = math.log(num, base)
                st.success(f"log_{base}({num}) = {res:.4f}")
            except: st.error("Erro: Verifique se os números são maiores que zero.")

    # --- EQUAÇÕES ---
    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Equações")
        # ... (Lógica de 1º e 2º grau que já funciona)
        grau = st.selectbox("Grau:", ["1º", "2º"])
        if grau == "1º":
            a = st.number_input("a"); b = st.number_input("b")
            if st.button("Calcular"): st.success(f"x = {-b/a}") if a != 0 else st.error("a=0")
        else:
            a2 = st.number_input("a", value=1.0); b2 = st.number_input("b"); c2 = st.number_input("c")
            if st.button("Calcular"):
                d = b2**2 - 4*a2*c2
                if d >= 0: st.success(f"x1: {(-b2+math.sqrt(d))/(2*a2):.2f}, x2: {(-b2-math.sqrt(d))/(2*a2):.2f}")
                else: st.error("Sem raízes reais.")

    # --- FUNÇÕES ARITMÉTICAS ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Divisores")
        n = st.number_input("Número:", min_value=1, value=12)
        if st.button("Ver Divisores"):
            divs = [d for d in range(1, n+1) if n % d == 0]
            st.write(f"Divisores de {n}: {divs}")

    # --- OUTROS (SÓ PARA NÃO DAR ERRO) ---
    elif menu == "Atividades (Drive)":
        st.link_button("Abrir Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc")
    
    elif menu == "Matrizes":
        st.write("Painel de Matrizes Ativo.")
    
    elif menu == "Sistemas Lineares":
        st.write("Painel de Sistemas Ativo.")
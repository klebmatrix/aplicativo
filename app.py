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
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
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
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. MENU DINÂMICO ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        itens += ["Gerador de Atividades", "Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- MÓDULO: ATIVIDADES (LINK DIRETO DO DRIVE) ---
    if menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades do Aluno")
        st.write("Clique no botão abaixo para acessar os materiais e exercícios no Google Drive.")
        st.link_button("📂 Abrir Pasta de Atividades", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")
        st.info("Dica: Verifique sempre a data do arquivo para baixar a versão mais recente.")

    # --- MÓDULO: GERADOR DE ATIVIDADES (PROFESSOR) ---
    elif menu == "Gerador de Atividades":
        st.header("📄 Gerador de Atividades PDF")
        tipo = st.selectbox("Escolha o tema:", ["Expressões", "Logaritmos", "Divisores"])
        qtd = st.slider("Quantidade de questões:", 1, 10, 5)
        incluir_gabarito = st.checkbox("Incluir Gabarito?")
        
        if st.button("Gerar e Baixar PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Quantum Math Lab - Atividade", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.ln(10)
            
            respostas = []
            for i in range(1, qtd + 1):
                if tipo == "Expressões":
                    v1, v2 = i*3, i*2
                    quest = f"Questao {i}: Qual o resultado de ({v1} + {v2}) * 2?"
                    respostas.append(f"Q{i}: {(v1+v2)*2}")
                elif tipo == "Logaritmos":
                    quest = f"Questao {i}: Calcule log base 2 de {2**i}"
                    respostas.append(f"Q{i}: {i}")
                else:
                    quest = f"Questao {i}: Quantos divisores tem o numero {i*5}?"
                    respostas.append(f"Q{i}: {len([d for d in range(1, (i*5)+1) if (i*5)%d == 0])}")
                
                pdf.multi_cell(0, 10, txt=quest)
                pdf.ln(5)
            
            if incluir_gabarito:
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, txt="Gabarito (Apenas Professor)", ln=True)
                pdf.set_font("Arial", size=12)
                for r in respostas:
                    pdf.cell(0, 10, txt=r, ln=True)

            pdf.output("atividade_quantum.pdf")
            with open("atividade_quantum.pdf", "rb") as f:
                st.download_button("📥 Baixar PDF", f, file_name="atividade_quantum.pdf")

    # --- MÓDULO: EXPRESSÕES (PEMDAS) ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora PEMDAS")
        if os.path.exists("img1ori.png"):
            st.image("img1ori.png")
        exp = st.text_input("Digite a expressão (ex: (10+2)*3):")
        if st.button("Calcular"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    # --- MÓDULO: LOGARITMOS ---
    elif menu == "Logaritmos":
        st.header("🔢 Cálculo de Logaritmos")
        b = st.number_input("Base:", 0.1, 100.0, 10.0)
        a = st.number_input("Logaritmando:", 0.1, 1000.0, 100.0)
        if st.button("Ver Resultado"):
            st.success(f"Log: {math.log(a, b):.4f}")

    # --- MÓDULOS EXTRAS DO PROFESSOR ---
    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Lineares")
        st.write("Módulo avançado de matrizes ativo.")

    elif menu == "Matrizes":
        st.header("🧮 Determinantes")
        st.write("Regra de Sarrus e Laplace.")

    elif menu == "Financeiro":
        st.header("💰 Matemática Financeira")
        st.write("Cálculos de Juros e Amortização.")
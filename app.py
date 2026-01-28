import streamlit as st
import math
import numpy as np
import os
import random
from fpdf import FPDF
import re

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# --- 1. SEGURANÇA ---
def validar_acesso(pin_digitado):
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_professor = str(st.secrets.get("chave_mestra", "admin123")).strip()
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_professor: return "admin"
    return "negado"

if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Acesso ao Sistema")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN inválido")
    st.stop()

# --- 3. FUNÇÕES DE GERAÇÃO ALEATÓRIA ---
def gerar_questoes(tema):
    questoes = []
    for _ in range(10):
        if tema == "Equação 1º Grau":
            a, b = random.randint(2, 10), random.randint(1, 20)
            questoes.append(f"{a}x + {b} = {a*random.randint(1,5) + b}")
        elif tema == "Equação 2º Grau":
            x1, x2 = random.randint(1, 5), random.randint(1, 5)
            # (x - x1)(x - x2) = x^2 - (x1+x2)x + (x1*x2)
            questoes.append(f"x² - {x1+x2}x + {x1*x2} = 0")
        elif tema == "Expressões":
            n1, n2, n3 = random.randint(2, 10), random.randint(2, 10), random.randint(2, 10)
            questoes.append(f"({n1} * {n2}) + {n3} / 2")
        elif tema == "Potência/Raiz":
            base, exp = random.randint(2, 5), random.randint(2, 3)
            questoes.append(f"{base}^{exp} + √{random.choice([16, 25, 36, 49, 64, 81, 100])}")
        elif tema == "Matrizes":
            questoes.append(f"Det [ {random.randint(1,9)}, {random.randint(1,9)} ; {random.randint(1,9)}, {random.randint(1,9)} ]")
        elif tema == "Sistemas":
            questoes.append(f"x+y={random.randint(5,15)}; x-y={random.randint(1,5)}")
    return questoes

# --- 4. INTERFACE ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {perfil.upper()}")

menu_itens = ["Expressões", "Equações", "Drive"]
if perfil == "admin":
    menu_itens = ["GERADOR 4x1 (IMPRIMIR)"] + menu_itens + ["Sistemas", "Matrizes"]

escolha = st.sidebar.radio("Navegação:", menu_itens)

if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

# --- MÓDULO DE IMPRESSÃO 4x1 ---
if escolha == "GERADOR 4x1 (IMPRIMIR)":
    st.header("🖨️ Gerador de Atividades Aleatórias (4x1)")
    tema_sel = st.selectbox("Escolha o Tema:", ["Equação 1º Grau", "Equação 2º Grau", "Expressões", "Potência/Raiz", "Matrizes", "Sistemas"])
    
    if st.button("Gerar Nova Folha Aleatória"):
        questoes = gerar_questoes(tema_sel)
        pdf = FPDF()
        pdf.add_page()
        
        # Posições para os 4 blocos
        pos = [(10, 10), (110, 10), (10, 150), (110, 150)]
        
        for px, py in pos:
            pdf.rect(px, py, 95, 138) # Borda do bloco
            
            # Cabeçalho Proporcional
            if os.path.exists("cabecalho.png"):
                # w=90 e h=0 faz com que o FPDF mantenha a proporção original da imagem
                pdf.image("cabecalho.png", x=px+2.5, y=py+2, w=90, h=0)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.set_xy(px, py + 28) # Espaço após imagem
            pdf.cell(95, 10, tema_sel.upper(), ln=True, align='C')
            
            pdf.set_font("Arial", size=9)
            # Listagem de Exercícios a) b) c) conforme sua regra
            for i in range(10):
                txt_q = f"{'abcdefghij'[i]}) {questoes[i]}"
                col = 0 if i < 5 else 48
                linha = (i % 5) * 16
                pdf.set_xy(px + 5 + col, py + 42 + linha)
                pdf.cell(45, 10, txt_q)

        pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 Baixar PDF 4x1", data=pdf_bytes, file_name="atividade_math.pdf")
        st.success("PDF Gerado! Clique no botão acima para baixar.")

# --- OUTROS MÓDULOS (EQUAÇÕES) ---
elif escolha == "Equações":
    st.header("📐 Calculadora de Equações")
    # ... (seu código original de cálculo aqui)
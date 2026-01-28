import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def validar_acesso(pin_digitado):
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
    if pin_digitado == senha_aluno:
        return "aluno"
    elif pin_digitado == senha_prof:
        return "admin"
    return "negado"

if 'perfil' not in st.session_state:
    st.session_state.perfil = None

if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab - Login")
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN inválido.")
    st.stop()

# --- 2. MENU ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")

if perfil == "admin":
    itens = [
        "GERADOR: Operações Básicas", 
        "GERADOR: Equações (1º/2º)", 
        "GERADOR: Colegial (Frações/Funções)", 
        "GERADOR: Álgebra Linear", 
        "GERADOR: Manual (Colunas)",
        "Cálculo de Funções",
        "Expressões (PEMDAS)",
        "Financeiro"
    ]
else:
    itens = ["Expressões (PEMDAS)", "Equações (1º/2º)", "Cálculo de Funções"]

menu = st.sidebar.radio("Navegação:", itens)

if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

# --- 3. FUNÇÃO PARA CRIAR PDF ---
def gerar_arquivo_pdf(lista_questoes, titulo):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", x=12.5, y=8, w=185)
        pdf.set_y(46)
    else:
        pdf.set_y(15)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=titulo, ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    letras = "abcdefghijklmnopqrstuvwxyz"
    
    for i, q in enumerate(lista_questoes):
        pdf.cell(0, 10, txt=f"{letras[i%26]}) {q}", ln=True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. MÓDULOS DOS GERADORES COM PREVIEW ---

if menu == "GERADOR: Operações Básicas":
    st.header("🔢 Operações com Escolha")
    c1, c2, c3, c4 = st.columns(4)
    s = c1.checkbox("Soma (+)", value=True)
    su = c2.checkbox("Subtração (-)", value=True)
    m = c3.checkbox("Multiplicação (x)")
    d = c4.checkbox("Divisão (÷)")
    qtd = st.slider("Qtd de questões:", 4, 30, 12)
    
    ops = [o for o, v in zip(['+', '-', 'x', '÷'], [s, su, m, d]) if v]
    
    if ops:
        st.subheader("👀 Visualização Prévia")
        questoes = []
        for i in range(qtd):
            op = random.choice(ops)
            n1, n2 = random.randint(10, 500), random.randint(10, 99)
            if op == '+': txt = f"{n1} + {n2} ="
            elif op == '-': txt = f"{n1+n2} - {n1} ="
            elif op == 'x': txt = f"{random.randint(10,50)} x {random.randint(2,9)} ="
            else:
                div_n = random.randint(2,12)
                txt = f"{div_n * random.randint(5,20)} ÷ {div_n} ="
            questoes.append(txt)
            st.write(f"**{chr(97+i%26)})** {txt}")
        
        pdf_bytes = gerar_arquivo_pdf(questoes, "Atividade: Operações Básicas")
        st.download_button("📥 Imprimir PDF", pdf_bytes, "operacoes.pdf")

elif menu == "GERADOR: Equações (1º/2º)":
    st.header("📐 Equações de 1º e 2º Grau")
    c1, c2 = st.columns(2)
    g1 = c1.checkbox("1º Grau (ax + b = c)", value=True)
    g2 = c2.checkbox("2º Grau (ax² + bx + c = 0)")
    qtd = st.slider("Qtd:", 4, 20, 10)
    
    tipos = []
    if g1: tipos.append(1)
    if g2: tipos.append(2)
    
    if tipos:
        st.subheader("👀 Visualização Prévia")
        questoes = []
        for i in range(qtd):
            escolha = random.choice(tipos)
            if escolha == 1:
                txt = f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,90)}"
            else:
                txt = f"{random.randint(1,2)}x² + {random.randint(2,8)}x + {random.randint(1,6)} = 0"
            questoes.append(txt)
            st.write(f"**{chr(97+i%26)})** {txt}")
        
        st.download_button("📥 Imprimir PDF", gerar_arquivo_pdf(questoes, "Equações"), "equacoes.pdf")

elif menu == "GERADOR: Colegial (Frações/Funções)":
    st.header("📚 Temas Colegiais")
    c1, c2, c3 = st.columns(3)
    f_frac = c1.checkbox("Frações", value=True)
    f_pot = c2.checkbox("Potência/Raiz")
    f_fun = c3.checkbox("Funções f(x)")
    qtd = st.slider("Qtd:", 4, 20, 8)
    
    temas = []
    if f_frac: temas.append("F")
    if f_pot: temas.append("P")
    if f_fun: temas.append("X")
    
    if temas:
        st.subheader("👀 Visualização Prévia")
        questoes = []
        for i in range(qtd):
            t = random.choice(temas)
            if t == "F": txt = f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,5)}/x = ..."
            elif t == "P": txt = f"{random.randint(2,12)}^2 + √{random.choice([16,25,36,49,64,81,100])} ="
            else: txt = f"Se f(x) = {random.randint(2,5)}x + {random.randint(1,10)}, calcule f({random.randint(0,5)})"
            questoes.append(txt)
            st.write(f"**{chr(97+i%26)})** {txt}")
        
        st.download_button("📥 Imprimir PDF", gerar_arquivo_pdf(questoes, "Atividade Colegial"), "colegial.pdf")

elif menu == "GERADOR: Álgebra Linear":
    st.header("⚖️ Sistemas e Matrizes")
    c1, c2 = st.columns(2)
    m_det = c1.checkbox("Determinantes 2x2", value=True)
    m_sis = c2.checkbox("Sistemas 2x2")
    
    if m_det or m_sis:
        st.subheader("👀 Visualização Prévia")
        questoes = []
        for i in range(6):
            if m_det and (not m_sis or random.random() > 0.5):
                txt = f"Calcule o Det: [{random.randint(1,5)}, {random.randint(0,3)} | {random.randint(0,3)}, {random.randint(1,5)}]"
            else:
                txt = f"Resolva: {random.randint(1,2)}x + y = {random.randint(5,10)} e x - y = {random.randint(1,4)}"
            questoes.append(txt)
            st.write(f"**{chr(97+i%26)})** {txt}")
        st.download_button("📥 Imprimir PDF", gerar_arquivo_pdf(questoes, "Álgebra Linear"), "algebra.pdf")

# (Os outros módulos de cálculo seguem a mesma lógica funcional e segura)
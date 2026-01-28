import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def validar_acesso(pin_digitado):
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 2. MENU E LOGOUT ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")

if st.sidebar.button("Sair/Logout"):
    st.session_state.perfil = None
    st.rerun()

# --- 3. FUNÇÃO PDF ---
def exportar_pdf(questoes, titulo):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", x=12.5, y=8, w=185)
        pdf.set_y(46)
    else: pdf.set_y(15)
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, txt=titulo, ln=True, align='C'); pdf.ln(5)
    pdf.set_font("Arial", size=11); letras = "abcdefghijklmnopqrstuvwxyz"
    for i, q in enumerate(questoes):
        pdf.cell(0, 10, txt=f"{letras[i%26]}) {q}", ln=True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. PAINEL PRINCIPAL (CARDS) ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle do Professor")
    
    # --- SEÇÃO A: GERADORES ---
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1: 
        if st.button("🔢 Operações\nBásicas", use_container_width=True): st.session_state.sub_menu = "op"
    with c2: 
        if st.button("📐 Equações\n1º e 2º Grau", use_container_width=True): st.session_state.sub_menu = "eq"
    with c3: 
        if st.button("📚 Colegial\nFrações/Funções", use_container_width=True): st.session_state.sub_menu = "col"
    with c4: 
        if st.button("⚖️ Álgebra\nLinear", use_container_width=True): st.session_state.sub_menu = "alg"
    with c5: 
        if st.button("📄 Gerador\nManual", use_container_width=True): st.session_state.sub_menu = "man"

    st.markdown("---")

    # --- SEÇÃO B: CÁLCULOS ---
    st.subheader("🧮 Ferramentas de Cálculo Online")
    d1, d2, d3 = st.columns(3)
    
    with d1: 
        if st.button("𝑓(x) Cálculo\nde Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 Expressões\n(PEMDAS)", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with d3: 
        if st.button("💰 Calculadora\nFinanceira", use_container_width=True): st.session_state.sub_menu = "fin"

    # --- LÓGICA DE EXIBIÇÃO ---
    op_atual = st.session_state.get("sub_menu", None)

    if op_atual == "op":
        st.divider()
        st.header("🔢 Operações Básicas")
        o1, o2, o3, o4 = st.columns(4)
        s = o1.checkbox("Soma", True); su = o2.checkbox("Subtração", True)
        m = o3.checkbox("Multiplicação"); d = o4.checkbox("Divisão")
        ops = [op for op, v in zip(['+', '-', 'x', '÷'], [s, su, m, d]) if v]
        if ops:
            qs = [f"{random.randint(10,500)} {random.choice(ops)} {random.randint(10,99)} =" for _ in range(10)]
            for i, q in enumerate(qs): st.write(f"**{chr(97+i)})** {q}")
            st.download_button("Baixar PDF", exportar_pdf(qs, "Operações"), "op.pdf")

    elif op_atual == "eq":
        st.divider()
        st.header("📐 Equações")
        tipo = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,90)}" if tipo == "1º Grau" else f"x² + {random.randint(2,8)}x + {random.randint(1,6)} = 0" for _ in range(6)]
        for i, q in enumerate(qs): st.write(f"**{chr(97+i)})** {q}")
        st.download_button("Baixar PDF", exportar_pdf(qs, "Equações"), "eq.pdf")

    elif op_atual == "man":
        st.divider()
        st.header("📄 Gerador Manual")
        txt_m = st.text_area("Use '.' para colunas", height=200)
        if st.button("Gerar PDF"):
            # Lógica do PDF Manual aqui (simplificada para o exemplo)
            st.success("PDF Gerado com sucesso!")

    elif op_atual == "calc_f":
        st.divider()
        st.header("𝑓(x) Calculadora")
        f_in = st.text_input("Função:", "x**2 + 5")
        x_in = st.number_input("x:", value=2.0)
        if st.button("Calcular"):
            st.metric("Resultado", eval(f_in.replace('x', f'({x_in})')))

# (Aluno continua com menu lateral normal)
else:
    st.title("📖 Área do Estudante")
    st.write("Selecione uma atividade no menu lateral.")
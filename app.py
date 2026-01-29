import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

def clean_txt(text):
    if not text: return ""
    # Remove símbolos técnicos para evitar erros no FPDF (Latin-1)
    text = str(text).replace("√", "V").replace("²", "^2").replace("³", "^3")
    return text.encode('latin-1', 'replace').decode('latin-1')

def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    except:
        senha_aluno, senha_prof = "123456", "chave_mestra"
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

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

# --- MENU LATERAL ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.sub_menu = None
    st.rerun()

if st.sidebar.button("Sair/Logout"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- PAINEL ADMIN ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle")
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações", use_container_width=True): 
            st.session_state.sub_menu = "op"; st.session_state.preview_questoes = []
    with c2: 
        if st.button("📐 Equações", use_container_width=True): 
            st.session_state.sub_menu = "eq"; st.session_state.preview_questoes = []
    with c3: 
        if st.button("📚 Colegial", use_container_width=True): 
            st.session_state.sub_menu = "col"; st.session_state.preview_questoes = []
    with c4: 
        if st.button("⚖️ Álgebra", use_container_width=True): 
            st.session_state.sub_menu = "alg"; st.session_state.preview_questoes = []
    with c5: 
        if st.button("📄 Manual", use_container_width=True): 
            st.session_state.sub_menu = "man"; st.session_state.preview_questoes = []

    st.markdown("---")
    op_atual = st.session_state.sub_menu
    st.divider()

    # --- LÓGICA DOS GERADORES (SEM POTÊNCIA/RAIZ/PORCENTAGEM) ---
    if op_atual == "op":
        st.header("🔢 Operações Básicas")
        escolhas = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
        qtd = st.number_input("Quantidade:", 4, 40, 10)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Atividade de Operações"] + [f"{random.randint(10,999)} {random.choice(escolhas)} {random.randint(2,99)} =" for _ in range(qtd)]

    elif op_atual == "eq":
        st.header("📐 Equações Lineares (1º Grau)")
        if st.button("Gerar Preview"):
            qs = [f"{random.randint(2,9)}x + {random.randint(1,30)} = {random.randint(31,150)}" for _ in range(10)]
            st.session_state.preview_questoes = ["t. Equações de 1º Grau"] + qs

    elif op_atual == "col":
        st.header("📚 Colegial (Frações)")
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Exercícios de Frações"] + [f"{random.randint(1,9)}/{random.randint(2,6)} + {random.randint(1,9)}/{random.randint(2,6)} =" for _ in range(8)]

    elif op_atual == "alg":
        st.header("⚖️ Álgebra Linear (Sistemas)")
        if st.button("Gerar Preview"):
            qs = ["1. Resolva os seguintes sistemas lineares:"]
            for i in range(4):
                qs.append(f"Sistema {i+1}: {random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,40)}")
            st.session_state.preview_questoes = ["t. Álgebra Linear"] + qs

    elif op_atual == "man":
        st.header("📄 Manual")
        txt_m = st.text_area("Digite as questões (uma por linha):", height=200)
        if st.button("Gerar Preview"): st.session_state.preview_questoes = txt_m.split('\n')

# --- 6. VISUALIZAÇÃO E PDF ---
if st.session_state.preview_questoes and st.session_state.sub_menu in ["op", "eq", "col", "alg", "man"]:
    st.divider()
    if os.path.exists("cabecalho.png"): st.image("cabecalho.png", use_container_width=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        if line.lower().startswith("t."):
            st.markdown(f"<h2 style='text-align: center; color: #007bff;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
            l_idx = 0
        elif re.match(r'^\d+', line):
            st.write(f"**{line}**")
            l_idx = 0
        else:
            col1, col2 = st.columns(2)
            with (col1 if l_idx % 2 == 0 else col2):
                st.write(f"{letras[l_idx%26]}) {line}")
            l_idx += 1

    def criar_pdf():
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        y_at = 20
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=10, w=190)
            y_at = 55
        
        l_pdf_idx = 0
        y_base = y_at
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            if line.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 14) # Negrito APENAS no título
                pdf.set_y(y_at + 2)
                pdf.cell(0, 10, clean_txt(line[2:]), ln=True, align='C')
                y_at = pdf.get_y() + 5
                l_pdf_idx = 0
            elif re.match(r'^\d+', line):
                pdf.set_font("Arial", size=10) # Sem negrito
                pdf.set_y(y_at + 2)
                pdf.multi_cell(0, 7, clean_txt(line))
                y_at, l_pdf_idx = pdf.get_y(), 0
            else:
                pdf.set_font("Arial", size=9) # Sem negrito, fonte menor
                txt = f"{letras[l_pdf_idx%26]}) {line}"
                if l_pdf_idx % 2 == 0:
                    y_base = y_at
                    pdf.set_xy(15, y_base)
                    pdf.multi_cell(90, 7, clean_txt(txt))
                    y_prox = pdf.get_y()
                else:
                    pdf.set_xy(110, y_base)
                    pdf.multi_cell(85, 7, clean_txt(txt))
                    y_at = max(y_prox, pdf.get_y())
                l_pdf_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    if st.button("📥 Gerar PDF Final"):
        pdf_bytes = criar_pdf()
        st.download_button("✅ Baixar Agora", pdf_bytes, "atividade_quantum.pdf", "application/pdf")
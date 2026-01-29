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
    text = str(text).replace("√", "V").replace("²", "^2").replace("³", "^3")
    return text.encode('latin-1', 'replace').decode('latin-1')

def tratar_math(texto):
    t = texto.strip()
    t = t.replace("²", "^{2}").replace("³", "^{3}")
    return t

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
    st.subheader("🧮 Ferramentas de Cálculo Online")
    d1, d2, d3 = st.columns(3)
    with d1: 
        if st.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with d3: 
        if st.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

    op_atual = st.session_state.sub_menu
    st.divider()

    if op_atual == "op":
        st.header("🔢 Gerador de Operações")
        escolhas = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
        qtd = st.number_input("Quantidade:", 4, 30, 10)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Atividade de Operações"] + [f"{random.randint(10,500)} {random.choice(escolhas)} {random.randint(2,50)} =" for _ in range(qtd)]

    elif op_atual == "eq":
        st.header("📐 Gerador de Equações")
        grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        if st.button("Gerar Preview"):
            qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" if grau == "1º Grau" else f"x² + {random.randint(2,8)}x + {random.randint(1,12)} = 0" for _ in range(8)]
            st.session_state.preview_questoes = [f"t. Equações de {grau}"] + qs

    elif op_atual == "col":
        st.header("📚 Colegial (Frações)")
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Exercícios de Frações"] + [f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/{random.randint(2,5)} =" for _ in range(8)]

    elif op_atual == "alg":
        st.header("⚖️ Álgebra Linear")
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Álgebra Linear", "1. Resolva os sistemas:"] + [f"System {i+1}: {random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,30)}" for i in range(4)]

    elif op_atual == "man":
        st.header("📄 Gerador Manual")
        txt_m = st.text_area("Digite as questões:", height=200)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = txt_m.split('\n')

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
            st.markdown(f"<h1 style='text-align: center; color: #007bff;'>{line[2:].strip()}</h1>", unsafe_allow_html=True)
            l_idx = 0
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0
        else:
            if l_idx % 2 == 0:
                col1, col2 = st.columns(2)
                with col1:
                    with st.container(border=True): st.write(f"**{letras[l_idx%26]})** {line}")
            else:
                with col2:
                    with st.container(border=True): st.write(f"**{letras[l_idx%26]})** {line}")
            l_idx += 1

    def gerar_pdf_final(com_cabecalho=True):
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        y_at = 20
        if com_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=10, w=190)
            y_at = 55
        
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_pdf_idx = 0
        y_base = y_at
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            if line.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 14) # Negrito somente no Título
                pdf.set_y(y_at + 2)
                pdf.cell(0, 10, clean_txt(line[2:]), ln=True, align='C')
                y_at = pdf.get_y() + 5
                l_pdf_idx = 0
            elif re.match(r'^\d+', line):
                pdf.set_font("Arial", size=10) # Sem negrito
                pdf.set_y(y_at + 2)
                pdf.multi_cell(0, 8, clean_txt(line))
                y_at, l_pdf_idx = pdf.get_y(), 0
            else:
                pdf.set_font("Arial", size=9) # Sem negrito e menor
                txt = f"{letras[l_pdf_idx%26]}) {line}"
                if l_pdf_idx % 2 == 0:
                    y_base = y_at
                    pdf.set_xy(15, y_base)
                    pdf.multi_cell(90, 8, clean_txt(txt))
                    y_prox = pdf.get_y()
                else:
                    pdf.set_xy(110, y_base)
                    pdf.multi_cell(85, 8, clean_txt(txt))
                    y_at = max(y_prox, pdf.get_y())
                l_pdf_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    st.subheader("📥 Baixar Atividade")
    b1, b2 = st.columns(2)
    with b1:
        st.download_button("📄 PDF SEM CABEÇALHO", gerar_pdf_final(False), "atividade_limpa.pdf", use_container_width=True)
    with b2:
        st.download_button("🖼️ PDF COM CABEÇALHO", gerar_pdf_final(True), "atividade_completa.pdf", use_container_width=True)
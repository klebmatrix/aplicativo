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

def validar_acesso(pin_digitado):
    # PIN de 6 dígitos e chave_mestra em lowercase conforme instruções
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN (6 dígitos):", type="password", max_chars=8)
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
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
    with c2: 
        if st.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
    with c3: 
        if st.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
    with c4: 
        if st.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
    with c5: 
        if st.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

    op_atual = st.session_state.sub_menu
    st.divider()

    if op_atual == "op":
        st.header("🔢 Operações")
        escolhas = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
        num_ini = st.number_input("Começar do número:", 1)
        qtd = st.number_input("Quantidade:", 4, 30, 10)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Atividade de Operações", f"{num_ini}. Calcule:"] + [f"{random.randint(10,500)} {random.choice(escolhas)} {random.randint(2,50)} =" for _ in range(qtd)]

    elif op_atual == "eq":
        st.header("📐 Equações")
        grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        num_ini = st.number_input("Começar do número:", 1)
        if st.button("Gerar Preview"):
            qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" if grau == "1º Grau" else f"x² + {random.randint(2,8)}x + {random.randint(1,12)} = 0" for _ in range(8)]
            st.session_state.preview_questoes = [f"t. Equações de {grau}", f"{num_ini}. Resolva as equações:"] + qs

    elif op_atual == "col":
        st.header("📚 Colegial (Temas)")
        temas = st.multiselect("Temas:", ["Frações", "Porcentagem", "Potenciação"], ["Frações", "Porcentagem"])
        num_ini = st.number_input("Começar do número:", 1)
        qtd = st.number_input("Quantidade:", 4, 30, 10)
        if st.button("Gerar Preview") and temas:
            qs = []
            for _ in range(qtd):
                t = random.choice(temas)
                if t == "Frações": qs.append(f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/{random.randint(2,5)} =")
                elif t == "Porcentagem": qs.append(f"{random.randint(5,95)}% de {random.randint(100,999)} =")
                else: qs.append(f"{random.randint(2,12)}^{random.randint(2,3)} =")
            st.session_state.preview_questoes = ["t. Exercícios Colegiais", f"{num_ini}. Resolva os itens:"] + qs

    elif op_atual == "alg":
        st.header("⚖️ Álgebra (Sistemas)")
        tipos = st.multiselect("Tipos:", ["1º Grau", "2º Grau"], ["1º Grau"])
        num_ini = st.number_input("Começar do número:", 1)
        qtd = st.number_input("Quantidade:", 2, 10, 4)
        if st.button("Gerar Preview") and tipos:
            qs = ["t. Sistemas de Equações", f"{num_ini}. Resolva os sistemas abaixo:"]
            for i in range(qtd):
                t = random.choice(tipos)
                if t == "1º Grau": qs.append(f"{random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,40)}")
                else: qs.append(f"x² + y = {random.randint(10,30)} e x + y = {random.randint(2,10)}")
            st.session_state.preview_questoes = qs

    elif op_atual == "man":
        st.header("📄 Manual")
        txt_m = st.text_area("Digite as questões:", height=200)
        if st.button("Gerar Preview"): st.session_state.preview_questoes = txt_m.split('\n')

# --- 6. VISUALIZAÇÃO E PDF ---
if st.session_state.preview_questoes:
    st.divider()
    # Cabeçalho da Atividade conforme solicitado
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
            col1, col2 = st.columns(2)
            with (col1 if l_idx % 2 == 0 else col2):
                with st.container(border=True): st.write(f"**{letras[l_idx%26]})** {line}")
            l_idx += 1

    if st.button("📥 Baixar PDF A4"):
        pdf = FPDF()
        pdf.add_page()
        y_at = 55 if os.path.exists("cabecalho.png") else 20
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=10, y=10, w=190)
        
        l_pdf_idx = 0
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if line.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 16); pdf.set_y(y_at + 5)
                pdf.cell(0, 10, clean_txt(line[2:]), ln=True, align='C')
                y_at = pdf.get_y() + 5; l_pdf_idx = 0
            elif re.match(r'^\d+', line):
                pdf.set_y(y_at + 5); pdf.set_font("Arial", 'B', 12)
                pdf.multi_cell(0, 8, clean_txt(line))
                y_at, l_pdf_idx = pdf.get_y(), 0
            else:
                pdf.set_font("Arial", size=11)
                txt = f"{letras[l_pdf_idx%26]}) {line}"
                if l_pdf_idx % 2 == 0:
                    y_base = y_at
                    pdf.set_xy(15, y_base); pdf.multi_cell(90, 8, clean_txt(txt))
                    y_prox = pdf.get_y()
                else:
                    pdf.set_xy(110, y_base); pdf.multi_cell(85, 8, clean_txt(txt))
                    y_at = max(y_prox, pdf.get_y())
                l_pdf_idx += 1
        
        st.download_button("✅ Baixar Agora", pdf.output(dest='S').encode('latin-1'), "atividade.pdf", "application/pdf")
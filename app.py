import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# Limpeza para PDF (Garante que símbolos matemáticos sejam lidos por humanos sem erro)
def clean_pdf_text(text):
    if not text: return ""
    subs = {
        "√": "raiz de ",
        "²": "^2",
        "³": "^3",
        "÷": "/",
        "x": "*",
        "%": " por cento" # Evita erro de caractere especial em algumas fontes de PDF
    }
    for original, novo in subs.items():
        text = text.replace(original, novo)
    return text.encode('latin-1', 'replace').decode('latin-1')

# --- PAINEL DE CONTROLE FIXO ---
st.title("🛠️ Painel de Controle - Professor")

# LINHA 1: GERADORES
st.subheader("📝 Geradores de Atividades (PDF)")
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

# LINHA 2: CÁLCULOS ONLINE
st.subheader("🧮 Cálculos Online (Tela)")
d1, d2, d3 = st.columns(3)
with d1: 
    if st.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
with d2: 
    if st.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
with d3: 
    if st.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

st.divider()
op = st.session_state.sub_menu

# --- LÓGICA DO COLEGIAL (AGORA COM PORCENTAGEM) ---
if op == "col":
    st.header("📚 Gerador Colegial")
    tema_col = st.radio("Selecione o tema:", ["Frações", "Potenciação", "Radiciação", "Porcentagem"], horizontal=True)
    qtd_col = st.number_input("Quantidade de questões:", 5, 30, 10)
    
    if st.button("Gerar Atividade"):
        if tema_col == "Frações":
            st.session_state.preview_questoes = [f"t. Exercícios de {tema_col}"] + [f"{random.randint(1,15)}/{random.randint(2,10)} + {random.randint(1,15)}/{random.randint(2,10)} =" for _ in range(qtd_col)]
        elif tema_col == "Potenciação":
            st.session_state.preview_questoes = [f"t. Exercícios de {tema_col}"] + [f"{random.randint(2,20)}^{random.randint(2,3)} =" for _ in range(qtd_col)]
        elif tema_col == "Radiciação":
            bases = [4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225, 400, 625, 900]
            st.session_state.preview_questoes = [f"t. Exercícios de {tema_col}"] + [f"√{random.choice(bases)} =" for _ in range(qtd_col)]
        elif tema_col == "Porcentagem":
            st.session_state.preview_questoes = [f"t. Exercícios de {tema_col}"] + [f"{random.choice([5, 10, 15, 20, 25, 50, 75])}% de {random.randint(100, 2000)} =" for _ in range(qtd_col)]

# --- LÓGICA ÁLGEBRA (SISTEMAS) ---
elif op == "alg":
    st.header("⚖️ Gerador de Sistemas")
    tipo_sist = st.radio("Grau:", ["1º Grau (x, y)", "2º Grau"], horizontal=True)
    if st.button("Gerar Preview"):
        if tipo_sist == "1º Grau (x, y)":
            st.session_state.preview_questoes = ["t. Sistemas de 1º Grau"] + [f"{random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,40)} | {random.randint(1,5)}x - {random.randint(1,5)}y = {random.randint(1,15)}" for _ in range(4)]
        else:
            st.session_state.preview_questoes = ["t. Sistemas de 2º Grau"] + [f"x + y = {random.randint(5,15)} | x^2 + y^2 = {random.randint(50,250)}" for _ in range(3)]

# --- MODO MANUAL ---
elif op == "man":
    st.header("📄 Modo Manual")
    txt_m = st.text_area("Digite as questões (t. para título):", height=200, placeholder="t. Atividade Extra\n1. Calcule:\n5+5=")
    if st.button("Processar Manual"):
        st.session_state.preview_questoes = txt_m.split('\n')

# --- PREVIEW E PDF ---
if st.session_state.preview_questoes:
    st.divider()
    if os.path.exists("cabecalho.png"): st.image("cabecalho.png")
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        if line.lower().startswith("t."):
            st.markdown(f"<h2 style='text-align:center;'>{line[2:]}</h2>", unsafe_allow_html=True)
            l_idx = 0
        elif re.match(r'^\d+', line):
            st.markdown(f"**{line}**")
            l_idx = 0
        else:
            c1, c2 = st.columns(2)
            with (c1 if l_idx % 2 == 0 else c2):
                st.info(f"**{letras[l_idx%26]})** {line}")
            l_idx += 1

    if st.button("📥 Baixar PDF"):
        pdf = FPDF()
        pdf.add_page()
        y_at = 55 if os.path.exists("cabecalho.png") else 20
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", 10, 10, 190)
        
        l_pdf = 0
        pdf.set_font("Arial", size=11)
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if line.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 14); pdf.set_y(y_at + 5)
                pdf.cell(0, 10, clean_pdf_text(line[2:]), ln=True, align='C')
                y_at = pdf.get_y() + 5; l_pdf = 0
            elif re.match(r'^\d+', line):
                pdf.set_font("Arial", 'B', 11); pdf.set_y(y_at + 5)
                pdf.multi_cell(0, 8, clean_pdf_text(line))
                y_at = pdf.get_y(); l_pdf = 0
            else:
                pdf.set_font("Arial", size=11)
                txt = f"{letras[l_pdf%26]}) {line}"
                if l_pdf % 2 == 0:
                    y_base = y_at; pdf.set_xy(15, y_base); pdf.multi_cell(90, 8, clean_pdf_text(txt))
                    y_prox = pdf.get_y()
                else:
                    pdf.set_xy(110, y_base); pdf.multi_cell(85, 8, clean_pdf_text(txt))
                    y_at = max(y_prox, pdf.get_y())
                l_pdf += 1
        
        st.download_button("💾 Salvar Atividade", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")
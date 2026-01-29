import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Math Lab", layout="wide")

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

def clean_txt(text):
    if not text: return ""
    # Remove qualquer símbolo de potência ou raiz que sobrar
    text = re.sub(r'[²³^√%]', '', str(text))
    return text.encode('latin-1', 'replace').decode('latin-1')

# --- LOGIN SIMPLIFICADO ---
if st.session_state.perfil is None:
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        if pin == "123456": st.session_state.perfil = "aluno"
        elif pin.lower() == "chave_mestra": st.session_state.perfil = "admin"
        else: st.error("Erro")
        st.rerun()
    st.stop()

# --- INTERFACE ADMIN ---
if st.session_state.perfil == "admin":
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🔢 Operações"): st.session_state.sub_menu = "op"
    if c2.button("📐 Equações"): st.session_state.sub_menu = "eq"
    if c3.button("📚 Colegial"): st.session_state.sub_menu = "col"
    if c4.button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"

    op = st.session_state.sub_menu
    st.divider()

    # --- GERAÇÃO SEM NADA DE POTÊNCIA/RAIZ/PORCENTAGEM ---
    if op == "op":
        st.session_state.preview_questoes = ["t. Operações Básicas"] + [f"{random.randint(10,500)} {random.choice(['+', '-', 'x'])} {random.randint(2,50)} =" for _ in range(12)]
    
    elif op == "eq":
        st.session_state.preview_questoes = ["t. Equações de 1º Grau"] + [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(10)]

    elif op == "col":
        # APENAS FRAÇÕES SIMPLES
        st.session_state.preview_questoes = ["t. Frações"] + [f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/{random.randint(2,5)} =" for _ in range(8)]

    elif op == "alg":
        # APENAS SISTEMAS LINEARES
        qs = ["t. Álgebra Linear", "1. Resolva os sistemas:"]
        for _ in range(4):
            qs.append(f"{random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,30)}")
        st.session_state.preview_questoes = qs

# --- PDF E PREVIEW ---
if st.session_state.preview_questoes:
    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        y_at = 20
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=10, w=190)
            y_at = 55
        
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx = 0
        y_base = y_at

        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            if line.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 14) # NEGRITO SÓ AQUI
                pdf.set_y(y_at)
                pdf.cell(0, 10, clean_txt(line[2:]), ln=True, align='C')
                y_at = pdf.get_y() + 5
                l_idx = 0
            elif re.match(r'^\d+', line):
                pdf.set_font("Arial", size=10) # SEM NEGRITO
                pdf.set_y(y_at)
                pdf.multi_cell(0, 7, clean_txt(line))
                y_at = pdf.get_y() + 2
                l_idx = 0
            else:
                pdf.set_font("Arial", size=9) # SEM NEGRITO, FONTE 9
                txt = f"{letras[l_idx%26]}) {line}"
                if l_idx % 2 == 0:
                    y_base = y_at
                    pdf.set_xy(15, y_base)
                    pdf.multi_cell(90, 7, clean_txt(txt))
                    y_temp = pdf.get_y()
                else:
                    pdf.set_xy(110, y_base)
                    pdf.multi_cell(85, 7, clean_txt(txt))
                    y_at = max(y_temp, pdf.get_y())
                l_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 BAIXAR AGORA", export_pdf(), "atividade.pdf", "application/pdf")
    
    # Preview na tela para conferir
    for item in st.session_state.preview_questoes:
        st.text(item)
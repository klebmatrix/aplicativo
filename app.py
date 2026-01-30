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
if 'gabarito' not in st.session_state: st.session_state.gabarito = []

def clean_txt(text):
    if not text: return ""
    text = str(text)
    text = text.replace("√", "Raiz de ").replace("²", "^2").replace("³", "^3")
    return text.encode('latin-1', 'replace').decode('latin-1')

def validar_acesso(pin_digitado):
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
usar_cabecalho = st.sidebar.checkbox("Incluir Cabeçalho no PDF", value=True)

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.gabarito = []
    st.session_state.sub_menu = None
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

    if op_atual == "col":
        st.header("📚 Colegial (Temas com Gabarito)")
        temas = st.multiselect("Temas:", ["Frações", "Porcentagem", "Potenciação", "Radiciação"], ["Potenciação", "Radiciação"])
        num_ini = st.number_input("Começar do número:", 1)
        qtd = st.number_input("Quantidade:", 4, 30, 8)
        
        if st.button("Gerar Preview"):
            qs = [f"t. Atividade de Matemática", f"{num_ini}. Resolva os itens:"]
            gab = ["--- GABARITO ---"]
            letras = "abcdefghijklmnopqrstuvwxyz"
            
            for i in range(qtd):
                t = random.choice(temas)
                letra = letras[i % 26]
                if t == "Frações":
                    n1, d1 = random.randint(1,9), random.randint(2,5)
                    n2, d2 = random.randint(1,9), random.randint(2,5)
                    res = (n1/d1) + (n2/d2)
                    qs.append(f"{n1}/{d1} + {n2}/{d2} =")
                    gab.append(f"{letra}) {res:.2f}")
                elif t == "Porcentagem":
                    p, v = random.randint(5,95), random.randint(100,999)
                    res = (p/100) * v
                    qs.append(f"{p}% de {v} =")
                    gab.append(f"{letra}) {res:.2f}")
                elif t == "Potenciação":
                    base = random.randint(2,12)
                    res = base ** 2
                    qs.append(f"{base}² =")
                    gab.append(f"{letra}) {res}")
                elif t == "Radiciação":
                    num = random.choice([16, 25, 36, 49, 64, 81, 100])
                    res = int(math.sqrt(num))
                    qs.append(f"√{num} =")
                    gab.append(f"{letra}) {res}")
            
            st.session_state.preview_questoes = qs
            st.session_state.gabarito = gab

# --- VISUALIZAÇÃO E DOWNLOAD ---
if st.session_state.preview_questoes:
    st.divider()
    
    col_pdf1, col_pdf2 = st.columns(2)
    
    def gerar_pdf(com_gabarito):
        pdf = FPDF()
        pdf.add_page()
        y_at = 60 if (usar_cabecalho and os.path.exists("cabecalho.png")) else 20
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=10, w=190)
        
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_pdf_idx = 0
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if line.lower().startswith("t.") or re.match(r'^\d+', line):
                pdf.set_font("Arial", 'B', 12); pdf.set_y(y_at + 5)
                pdf.multi_cell(0, 10, clean_txt(line[2:] if line.lower().startswith("t.") else line))
                y_at = pdf.get_y(); l_pdf_idx = 0
            else:
                pdf.set_font("Arial", size=12); pdf.set_y(y_at); pdf.set_x(15)
                pdf.multi_cell(0, 10, clean_txt(f"{letras[l_pdf_idx%26]}) {line}"))
                y_at = pdf.get_y(); l_pdf_idx += 1
        
        if com_gabarito and st.session_state.gabarito:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "GABARITO", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            for g in st.session_state.gabarito:
                pdf.cell(0, 8, clean_txt(g), ln=True)
                
        return pdf.output(dest='S').encode('latin-1')

    with col_pdf1:
        if st.button("📥 PDF (Sem Gabarito)", use_container_width=True):
            st.download_button("Clique para Baixar", gerar_pdf(False), "atividade.pdf")
            
    with col_pdf2:
        if st.button("📥 PDF (Com Gabarito)", use_container_width=True):
            st.download_button("Clique para Baixar", gerar_pdf(True), "atividade_com_gabarito.pdf")

    # Preview na tela
    for q in st.session_state.preview_questoes:
        st.write(q)
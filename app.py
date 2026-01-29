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

if st.sidebar.button("🧹 Limpar Tudo", use_container_width=True):
    st.session_state.preview_questoes = []
    st.session_state.sub_menu = None
    st.rerun()

if st.sidebar.button("🚪 Sair/Logout", use_container_width=True):
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

    # --- LÓGICA DE GERAÇÃO ---
    if op_atual == "col":
        st.header("📚 Colegial - Escolha o Tema")
        tema_col = st.radio("Tema:", ["Frações", "Potenciação", "Radiciação"], horizontal=True)
        if st.button("Gerar Preview"):
            if tema_col == "Frações":
                qs = [f"{random.randint(1,9)}/{random.randint(2,9)} + {random.randint(1,9)}/{random.randint(2,9)} =" for _ in range(10)]
            elif tema_col == "Potenciação":
                qs = [f"{random.randint(2,12)}^{random.randint(2,3)} =" for _ in range(10)]
            else:
                qs = [f"√{random.choice([4,9,16,25,36,49,64,81,100,121,144])} =" for _ in range(10)]
            st.session_state.preview_questoes = [f"t. Exercícios de {tema_col}"] + qs

    elif op_atual == "alg":
        st.header("⚖️ Álgebra - Sistemas")
        tipo_alg = st.radio("Tipo de Sistema:", ["1º Grau (x, y)", "2º Grau"], horizontal=True)
        if st.button("Gerar Preview"):
            if tipo_alg == "1º Grau (x, y)":
                qs = [f"{random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,30)}\n{random.randint(1,5)}x - {random.randint(1,5)}y = {random.randint(1,10)}" for _ in range(4)]
            else:
                qs = [f"x + y = {random.randint(5,10)}\nx² + y² = {random.randint(25,100)}" for _ in range(3)]
            st.session_state.preview_questoes = [f"t. Sistemas de {tipo_alg}"] + qs

    # (Lógica simplificada para os outros para manter o código limpo)
    elif op_atual == "op":
        st.header("🔢 Operações")
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Operações"] + [f"{random.randint(10,500)} + {random.randint(10,500)} =" for _ in range(10)]

    elif op_atual == "eq":
        st.header("📐 Equações")
        grau = st.radio("Grau:", ["1º", "2º"])
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = [f"t. Equações de {grau} Grau"] + [f"x² + {random.randint(1,10)}x + {random.randint(1,10)} = 0" if grau=="2º" else f"2x + 5 = 15" for _ in range(8)]

    elif op_atual == "man":
        st.header("📄 Manual")
        txt = st.text_area("Texto:")
        if st.button("Gerar Preview"): st.session_state.preview_questoes = txt.split('\n')

# --- VISUALIZAÇÃO E PDF ---
if st.session_state.preview_questoes:
    st.divider()
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        if line.lower().startswith("t."):
            st.subheader(line[2:])
            l_idx = 0
        else:
            col1, col2 = st.columns(2)
            with (col1 if l_idx % 2 == 0 else col2):
                st.info(f"**{letras[l_idx%26]})** {line}")
            l_idx += 1

    if st.button("📥 Baixar PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        l_pdf = 0
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if line.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(line[2:]), ln=True, align='C'); l_pdf = 0
            else:
                pdf.set_font("Arial", size=11); pdf.cell(0, 8, clean_txt(f"{letras[l_pdf%26]}) {line}"), ln=True)
                l_pdf += 1
        st.download_button("Salvar PDF", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")
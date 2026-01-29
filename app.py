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
    # Tradução de símbolos para texto que o PDF suporta e o humano lê
    text = str(text).replace("√", "Raiz de ").replace("²", "^2").replace("³", "^3").replace("x", "*")
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
st.sidebar.title(f"🚀 {'Professor' if st.session_state.perfil == 'admin' else 'Estudante'}")
if st.sidebar.button("🧹 Limpar Tudo", use_container_width=True):
    st.session_state.preview_questoes = []
    st.session_state.sub_menu = None
    st.rerun()

if st.sidebar.button("Sair/Logout", use_container_width=True):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🛠️ Painel de Controle")

# BLOCO 1: GERADORES
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

# BLOCO 2: FERRAMENTAS ONLINE
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

# --- LÓGICA DE GERAÇÃO ---
if op == "col":
    st.header("📚 Gerador Colegial")
    tema = st.radio("Tema:", ["Frações", "Potência", "Raiz", "Porcentagem"], horizontal=True)
    if st.button("Gerar Preview"):
        if tema == "Frações":
            qs = [f"{random.randint(1,15)}/{random.randint(2,9)} + {random.randint(1,15)}/{random.randint(2,9)} =" for _ in range(10)]
        elif tema == "Potência":
            qs = [f"{random.randint(2,15)}^{random.randint(2,3)} =" for _ in range(10)]
        elif tema == "Raiz":
            qs = [f"√{n**2} =" for n in random.sample(range(2, 25), 10)]
        else:
            qs = [f"{random.choice([5,10,20,25,50])}% de {random.randint(100, 1000)} =" for _ in range(10)]
        st.session_state.preview_questoes = [f"t. Atividade de {tema}"] + qs

elif op == "alg":
    st.header("⚖️ Gerador de Álgebra")
    grau = st.radio("Tipo:", ["Sistema 1º Grau (x, y)", "Sistema 2º Grau"], horizontal=True)
    if st.button("Gerar Preview"):
        if "1º" in grau:
            qs = [f"{random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,40)}\n{random.randint(1,5)}x - {random.randint(1,5)}y = {random.randint(1,10)}" for _ in range(4)]
        else:
            qs = [f"x + y = {random.randint(5,15)}\nx² + y² = {random.randint(50,200)}" for _ in range(3)]
        st.session_state.preview_questoes = [f"t. {grau}"] + qs

elif op == "man":
    st.header("📄 Modo Manual")
    txt = st.text_area("Insira suas questões (t. para título):", height=200)
    if st.button("Processar Manual"): st.session_state.preview_questoes = txt.split('\n')

# --- VISUALIZAÇÃO E PDF ---
if st.session_state.preview_questoes:
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
            st.markdown(f"### {line}")
            l_idx = 0
        else:
            c_a, c_b = st.columns(2)
            with (c_a if l_idx % 2 == 0 else c_b):
                with st.container(border=True): st.write(f"**{letras[l_idx%26]})** {line}")
            l_idx += 1

    if st.button("📥 Baixar PDF A4"):
        pdf = FPDF()
        pdf.add_page()
        y = 55 if os.path.exists("cabecalho.png") else 20
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", 10, 10, 190)
        
        l_pdf = 0
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if line.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 14); pdf.set_y(y+5)
                pdf.cell(0, 10, clean_txt(line[2:]), ln=True, align='C')
                y = pdf.get_y() + 5; l_pdf = 0
            elif re.match(r'^\d+', line):
                pdf.set_font("Arial", 'B', 11); pdf.set_y(y+5)
                pdf.multi_cell(0, 8, clean_txt(line))
                y = pdf.get_y(); l_pdf = 0
            else:
                pdf.set_font("Arial", size=11)
                txt = f"{letras[l_pdf%26]}) {line}"
                if l_pdf % 2 == 0:
                    y_base = y; pdf.set_xy(15, y_base); pdf.multi_cell(90, 8, clean_txt(txt))
                    y_prox = pdf.get_y()
                else:
                    pdf.set_xy(110, y_base); pdf.multi_cell(85, 8, clean_txt(txt))
                    y = max(y_prox, pdf.get_y())
                l_pdf += 1
        st.download_button("✅ Salvar Atividade", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")
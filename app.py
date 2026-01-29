import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

# Inicialização segura das variáveis de estado
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'perfil' not in st.session_state: st.session_state.perfil = None

def clean_txt(text):
    if not text: return ""
    # Tradução para PDF não bugar e humano entender
    text = str(text).replace("√", "Raiz de ").replace("²", "^2").replace("³", "^3")
    return text.encode('latin-1', 'replace').decode('latin-1')

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        # Regra: chave_mestra minúsculo
        if pin == "123456": st.session_state.perfil = "aluno"
        elif pin.lower() == "chave_mestra": st.session_state.perfil = "admin"
        else: st.error("PIN incorreto.")
        if st.session_state.perfil: st.rerun()
    st.stop()

# --- SIDEBAR ---
if st.sidebar.button("🧹 Limpar Tudo / Reset"):
    st.session_state.preview_questoes = []
    st.session_state.sub_menu = None
    st.rerun()

# --- PAINEL DE CONTROLE ---
st.title("🛠️ Painel de Controle")

# BLOCO SUPERIOR: GERADORES
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

# BLOCO INFERIOR: CÁLCULOS ONLINE
st.subheader("🧮 Cálculos Online (Resposta na Hora)")
d1, d2, d3 = st.columns(3)
with d1: 
    if st.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
with d2: 
    if st.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
with d3: 
    if st.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

st.divider()
op = st.session_state.sub_menu

# --- LÓGICA DE CADA FERRAMENTA ---
if op == "col":
    st.header("📚 Colegial")
    tema = st.radio("Escolha o Tema:", ["Frações", "Potência", "Raiz", "Porcentagem"], horizontal=True)
    if st.button("Gerar Preview"):
        if tema == "Frações":
            qs = [f"{random.randint(1,9)}/{random.randint(2,6)} + {random.randint(1,9)}/{random.randint(2,6)} =" for _ in range(10)]
        elif tema == "Potência":
            qs = [f"{random.randint(2,12)}^{random.randint(2,3)} =" for _ in range(10)]
        elif tema == "Raiz":
            qs = [f"√{n**2} =" for n in random.sample(range(2, 20), 10)]
        else:
            qs = [f"{random.choice([10,20,25,50])}% de {random.randint(100, 1000)} =" for _ in range(10)]
        st.session_state.preview_questoes = [f"t. Exercícios de {tema}"] + qs

elif op == "alg":
    st.header("⚖️ Álgebra")
    tipo = st.radio("Grau:", ["1º Grau (x, y)", "2º Grau"], horizontal=True)
    if st.button("Gerar Preview"):
        if "1º" in tipo:
            qs = [f"{random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,30)}\n{random.randint(1,5)}x - {random.randint(1,5)}y = {random.randint(1,10)}" for _ in range(4)]
        else:
            qs = [f"x + y = {random.randint(5,15)}\nx² + y² = {random.randint(50,200)}" for _ in range(3)]
        st.session_state.preview_questoes = [f"t. Sistemas {tipo}"] + qs

elif op == "man":
    st.header("📄 Manual")
    txt = st.text_area("Cole seu texto (t. para Título, número para questão):")
    if st.button("Criar"): st.session_state.preview_questoes = txt.split('\n')

elif op == "calc_f":
    st.header("Calculadora f(x)")
    f_in = st.text_input("Equação (use x):", "x**2 + 2*x")
    x_val = st.number_input("Valor de x:", value=1.0)
    if st.button("Resolver"): st.success(f"Resultado: {eval(f_in.replace('x', f'({x_val})'))}")

# --- VISUALIZAÇÃO (Regras de Numeração e Cabeçalho) ---
if st.session_state.preview_questoes:
    st.divider()
    if os.path.exists("cabecalho.png"): st.image("cabecalho.png")
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        if line.lower().startswith("t."):
            st.markdown(f"<h2 style='text-align: center;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
            l_idx = 0
        elif re.match(r'^\d+', line): # Se começa com número
            st.markdown(f"**{line}**")
            l_idx = 0 # Próxima linha será letra 'a'
        else:
            col1, col2 = st.columns(2)
            with (col1 if l_idx % 2 == 0 else col2):
                st.info(f"**{letras[l_idx%26]})** {line}")
            l_idx += 1

    if st.button("📥 Baixar PDF"):
        pdf = FPDF()
        pdf.add_page()
        y = 55 if os.path.exists("cabecalho.png") else 20
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", 10, 10, 190)
        
        l_pdf = 0
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if line.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 14); pdf.set_y(y+5); pdf.cell(0, 10, clean_txt(line[2:]), ln=True, align='C')
                y = pdf.get_y(); l_pdf = 0
            elif re.match(r'^\d+', line):
                pdf.set_font("Arial", 'B', 11); pdf.set_y(y+5); pdf.multi_cell(0, 8, clean_txt(line))
                y = pdf.get_y(); l_pdf = 0
            else:
                pdf.set_font("Arial", size=11)
                txt = f"{letras[l_pdf%26]}) {line}"
                if l_pdf % 2 == 0:
                    y_base = y; pdf.set_xy(15, y_base); pdf.multi_cell(90, 8, clean_txt(txt))
                    y_p = pdf.get_y()
                else:
                    pdf.set_xy(110, y_base); pdf.multi_cell(85, 8, clean_txt(txt))
                    y = max(y_p, pdf.get_y())
                l_pdf += 1
        st.download_button("Salvar PDF", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")
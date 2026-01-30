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

# --- MENU LATERAL (FIXO) ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
usar_cabecalho = st.sidebar.checkbox("Incluir Cabeçalho no PDF", value=True)

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.gabarito = []
    st.session_state.sub_menu = None
    st.rerun()

if st.sidebar.button("🚪 Sair / Logout"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🛠️ Painel de Controle")

# Botões de Navegação
c1, c2, c3, c4, c5 = st.columns(5)
with c1: 
    if st.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
with c2: 
    if st.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
with c3: 
    if st.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
with c4: 
    if st.button("📊 Cálculos Online", use_container_width=True): st.session_state.sub_menu = "calc_online"
with c5: 
    if st.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

st.divider()
op_atual = st.session_state.sub_menu

# --- MÓDULO MANUAL (CORRIGIDO) ---
if op_atual == "man":
    st.header("📄 Módulo Manual")
    txt_m = st.text_area("Digite as questões (T. para título, número para comando):", height=250)
    if st.button("Gerar Preview"):
        st.session_state.preview_questoes = txt_m.split('\n')
        st.session_state.gabarito = [] # Manual não tem gabarito automático

# --- CÁLCULOS ONLINE ---
elif op_atual == "calc_online":
    st.header("🧮 Ferramentas de Cálculo")
    escolha = st.radio("Selecione a ferramenta:", ["Funções f(x)", "PEMDAS", "Financeira"], horizontal=True)
    
    if escolha == "Funções f(x)":
        exp = st.text_input("Função (ex: x**2 + 5):", "x + 10")
        val_x = st.number_input("Valor de x:", value=1.0)
        if st.button("Calcular"):
            st.success(f"f({val_x}) = {eval(exp.replace('x', f'({val_x})'))}")
            
    elif escolha == "PEMDAS":
        expr = st.text_input("Expressão:", "2 + 2 * 5")
        if st.button("Resolver"):
            st.info(f"Resultado: {eval(expr)}")

# --- GERADOR COLEGIAL ---
elif op_atual == "col":
    st.header("📚 Colegial")
    temas = st.multiselect("Temas:", ["Potenciação", "Radiciação"], ["Potenciação"])
    qtd = st.number_input("Quantidade:", 1, 20, 5)
    if st.button("Gerar Atividade"):
        qs, gab = ["t. Atividade Colegial", "1. Resolva:"], ["--- GABARITO ---"]
        letras = "abcdefghijklmnopqrstuvwxyz"
        for i in range(qtd):
            t = random.choice(temas)
            if t == "Potenciação":
                b = random.randint(2,10)
                qs.append(f"{b}² ="); gab.append(f"{letras[i%26]}) {b**2}")
            else:
                n = random.choice([16, 25, 36, 49, 64])
                qs.append(f"√{n} ="); gab.append(f"{letras[i%26]}) {int(math.sqrt(n))}")
        st.session_state.preview_questoes = qs
        st.session_state.gabarito = gab

# --- PDF E VISUALIZAÇÃO ---
if st.session_state.preview_questoes:
    st.divider()
    col_d1, col_d2 = st.columns(2)
    
    def export_pdf(com_gab):
        pdf = FPDF()
        pdf.add_page()
        y = 60 if (usar_cabecalho and os.path.exists("cabecalho.png")) else 20
        if usar_cabecalho and os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", 10, 10, 190)
        
        l_idx = 0
        letras = "abcdefghijklmnopqrstuvwxyz"
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if line.lower().startswith("t.") or re.match(r'^\d+', line):
                pdf.set_font("Arial", 'B', 12); pdf.set_y(y + 5)
                pdf.multi_cell(0, 10, clean_txt(line[2:] if line.lower().startswith("t.") else line))
                y, l_idx = pdf.get_y(), 0
            else:
                pdf.set_font("Arial", size=12); pdf.set_y(y); pdf.set_x(15)
                pdf.multi_cell(0, 10, clean_txt(f"{letras[l_idx%26]}) {line}"))
                y, l_idx = pdf.get_y(), l_idx + 1
        
        if com_gab and st.session_state.gabarito:
            pdf.add_page(); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "GABARITO", ln=1, align='C')
            for g in st.session_state.gabarito: pdf.cell(0, 8, clean_txt(g), ln=1)
        return pdf.output(dest='S').encode('latin-1')

    with col_d1: st.download_button("📥 Sem Gabarito", export_pdf(False), "questoes.pdf")
    with col_d2: st.download_button("📥 Com Gabarito", export_pdf(True), "gabarito.pdf")

    for item in st.session_state.preview_questoes: st.write(item)
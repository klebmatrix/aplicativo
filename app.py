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

if st.sidebar.button("Sair/Logout", use_container_width=True):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- PAINEL ---
st.title("🛠️ Quantum Math Lab - Painel Principal")

# Seção de Geradores de PDF
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

st.markdown("---")

# Seção de Cálculos Online (AQUI!)
st.subheader("🧮 Calculadoras Online (Resolução em tempo real)")
d1, d2, d3 = st.columns(3)
with d1: 
    if st.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
with d2: 
    if st.button("📊 PEMDAS / Expressões", use_container_width=True): st.session_state.sub_menu = "pemdas"
with d3: 
    if st.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

st.divider()
op_atual = st.session_state.sub_menu

# --- LÓGICA DAS CALCULADORAS ONLINE ---
if op_atual == "calc_f":
    st.header("𝑓(x) Calculadora de Funções")
    f_in = st.text_input("Função (ex: x**2 + 5*x):", "x**2")
    x_val = st.number_input("Valor de x:", value=2.0)
    if st.button("Calcular"):
        try:
            res = eval(f_in.replace('x', f'({x_val})'))
            st.success(f"Resultado: f({x_val}) = {res}")
        except Exception as e: st.error(f"Erro: {e}")

elif op_atual == "pemdas":
    st.header("📊 Resolutor de Expressões")
    expr = st.text_input("Digite a expressão (ex: (10+5)*2):", "2 + 2")
    if st.button("Resolver"):
        try: st.info(f"Resultado: {eval(expr)}")
        except: st.error("Expressão inválida.")

elif op_atual == "fin":
    st.header("💰 Matemática Financeira")
    f1, f2, f3 = st.columns(3)
    p = f1.number_input("Capital (R$):", 1000.0)
    i = f2.number_input("Taxa (% a.m.):", 2.0)
    t = f3.number_input("Tempo (meses):", 12)
    if st.button("Calcular Montante"):
        m = p * (1 + i/100)**t
        st.metric("Montante Final", f"R$ {m:.2f}")

# --- LÓGICA DOS GERADORES DE ATIVIDADES ---
elif op_atual == "col":
    st.header("📚 Colegial")
    tema = st.radio("Escolha o Tema:", ["Frações", "Potenciação", "Radiciação"], horizontal=True)
    if st.button("Gerar Atividade"):
        if tema == "Frações":
            st.session_state.preview_questoes = ["t. Frações"] + [f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/{random.randint(2,5)} =" for _ in range(10)]
        elif tema == "Potenciação":
            st.session_state.preview_questoes = ["t. Potenciação"] + [f"{random.randint(2,15)}^{random.randint(2,3)} =" for _ in range(10)]
        else:
            st.session_state.preview_questoes = ["t. Radiciação"] + [f"√{n**2} =" for n in range(2, 12)]

elif op_atual == "alg":
    st.header("⚖️ Álgebra Linear")
    grau_alg = st.radio("Sistema:", ["1º Grau (x, y)", "2º Grau"], horizontal=True)
    if st.button("Gerar Atividade"):
        if grau_alg == "1º Grau (x, y)":
            st.session_state.preview_questoes = ["t. Sistemas de 1º Grau"] + [f"{random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,30)}\n{random.randint(1,5)}x - {random.randint(1,5)}y = {random.randint(1,10)}" for _ in range(4)]
        else:
            st.session_state.preview_questoes = ["t. Sistemas de 2º Grau"] + [f"x + y = {random.randint(5,10)}\nx² + y² = {random.randint(25,100)}" for _ in range(3)]

# --- PREVIEW E PDF ---
if st.session_state.preview_questoes and op_atual in ["op", "eq", "col", "alg", "man"]:
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
    
    if st.button("📥 Baixar Atividade em PDF"):
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
        st.download_button("Clique para salvar", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")
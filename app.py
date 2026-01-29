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

    # --- LÓGICA DE GERAÇÃO DE QUESTÕES ---
    if op_atual == "op":
        st.header("🔢 Operações Fundamentais")
        sinal = st.selectbox("Operação:", ["+", "-", "x", "÷"])
        qtd = st.slider("Questões:", 4, 40, 12)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Atividade de Matemática"] + [f"{random.randint(10,999)} {sinal} {random.randint(10,99)} =" for _ in range(qtd)]

    elif op_atual == "eq":
        st.header("📐 Equações")
        tipo = st.radio("Grau:", ["1º Grau", "2º Grau"])
        if st.button("Gerar Preview"):
            if tipo == "1º Grau":
                qs = [f"{random.randint(2,10)}x + {random.randint(1,50)} = {random.randint(51,150)}" for _ in range(10)]
            else:
                qs = [f"x² + {random.randint(2,10)}x + {random.randint(1,15)} = 0" for _ in range(8)]
            st.session_state.preview_questoes = [f"t. Equações de {tipo}"] + qs

    elif op_atual == "col":
        st.header("📚 Colegial (Frações)")
        if st.button("Gerar Preview"):
            qs = [f"{random.randint(1,9)}/{random.randint(2,9)} + {random.randint(1,9)}/{random.randint(2,9)} =" for _ in range(10)]
            st.session_state.preview_questoes = ["t. Exercícios com Frações"] + qs

    elif op_atual == "alg":
        st.header("⚖️ Álgebra Linear (Sistemas)")
        if st.button("Gerar Preview"):
            qs = [f"Sist. {i+1}: {random.randint(1,5)}x {'+' if random.random()>0.5 else '-'} {random.randint(1,5)}y = {random.randint(5,25)}" for i in range(6)]
            st.session_state.preview_questoes = ["t. Sistemas Lineares"] + qs

    elif op_atual == "man":
        st.header("📄 Modo Manual")
        txt = st.text_area("Insira suas questões aqui:", height=200)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = txt.split('\n')

    # --- FERRAMENTAS ONLINE ---
    elif op_atual == "calc_f":
        st.header("𝑓(x) Calculadora de Funções")
        f_in = st.text_input("Função (use x):", "x**2 + 2*x + 1")
        x_val = st.number_input("Valor de x:", value=0.0)
        if st.button("Calcular"):
            try: st.success(f"f({x_val}) = {eval(f_in.replace('x', f'({x_val})'))}")
            except: st.error("Erro na função.")

    elif op_atual == "pemdas":
        st.header("📊 Expressões Numéricas")
        exp = st.text_input("Expressão:", "5 + 2 * (10 / 2)")
        if st.button("Resolver"):
            try: st.info(f"Resultado: {eval(exp)}")
            except: st.error("Expressão inválida.")

    elif op_atual == "fin":
        st.header("💰 Matemática Financeira")
        c1, c2, c3 = st.columns(3)
        cap = c1.number_input("Capital (R$):", 100.0)
        tax = c2.number_input("Taxa (% a.m.):", 1.0)
        per = c3.number_input("Meses:", 1)
        if st.button("Juros Compostos"):
            m = cap * (1 + tax/100)**per
            st.metric("Montante", f"R$ {m:.2f}")

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
            st.markdown(f"<h2 style='text-align: center;'>{line[2:]}</h2>", unsafe_allow_html=True)
            l_idx = 0
        elif re.match(r'^\d+', line):
            st.markdown(f"**{line}**")
            l_idx = 0
        else:
            col1, col2 = st.columns(2)
            alvo = col1 if l_idx % 2 == 0 else col2
            with alvo: st.info(f"**{letras[l_idx%26]})** {line}")
            l_idx += 1

    if st.button("📥 Baixar Atividade"):
        pdf = FPDF()
        pdf.add_page()
        y_pos = 55 if os.path.exists("cabecalho.png") else 20
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", 10, 10, 190)
        
        pdf.set_font("Arial", size=11)
        l_pdf = 0
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if line.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 14); pdf.set_y(y_pos); pdf.cell(0, 10, clean_txt(line[2:]), ln=True, align='C')
                y_pos = pdf.get_y() + 5; l_pdf = 0
            elif re.match(r'^\d+', line):
                pdf.set_font("Arial", 'B', 11); pdf.set_y(y_pos); pdf.multi_cell(0, 8, clean_txt(line))
                y_pos = pdf.get_y(); l_pdf = 0
            else:
                pdf.set_font("Arial", size=11)
                txt = f"{letras[l_pdf%26]}) {line}"
                if l_pdf % 2 == 0:
                    y_base = y_pos; pdf.set_xy(15, y_base); pdf.multi_cell(90, 8, clean_txt(txt))
                    y_prox = pdf.get_y()
                else:
                    pdf.set_xy(110, y_base); pdf.multi_cell(85, 8, clean_txt(txt))
                    y_pos = max(y_prox, pdf.get_y())
                l_pdf += 1
        
        st.download_button("Clique para salvar", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")
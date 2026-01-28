import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

def clean_txt(text):
    """Limpa caracteres para compatibilidade com FPDF latin-1"""
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# Inicialização de variáveis de estado (Evita que o app resete dados)
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'menu_ativo' not in st.session_state: st.session_state.menu_ativo = "🔢 Operações"
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- 2. ACESSO E SEGURANÇA ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab - Login")
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        # Pega a chave do Render (chave_mestra em minúsculo) ou usa padrão
        s_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        if pin == s_prof: 
            st.session_state.perfil = "admin"
            st.rerun()
        else:
            st.error("Acesso Negado. Verifique o PIN.")
    st.stop()

# --- 3. MENU LATERAL ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
st.session_state.menu_ativo = st.sidebar.radio("Navegação:", 
    ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual", "🧮 Calculadoras"])

if st.sidebar.button("Sair/Logout"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

menu = st.session_state.menu_ativo
st.title(f"Módulo: {menu}")

# --- 4. LÓGICA DOS MÓDULOS ---

# OPERAÇÕES BÁSICAS
if menu == "🔢 Operações":
    ops = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
    qtd = st.number_input("Quantidade:", 5, 50, 12)
    if st.button("🎲 Gerar"):
        st.session_state.preview_questoes = [f"{random.randint(10,999)} {random.choice(ops)} {random.randint(2,99)} =" for _ in range(qtd)]

# EQUAÇÕES
elif menu == "📐 Equações":
    grau_eq = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("🎲 Gerar Equações"):
        qs = []
        for _ in range(10):
            if grau_eq == "1º Grau":
                a, b = random.randint(2,10), random.randint(1,50)
                qs.append(f"{a}x + {b} = {a*random.randint(1,10) + b}")
            else:
                qs.append(f"x² - {random.randint(2,12)}x + {random.randint(1,30)} = 0")
        st.session_state.preview_questoes = qs

# COLEGIAL (Aritmética + Porcentagem)
elif menu == "📚 Colegial":
    temas = st.multiselect("Temas:", ["Frações", "Potenciação", "Radiciação", "Porcentagem"], ["Frações", "Porcentagem"])
    if st.button("🎲 Gerar Colegial"):
        qs = []
        for _ in range(10):
            t = random.choice(temas)
            if t == "Frações":
                qs.append(f"{random.randint(1,9)}/{random.randint(2,5)} {random.choice(['+', 'x'])} {random.randint(1,9)}/{random.randint(2,5)} =")
            elif t == "Potenciação":
                qs.append(f"{random.randint(2,15)}^{random.randint(2,3)} =")
            elif t == "Radiciação":
                qs.append(f"√{random.randint(4,144)} =")
            else: # Porcentagem
                qs.append(f"Calcule {random.choice([5,10,20,25,50])}% de {random.randint(10,1000)}.")
        st.session_state.preview_questoes = qs

# ÁLGEBRA LINEAR (Sistemas, Matrizes e Funções)
elif menu == "⚖️ Álgebra Linear":
    sub_alg = st.radio("Tipo:", ["Sistemas", "Matrizes", "Funções"], horizontal=True)
    if sub_alg == "Sistemas":
        grau_s = st.radio("Grau do Sistema:", ["1º Grau", "2º Grau"], horizontal=True)
        if st.button("🎲 Gerar Sistemas"):
            qs = []
            for _ in range(3):
                if "1º" in grau_s:
                    x, y = random.randint(1,5), random.randint(1,5)
                    qs.append(f"Sistema Linear:\n{{ x + y = {x+y} \n{{ x - y = {x-y}")
                else:
                    qs.append(f"Sistema Não-Linear:\n{{ x + y = {random.randint(5,10)} \n{{ x² + y² = {random.randint(20,80)}")
            st.session_state.preview_questoes = qs
    elif sub_alg == "Matrizes":
        if st.button("🎲 Gerar Matriz 2x2"):
            m = np.random.randint(-10, 11, size=(2, 2))
            m_str = "\n" + "\n".join([" | ".join(map(str, linha)) for linha in m])
            st.session_state.preview_questoes = [f"Calcule o determinante da matriz:{m_str}"]
    else: # Funções
        if st.button("🎲 Gerar Funções"):
            st.session_state.preview_questoes = [
                f"Determine o domínio de f(x) = {random.randint(1,9)}/(x - {random.randint(1,20)})",
                f"Calcule f({random.randint(1,10)}) para f(x) = 2x² - 5"
            ]

# MANUAL
elif menu == "📄 Manual":
    st.info("t. Título | 1. Questão | . Coluna")
    txt = st.text_area("Digite sua atividade:", height=300)
    if st.button("🔍 Visualizar"):
        st.session_state.preview_questoes = txt.split('\n')

# CALCULADORAS
elif menu == "🧮 Calculadoras":
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📊 PEMDAS")
        exp = st.text_input("Expressão:", "10 / (2 + 3) * 4")
        if st.button("Resolver"): st.success(f"Resultado: {eval(exp)}")
    with c2:
        st.subheader("𝑓(x) Função")
        fun = st.text_input("f(x):", "x**2 - 4")
        val = st.number_input("x:", 0)
        if st.button("Calcular"): st.metric("f(x)", eval(fun.replace('x', str(val))))

# --- 5. ÁREA DE PREVIEW E PDF (ESTRUTURA FIXA) ---
if st.session_state.preview_questoes and menu != "🧮 Calculadoras":
    st.divider()
    st.subheader("👀 Prévia da Atividade")
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    
    with st.container(border=True):
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if line.startswith("t."):
                st.markdown(f"<h2 style='text-align: center;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
            elif re.match(r'^\d+', line):
                st.markdown(f"**{line}**")
                l_idx = 0
            else:
                st.write(f"**{letras[l_idx%26]})** {line.replace('.', '').strip()}")
                l_idx += 1

    if st.button("📥 Baixar PDF"):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10); l_idx = 0
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            if line.startswith("t."):
                pdf.ln(5); pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, clean_txt(line[2:].strip()), ln=True, align='C')
                pdf.set_font("Arial", size=10)
            elif re.match(r'^\d+', line):
                pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(line))
                pdf.set_font("Arial", size=10); l_idx = 0
            else:
                match = re.match(r'^(\.+)', line); pts = len(match.group(1)) if match else 0
                if pts > 0:
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*45); pdf.cell(45, 8, f"{letras[l_idx%26]}) {clean_txt(line[pts:].strip())}", ln=True)
                else:
                    pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(line)}")
                l_idx += 1
        
        st.download_button("✅ Clique para Salvar", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade_quantum.pdf")
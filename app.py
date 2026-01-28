import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'menu_ativo' not in st.session_state: st.session_state.menu_ativo = "🔢 Operações"
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        s_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        if pin == s_prof: 
            st.session_state.perfil = "admin"
            st.rerun()
        else: st.error("PIN Inválido.")
    st.stop()

# --- 3. MENU LATERAL ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
st.session_state.menu_ativo = st.sidebar.radio("Módulos:", 
    ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual", "🧮 Calculadoras"])

if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

menu = st.session_state.menu_ativo
st.title(f"Módulo: {menu}")

# --- 4. LÓGICA POR MÓDULO ---

if menu == "📚 Colegial":
    st.subheader("Aritmética Básica")
    temas = st.multiselect("Tópicos:", ["Frações (4 ops)", "Potenciação", "Radiciação"], ["Frações (4 ops)"])
    if st.button("🎲 Gerar Atividade Colegial"):
        qs = []
        for _ in range(10):
            t = random.choice(temas)
            if t == "Frações (4 ops)":
                op = random.choice(['+', '-', 'x', '÷'])
                qs.append(f"{random.randint(1,9)}/{random.randint(2,5)} {op} {random.randint(1,9)}/{random.randint(2,5)} =")
            elif t == "Potenciação":
                qs.append(f"{random.randint(2,12)}^{random.randint(2,3)} =")
            else: # Radiciação
                qs.append(f"√{random.randint(2,12)**2} =")
        st.session_state.preview_questoes = qs

elif menu == "⚖️ Álgebra Linear":
    st.subheader("Sistemas, Matrizes e Funções")
    tipo_alg = st.radio("O que gerar:", ["Sistemas", "Matrizes", "Funções"], horizontal=True)
    
    if tipo_alg == "Sistemas":
        grau_sis = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        if st.button("🎲 Gerar Sistemas"):
            qs = []
            for _ in range(4):
                if "1º Grau" in grau_sis:
                    x, y = random.randint(1,5), random.randint(1,5)
                    qs.append(f"Resolva o sistema:\n{{ x + y = {x+y} \n{{ x - y = {x-y}")
                else:
                    qs.append(f"Resolva o sistema de 2º grau:\n{{ x + y = {random.randint(5,10)} \n{{ x² + y² = {random.randint(25,100)}")
            st.session_state.preview_questoes = qs

    elif tipo_alg == "Matrizes":
        ordem = st.selectbox("Ordem:", ["2x2", "3x3"])
        if st.button("🎲 Gerar Matrizes"):
            size = 2 if ordem == "2x2" else 3
            qs = []
            for _ in range(3):
                m = np.random.randint(-10, 10, size=(size, size))
                m_str = "\n" + "\n".join([" | ".join(map(str, linha)) for linha in m])
                qs.append(f"Calcule o determinante da matriz {ordem}:{m_str}")
            st.session_state.preview_questoes = qs
            
    else: # Funções
        if st.button("🎲 Gerar Questões de Funções"):
            st.session_state.preview_questoes = [
                f"Determine o domínio da função f(x) = {random.randint(1,9)} / (x - {random.randint(1,20)})",
                f"Dada f(x) = {random.randint(2,5)}x + {random.randint(1,10)}, calcule f({random.randint(1,5)})",
                f"Encontre a raiz da função f(x) = {random.randint(2,10)}x - {random.randint(10,50)}"
            ]

elif menu == "📐 Equações":
    grau = st.radio("Tipo:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("🎲 Gerar Equações"):
        qs = []
        for _ in range(8):
            if grau == "1º Grau":
                a, b = random.randint(2,10), random.randint(1,30)
                qs.append(f"{a}x + {b} = {a*random.randint(1,5) + b}")
            else:
                qs.append(f"x² - {random.randint(2,10)}x + {random.randint(1,20)} = 0")
        st.session_state.preview_questoes = qs

elif menu == "📄 Manual":
    st.info("Comandos: t. Título | 1. Questão (reseta letras) | . Coluna")
    txt_m = st.text_area("Digite o conteúdo:", height=250)
    if st.button("🔍 Visualizar"):
        st.session_state.preview_questoes = txt_m.split('\n')

# --- 5. ÁREA DE PREVIEW E PDF ---
if st.session_state.preview_questoes and menu != "🧮 Calculadoras":
    st.divider()
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    with st.container(border=True):
        for q in st.session_state.preview_questoes:
            t = q.strip()
            if not t: continue
            if t.startswith("t."):
                st.markdown(f"### {t[2:].strip()}")
            elif re.match(r'^\d+', t):
                st.markdown(f"**{t}**")
                l_idx = 0
            else:
                st.write(f"**{letras[l_idx%26]})** {t.replace('.', '').strip()}")
                l_idx += 1

    if st.button("📥 Baixar PDF"):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10); l_idx = 0
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
        
        for q in st.session_state.preview_questoes:
            t = q.strip()
            if not t: continue
            if t.startswith("t."):
                pdf.ln(5); pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, clean_txt(t[2:].strip()), ln=True, align='C')
                pdf.set_font("Arial", size=10)
            elif re.match(r'^\d+', t):
                pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(t))
                pdf.set_font("Arial", size=10); l_idx = 0
            else:
                match = re.match(r'^(\.+)', t); pts = len(match.group(1)) if match else 0
                if pts > 0:
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*45); pdf.cell(45, 8, f"{letras[l_idx%26]}) {clean_txt(t[pts:].strip())}", ln=True)
                else: pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(t)}")
                l_idx += 1
        st.download_button("✅ Download PDF", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")
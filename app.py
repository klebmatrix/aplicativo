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
        s_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
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

# --- 4. LÓGICA DE ÁLGEBRA LINEAR (CORRIGIDA) ---
if menu == "⚖️ Álgebra Linear":
    ordem = st.radio("Ordem da Matriz:", ["2x2", "3x3"], horizontal=True)
    if st.button("🎲 Gerar Matrizes"):
        size = 2 if ordem == "2x2" else 3
        qs = []
        for i in range(3):
            m = np.random.randint(-10, 10, size=(size, size))
            # Formatação manual para evitar erro de exibição
            m_str = "\n" + "\n".join([" | ".join(map(str, linha)) for linha in m])
            qs.append(f"Calcule o determinante da matriz {ordem}:{m_str}")
        st.session_state.preview_questoes = qs

# --- 5. OUTROS MÓDULOS (OPERAÇÕES, EQUAÇÕES, COLEGIAL, MANUAL) ---
elif menu == "🔢 Operações":
    ops = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+"])
    if st.button("🎲 Gerar"):
        st.session_state.preview_questoes = [f"{random.randint(10,500)} {random.choice(ops)} {random.randint(2,50)} =" for _ in range(10)]

elif menu == "📐 Equações":
    grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("🎲 Gerar"):
        st.session_state.preview_questoes = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" if grau == "1º Grau" else f"x² - {random.randint(2,10)}x + {random.randint(1,20)} = 0" for _ in range(8)]

elif menu == "📚 Colegial":
    temas = st.multiselect("Tópicos:", ["Frações", "Sistemas", "Potência"], ["Frações"])
    if st.button("🎲 Gerar"):
        st.session_state.preview_questoes = [f"{random.randint(1,9)}/2 + {random.randint(1,9)}/3 =" for _ in range(8)]

elif menu == "📄 Manual":
    txt_m = st.text_area("t. Título | 1. Questão | . Coluna", height=200)
    if st.button("🔍 Visualizar"): st.session_state.preview_questoes = txt_m.split('\n')

elif menu == "🧮 Calculadoras":
    exp = st.text_input("PEMDAS:", "2 + 2")
    if st.button("Calcular"): st.success(f"Res: {eval(exp)}")

# --- 6. ÁREA DE PREVIEW E PDF ---
if st.session_state.preview_questoes and menu != "🧮 Calculadoras":
    st.divider()
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    with st.container(border=True):
        for q in st.session_state.preview_questoes:
            t = q.strip()
            if not t: continue
            if t.startswith("t."): st.markdown(f"### {t[2:].strip()}")
            elif re.match(r'^\d+', t): st.markdown(f"**{t}**"); l_idx = 0
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
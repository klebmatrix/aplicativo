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
        # Ajustado para usar lowercase como solicitado
        s_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        if pin == s_prof: 
            st.session_state.perfil = "admin"
            st.rerun()
        else: st.error("PIN Inválido.")
    st.stop()

# --- 3. MENU LATERAL (TODOS OS MÓDULOS) ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
st.session_state.menu_ativo = st.sidebar.radio("Módulos:", 
    ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual", "🧮 Calculadoras"])

if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

menu = st.session_state.menu_ativo
st.title(f"Módulo: {menu}")

# --- 4. LÓGICA DE CADA MÓDULO (RESTAURADOS) ---

# --- MÓDULO OPERAÇÕES ---
if menu == "🔢 Operações":
    ops = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
    qtd_op = st.number_input("Quantidade:", 5, 50, 10)
    if st.button("🎲 Gerar Operações"):
        st.session_state.preview_questoes = [f"{random.randint(10,500)} {random.choice(ops)} {random.randint(2,50)} =" for _ in range(qtd_op)]

# --- MÓDULO EQUAÇÕES ---
elif menu == "📐 Equações":
    grau_eq = st.radio("Tipo:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("🎲 Gerar Equações"):
        qs = []
        for _ in range(8):
            if grau_eq == "1º Grau":
                a, b = random.randint(2,10), random.randint(1,30)
                qs.append(f"{a}x + {b} = {a*random.randint(1,5) + b}")
            else:
                qs.append(f"x² - {random.randint(2,10)}x + {random.randint(1,20)} = 0")
        st.session_state.preview_questoes = qs

# --- MÓDULO COLEGIAL (APENAS ARITMÉTICA) ---
elif menu == "📚 Colegial":
    temas_col = st.multiselect("Tópicos:", ["Frações (4 ops)", "Potenciação", "Radiciação"], ["Frações (4 ops)"])
    if st.button("🎲 Gerar Atividade Colegial"):
        qs = []
        for _ in range(10):
            t = random.choice(temas_col)
            if t == "Frações (4 ops)":
                op = random.choice(['+', '-', 'x', '÷'])
                qs.append(f"{random.randint(1,9)}/{random.randint(2,5)} {op} {random.randint(1,9)}/{random.randint(2,5)} =")
            elif t == "Potenciação":
                qs.append(f"{random.randint(2,12)}^{random.randint(2,3)} =")
            else:
                qs.append(f"√{random.randint(2,12)**2} =")
        st.session_state.preview_questoes = qs

# --- MÓDULO ÁLGEBRA LINEAR (SISTEMAS, MATRIZES E FUNÇÕES) ---
elif menu == "⚖️ Álgebra Linear":
    tipo_alg = st.radio("Escolha:", ["Sistemas", "Matrizes", "Funções"], horizontal=True)
    if tipo_alg == "Sistemas":
        grau_s = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        if st.button("🎲 Gerar Sistemas"):
            qs = []
            for _ in range(4):
                if "1º Grau" in grau_s:
                    x, y = random.randint(1,5), random.randint(1,5)
                    qs.append(f"Sistema:\n{{ x + y = {x+y} \n{{ x - y = {x-y}")
                else:
                    qs.append(f"Sistema 2º Grau:\n{{ x + y = {random.randint(5,10)} \n{{ x² + y² = {random.randint(25,100)}")
            st.session_state.preview_questoes = qs
    elif tipo_alg == "Matrizes":
        ordem = st.selectbox("Ordem:", ["2x2", "3x3"])
        if st.button("🎲 Gerar Matrizes"):
            size = 2 if ordem == "2x2" else 3
            qs = []
            for _ in range(3):
                m = np.random.randint(-10, 10, size=(size, size))
                m_str = "\n" + "\n".join([" | ".join(map(str, linha)) for linha in m])
                qs.append(f"Determine o Det da matriz {ordem}:{m_str}")
            st.session_state.preview_questoes = qs
    else: # Funções
        if st.button("🎲 Gerar Funções"):
            st.session_state.preview_questoes = [
                f"Determine o domínio de f(x) = {random.randint(1,9)}/(x - {random.randint(1,15)})",
                f"Dada f(x) = {random.randint(2,5)}x + {random.randint(1,10)}, calcule f({random.randint(1,5)})"
            ]

# --- MÓDULO MANUAL ---
elif menu == "📄 Manual":
    st.info("t. Título | 1. Questão | . Coluna")
    txt_m = st.text_area("Digite o conteúdo:", height=250)
    if st.button("🔍 Visualizar"):
        st.session_state.preview_questoes = txt_m.split('\n')

# --- MÓDULO CALCULADORAS ---
elif menu == "🧮 Calculadoras":
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📊 PEMDAS / Expressões")
        exp_calc = st.text_input("Expressão:", "2 + 3 * (10 / 2)")
        if st.button("Resolver"): 
            try: st.success(f"Resultado: {eval(exp_calc)}")
            except: st.error("Expressão Inválida")
    with c2:
        st.subheader("𝑓(x) Função")
        f_calc = st.text_input("f(x):", "x**2 + 3")
        x_calc = st.number_input("Valor de x:", 2)
        if st.button("Calcular f(x)"):
            try: st.metric("Resultado", eval(f_calc.replace('x', str(x_calc))))
            except: st.error("Erro no cálculo")

# --- 5. ÁREA DE PREVIEW E PDF (ESTÁVEL) ---
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
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
    st.title("🔐 Acesso")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        s_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
        s_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        if pin == s_prof: st.session_state.perfil = "admin"
        elif pin == s_aluno: st.session_state.perfil = "aluno"
        else: st.error("PIN Inválido.")
        st.rerun()
    st.stop()

# --- 3. MENU LATERAL ---
st.sidebar.title(f"👤 {st.session_state.perfil.upper()}")
st.session_state.menu_ativo = st.sidebar.radio("Módulos:", 
    ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual", "🧮 Calculadoras"])

if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

# --- 4. LÓGICA DOS MÓDULOS ---
menu = st.session_state.menu_ativo
st.title(f"Módulo: {menu}")

# --- MÓDULO OPERAÇÕES ---
if menu == "🔢 Operações":
    ops = st.multiselect("Operações:", ["+", "-", "x", "÷"], ["+"])
    qtd = st.number_input("Quantidade:", 5, 50, 10)
    if st.button("🎲 Gerar Operações"):
        st.session_state.preview_questoes = [f"{random.randint(10,500)} {random.choice(ops)} {random.randint(2,50)} =" for _ in range(qtd)]

# --- MÓDULO EQUAÇÕES (CORRIGIDO) ---
elif menu == "📐 Equações":
    grau = st.radio("Escolha o Grau:", ["1º Grau", "2º Grau", "Misto"], horizontal=True)
    qtd_eq = st.number_input("Quantidade:", 4, 30, 8)
    if st.button("🎲 Gerar Equações"):
        qs = []
        for _ in range(qtd_eq):
            tipo = grau if grau != "Misto" else random.choice(["1º Grau", "2º Grau"])
            if tipo == "1º Grau":
                a, b = random.randint(2, 10), random.randint(1, 30)
                qs.append(f"{a}x + {b} = {a * random.randint(1, 10) + b}")
            else:
                x1, x2 = random.randint(1, 5), random.randint(1, 5)
                s, p = x1 + x2, x1 * x2
                qs.append(f"x² - {s}x + {p} = 0")
        st.session_state.preview_questoes = qs

# --- MÓDULO COLEGIAL ---
elif menu == "📚 Colegial":
    temas = st.multiselect("Tópicos:", ["Frações", "Potência", "Raiz", "Sistemas 2x2", "Matrizes"], ["Frações"])
    if st.button("🎲 Gerar Colegial"):
        qs = []
        for _ in range(10):
            t = random.choice(temas)
            if t == "Frações": qs.append(f"{random.randint(1,9)}/{random.randint(2,5)} {random.choice(['+', '-', 'x', '÷'])} {random.randint(1,9)}/{random.randint(2,5)} =")
            elif t == "Potência": qs.append(f"{random.randint(2,10)}^{random.randint(2,3)} =")
            elif t == "Raiz": qs.append(f"√{random.randint(2,12)**2} =")
            elif t == "Sistemas 2x2": qs.append(f"Sistema: {{ x+y={random.randint(5,15)} | x-y={random.randint(1,5)} }}")
            else: qs.append(f"Matriz 2x2: {np.random.randint(1,9, (2,2)).tolist()}")
        st.session_state.preview_questoes = qs

# --- MÓDULO MANUAL ---
elif menu == "📄 Manual":
    st.info("t. Título | 1. Questão | . Coluna")
    txt_m = st.text_area("Conteúdo:", height=250)
    if st.button("🔍 Visualizar"):
        st.session_state.preview_questoes = txt_m.split('\n')

# --- CALCULADORAS ---
elif menu == "🧮 Calculadoras":
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📊 PEMDAS")
        exp = st.text_input("Expressão:", "2 + 3 * 5")
        if st.button("Resolver"): st.success(f"Resultado: {eval(exp)}")
    with c2:
        st.subheader("𝑓(x) Função")
        f_in = st.text_input("f(x):", "x**2 + 5")
        x_in = st.number_input("x:", 3)
        if st.button("Calcular"): st.metric("Resultado", eval(f_in.replace('x', str(x_in))))

# --- 5. VISUALIZAÇÃO E PDF ---
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
        st.download_button("✅ Download", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")
import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# --- 2. GESTÃO DE ESTADO (ESSENCIAL) ---
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_data' not in st.session_state: st.session_state.preview_data = []

# --- 3. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        s_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        s_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
        if pin == s_prof: st.session_state.perfil = "admin"; st.rerun()
        elif pin == s_aluno: st.session_state.perfil = "aluno"; st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 4. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
if st.sidebar.button("Logout / Sair"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- 5. PAINEL PROFESSOR ---
if st.session_state.perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"; st.session_state.preview_data = []
    with c2: 
        if st.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"; st.session_state.preview_data = []
    with c3: 
        if st.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"; st.session_state.preview_data = []
    with c4: 
        if st.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"; st.session_state.preview_data = []
    with c5: 
        if st.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"; st.session_state.preview_data = []

    st.markdown("---")
    op = st.session_state.sub_menu

    # --- COLEGIAL COMPLETO ---
    if op == "col":
        st.header("📚 Gerador Colegial")
        temas = st.multiselect("Tópicos:", ["Frações", "Potência", "Raiz", "Sistemas", "Matrizes", "Funções"], ["Frações"])
        qtd = st.number_input("Qtd:", 1, 30, 8)
        
        if st.button("🔍 Gerar/Sortear"):
            res = []
            for _ in range(qtd):
                t = random.choice(temas)
                if t == "Frações":
                    op_f = random.choice(['+', '-', 'x', '÷'])
                    res.append(f"{random.randint(1,9)}/{random.randint(2,5)} {op_f} {random.randint(1,9)}/{random.randint(2,5)} =")
                elif t == "Potência": res.append(f"{random.randint(2,12)}^{random.randint(2,3)} =")
                elif t == "Raiz": res.append(f"√{random.randint(2,12)**2} =")
                elif t == "Sistemas":
                    x, y = random.randint(1,4), random.randint(1,4)
                    res.append(f"Resolva o sistema: {{ x + y = {x+y} | x - y = {x-y} }}")
                elif t == "Matrizes": res.append(f"Calcule Det da Matriz 2x2:\n{np.random.randint(1,9, (2,2))}")
                else: res.append(f"Domínio de f(x) = {random.randint(1,9)} / (x - {random.randint(1,15)})")
            st.session_state.preview_data = res

    # --- MANUAL (COM REGRAS DE NÚMEROS E PONTOS) ---
    elif op == "man":
        st.header("📄 Gerador Manual")
        tit_m = st.text_input("Título:", "Atividade")
        txt_m = st.text_area("Use . para colunas", height=200)
        if st.button("🔍 Visualizar"):
            st.session_state.preview_data = txt_m.split('\n')
            st.session_state.manual_tit = tit_m

    # --- ÁREA DE PREVIEW E PDF (COMUM) ---
    if st.session_state.preview_data:
        st.subheader("👀 Visualização")
        letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
        with st.container(border=True):
            for q in st.session_state.preview_data:
                if not q.strip(): continue
                if op == "man" and re.match(r'^\d+', q):
                    st.markdown(f"**{q}**"); l_idx = 0
                else:
                    st.write(f"**{letras[l_idx%26]})** {q.replace('.', '')}")
                    l_idx += 1
        
        if st.button("📥 Baixar PDF"):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10); l_idx = 0
            if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
            tit_f = st.session_state.get("manual_tit", "Atividade")
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(tit_f), ln=True, align='C'); pdf.ln(5)
            
            for q in st.session_state.preview_data:
                if not q.strip(): continue
                match = re.match(r'^(\.+)', q); pts = len(match.group(1)) if match else 0
                if re.match(r'^\d+', q):
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(q)); pdf.set_font("Arial", size=10); l_idx = 0
                elif pts > 0:
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*45); pdf.cell(45, 8, f"{letras[l_idx%26]}) {clean_txt(q[pts:].strip())}", ln=True); l_idx += 1
                else:
                    pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(q)}"); l_idx += 1
            st.download_button("✅ Clique aqui para baixar", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")

# --- FERRAMENTAS ONLINE (ALUNO E PROFESSOR) ---
st.divider()
st.subheader("🧮 Calculadoras Rápidas")
f1, f2 = st.columns(2)
with f1:
    exp_in = st.text_input("Expressão (PEMDAS):", "2 * (3 + 4)")
    if st.button("Resolver"): st.success(f"Resultado: {eval(exp_in)}")
with f2:
    f_in = st.text_input("f(x):", "x**2")
    x_val = st.number_input("Valor de x:", 2)
    if st.button("Calcular f(x)"): st.metric("f(x)", eval(f_in.replace('x', str(x_val))))
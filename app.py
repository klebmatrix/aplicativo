import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES TÉCNICAS (NÃO ALTERAR) ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    """Garante que caracteres especiais não quebrem o PDF"""
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "x"}
    for original, novo in rep.items():
        text = text.replace(original, novo)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# Inicialização de Memória Blindada
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- 2. LOGIN (chave_mestra) ---
if st.session_state.perfil is None:
    st.title("🔐 Acesso Restrito")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        # Busca no Render a chave_mestra em minúsculo
        s_prof = str(st.secrets.get("chave_mestra", "12345678")).strip().lower()
        if pin == s_prof: 
            st.session_state.perfil = "admin"
            st.rerun()
        else: st.error("PIN Inválido.")
    st.stop()

# --- 3. MENU LATERAL ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
aba = st.sidebar.radio("Módulos:", 
    ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual", "🧮 Calculadoras"])

if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

st.title(f"Módulo: {aba}")

# --- 4. LÓGICA DE CADA MÓDULO ---

if aba == "🔢 Operações":
    ops = st.multiselect("Sinais:", ["+", "-", "x", "/"], ["+", "-"])
    if st.button("🎲 Gerar Operações"):
        st.session_state.preview_questoes = [f"{random.randint(10,999)} {random.choice(ops)} {random.randint(10,99)} =" for _ in range(10)]

elif aba == "📐 Equações":
    tipo_eq = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("🎲 Gerar Equações"):
        qs = []
        for _ in range(8):
            if tipo_eq == "1º Grau": qs.append(f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}")
            else: qs.append(f"x² - {random.randint(2,10)}x + {random.randint(1,20)} = 0")
        st.session_state.preview_questoes = qs

elif aba == "📚 Colegial":
    temas = st.multiselect("Tópicos:", ["Frações", "Potência", "Raiz (V)", "Porcentagem"], ["Frações", "Porcentagem"])
    if st.button("🎲 Gerar Atividade"):
        qs = []
        for _ in range(10):
            t = random.choice(temas)
            if t == "Raiz (V)": qs.append(f"{random.randint(2,5)}V{random.randint(2,12)**2} =")
            elif t == "Frações": qs.append(f"{random.randint(1,9)}/2 + {random.randint(1,9)}/3 =")
            elif t == "Potência": qs.append(f"{random.randint(2,10)}^2 =")
            else: qs.append(f"{random.randint(5,50)}% de {random.randint(100,1000)} =")
        st.session_state.preview_questoes = qs

elif aba == "⚖️ Álgebra Linear":
    sub_alg = st.radio("Opção:", ["Sistemas", "Matrizes", "Funções"], horizontal=True)
    if st.button(f"🎲 Gerar {sub_alg}"):
        if sub_alg == "Sistemas":
            x, y = random.randint(1,5), random.randint(1,5)
            st.session_state.preview_questoes = [f"[SIS] x + y = {x+y} | x - y = {x-y}"]
        elif sub_alg == "Matrizes":
            m = np.random.randint(1, 10, (2,2))
            st.session_state.preview_questoes = ["Determine o Det:\n" + "\n".join([" | ".join(map(str, l)) for l in m])]
        else: # Funções
            st.session_state.preview_questoes = [f"Dada f(x) = {random.randint(2,5)}x + 10, calcule f({random.randint(1,9)})"]

elif aba == "📄 Manual":
    txt = st.text_area("t. Título | 1. Questão | [SIS] Eq1 | Eq2 | V para Raiz", height=250)
    if st.button("🔍 Preview"): st.session_state.preview_questoes = txt.split('\n')

elif aba == "🧮 Calculadoras":
    exp = st.text_input("Expressão:", "2 + 3 * 4")
    if st.button("Calcular"): st.success(f"Resultado: {eval(exp)}")

# --- 5. PREVIEW E PDF (ESTÁVEL) ---
if st.session_state.preview_questoes and aba != "🧮 Calculadoras":
    st.divider()
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    with st.container(border=True):
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if "[SIS]" in line:
                partes = line.replace("[SIS]", "").split("|")
                st.write(f"**{letras[l_idx%26]})**")
                st.latex(r" \begin{cases} " + partes[0] + r" \\ " + partes[1] + r" \end{cases} ")
                l_idx += 1
            elif line.startswith("t."): st.markdown(f"### {line[2:].strip()}")
            elif re.match(r'^\d+', line): st.markdown(f"**{line}**"); l_idx = 0
            else:
                st.write(f"**{letras[l_idx%26]})** {line.replace('.', '').strip()}")
                l_idx += 1

    if st.button("📥 Baixar PDF Final"):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11); l_idx = 0
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if "[SIS]" in line:
                partes = line.replace("[SIS]", "").split("|")
                pdf.set_font("Arial", 'B', 11); pdf.cell(10, 10, f"{letras[l_idx%26]})")
                cx, cy = pdf.get_x(), pdf.get_y()
                pdf.set_font("Courier", size=18); pdf.text(cx, cy + 7, "{"); pdf.set_font("Arial", size=11)
                pdf.text(cx + 5, cy + 4, clean_txt(partes[0].strip())); pdf.text(cx + 5, cy + 9, clean_txt(partes[1].strip()))
                pdf.ln(12); l_idx += 1
            elif line.startswith("t."):
                pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(line[2:].strip()), ln=True, align='C'); pdf.set_font("Arial", size=11)
            elif re.match(r'^\d+', line):
                pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(line)); pdf.set_font("Arial", size=11); l_idx = 0
            else:
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(line.replace('.',''))}"); l_idx += 1
        st.download_button("✅ Download", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")
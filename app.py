import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES TÉCNICAS ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# Inicialização de Memória (Impede que os dados sumam ao clicar)
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'menu_ativo' not in st.session_state: st.session_state.menu_ativo = "🔢 Operações"
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- 2. LOGIN (chave_mestra em minúsculo) ---
if st.session_state.perfil is None:
    st.title("🔐 Acesso Quantum Lab")
    pin = st.text_input("Digite o PIN:", type="password")
    if st.button("Liberar Acesso"):
        s_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        if pin == s_prof: 
            st.session_state.perfil = "admin"
            st.rerun()
        else: st.error("PIN Incorreto.")
    st.stop()

# --- 3. MENU LATERAL FIXO ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
st.session_state.menu_ativo = st.sidebar.radio("Escolha o Módulo:", 
    ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual", "🧮 Calculadoras"])

if st.sidebar.button("🔴 Logout"):
    st.session_state.perfil = None
    st.rerun()

menu = st.session_state.menu_ativo
st.title(f"Módulo: {menu}")

# --- 4. LÓGICA DOS MÓDULOS ---

if menu == "🔢 Operações":
    ops = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
    if st.button("🎲 Gerar Operações"):
        st.session_state.preview_questoes = [f"{random.randint(10,999)} {random.choice(ops)} {random.randint(2,99)} =" for _ in range(10)]

elif menu == "📐 Equações":
    grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("🎲 Gerar Equações"):
        qs = []
        for _ in range(10):
            if grau == "1º Grau": qs.append(f"{random.randint(2,9)}x + {random.randint(1,50)} = {random.randint(51,150)}")
            else: qs.append(f"x² - {random.randint(2,12)}x + {random.randint(1,30)} = 0")
        st.session_state.preview_questoes = qs

elif menu == "📚 Colegial":
    temas = st.multiselect("Tópicos:", ["Frações", "Potenciação", "Radiciação", "Porcentagem"], ["Frações", "Porcentagem"])
    if st.button("🎲 Gerar Atividade"):
        qs = []
        for _ in range(10):
            t = random.choice(temas)
            if t == "Frações": qs.append(f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/2 =")
            elif t == "Potenciação": qs.append(f"{random.randint(2,12)}^{random.randint(2,3)} =")
            elif t == "Radiciação": qs.append(f"√{random.randint(4,144)} =")
            else: qs.append(f"Quanto é {random.randint(5,50)}% de {random.randint(100,1000)}?")
        st.session_state.preview_questoes = qs

elif menu == "⚖️ Álgebra Linear":
    sub = st.radio("Tipo:", ["Sistemas", "Matrizes", "Funções"], horizontal=True)
    if st.button(f"🎲 Gerar {sub}"):
        qs = []
        if sub == "Sistemas":
            for _ in range(3):
                x, y = random.randint(1,5), random.randint(1,5)
                qs.append(f"[SIS] x + y = {x+y} | x - y = {x-y}")
        elif sub == "Matrizes":
            m = np.random.randint(-5, 10, size=(2, 2))
            qs.append("Determine o Det da matriz:\n" + "\n".join([" | ".join(map(str, l)) for l in m]))
        else: # Funções
            qs.append(f"Determine o domínio de f(x) = {random.randint(1,9)}/(x - {random.randint(1,20)})")
        st.session_state.preview_questoes = qs

elif menu == "📄 Manual":
    txt = st.text_area("t. Título | 1. Questão | . Coluna | [SIS] Eq1 | Eq2", height=250)
    if st.button("🔍 Visualizar"): st.session_state.preview_questoes = txt.split('\n')

elif menu == "🧮 Calculadoras":
    exp = st.text_input("Expressão (PEMDAS):", "2 + 3 * 5")
    if st.button("Resolver"): st.success(f"Resultado: {eval(exp)}")

# --- 5. PREVIEW E PDF COM SUPORTE A SISTEMAS ---
if st.session_state.preview_questoes and menu != "🧮 Calculadoras":
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

    if st.button("📥 Baixar Atividade (PDF)"):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10); l_idx = 0
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if "[SIS]" in line:
                partes = line.replace("[SIS]", "").split("|")
                pdf.set_font("Arial", 'B', 10); pdf.cell(10, 10, f"{letras[l_idx%26]})")
                cx, cy = pdf.get_x(), pdf.get_y()
                pdf.set_font("Courier", size=18); pdf.text(cx, cy + 7, "{"); pdf.set_font("Arial", size=10)
                pdf.text(cx + 5, cy + 4, clean_txt(partes[0].strip())); pdf.text(cx + 5, cy + 9, clean_txt(partes[1].strip()))
                pdf.ln(12); l_idx += 1
            elif line.startswith("t."):
                pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(line[2:].strip()), ln=True, align='C'); pdf.set_font("Arial", size=10)
            elif re.match(r'^\d+', line):
                pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(line)); pdf.set_font("Arial", size=10);
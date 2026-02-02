import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if 'logado' not in st.session_state:
    st.session_state.perfil = None

for key in ['sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else ""

# --- 2. LOGIN ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    return "admin" if pin == p_prof else "aluno" if pin == p_aluno else None

if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin_input)
        if res: 
            st.session_state.perfil = res
            st.session_state.logado = True 
            st.rerun()
        else: st.error("PIN Incorreto")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Usar cabecalho.png", value=True)
recuo_cabecalho = st.sidebar.slider("Altura do Título:", 20, 80, 45)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 Limpar Atividade", use_container_width=True):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()

if st.sidebar.button("🚪 Sair / Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- 4. CENTRO DE COMANDO ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas", use_container_width=True): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
if g6.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara", use_container_width=True): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS (FOCO NO COLEGIAL COM SÍMBOLOS) ---
if menu == "op":
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Atividade"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        qs = [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", f"t. Atividade de {tipo}", "1. Calcule:"] + qs

elif menu == "eq":
    tipo = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Equações"):
        if tipo == "1º Grau":
            qs = [f"{random.randint(2,10)}x {'+' if random.random()>0.5 else '-'} {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(8)]
        else:
            qs = [f"x² {'-' if random.random()>0.5 else '+'} {random.randint(2,10)}x + {random.randint(1,16)} = 0" for _ in range(5)]
        st.session_state.preview_questoes = [".M1", f"t. Equações de {tipo}", "1. Resolva:"] + qs

elif menu == "col":
    tipo = st.radio("Tema:", ["Potenciação", "Radiciação", "Porcentagem"], horizontal=True)
    if st.button("Gerar Atividade Colegial"):
        if tipo == "Potenciação":
            qs = [f"{random.randint(2,12)}² =" for _ in range(12)]
            st.session_state.preview_questoes = [".M1", "t. Potenciação", "1. Calcule:"] + qs
        elif tipo == "Radiciação":
            qs = []
            for _ in range(10):
                if random.choice([True, False]):
                    base = random.randint(2, 12)**2
                    qs.append(f"√{base} =")
                else:
                    base = random.randint(2, 5)**3
                    qs.append(f"³√{base} =")
            st.session_state.preview_questoes = [".M1", "t. Radiciação", "1. Calcule as raízes:"] + qs
        else:
            qs = [f"{random.choice([5,10,25,50])}% de {random.randint(10, 500)} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", "t. Porcentagem", "1. Calcule:"] + qs

elif menu == "man":
    txt = st.text_area("Texto Manual:")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n")

# --- 7. MOTOR PDF (SUPORTE A SÍMBOLOS) ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    for line in st.session_state.preview_questoes: st.write(line)

    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        y_ini = 10
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            y_ini = recuo_cabecalho 
        pdf.set_y(y_ini)
        letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
        larg_col = 190 / int(layout_cols)
        
        # O segredo para símbolos: Usar fontes padrão que aceitem o mapeamento
        pdf.set_font("Helvetica", size=12)
        
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            
            # Ajuste de símbolos para o PDF
            line = line.replace('³√', '3v').replace('√', 'v')
            
            if line.startswith(".M"):
                pdf.set_font("Helvetica", size=12); pdf.cell(190, 10, line[1:], ln=True)
            elif line.lower().startswith("t."):
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", size=12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                pdf.set_font("Helvetica", size=12)
                col = l_idx % int(layout_cols)
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line}", ln=(col == int(layout_cols)-1))
                l_idx += 1
        
        return bytes(pdf.output())

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf", mime="application/pdf")
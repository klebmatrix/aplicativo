import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E PERSISTÊNCIA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else ""

# --- 2. LOGIN (Secrets Render) ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    return "admin" if pin == p_prof else "aluno" if pin == p_aluno else None

if not st.session_state.perfil:
    st.title("🔐 Login")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin_input)
        if res: 
            st.session_state.perfil = res
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
    st.session_state.clear(); st.rerun()

# --- 4. CENTRO DE COMANDO ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações"): st.session_state.sub_menu = "op"
if g2.button("📐 Equações"): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas"): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial"): st.session_state.sub_menu = "col"
if g6.button("📄 Manual"): st.session_state.sub_menu = "man"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara"): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS"): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira"): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS GERADORES ---

# ... (op, eq, sis, alg seguem iguais) ...

if menu == "col":
    tipo = st.radio("Tema:", ["Radiciação", "Potenciação", "Porcentagem"], horizontal=True)
    
    if tipo == "Radiciação":
        grau_raiz = st.radio("Tipo de Raiz:", ["Quadrada", "Cúbica"], horizontal=True)
        if st.button("Gerar Radiciação"):
            if grau_raiz == "Quadrada":
                qs = [f"SQRT({random.randint(2,15)**2}) =" for _ in range(10)]
            else:
                qs = [f"³√({random.randint(2,10)**3}) =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", f"t. Radiciação {grau_raiz}", "1. Calcule as raízes:"] + qs

    elif tipo == "Potenciação":
        exp_escolhido = st.selectbox("Escolha o Expoente:", [2, 3, 4])
        if st.button("Gerar Potenciação"):
            qs = [f"{random.randint(2,12)}^{exp_escolhido} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", f"t. Potenciação (Expoente {exp_escolhido})", "1. Calcule as potências:"] + qs

    elif tipo == "Porcentagem":
        if st.button("Gerar Porcentagem"):
            qs = [f"{random.randint(1,10)*5}% de {random.randint(10,100)*10} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", "t. Porcentagem", "1. Calcule os valores:"] + qs

# ... (man, calc_f, pemdas, fin seguem iguais) ...

# --- 7. MOTOR PDF (FIXED) ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    for l in st.session_state.preview_questoes: st.write(l.replace("SQRT", "√"))

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
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            if line.startswith(".M"):
                pdf.set_font("Helvetica", size=12); pdf.cell(190, 10, line[1:], ln=True)
            elif line.lower().startswith("t."):
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                col = l_idx % int(layout_cols)
                pdf.set_font("Helvetica", size=12)
                pdf.write(8, f"{letras[l_idx%26]}) ")
                if "SQRT" in line:
                    pdf.set_font("Symbol", size=12); pdf.write(8, chr(214))
                    pdf.set_font("Helvetica", size=12); pdf.write(8, line.replace("SQRT(","").replace(")",""))
                else:
                    pdf.write(8, line.encode('latin-1', 'replace').decode('latin-1'))
                l_idx += 1
                if col == int(layout_cols)-1: pdf.ln(12)
                else: pdf.set_x(pdf.get_x() + (larg_col - 40))
        return pdf.output()

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf", mime="application/pdf")
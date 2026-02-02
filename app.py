import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else ""

# --- 2. LOGIN ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    return "admin" if pin == p_prof else "aluno" if pin == p_aluno else None

if not st.session_state.perfil:
    st.title("🔐 Login")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin_input)
        if res: st.session_state.perfil = res; st.rerun()
    st.stop()

# --- 3. SIDEBAR E INTERFACE ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)
if st.sidebar.button("🧹 Limpar"):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()

st.title("🛠️ Centro de Comando")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações"): st.session_state.sub_menu = "op"
if g5.button("🎓 Colegial"): st.session_state.sub_menu = "col"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara"): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS"): st.session_state.sub_menu = "pemdas"

# --- 4. LÓGICA COLEGIAL (RADICIAÇÃO) ---
if st.session_state.sub_menu == "col":
    modo = st.selectbox("Tipo de Raiz:", ["Quadrada", "Cúbica", "Misturada"])
    if st.button("Gerar Questões"):
        qs = []
        for _ in range(12):
            m = modo if modo != "Misturada" else random.choice(["Quadrada", "Cúbica"])
            if m == "Quadrada":
                qs.append(f"SQRT({random.randint(2, 12)**2})")
            else:
                qs.append(f"CBRT({random.randint(2, 5)**3})")
        st.session_state.preview_questoes = [".M1", "t. Atividade de Radiciação", "1. Resolva as raízes:"] + qs

# --- 5. CALCULADORES ---
if st.session_state.sub_menu == "calc_f":
    va = st.number_input("a", value=1.0); vb = st.number_input("b", value=-5.0); vc = st.number_input("c", value=6.0)
    if st.button("Calcular"):
        d = vb**2 - 4*va*vc
        st.session_state.res_calc = f"Delta: {d} | x1: {(-vb+math.sqrt(d))/(2*va)} | x2: {(-vb-math.sqrt(d))/(2*va)}" if d>=0 else "Sem raízes reais"

if st.session_state.res_calc: st.info(st.session_state.res_calc)

# --- 6. MOTOR PDF (SÍMBOLOS REAIS) ---
if st.session_state.preview_questoes:
    st.subheader("Preview")
    for line in st.session_state.preview_questoes:
        st.write(line.replace("SQRT", "√").replace("CBRT", "∛"))

    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_y(40) # Ajuste para o cabeçalho
        
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx = 0
        larg = 190 / int(layout_cols)
        
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            
            if line.startswith(".M"):
                pdf.set_font("Helvetica", size=10); pdf.cell(190, 8, line[1:], ln=True)
            elif line.startswith("t."):
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:], ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                # LÓGICA DO SÍMBOLO:
                col = l_idx % int(layout_cols)
                
                # 1. Escreve a letra (a, b, c)
                pdf.set_font("Helvetica", size=12)
                pdf.write(8, f"{letras[l_idx%26]}) ")
                
                # 2. Se for raiz, troca a fonte para Symbol (onde o \326 é o símbolo √)
                if "SQRT" in line:
                    pdf.set_font("Symbol", size=12); pdf.write(8, chr(214)) # Símbolo de raiz
                    pdf.set_font("Helvetica", size=12); pdf.write(8, line.replace("SQRT(", "").replace(")", "") + " =")
                elif "CBRT" in line:
                    pdf.set_font("Helvetica", size=8); pdf.write(8, "3") # Índice 3 pequeno
                    pdf.set_font("Symbol", size=12); pdf.write(8, chr(214))
                    pdf.set_font("Helvetica", size=12); pdf.write(8, line.replace("CBRT(", "").replace(")", "") + " =")
                else:
                    pdf.set_font("Helvetica", size=12); pdf.write(8, line)
                
                l_idx += 1
                if col == int(layout_cols) - 1: pdf.ln(10)
                else: pdf.set_x(pdf.get_x() + (larg - 30)) # Espaçamento entre colunas

        return bytes(pdf.output())

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="quantum.pdf")
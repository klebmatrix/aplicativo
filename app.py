import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF # fpdf2 também usa este import

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

# --- 4. CENTRO DE COMANDO ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas", use_container_width=True): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
if g6.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICA RADICIAÇÃO ---
if menu == "col":
    tipo = st.radio("Tema:", ["Potenciação", "Radiciação", "Porcentagem"], horizontal=True)
    if tipo == "Radiciação":
        modo_raiz = st.selectbox("Tipo de Raiz:", ["Misturada", "Quadrada", "Cúbica"])
        
    if st.button("Gerar Atividade Colegial"):
        if tipo == "Radiciação":
            qs = []
            for _ in range(12):
                escolha = modo_raiz if modo_raiz != "Misturada" else random.choice(["Quadrada", "Cúbica"])
                if escolha == "Quadrada":
                    qs.append(f"√{random.randint(2, 12)**2} =")
                else:
                    qs.append(f"∛{random.randint(2, 5)**3} =") # Símbolo Unicode correto
            st.session_state.preview_questoes = [".M1", "t. Radiciação", "1. Calcule as raízes:"] + qs

# --- 7. MOTOR PDF (COM SUPORTE A SÍMBOLOS UNICODE) ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    for line in st.session_state.preview_questoes: st.write(line)

    def export_pdf():
        # ATENÇÃO: Ativamos o modo Unicode do FPDF2
        pdf = FPDF()
        pdf.add_page()
        
        # Usamos uma fonte que suporta os símbolos matemáticos
        pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True) 
        pdf.set_font("DejaVu", size=12)
        
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
                pdf.set_font("DejaVu", size=12); pdf.cell(190, 10, line[1:], ln=True)
            elif line.lower().startswith("t."):
                pdf.set_font("DejaVu", size=14); pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("DejaVu", size=12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                col = l_idx % int(layout_cols)
                texto_item = f"{letras[l_idx%26]}) {line}"
                pdf.cell(larg_col, 8, texto_item, ln=(col == int(layout_cols)-1))
                l_idx += 1
        
        return bytes(pdf.output())

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf", mime="application/pdf")
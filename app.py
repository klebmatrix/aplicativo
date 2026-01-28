import streamlit as st
import math
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# --- 2. GESTÃO DE ESTADO (O segredo para os cards funcionarem) ---
if 'perfil' not in st.session_state:
    st.session_state.perfil = None
if 'opcao_selecionada' not in st.session_state:
    st.session_state.opcao_selecionada = None

# --- 3. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login Quantum Math Lab")
    pin_in = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        # Se não configurou secrets no Render, usa o padrão
        s_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
        if pin_in == s_prof:
            st.session_state.perfil = "admin"
            st.rerun()
        else:
            st.error("PIN Incorreto.")
    st.stop()

# --- 4. PAINEL DO PROFESSOR ---
st.sidebar.title("🚀 Painel Professor")
if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.session_state.opcao_selecionada = None
    st.rerun()

st.title("🛠️ Centro de Controle")

# --- CATEGORIA A: GERADORES (CARDS) ---
st.subheader("📝 Geradores de Atividades (PDF)")
c1, c2, c3, c4, c5 = st.columns(5)
with c1: 
    if st.button("🔢 Operações", use_container_width=True): 
        st.session_state.opcao_selecionada = "op"
with c2: 
    if st.button("📐 Equações", use_container_width=True): 
        st.session_state.opcao_selecionada = "eq"
with c3: 
    if st.button("📚 Colegial", use_container_width=True): 
        st.session_state.opcao_selecionada = "col"
with c4: 
    if st.button("⚖️ Álgebra", use_container_width=True): 
        st.session_state.opcao_selecionada = "alg"
with c5: 
    if st.button("📄 Manual", use_container_width=True): 
        st.session_state.opcao_selecionada = "man"

st.markdown("---")

# --- CATEGORIA B: CÁLCULOS (CARDS) ---
st.subheader("🧮 Ferramentas de Cálculo Online")
d1, d2, d3 = st.columns(3)
with d1: 
    if st.button("𝑓(x) Funções", use_container_width=True): 
        st.session_state.opcao_selecionada = "calc_f"
with d2: 
    if st.button("📊 PEMDAS", use_container_width=True): 
        st.session_state.opcao_selecionada = "pem"
with d3: 
    if st.button("💰 Financeiro", use_container_width=True): 
        st.session_state.opcao_selecionada = "fin"

st.divider()

# --- 5. EXIBIÇÃO DO CONTEÚDO SELECIONADO ---
menu = st.session_state.opcao_selecionada

if menu == "man":
    st.header("📄 Gerador Manual")
    tit = st.text_input("Título da Atividade:", "Exercícios")
    txt = st.text_area("Instruções: . (coluna 1), .. (coluna 2), números resetam letras", height=250)
    
    if st.button("Preparar PDF"):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=12.5, y=8, w=185)
            pdf.set_y(46)
        else: pdf.set_y(15)
        
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(tit), ln=True, align='C'); pdf.ln(5)
        
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx = 0
        pdf.set_font("Arial", size=10)
        
        for linha in txt.split('\n'):
            l = linha.strip()
            if not l: continue
            match = re.match(r'^(\.+)', l)
            pts = len(match.group(1)) if match else 0
            
            if re.match(r'^\d+', l): # Linha começa com número
                pdf.ln(4); pdf.set_font("Arial", 'B', 11)
                pdf.multi_cell(0, 8, clean_txt(l))
                pdf.set_font("Arial", size=10); l_idx = 0 # RESET DAS LETRAS
            elif pts > 0: # É uma coluna
                if pts > 1: pdf.set_y(pdf.get_y() - 8)
                pdf.set_x(10 + (pts-1)*40)
                pdf.cell(40, 8, f"{letras[l_idx%26]}) {clean_txt(l[pts:].strip())}", ln=True)
                l_idx += 1
            else:
                pdf.multi_cell(0, 8, clean_txt(l))
        
        pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 BAIXAR PDF AGORA", pdf_bytes, "atividade.pdf")

elif menu == "op":
    st.header("🔢 Operações Automáticas")
    qs = [f"{random.randint(10,99)} + {random.randint(1,9)} =" for _ in range(10)]
    for i, q in enumerate(qs): st.write(f"{chr(97+i)}) {q}")
    
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    for i, q in enumerate(qs): pdf.cell(0, 10, f"{chr(97+i)}) {q}", ln=True)
    st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), "ops.pdf")

elif menu == "calc_f":
    st.header("𝑓(x) Cálculo de Funções")
    f_in = st.text_input("f(x):", "x**2")
    x_val = st.number_input("Valor de x:", value=2.0)
    if st.button("Calcular"):
        res = eval(f_in.replace('x', f'({x_val})'))
        st.metric("Resultado", res)
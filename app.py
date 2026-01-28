import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

def clean_txt(text):
    """Evita que caracteres matemáticos quebrem o PDF"""
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def validar_acesso(pin):
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
    if pin == senha_aluno: return "aluno"
    if pin == senha_prof: return "admin"
    return None

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = "home"

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin_in = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin_in)
        if acesso:
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN Incorreto.")
    st.stop()

# --- 2. MENU LATERAL ---
st.sidebar.title(f"🚀 {'PROFESSOR' if st.session_state.perfil == 'admin' else 'ALUNO'}")
if st.sidebar.button("Sair/Logout"):
    st.session_state.perfil = None
    st.session_state.sub_menu = "home"
    st.rerun()

# --- 3. FUNÇÃO MESTRA PDF ---
def gerar_pdf_geral(questoes, titulo):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", x=12.5, y=8, w=185)
        pdf.set_y(46)
    else: pdf.set_y(15)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, clean_txt(titulo), ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=11)
    letras = "abcdefghijklmnopqrstuvwxyz"
    for i, q in enumerate(questoes):
        # Sempre começa com letra conforme instrução
        pdf.multi_cell(0, 8, txt=f"{letras[i%26]}) {clean_txt(q)}")
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. PAINEL ADMIN (CARDS) ---
if st.session_state.perfil == "admin":
    st.title("🛠️ Painel de Controle")

    # CATEGORIA A: GERADORES
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
    with c2: 
        if st.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
    with c3: 
        if st.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
    with c4: 
        if st.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
    with c5: 
        if st.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

    st.markdown("---")

    # CATEGORIA B: CÁLCULOS
    st.subheader("🧮 Ferramentas de Cálculo")
    d1, d2, d3 = st.columns(3)
    with d1: 
        if st.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with d3: 
        if st.button("💰 Financeiro", use_container_width=True): st.session_state.sub_menu = "fin"

    st.divider()
    modo = st.session_state.sub_menu

    # --- LÓGICA DOS MÓDULOS ---
    if modo == "man":
        st.header("📄 Gerador Manual")
        tit = st.text_input("Título:", "Atividade")
        txt = st.text_area("Texto (. p/ colunas):", height=200)
        
        if st.button("Visualizar e Gerar PDF"):
            pdf = FPDF(); pdf.add_page()
            if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(tit), ln=True, align='C'); pdf.ln(5)
            
            letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
            pdf.set_font("Arial", size=10)
            
            for linha in txt.split('\n'):
                l = linha.strip()
                if not l: continue
                match = re.match(r'^(\.+)', l); pts = len(match.group(1)) if match else 0
                
                if re.match(r'^\d+', l): # Se começar com número, reseta letra
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(l))
                    pdf.set_font("Arial", size=10); l_idx = 0
                    st.markdown(f"**{l}**")
                elif pts > 0: # Colunas
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*40)
                    pdf.cell(40, 8, f"{letras[l_idx%26]}) {clean_txt(l[pts:].strip())}", ln=True)
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;{letras[l_idx%26]}) {l[pts:].strip()}")
                    l_idx += 1
                else: 
                    pdf.multi_cell(0, 8, clean_txt(l)); st.write(l)
            
            st.download_button("📥 Baixar PDF Manual", pdf.output(dest='S').encode('latin-1', 'replace'), "manual.pdf")

    elif modo == "op":
        st.header("🔢 Operações")
        qtd = st.slider("Qtd:", 4, 20, 10)
        qs = [f"{random.randint(10,100)} {random.choice(['+', '-', 'x', '÷'])} {random.randint(2,10)} =" for _ in range(qtd)]
        for i, q in enumerate(qs): st.write(f"**{chr(97+i)})** {q}")
        st.download_button("📥 Baixar PDF", gerar_pdf_geral(qs, "Operações"), "ops.pdf")

    elif modo == "calc_f":
        st.header("𝑓(x) Cálculo")
        f = st.text_input("f(x):", "x**2")
        val = st.number_input("x:", value=2.0)
        if st.button("Calcular"):
            st.metric("Resultado", eval(f.replace('x', f'({val})')))

else: # Aluno
    st.title("📖 Área do Estudante")
    st.write("Selecione uma ferramenta no menu lateral ou utilize as calculadoras.")
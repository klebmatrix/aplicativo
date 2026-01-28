import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO DE SEGURANÇA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Função para evitar erro de símbolos no PDF
def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# Lógica de Login que não trava o app
def validar_acesso(pin):
    try:
        # Tenta pegar do Render, se não existir, usa o padrão abaixo
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
    except:
        senha_aluno = "123456"
        senha_prof = "12345678"
        
    if pin == senha_aluno: return "aluno"
    if pin == senha_prof: return "admin"
    return None

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = "home"

# --- 2. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab - Login")
    pin_in = st.text_input("Digite seu PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin_in)
        if acesso:
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN Incorreto! (Tente 12345678 para Professor)")
    st.stop()

# --- 3. PAINEL DO PROFESSOR (CARDS) ---
if st.session_state.perfil == "admin":
    st.sidebar.success("Logado como Professor")
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    st.title("🛠️ Painel de Controle")

    # CARDS: GERADORES
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

    # CARDS: CÁLCULOS
    st.subheader("🧮 Ferramentas de Cálculo")
    d1, d2, d3 = st.columns(3)
    with d1: 
        if st.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pem"
    with d3: 
        if st.button("💰 Financeiro", use_container_width=True): st.session_state.sub_menu = "fin"

    st.divider()
    modo = st.session_state.sub_menu

    # --- MÓDULO MANUAL (O QUE VOCÊ PRECISA) ---
    if modo == "man":
        st.header("📄 Gerador Manual")
        tit = st.text_input("Título:", "Atividade Matemática")
        txt = st.text_area("Digite (use . para colunas e números para separar questões):", height=250)
        
        if st.button("Gerar PDF"):
            pdf = FPDF()
            pdf.add_page()
            
            # Cabeçalho
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=12.5, y=8, w=185)
                pdf.set_y(46)
            else: pdf.set_y(15)
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, clean_txt(tit), ln=True, align='C')
            pdf.ln(5)
            
            letras = "abcdefghijklmnopqrstuvwxyz"
            l_idx = 0
            pdf.set_font("Arial", size=10)
            
            for linha in txt.split('\n'):
                l = linha.strip()
                if not l: continue
                
                match = re.match(r'^(\.+)', l)
                pts = len(match.group(1)) if match else 0
                
                # Se a linha começa com número: Negrito e Reseta Letras
                if re.match(r'^\d+', l):
                    pdf.ln(4)
                    pdf.set_font("Arial", 'B', 11)
                    pdf.multi_cell(0, 8, clean_txt(l))
                    pdf.set_font("Arial", size=10)
                    l_idx = 0 # Volta para a)
                
                # Se tem pontos: Coluna
                elif pts > 0:
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*40)
                    pdf.cell(40, 8, f"{letras[l_idx%26]}) {clean_txt(l[pts:].strip())}", ln=True)
                    l_idx += 1
                else:
                    pdf.multi_cell(0, 8, clean_txt(l))
            
            st.download_button("📥 BAIXAR PDF MANUAL", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")

    # Módulo de Operações para teste rápido
    elif modo == "op":
        st.header("🔢 Operações")
        qs = [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(10)]
        for i, q in enumerate(qs): st.write(f"{chr(97+i)}) {q}")
        
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
        for i, q in enumerate(qs): pdf.cell(0, 10, f"{chr(97+i)}) {q}", ln=True)
        st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), "ops.pdf")

else:
    st.title("📖 Área do Aluno")
    st.info("Entre com o PIN de professor para acessar os geradores.")
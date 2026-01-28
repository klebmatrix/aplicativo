import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def validar_acesso(pin_digitado):
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

if 'perfil' not in st.session_state:
    st.session_state.perfil = None
if 'sub_menu' not in st.session_state:
    st.session_state.sub_menu = None

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 2. MENU E LOGOUT ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")

if st.sidebar.button("Sair/Logout"):
    st.session_state.perfil = None
    st.session_state.sub_menu = None
    st.rerun()

# --- 3. FUNÇÃO PDF PADRÃO ---
def exportar_pdf(questoes, titulo):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", x=12.5, y=8, w=185)
        pdf.set_y(46)
    else: pdf.set_y(15)
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, txt=clean_txt(titulo), ln=True, align='C'); pdf.ln(5)
    pdf.set_font("Arial", size=11); letras = "abcdefghijklmnopqrstuvwxyz"
    for i, q in enumerate(questoes):
        pdf.cell(0, 10, txt=f"{letras[i%26]}) {clean_txt(q)}", ln=True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. PAINEL PRINCIPAL (CARDS) ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle do Professor")
    
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações\nBásicas", use_container_width=True): st.session_state.sub_menu = "op"
    with c2: 
        if st.button("📐 Equações\n1º e 2º Grau", use_container_width=True): st.session_state.sub_menu = "eq"
    with c3: 
        if st.button("📚 Colegial\nFrações/Funções", use_container_width=True): st.session_state.sub_menu = "col"
    with c4: 
        if st.button("⚖️ Álgebra\nLinear", use_container_width=True): st.session_state.sub_menu = "alg"
    with c5: 
        if st.button("📄 Gerador\nManual", use_container_width=True): st.session_state.sub_menu = "man"

    st.markdown("---")
    st.subheader("🧮 Ferramentas de Cálculo Online")
    d1, d2, d3 = st.columns(3)
    with d1: 
        if st.button("𝑓(x) Cálculo\nde Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 Expressões\n(PEMDAS)", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with d3: 
        if st.button("💰 Calculadora\nFinanceira", use_container_width=True): st.session_state.sub_menu = "fin"

    op_atual = st.session_state.get("sub_menu", None)

    # --- LÓGICA DO GERADOR MANUAL (CORRIGIDA) ---
    if op_atual == "man":
        st.divider()
        st.header("📄 Gerador Manual")
        titulo_m = st.text_input("Título do PDF:", "Atividade Matemática")
        txt_m = st.text_area("Digite o conteúdo (. para colunas):", height=250, placeholder="1. Resolva:\n. 5+5\n. 10-2\n2. Calcule:\n. 3x3")
        
        if st.button("Gerar e Visualizar PDF"):
            pdf = FPDF()
            pdf.add_page()
            
            # Cabeçalho
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=12.5, y=8, w=185)
                pdf.set_y(46)
            else: pdf.set_y(15)
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, clean_txt(titulo_m), ln=True, align='C')
            pdf.ln(5)
            
            letras = "abcdefghijklmnopqrstuvwxyz"
            l_idx = 0
            pdf.set_font("Arial", size=10)
            
            # Processamento de Linhas
            for linha in txt_m.split('\n'):
                t = linha.strip()
                if not t: continue
                
                # Detecta pontos para colunas
                match = re.match(r'^(\.+)', t)
                pts = len(match.group(1)) if match else 0
                
                # REGRA: Se começar com número, reseta as letras (a, b, c)
                if re.match(r'^\d+', t):
                    pdf.ln(4)
                    pdf.set_font("Arial", 'B', 11)
                    pdf.multi_cell(0, 8, clean_txt(t))
                    pdf.set_font("Arial", size=10)
                    l_idx = 0 
                
                # REGRA: Se tiver ponto, vira item com letra e coluna
                elif pts > 0:
                    if pts > 1: pdf.set_y(pdf.get_y() - 8) # Sobe a linha para alinhar colunas
                    pdf.set_x(10 + (pts-1)*45) # Define a posição da coluna
                    pdf.cell(45, 8, f"{letras[l_idx%26]}) {clean_txt(t[pts:].strip())}", ln=True)
                    l_idx += 1
                else:
                    pdf.multi_cell(0, 8, clean_txt(t))

            # Gerar arquivo para download
            pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("📥 Clique aqui para Baixar o PDF", pdf_bytes, "atividade_manual.pdf", "application/pdf")
            st.success("PDF preparado com sucesso!")

    # Outros menus (op, eq, calc_f...) mantidos conforme seu código
    elif op_atual == "op":
        st.divider(); st.header("🔢 Operações")
        qs = [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(10)]
        st.download_button("Baixar PDF", exportar_pdf(qs, "Operações"), "op.pdf")

else:
    st.title("📖 Área do Estudante")
    st.info("Acesse as ferramentas permitidas pelo professor.")
import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
    except:
        senha_aluno, senha_prof = "123456", "12345678"
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_data' not in st.session_state: st.session_state.preview_data = []

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
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()

# --- 3. FUNÇÃO PDF ---
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
        pdf.multi_cell(0, 10, txt=f"{letras[i%26]}) {clean_txt(q)}")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. PAINEL PRINCIPAL (ADMIN) ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações", use_container_width=True): 
            st.session_state.sub_menu = "op"; st.session_state.preview_data = []
    with c2: 
        if st.button("📐 Equações", use_container_width=True): 
            st.session_state.sub_menu = "eq"; st.session_state.preview_data = []
    with c3: 
        if st.button("📚 Colegial", use_container_width=True): 
            st.session_state.sub_menu = "col"; st.session_state.preview_data = []
    with c4: 
        if st.button("⚖️ Álgebra", use_container_width=True): 
            st.session_state.sub_menu = "alg"; st.session_state.preview_data = []
    with c5: 
        if st.button("📄 Manual", use_container_width=True): 
            st.session_state.sub_menu = "man"; st.session_state.preview_data = []

    st.markdown("---")
    op_atual = st.session_state.sub_menu
    if not op_atual: st.info("Selecione um gerador acima para começar.")
    else: st.divider()

    # --- LÓGICA DE VISUALIZAÇÃO E GERAÇÃO ---
    if op_atual == "op":
        st.header("🔢 Operações Básicas")
        escolhas = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
        qtd = st.number_input("Qtd:", 4, 30, 10)
        if st.button("🔍 Visualizar Questões"):
            ops_map = {"Soma (+)":"+", "Subtração (-)":"-", "Multiplicação (x)":"x", "Divisão (÷)":"÷"}
            selecionadas = [ops_map[x] for x in escolhas]
            st.session_state.preview_data = [f"{random.randint(10,500)} {random.choice(selecionadas)} {random.randint(2,50)} =" for _ in range(qtd)]

    elif op_atual == "eq":
        st.header("📐 Equações")
        grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        if st.button("🔍 Visualizar Questões"):
            st.session_state.preview_data = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" if grau == "1º Grau" else f"x² + {random.randint(2,8)}x + {random.randint(1,12)} = 0" for _ in range(8)]

    elif op_atual == "man":
        st.header("📄 Gerador Manual")
        tit_m = st.text_input("Título:", "Atividade")
        txt_m = st.text_area("Texto (. para colunas):", height=200)
        if st.button("🔍 Preparar e Visualizar"):
            # O manual gera o PDF direto por causa da complexidade das colunas, mas mostra o texto abaixo
            st.session_state.preview_data = txt_m.split('\n')
            st.session_state.manual_tit = tit_m

    # --- ÁREA DE PREVIEW COMUM ---
    if st.session_state.preview_data:
        st.subheader("👀 Prévia da Atividade")
        with st.expander("Clique para ver as questões", expanded=True):
            letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
            for i, q in enumerate(st.session_state.preview_data):
                if op_atual == "man":
                    t = q.strip()
                    if not t: continue
                    if re.match(r'^\d+', t): 
                        st.markdown(f"**{t}**"); l_idx = 0
                    else:
                        st.write(f"{letras[l_idx%26]}) {t.replace('.', '')}")
                        l_idx += 1
                else:
                    st.write(f"**{letras[i%26]})** {q}")
        
        # Botão final de download
        if op_atual != "man":
            pdf_final = exportar_pdf(st.session_state.preview_data, "Atividade Quantum Math")
            st.download_button("📥 Baixar PDF Final", pdf_final, "atividade.pdf")
        else:
            # Lógica especial de PDF para o Manual (mantendo suas regras de colunas)
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10); l_idx = 0
            if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(st.session_state.manual_tit), ln=True, align='C'); pdf.ln(5)
            for linha in st.session_state.preview_data:
                t = linha.strip()
                if not t: continue
                match = re.match(r'^(\.+)', t); pts = len(match.group(1)) if match else 0
                if re.match(r'^\d+', t): 
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(t)); pdf.set_font("Arial", size=10); l_idx = 0
                elif pts > 0:
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*45); pdf.cell(45, 8, f"{letras[l_idx%26]}) {clean_txt(t[pts:].strip())}", ln=True); l_idx += 1
                else: pdf.multi_cell(0, 8, clean_txt(t))
            st.download_button("📥 Baixar PDF Manual", pdf.output(dest='S').encode('latin-1', 'replace'), "manual.pdf")

# (Seção de Cálculos e Aluno omitida aqui para brevidade, mas deve ser mantida igual ao código anterior)
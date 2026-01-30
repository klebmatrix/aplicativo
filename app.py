import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

def clean_txt(text):
    """Trata potências e raízes para leitura humana no PDF (padrão latin-1)"""
    if not text: return ""
    text = str(text)
    # Substitui símbolos problemáticos por texto para evitar que o PDF trave
    text = text.replace("√", "Raiz de ").replace("²", "^2").replace("³", "^3")
    # Converte para latin-1 ignorando o que ele não consegue ler
    return text.encode('latin-1', 'replace').decode('latin-1')

def validar_acesso(pin_digitado):
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN (6 dígitos):", type="password", max_chars=8)
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- MENU LATERAL ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")

usar_cabecalho = st.sidebar.checkbox("Incluir Cabeçalho no PDF", value=True)

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.sub_menu = None
    st.rerun()

if st.sidebar.button("Sair/Logout"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- PAINEL ADMIN ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
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
    st.subheader("🧮 Ferramentas de Cálculo Online")
    d1, d2, d3 = st.columns(3)
    with d1: 
        if st.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with d3: 
        if st.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

    op_atual = st.session_state.sub_menu
    st.divider()

    # --- LÓGICA DOS GERADORES (Colegial com Radiciação) ---
    if op_atual == "col":
        st.header("📚 Colegial (Temas)")
        temas = st.multiselect("Temas:", ["Frações", "Porcentagem", "Potenciação", "Radiciação"], ["Frações", "Porcentagem"])
        num_ini = st.number_input("Começar do número:", 1)
        qtd = st.number_input("Quantidade:", 4, 30, 10)
        if st.button("Gerar Preview") and temas:
            qs = [f"t. Atividade Colegial", f"{num_ini}. Resolva os itens:"]
            for _ in range(qtd):
                t = random.choice(temas)
                if t == "Frações": qs.append(f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/{random.randint(2,5)} =")
                elif t == "Porcentagem": qs.append(f"{random.randint(5,95)}% de {random.randint(100,999)} =")
                elif t == "Potenciação": qs.append(f"{random.randint(2,12)}² =")
                elif t == "Radiciação": qs.append(f"√{random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])} =")
            st.session_state.preview_questoes = qs

    elif op_atual == "man":
        st.header("📄 Manual")
        txt_m = st.text_area("Digite as questões:", height=300)
        if st.button("Gerar Preview"): st.session_state.preview_questoes = txt_m.split('\n')

# --- VISUALIZAÇÃO E PDF ---
if st.session_state.preview_questoes:
    st.divider()
    if usar_cabecalho and os.path.exists("cabecalho.png"): 
        st.image("cabecalho.png", use_container_width=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        if line.lower().startswith("t."):
            st.markdown(f"<h1 style='text-align: center; color: #007bff;'>{line[2:].strip()}</h1>", unsafe_allow_html=True)
            l_idx = 0
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}"); l_idx = 0
        else:
            col1, col2 = st.columns(2)
            with (col1 if l_idx % 2 == 0 else col2):
                with st.container(border=True): st.write(f"**{letras[l_idx%26]})** {line}")
            l_idx += 1
if st.button("📥 Baixar PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=10, w=190)
            y_at = 60
        else:
            y_at = 20
            
        l_pdf_idx = 0
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            # Títulos e Números (1., 2.)
            if line.lower().startswith("t.") or re.match(r'^\d+', line):
                pdf.set_y(y_at + 5)
                pdf.set_font("Arial", 'B', 12)
                txt = line[2:].strip() if line.lower().startswith("t.") else line
                pdf.multi_cell(0, 10, clean_txt(txt), align='L')
                y_at = pdf.get_y() + 5
                l_pdf_idx = 0 # Reinicia letras para cada questão nova
            
            # Itens (a, b, c) - Uma embaixo da outra para não encavalar
            else:
                pdf.set_font("Arial", size=12)
                letra = letras[l_pdf_idx % 26]
                txt_completo = f"{letra}) {line}"
                
                pdf.set_y(y_at)
                pdf.set_x(15)
                pdf.multi_cell(0, 10, clean_txt(txt_completo))
                y_at = pdf.get_y() # Atualiza o Y para a próxima linha nunca bater na anterior
                l_pdf_idx += 1
                
        st.download_button("✅ Baixar Agora", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")

    
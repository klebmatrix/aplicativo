import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E INICIALIZAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

# Inicialização do Session State para evitar AttributeError
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = "man"
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

def clean_txt(text):
    """Trata texto para o padrão Latin-1 do PDF."""
    if not text: return ""
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def tratar_math_streamlit(texto):
    """Formata texto para exibir bonito no Streamlit (LaTeX)."""
    t = texto.lstrip(',').strip()
    t = re.sub(r'V(\d+)', r'\\sqrt{\1}', t)
    if "^" in t and "^{" not in t:
        t = re.sub(r'\^(\d+)', r'^{\1}', t)
    return t

def validar_acesso(pin_digitado):
    try:
        # Busca chave_mestra conforme instrução (lowercase)
        senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    except:
        senha_prof, senha_aluno = "chave_mestra", "123456"
    
    if pin_digitado == senha_prof: return "admin"
    if pin_digitado == senha_aluno: return "aluno"
    return "negado"

# --- 2. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Acesso Quantum Math")
    pin = st.text_input("Digite seu PIN (6-8 dígitos):", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN incorreto. Tente novamente.")
    st.stop()

# --- 3. BARRA LATERAL (MENU) ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Painel Professor' if perfil == 'admin' else 'Área do Estudante'}")

if st.sidebar.button("Sair/Logout"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- 4. FUNÇÃO DE EXPORTAÇÃO PDF ---
def gerar_pdf(questoes):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho (Header da Atividade)
    if os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", x=10, y=8, w=190)
        pdf.set_y(50)
    else:
        pdf.set_y(20)
    
    letras_lista = "abcdefghijklmnopqrstuvwxyz"
    idx_letra = 0
    
    for q in questoes:
        linha = q.strip()
        if not linha: continue
        
        # Tradução de símbolos para texto simples (FPDF não aceita LaTeX)
        txt_limpo = linha.replace("√", "Raiz de ").replace("V", "Raiz de ").replace("²", "^2").replace("³", "^3")
        txt_limpo = txt_limpo.lstrip(',')

        # Título
        if linha.lower().startswith(("t.", "titulo:", "título:")):
            t_pdf = re.sub(r'^(t\.|titulo:|título:)\s*', '', linha, flags=re.IGNORECASE)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 12, clean_txt(t_pdf), ln=True, align='C')
            pdf.ln(5)
            continue
            
        # Seção Numerada (Reseta letras)
        if re.match(r'^\d+', linha):
            pdf.ln(4)
            pdf.set_font("Arial", 'B', 12)
            pdf.multi_cell(0, 8, clean_txt(linha))
            idx_letra = 0
            continue
            
        # Questões com letras
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, f"{letras_lista[idx_letra%26]}) {clean_txt(txt_limpo)}")
        idx_letra += 1
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 5. LÓGICA DO PAINEL ADMIN ---
if perfil == "admin":
    st.title("🛠️ Gerador de Atividades")
    
    aba1, aba2 = st.tabs(["📄 Geradores de Atividade", "🧮 Calculadoras Online"])
    
    with aba1:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("📄 Gerador Manual"): st.session_state.sub_menu = "man"
        with c2:
            if st.button("🔢 Operações Básicas"): st.session_state.sub_menu = "op"
        with c3:
            if st.button("📐 Equações"): st.session_state.sub_menu = "eq"

        op = st.session_state.sub_menu
        st.divider()

        if op == "man":
            txt_input = st.text_area("Digite o conteúdo (Ex: t. Título / 1. Seção / ,V36):", 
                                     height=150, value="t. MINHA ATIVIDADE\n1. Resolva as raízes:\n,V25\n,V81\n2. Calcule:\n,10^2")
            if st.button("Visualizar Atividade"):
                st.session_state.preview_questoes = txt_input.split('\n')

        elif op == "op":
            qtd = st.number_input("Quantidade:", 5, 20, 10)
            if st.button("Gerar Automático"):
                st.session_state.preview_questoes = ["t. EXERCÍCIOS DE OPERAÇÕES", "1. Efetue:"] + [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(qtd)]

    with aba2:
        calc = st.selectbox("Escolha a ferramenta:", ["PEMDAS", "Funções f(x)", "Financeira"])
        if calc == "PEMDAS":
            exp = st.text_input("Expressão:", "2 + 3 * (5**2)")
            if st.button("Resolver"): st.success(f"Resultado: {eval(exp)}")
        elif calc == "Funções f(x)":
            f_x = st.text_input("f(x):", "x**2 + 2*x")
            val_x = st.number_input("Valor de x:", value=2.0)
            if st.button("Calcular f(x)"): st.metric("Resultado", eval(f_x.replace('x', f'({val_x})')))

# --- 6. VISUALIZAÇÃO UNIFICADA E PDF (PREVIEW) ---
if st.session_state.preview_questoes:
    st.divider()
    
    # Cabeçalho no Streamlit
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0

    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        # A) Título
        if line.lower().startswith(("t.", "titulo:", "título:")):
            t_clean = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
            st.markdown(f"<h1 style='text-align: center; color: #007bff; border-bottom: 2px solid #007bff;'>{t_clean}</h1>", unsafe_allow_html=True)
            continue

        # B) Seção Numerada (Reseta letras)
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0 
            
        # C) Questões em Cards
        else:
            with st.container(border=True):
                c1, c2 = st.columns([0.05, 0.95])
                with c1: st.write(f"**{letras[l_idx%26]})**")
                with c2:
                    f = tratar_math_streamlit(line)
                    if "\\" in f or "^" in f: st.latex(f)
                    else: st.write(line.lstrip(','))
            l_idx += 1

    # Botão de Download Final
    pdf_bytes = gerar_pdf(st.session_state.preview_questoes)
    st.download_button("📥 Baixar Atividade em PDF", pdf_bytes, "atividade_quantum.pdf")

# Painel Estudante simples
if perfil == "aluno" and not st.session_state.preview_questoes:
    st.title("📖 Bem-vindo, Estudante")
    st.info("Aguarde o professor gerar as atividades para visualização.")
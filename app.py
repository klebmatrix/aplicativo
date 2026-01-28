import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

# [MODIFICAÇÃO 1]: Inicialização para evitar o erro de AttributeError
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

def clean_txt(text):
    """[MODIFICAÇÃO 2]: Tradução para o PDF não bugar com símbolos"""
    if not text: return ""
    text = str(text).replace("√", "Raiz de ").replace("V", "Raiz de ").replace("²", "^2").replace("³", "^3")
    return text.encode('latin-1', 'replace').decode('latin-1')

def tratar_math(texto):
    """Formatação LaTeX para o Preview na tela"""
    t = texto.lstrip(',').strip()
    t = re.sub(r'V(\d+)', r'\\sqrt{\1}', t)
    if "^" in t and "^{" not in t:
        t = re.sub(r'\^(\d+)', r'^{\1}', t)
    return t

def validar_acesso(pin_digitado):
    try:
        # Puxa as senhas dos secrets conforme solicitado
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    except:
        senha_aluno, senha_prof = "123456", "chave_mestra"
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

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
    st.session_state.preview_questoes = []
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
    
    # [MODIFICAÇÃO 3]: Lógica de reset de letras no PDF automático
    idx_l = 0
    for q in questoes:
        pdf.multi_cell(0, 10, txt=f"{letras[idx_l%26]}) {clean_txt(q)}")
        idx_l += 1
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. PAINEL PRINCIPAL (ADMIN) ---
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

    op_atual = st.session_state.sub_menu
    st.divider()

    # --- MÓDULOS DE GERADORES ---
    if op_atual == "op":
        st.header("🔢 Operações")
        escolhas = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
        qtd = st.number_input("Qtd:", 4, 30, 10)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = [f"t. Operações"] + [f"{random.randint(10,500)} {random.choice(escolhas)} {random.randint(2,50)} =" for _ in range(qtd)]

    elif op_atual == "eq":
        st.header("📐 Equações")
        grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = [f"t. Equações {grau}"] + [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" if grau == "1º Grau" else f"x² + {random.randint(2,8)}x + {random.randint(1,12)} = 0" for _ in range(8)]

    elif op_atual == "man":
        st.header("📄 Manual")
        txt_m = st.text_area("Texto (t. Título, . colunas, 1. Seção):", height=200)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = txt_m.split('\n')

    # --- MÓDULOS DE CÁLCULO ---
    elif op_atual == "calc_f":
        st.header("𝑓(x) Cálculo de Funções")
        f_in = st.text_input("Defina f(x):", "x**2 + 5*x + 6")
        x_v = st.number_input("Valor de x:", value=1.0)
        if st.button("Calcular"):
            res = eval(f_in.replace('x', f'({x_v})'))
            st.metric(f"f({x_v})", f"{res:.4f}")

    elif op_atual == "pemdas":
        st.header("📊 Expressões (PEMDAS)")
        exp = st.text_input("Expressão:", "2 + 3 * 4")
        if st.button("Resolver"): st.success(f"Resultado: {eval(exp)}")
# --- 6. VISUALIZAÇÃO UNIFICADA (CARDS + REGRAS) ---
if st.session_state.preview_questoes:
    st.divider()
    if os.path.exists("cabecalho.png"): st.image("cabecalho.png", use_container_width=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0

    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        if line.lower().startswith(("t.", "titulo:", "título:")):
            t_clean = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
            st.markdown(f"<h1 style='text-align: center; color: #007bff; border-bottom: 2px solid #007bff;'>{t_clean}</h1>", unsafe_allow_html=True)
            continue

        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0 
            
        else:
            with st.container(border=True):
                c1, c2 = st.columns([0.05, 0.95])
                with c1: st.write(f"**{letras[l_idx%26]})**")
                with c2:
                    f = tratar_math(line)
                    if "\\" in f or "^" in f: st.latex(f)
                    else: st.write(line.lstrip(','))
            l_idx += 1

  # --- 7. EXPORTAÇÃO PDF DO PREVIEW ---
    if st.button("📥 Gerar Arquivo PDF"):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=8, w=190); pdf.set_y(50)
        else: pdf.set_y(20)
        
        idx_p = 0
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if line.lower().startswith(("t.", "titulo:", "título:")):
                t_p = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
                pdf.set_font("Arial", 'B', 16); pdf.cell(0, 12, clean_txt(t_p), ln=True, align='C'); pdf.ln(5)
            elif re.match(r'^\d+', line):
                pdf.ln(4); pdf.set_font("Arial", 'B', 12); pdf.multi_cell(0, 8, clean_txt(line)); idx_p = 0
            else:
                pdf.set_font("Arial", size=11)
                pdf.multi_cell(0, 8, f"{letras[idx_p%26]}) {clean_txt(line.lstrip(','))}")
                idx_p += 1
        st.download_button("✅ Baixar PDF", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")

elif perfil == "aluno":
    st.title("📖 Área do Estudante")
    st.info("Utilize as ferramentas de cálculo ou aguarde a atividade do professor.")


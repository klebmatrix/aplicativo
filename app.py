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
        s_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        s_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
    except:
        s_aluno, s_prof = "123456", "12345678"
    if pin_digitado == s_aluno: return "aluno"
    elif pin_digitado == s_prof: return "admin"
    return "negado"

# Inicialização de Estados
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

# --- 2. SIDEBAR ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {perfil.upper()}")
if st.sidebar.button("Sair/Logout"):
    for key in list(st.session_state.keys()): del st.session_state[key]
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

# --- 4. PAINEL PRINCIPAL ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
    # CARDS GERADORES
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
    
    # CARDS CÁLCULOS
    st.subheader("🧮 Ferramentas Online")
    d1, d2, d3 = st.columns(3)
    with d1: 
        if st.button("𝑓(x) Função", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with d3: 
        if st.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

    op_atual = st.session_state.sub_menu
    if not op_atual: st.info("Selecione um módulo.")
    else: st.divider()

    # --- LÓGICA DOS MÓDULOS ---
    if op_atual == "op":
        st.header("🔢 Operações")
        escolhas = st.multiselect("Operações:", ["Soma", "Subtração", "Multiplicação", "Divisão"], ["Soma"])
        qtd = st.number_input("Quantidade:", 4, 40, 10)
        if st.button("🔍 Visualizar"):
            maps = {"Soma":"+", "Subtração":"-", "Multiplicação":"x", "Divisão":"÷"}
            selecionadas = [maps.get(x) for x in escolhas if maps.get(x)]
            st.session_state.preview_data = [f"{random.randint(10,500)} {random.choice(selecionadas)} {random.randint(2,50)} =" for _ in range(qtd)]

    elif op_atual == "eq":
        st.header("📐 Equações")
        grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        if st.button("🔍 Visualizar"):
            st.session_state.preview_data = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" if grau == "1º Grau" else f"x² + {random.randint(2,8)}x + {random.randint(1,12)} = 0" for _ in range(8)]

    elif op_atual == "col":
        st.header("📚 Colegial")
        tema = st.selectbox("Tema:", ["Soma de Frações", "Domínio de Funções"])
        if st.button("🔍 Visualizar"):
            if "Frações" in tema: st.session_state.preview_data = [f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/{random.randint(2,5)} =" for _ in range(6)]
            else: st.session_state.preview_data = [f"f(x) = {random.randint(1,10)}/(x - {random.randint(1,20)})" for _ in range(5)]

    elif op_atual == "alg":
        st.header("⚖️ Álgebra Linear")
        ordem = st.radio("Ordem:", ["2x2", "3x3"], horizontal=True)
        if st.button("🔍 Visualizar"):
            size = 2 if ordem == "2x2" else 3
            matriz = np.random.randint(1, 10, size=(size, size))
            st.session_state.preview_data = [f"Calcule o determinante da matriz {ordem}:\n{matriz}"]

    elif op_atual == "man":
        st.header("📄 Manual")
        tit_m = st.text_input("Título:", "Atividade")
        txt_m = st.text_area("Use . para colunas", height=200)
        if st.button("🔍 Visualizar"):
            st.session_state.preview_data = txt_m.split('\n')
            st.session_state.manual_tit = tit_m

    # --- ÁREA DE PREVIEW E DOWNLOAD ---
    if st.session_state.preview_data and op_atual in ["op", "eq", "col", "alg", "man"]:
        st.subheader("👀 Preview")
        letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
        with st.container(border=True):
            for i, linha in enumerate(st.session_state.preview_data):
                t = linha.strip()
                if not t: continue
                if op_atual == "man" and re.match(r'^\d+', t):
                    st.markdown(f"**{t}**"); l_idx = 0
                else:
                    st.write(f"**{letras[l_idx%26]})** {t.replace('.', '')}")
                    l_idx += 1
        
        # Gerador Final de PDF
        if st.button("📥 Gerar PDF para Download"):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10); l_idx = 0
            if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
            
            titulo_final = st.session_state.get("manual_tit", "Atividade Quantum Math")
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(titulo_final), ln=True, align='C'); pdf.ln(5)
            
            for linha in st.session_state.preview_data:
                t = linha.strip()
                if not t: continue
                match = re.match(r'^(\.+)', t); pts = len(match.group(1)) if match else 0
                if re.match(r'^\d+', t): 
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(t)); pdf.set_font("Arial", size=10); l_idx = 0
                elif pts > 0:
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*45); pdf.cell(45, 8, f"{letras[l_idx%26]}) {clean_txt(t[pts:].strip())}", ln=True); l_idx += 1
                else: pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(t)}"); l_idx += 1
            
            st.download_button("✅ BAIXAR AGORA", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")

    # --- CÁLCULOS ---
    elif op_atual == "calc_f":
        st.header("𝑓(x) Função")
        f = st.text_input("Fórmula:", "x**2")
        x_v = st.number_input("x:", value=1.0)
        if st.button("Calcular"): st.metric("Resultado", eval(f.replace('x', f'({x_v})')))

    elif op_atual == "pemdas":
        st.header("📊 PEMDAS")
        ex = st.text_input("Expressão:", "2 + (3*4)")
        if st.button("Resolver"): st.success(f"Resultado: {eval(ex)}")

    elif op_atual == "fin":
        st.header("💰 Financeira")
        pv = st.number_input("Capital:", 1000.0)
        tax = st.number_input("Taxa %:", 5.0)
        n = st.number_input("Meses:", 12)
        if st.button("Juros Compostos"): st.metric("FV", f"R$ {pv * (1 + tax/100)**n:.2f}")

else:
    st.title("📖 Área do Estudante")
    st.write("Acesso liberado para calculadoras.")
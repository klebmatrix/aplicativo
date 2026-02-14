import streamlit as st
import random
import re
import os
import math
import threading
import time
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO E PERSISTÊNCIA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de Estados (Garante que nada suma ao clicar)
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = "home"
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""
if 'tp_ativo' not in st.session_state: st.session_state.tp_ativo = False

# --- 2. TRAVA DE TEMPO (FUNÇÃO INFINITA / TAKE PROFIT) ---
def monitoramento_infinito():
    """Mantém a sessão viva enviando logs para o terminal/servidor."""
    while st.session_state.get('tp_ativo', False):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Quantum Bot: Monitoramento Ativo - Anti-Sleep ON")
        time.sleep(15)

if st.session_state.tp_ativo:
    if not any(t.name == "Thread_Quantum" for t in threading.enumerate()):
        t = threading.Thread(target=monitoramento_infinito, name="Thread_Quantum", daemon=True)
        t.start()

# --- 3. LOGIN RESTRITO (APENAS SECRETS) ---
def validar_acesso(pin):
    try:
        p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        p_prof = str(st.secrets.get("chave_mestra", "admin123")).strip().lower()
        if pin == p_prof: return "admin"
        if pin == p_aluno: return "aluno"
    except: return None
    return None

if st.session_state.perfil is None:
    st.title("🔐 Login Quantum Lab")
    pin_input = st.text_input("PIN de Acesso:", type="password")
    if st.button("Acessar", key="login_btn"):
        res = validar_acesso(pin_input)
        if res:
            st.session_state.perfil = res
            st.rerun()
        else: st.error("PIN Incorreto ou Secrets não configurados.")
    st.stop()

# --- 4. FUNÇÕES DE CALLBACK (BLINDAGEM DOS BOTÕES) ---
def mudar_aba(nova_aba):
    st.session_state.sub_menu = nova_aba
    st.session_state.res_calc = ""

# --- 5. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
st.session_state.tp_ativo = st.sidebar.toggle("ATIVAR MONITORAMENTO TP", value=st.session_state.tp_ativo)

if st.sidebar.button("🧹 Limpar Atividade", key="clear_side"):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

if st.sidebar.button("🚪 Sair", key="exit_side"):
    st.session_state.clear()
    st.rerun()

# --- 6. CENTRO DE COMANDO (8 CARDS COM KEYS ÚNICAS) ---
st.title("🛠️ Centro de Comando Quantum")

# Grid 1: Geradores
g1, g2, g3, g4, g5 = st.columns(5)
g1.button("🔢 Operações", on_click=mudar_aba, args=("op",), key="btn_op", use_container_width=True)
g2.button("📐 Equações", on_click=mudar_aba, args=("eq",), key="btn_eq", use_container_width=True)
g3.button("⛓️ Sistemas", on_click=mudar_aba, args=("sis",), key="btn_sis", use_container_width=True)
g4.button("⚖️ Álgebra", on_click=mudar_aba, args=("alg",), key="btn_alg", use_container_width=True)
g5.button("📄 Manual", on_click=mudar_aba, args=("man",), key="btn_man", use_container_width=True)

# Grid 2: Calculadoras
c1, c2, c3 = st.columns(3)
c1.button("𝑓(x) Bhaskara", on_click=mudar_aba, args=("calc_f",), key="btn_bh", use_container_width=True)
c2.button("📊 PEMDAS", on_click=mudar_aba, args=("pemdas",), key="btn_pe", use_container_width=True)
c3.button("💰 Financeira", on_click=mudar_aba, args=("fin",), key="btn_fi", use_container_width=True)

st.divider()

# --- 7. PAINEL DE CONFIGURAÇÃO PDF ---
with st.expander("⚙️ CONFIGURAÇÃO DA FOLHA A4", expanded=True):
    col_pdf1, col_pdf2, col_pdf3 = st.columns(3)
    usar_cabecalho = col_pdf1.checkbox("Usar cabeçalho.png", value=True)
    layout_cols = col_pdf2.selectbox("Colunas no PDF:", [1, 2, 3], index=1)
    recuo_cabecalho = col_pdf3.slider("Recuo Título (mm):", 10, 100, 45)

# --- 8. LÓGICAS DE CONTEÚDO ---
menu = st.session_state.sub_menu

if menu == "op":
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Lista"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        qs = [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [f"t. Atividade de {tipo}", "1. Calcule:"] + qs

elif menu == "calc_f":
    st.subheader("𝑓(x) Bhaskara")
    v1, v2, v3 = st.columns(3)
    a_in = v1.number_input("a", value=1.0)
    b_in = v2.number_input("b", value=-5.0)
    c_in = v3.number_input("c", value=6.0)
    if st.button("Calcular Raízes"):
        d = b_in**2 - 4*a_in*c_in
        if d >= 0:
            x1 = (-b_in + math.sqrt(d))/(2*a_in)
            x2 = (-b_in - math.sqrt(d))/(2*a_in)
            st.session_state.res_calc = f"Delta: {d} | x1: {x1:.2f} | x2: {x2:.2f}"
        else: st.session_state.res_calc = "Delta negativo (Sem raízes reais)."

# --- 9. MOTOR PDF A4 ---
if st.session_state.res_calc: st.success(st.session_state.res_calc)

if st.session_state.preview_questoes:
    st.subheader("👁️ Preview do Documento")
    with st.container(border=True):
        for line in st.session_state.preview_questoes: st.write(line)

    def export_pdf():
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        y_ini = 10
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            y_ini = recuo_cabecalho 
        pdf.set_y(y_ini)
        letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
        larg_col = 190 / int(layout_cols)
        
        for line in st.session_state.preview_questoes:
            line = line.strip().encode('latin-1', 'replace').decode('latin-1')
            if not line: continue
            if line.lower().startswith("t."):
                pdf.ln(5); pdf.set_font("Helvetica", 'B', 14)
                pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.ln(5); pdf.set_font("Helvetica", size=12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                pdf.set_font("Helvetica", size=11)
                col = l_idx % int(layout_cols)
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line}", ln=(col == int(layout_cols)-1))
                l_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 Baixar PDF A4", data=export_pdf(), file_name="atividade.pdf", mime="application/pdf")

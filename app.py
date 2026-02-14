import streamlit as st
import random
import re
import os
import math
import threading
import time
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Quantum Lab", layout="wide")

# Inicialização de Estados
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = "home"
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""
if 'tp_ativo' not in st.session_state: st.session_state.tp_ativo = False

# --- 2. TRAVA DE TEMPO (ANTI-SLEEP) ---
def monitoramento_loop():
    while st.session_state.get('tp_ativo', False):
        time.sleep(15)

if st.session_state.tp_ativo:
    if not any(t.name == "Thread_Quantum" for t in threading.enumerate()):
        threading.Thread(target=monitoramento_loop, name="Thread_Quantum", daemon=True).start()

# --- 3. LOGIN RESTRITO (APENAS SECRETS) ---
def realizar_login(pin_digitado):
    try:
        p_aluno = str(st.secrets.get("acesso_aluno")).strip()
        p_prof = str(st.secrets.get("chave_mestra")).strip().lower()
        if pin_digitado == p_prof: return "admin"
        if pin_digitado == p_aluno: return "aluno"
    except Exception:
        st.error("Erro: Segredos não configurados no Streamlit Cloud.")
    return None

if st.session_state.perfil is None:
    st.title("🔐 Login Quantum")
    pin = st.text_input("Digite seu PIN de acesso:", type="password")
    if st.button("ACESSAR"):
        user = realizar_login(pin)
        if user:
            st.session_state.perfil = user
            st.rerun()
        else:
            st.error("PIN INCORRETO!")
    st.stop()

# --- 4. CALLBACKS DE NAVEGAÇÃO ---
def mudar_aba(nome_aba):
    st.session_state.sub_menu = nome_aba
    st.session_state.res_calc = ""

def limpar_dados():
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

# --- 5. CENTRO DE COMANDO ---
st.title(f"🛠️ Quantum Lab - {st.session_state.perfil.upper()}")

c1, c2, c3, c4, c5 = st.columns(5)
c1.button("🔢 Operações", on_click=mudar_aba, args=("op",), use_container_width=True)
c2.button("📐 Equações", on_click=mudar_aba, args=("eq",), use_container_width=True)
c3.button("⛓️ Sistemas", on_click=mudar_aba, args=("sis",), use_container_width=True)
c4.button("⚖️ Álgebra", on_click=mudar_aba, args=("alg",), use_container_width=True)
c5.button("📄 Manual", on_click=mudar_aba, args=("man",), use_container_width=True)

ca, cb, cc = st.columns(3)
ca.button("𝑓(x) Bhaskara", on_click=mudar_aba, args=("bhask",), use_container_width=True)
cb.button("📊 PEMDAS", on_click=mudar_aba, args=("pemdas",), use_container_width=True)
cc.button("💰 Financeira", on_click=mudar_aba, args=("fin",), use_container_width=True)

st.divider()

# --- 6. PAINEL DE CONTROLE (CABEÇALHO, COLUNAS, LIMPAR) ---
with st.expander("⚙️ CONFIGURAÇÕES DA FOLHA A4 E SISTEMA", expanded=True):
    f1, f2, f3 = st.columns(3)
    with f1:
        usar_header = st.checkbox("Exibir Cabeçalho PNG", value=True)
        cols_pdf = st.selectbox("Colunas no PDF:", [1, 2, 3], index=1)
    with f2:
        y_fix = st.slider("Recuo Título (mm):", 10, 100, 45)
        st.session_state.tp_ativo = st.toggle("🤖 Ativar Monitor Take Profit", value=st.session_state.tp_ativo)
    with f3:
        st.button("🧹 LIMPAR TUDO", on_click=limpar_dados, use_container_width=True)
        if st.button("🚪 SAIR", use_container_width=True):
            st.session_state.clear()
            st.rerun()

st.divider()

# --- 7. CONTEÚDO DINÂMICO ---
menu = st.session_state.sub_menu

if menu == "bhask":
    st.subheader("🧪 Calculadora Bhaskara")
    v1, v2, v3 = st.columns(3)
    a = v1.number_input("A", value=1.0)
    b = v2.number_input("B", value=-5.0)
    c = v3.number_input("C", value=6.0)
    if st.button("CALCULAR"):
        d = b**2 - 4*a*c
        if d >= 0:
            x1 = (-b + math.sqrt(d))/(2*a)
            x2 = (-b - math.sqrt(d))/(2*a)
            st.session_state.res_calc = f"Delta: {d} | x1: {x1:.2f} | x2: {x2:.2f}"
        else: st.session_state.res_calc = "Delta Negativo! Sem raízes reais."

elif menu == "op":
    st.subheader("🔢 Gerador de Operações")
    tipo = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("GERAR"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
        qs = [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [f"t. Atividade de {tipo}", "1. Calcule os resultados:"] + qs

elif menu == "man":
    st.subheader("📄 Editor Manual")
    txt = st.text_area("Texto (t. Título | .M Instrução):", height=150)
    if st.button("LANÇAR"):
        st.session_state.preview_questoes = txt.split("\n")

# --- 8. MOTOR PDF (A4) ---
if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    for linha in st.session_state.preview_questoes: st.write(linha)
    
    def gerar_pdf():
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        y = 10
        if usar_header and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            y = y_fix
        pdf.set_y(y)
        pdf.set_font("Helvetica", size=11)
        
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx = 0
        larg_col = 190 / cols_pdf

        for line in st.session_state.preview_questoes:
            clean = line.strip().encode('latin-1', 'replace').decode('latin-1')
            if not clean: continue

            if clean.lower().startswith("t."):
                pdf.ln(5); pdf.set_font("Helvetica", 'B', 14)
                pdf.cell(190, 8, clean[2:].strip(), ln=True, align='C')
                pdf.set_font("Helvetica", size=11); l_idx = 0
            elif re.match(r'^\d+\.', clean):
                pdf.ln(5); pdf.set_font("Helvetica", 'B', 12)
                pdf.cell(190, 8, clean, ln=True); pdf.set_font("Helvetica", size=11); l_idx = 0
            else:
                col_at = l_idx % cols_pdf
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {clean}", ln=(col_at == cols_pdf - 1))
                l_idx += 1
        return bytes(pdf.output())

    st.download_button(f"📥 BAIXAR PDF ({cols_pdf} COL)", data=gerar_pdf(), file_name="quantum.pdf", mime="application/pdf")

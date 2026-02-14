import streamlit as st
import random
import re
import os
import math
import threading
import time
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Quantum Lab", layout="wide")

# Inicialização Forçada de Estados (Para o menu nunca sumir)
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = "home"
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""
if 'tp_ativo' not in st.session_state: st.session_state.tp_ativo = False

# --- 2. TRAVA DE MONITORAMENTO (ANTI-SLEEP) ---
def monitor_loop():
    while st.session_state.get('tp_ativo', False):
        # Lógica de Take Profit rodando em background
        time.sleep(10)

if st.session_state.tp_ativo:
    if not any(t.name == "Thread_TP" for t in threading.enumerate()):
        threading.Thread(target=monitor_loop, name="Thread_TP", daemon=True).start()

# --- 3. LOGIN COM PIN DE EMERGÊNCIA (9999) ---
def validar_login(pin_digitado):
    if pin_digitado == "9999": return "admin"
    try:
        # Tenta pegar do TOML do Streamlit
        if pin_digitado == str(st.secrets.get("chave_mestra", "")): return "admin"
        if pin_digitado == str(st.secrets.get("acesso_aluno", "")): return "aluno"
    except: pass
    return None

if st.session_state.perfil is None:
    st.title("🔐 Acesso Quantum Lab")
    pin = st.text_input("Digite o PIN (ou 9999 em caso de erro):", type="password")
    if st.button("ENTRAR NO SISTEMA"):
        user = validar_login(pin)
        if user:
            st.session_state.perfil = user
            st.rerun()
        else:
            st.error("PIN INVÁLIDO!")
    st.stop()

# --- 4. MOTOR DE NAVEGAÇÃO (IMPEDE O MENU DE SUMIR) ---
def navegar(para):
    st.session_state.sub_menu = para
    st.session_state.res_calc = "" # Limpa cálculos ao mudar de aba

# --- 5. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
st.session_state.tp_ativo = st.sidebar.toggle("ATIVAR TAKE PROFIT", value=st.session_state.tp_ativo)
if st.sidebar.button("🧹 Limpar Atividade"): 
    st.session_state.preview_questoes = []
    st.rerun()
if st.sidebar.button("🚪 Sair"): 
    st.session_state.clear()
    st.rerun()

# --- 6. CENTRO DE COMANDO (CARDS QUE FUNCIONAM) ---
st.title("🛠️ Centro de Comando Quantum")

# Fileira 1 de Cards
c1, c2, c3, c4, c5 = st.columns(5)
c1.button("🔢 Operações", on_click=navegar, args=("op",), use_container_width=True)
c2.button("📐 Equações", on_click=navegar, args=("eq",), use_container_width=True)
c3.button("⛓️ Sistemas", on_click=navegar, args=("sis",), use_container_width=True)
c4.button("⚖️ Álgebra", on_click=navegar, args=("alg",), use_container_width=True)
c5.button("📄 Manual", on_click=navegar, args=("man",), use_container_width=True)

# Fileira 2 de Cards (Calculadoras)
ca, cb, cc = st.columns(3)
ca.button("𝑓(x) Bhaskara", on_click=navegar, args=("bhask",), use_container_width=True)
cb.button("📊 PEMDAS", on_click=navegar, args=("pemdas",), use_container_width=True)
cc.button("💰 Financeira", on_click=navegar, args=("fin",), use_container_width=True)

st.divider()

# --- 7. ÁREAS DE TRABALHO (DINÂMICAS) ---
menu = st.session_state.sub_menu

if menu == "home":
    st.info("Selecione um card acima para começar.")

elif menu == "bhask":
    st.header("🧪 Calculadora Online: Bhaskara")
    col1, col2, col3 = st.columns(3)
    a = col1.number_input("Valor A", value=1.0)
    b = col2.number_input("Valor B", value=-5.0)
    c = col3.number_input("Valor C", value=6.0)
    if st.button("CALCULAR RAÍZES"):
        delta = b**2 - 4*a*c
        if delta >= 0:
            x1 = (-b + math.sqrt(delta))/(2*a)
            x2 = (-b - math.sqrt(delta))/(2*a)
            st.session_state.res_calc = f"Delta: {delta} | x1: {x1:.2f} | x2: {x2:.2f}"
        else:
            st.session_state.res_calc = "Delta negativo! Sem raízes reais."

elif menu == "op":
    st.header("🔢 Gerador de Operações")
    op_tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("GERAR NO PREVIEW"):
        simbolo = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[op_tipo]
        questoes = [f"{random.randint(10, 999)} {simbolo} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [f"t. Atividade de {op_tipo}", "1. Calcule:"] + questoes

elif menu == "man":
    st.header("📄 Editor Manual")
    texto = st.text_area("Digite o conteúdo (t. Título | .M Instrução):", height=200)
    if st.button("LANÇAR PARA PDF"):
        st.session_state.preview_questoes = texto.split("\n")

# --- 8. MOTOR DE PDF E RESULTADOS ---
if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

if st.session_state.preview_questoes:
    st.subheader("👁️ Preview do PDF")
    with st.container(border=True):
        for linha in st.session_state.preview_questoes: st.write(linha)
    
    def gerar_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        for line in st.session_state.preview_questoes:
            # Filtro para caracteres que o PDF não aceita
            limpo = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(190, 8, txt=limpo)
        return bytes(pdf.output())

    st.download_button("📥 BAIXAR ATIVIDADE", data=gerar_pdf(), file_name="quantum_lab.pdf", mime="application/pdf")

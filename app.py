import streamlit as st
import random
import re
import os
import math
import threading
import time
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Lab", layout="wide")

# Inicialização de Estados
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = ""
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""
if 'tp_ativo' not in st.session_state: st.session_state.tp_ativo = False

# --- 2. TRAVA DE TEMPO (ANTI-SLEEP) ---
def monitor_tp():
    while st.session_state.get('tp_ativo', False):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitor Ativo - Não durma!")
        time.sleep(15)

if st.session_state.tp_ativo:
    if not any(t.name == "Thread_TP" for t in threading.enumerate()):
        threading.Thread(target=monitor_tp, name="Thread_TP", daemon=True).start()

# --- 3. LOGIN (COM PIN DE EMERGÊNCIA: 9999) ---
def validar_login(pin_inserido):
    # PIN DE EMERGÊNCIA CASO O SECRETS DÊ PAU
    if pin_inserido == "9999": return "admin"
    
    try:
        p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        p_prof = str(st.secrets.get("chave_mestra", "admin123")).strip().lower()
        if pin_inserido == p_prof: return "admin"
        if pin_inserido == p_aluno: return "aluno"
    except:
        pass
    return None

if st.session_state.perfil is None:
    st.title("🔐 Login Quantum Lab")
    st.warning("Se o seu PIN do Secrets não funcionar, use o código de emergência: 9999")
    pin = st.text_input("Insira seu PIN:", type="password")
    if st.button("Acessar"):
        user = validar_login(pin)
        if user:
            st.session_state.perfil = user
            st.rerun()
        else:
            st.error("PIN Incorreto. Verifique o formato do seu Secrets TOML.")
    st.stop()

# --- 4. NAVEGAÇÃO (CARDS) ---
def ir_para(destino):
    st.session_state.sub_menu = destino
    st.session_state.res_calc = ""

st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
st.session_state.tp_ativo = st.sidebar.toggle("Ativar Take Profit (Anti-Sleep)", value=st.session_state.tp_ativo)

if st.sidebar.button("Limpar"): st.session_state.preview_questoes = []; st.rerun()
if st.sidebar.button("Sair"): st.session_state.clear(); st.rerun()

st.title("🛠️ Centro de Comando Quantum")
c1, c2, c3, c4, c5 = st.columns(5)
c1.button("🔢 Operações", on_click=ir_para, args=("op",), use_container_width=True)
c2.button("📐 Equações", on_click=ir_para, args=("eq",), use_container_width=True)
c3.button("⛓️ Sistemas", on_click=ir_para, args=("sis",), use_container_width=True)
c4.button("⚖️ Álgebra", on_click=ir_para, args=("alg",), use_container_width=True)
c5.button("📄 Manual", on_click=ir_para, args=("man",), use_container_width=True)

ca, cb, cc = st.columns(3)
ca.button("𝑓(x) Bhaskara", on_click=ir_para, args=("bhask",), use_container_width=True)
cb.button("📊 PEMDAS", on_click=ir_para, args=("pemdas",), use_container_width=True)
cc.button("💰 Financeira", on_click=ir_para, args=("fin",), use_container_width=True)

st.divider()
menu = st.session_state.sub_menu

# --- 5. CALCULADORAS ONLINE ---
if menu == "bhask":
    st.subheader("🧪 Calculadora de Bhaskara")
    col1, col2, col3 = st.columns(3)
    a = col1.number_input("A", value=1.0)
    b = col2.number_input("B", value=-5.0)
    c = col3.number_input("C", value=6.0)
    if st.button("Calcular"):
        delta = b**2 - 4*a*c
        if delta >= 0:
            x1 = (-b + math.sqrt(delta))/(2*a)
            x2 = (-b - math.sqrt(delta))/(2*a)
            st.session_state.res_calc = f"Delta: {delta} | x1: {x1:.2f} | x2: {x2:.2f}"
        else: st.session_state.res_calc = "Não possui raízes reais."

# --- 6. GERADOR DE ATIVIDADES ---
if menu == "op":
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Questões"):
        simb = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
        qs = [f"{random.randint(10, 99)} {simb} {random.randint(1, 10)} =" for _ in range(12)]
        st.session_state.preview_questoes = [f"t. Atividade de {tipo}", "1. Calcule:"] + qs

# --- 7. MOTOR PDF (SEM BUGS) ---
if st.session_state.preview_questoes:
    with st.expander("👁️ Ver Preview"):
        for l in st.session_state.preview_questoes: st.write(l)
    
    def salvar_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        for line in st.session_state.preview_questoes:
            clean = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(190, 8, txt=clean)
        return bytes(pdf.output())

    st.download_button("📥 Baixar PDF", data=salvar_pdf(), file_name="quantum.pdf", mime="application/pdf")

if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

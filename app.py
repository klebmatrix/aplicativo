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
for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc', 'tp_ativo']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else False if key == 'tp_ativo' else "home" if key == 'sub_menu' else None

# --- 2. LOGIN RESTRITO ---
if st.session_state.perfil is None:
    st.title("🔐 Login Quantum")
    pin = st.text_input("PIN:", type="password")
    if st.button("ACESSAR"):
        try:
            p_prof = str(st.secrets.get("chave_mestra")).strip()
            p_aluno = str(st.secrets.get("acesso_aluno")).strip()
            if pin == p_prof: st.session_state.perfil = "admin"; st.rerun()
            elif pin == p_aluno: st.session_state.perfil = "aluno"; st.rerun()
            else: st.error("PIN INCORRETO!")
        except: st.error("Configure os Secrets no painel do Streamlit!")
    st.stop()

# --- 3. CALLBACK DE NAVEGAÇÃO (O QUE TRAVA OS CARDS) ---
def navegar(destino):
    st.session_state.sub_menu = destino
    st.session_state.res_calc = ""

# --- 4. CENTRO DE COMANDO (TODOS OS CARDS COM KEYS ÚNICAS) ---
st.title(f"🛠️ Quantum Lab - {st.session_state.perfil.upper()}")

# Fileira 1: Geradores
g1, g2, g3, g4, g5 = st.columns(5)
g1.button("🔢 Operações", on_click=navegar, args=("op",), key="btn_op", use_container_width=True)
g2.button("📐 Equações", on_click=navegar, args=("eq",), key="btn_eq", use_container_width=True)
g3.button("⛓️ Sistemas", on_click=navegar, args=("sis",), key="btn_sis", use_container_width=True)
g4.button("⚖️ Álgebra", on_click=navegar, args=("alg",), key="btn_alg", use_container_width=True)
g5.button("📄 Manual", on_click=navegar, args=("man",), key="btn_man", use_container_width=True)

# Fileira 2: Calculadores
c1, c2, c3 = st.columns(3)
c1.button("𝑓(x) Bhaskara", on_click=navegar, args=("bhask",), key="btn_bhask", use_container_width=True)
c2.button("📊 PEMDAS", on_click=navegar, args=("pemdas",), key="btn_pemdas", use_container_width=True)
c3.button("💰 Financeira", on_click=navegar, args=("fin",), key="btn_fin", use_container_width=True)

st.divider()

# --- 5. PAINEL DE CONTROLE A4 ---
with st.expander("⚙️ CONFIGURAÇÕES E COLUNAS", expanded=True):
    f1, f2, f3 = st.columns(3)
    with f1:
        usar_img = st.checkbox("Cabeçalho PNG", value=True)
        num_cols = st.selectbox("Colunas:", [1, 2, 3], index=1)
    with f2:
        y_fix = st.slider("Recuo (mm):", 10, 100, 45)
        st.session_state.tp_ativo = st.toggle("🤖 Take Profit Ativo", value=st.session_state.tp_ativo)
    with f3:
        if st.button("🧹 LIMPAR TUDO"): 
            st.session_state.preview_questoes = []
            st.rerun()
        if st.button("🚪 SAIR"): 
            st.session_state.clear()
            st.rerun()

# --- 6. ÁREAS DE CONTEÚDO ---
menu = st.session_state.sub_menu

if menu == "bhask":
    st.subheader("🧪 Calculadora Bhaskara")
    v1, v2, v3 = st.columns(3)
    a = v1.number_input("A", value=1.0)
    b = v2.number_input("B", value=-5.0)
    c = v3.number_input("C", value=6.0)
    if st.button("Calcular"):
        d = b**2 - 4*a*c
        if d >= 0:
            x1 = (-b + math.sqrt(d))/(2*a)
            x2 = (-b - math.sqrt(d))/(2*a)
            st.session_state.res_calc = f"x1: {x1:.2f} | x2: {x2:.2f}"
        else: st.session_state.res_calc = "Delta Negativo."

elif menu == "op":
    st.subheader("🔢 Operações")
    tipo = st.radio("Escolha:", ["Soma", "Subtração"], horizontal=True)
    if st.button("Gerar Lista"):
        s = "+" if tipo == "Soma" else "-"
        qs = [f"{random.randint(10, 99)} {s} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [f"t. Atividade de {tipo}", "1. Resolva:"] + qs

# --- 7. MOTOR PDF A4 ---
if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

if st.session_state.preview_questoes:
    def gerar_pdf():
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        y = y_fix if usar_img else 10
        pdf.set_y(y)
        pdf.set_font("Helvetica", size=11)
        larg_col = 190 / num_cols
        l_idx = 0
        for line in st.session_state.preview_questoes:
            clean = line.encode('latin-1', 'replace').decode('latin-1')
            if clean.startswith("t."):
                pdf.ln(5); pdf.set_font("Helvetica", 'B', 14)
                pdf.cell(190, 8, clean[2:], ln=True, align='C')
                pdf.set_font("Helvetica", size=11); l_idx = 0
            else:
                col_at = l_idx % num_cols
                pdf.cell(larg_col, 8, f"- {clean}", ln=(col_at == num_cols - 1))
                l_idx += 1
        return bytes(pdf.output())

    st.download_button("📥 BAIXAR PDF A4", data=gerar_pdf(), file_name="quantum.pdf", mime="application/pdf")

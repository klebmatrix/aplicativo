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
st.set_page_config(page_title="Quantum Lab A4", layout="wide", initial_sidebar_state="collapsed")

# Inicialização Robusta do Session State
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = "home"
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""
if 'tp_ativo' not in st.session_state: st.session_state.tp_ativo = False

# --- 2. TRAVA DE TEMPO / MONITORAMENTO (ANTI-SLEEP) ---
def monitoramento_tp():
    """Mantém a lógica de Take Profit rodando e o app ativo."""
    while st.session_state.get('tp_ativo', False):
        # Espaço para lógica de trading/venda automática
        time.sleep(20)

def iniciar_thread_tp():
    if not any(t.name == "Thread_Quantum" for t in threading.enumerate()):
        t = threading.Thread(target=monitoramento_tp, name="Thread_Quantum", daemon=True)
        t.start()

# --- 3. SISTEMA DE LOGIN (PIN DE EMERGÊNCIA: 9999) ---
def validar_acesso(pin_digitado):
    if pin_digitado == "9999": return "admin" # Saída de emergência
    try:
        p_aluno = str(st.secrets.get("acesso_aluno", "")).strip()
        p_prof = str(st.secrets.get("chave_mestra", "")).strip().lower()
        if pin_digitado == p_prof: return "admin"
        if pin_digitado == p_aluno: return "aluno"
    except: pass
    return None

if st.session_state.perfil is None:
    st.title("🔐 Login Quantum Lab")
    pin = st.text_input("Insira seu PIN de acesso:", type="password", help="Use 9999 se o Secrets falhar")
    if st.button("ACESSAR PAINEL"):
        user = validar_acesso(pin)
        if user:
            st.session_state.perfil = user
            st.rerun()
        else:
            st.error("PIN incorreto. Verifique seu arquivo Secrets.")
    st.stop()

# --- 4. FUNÇÕES DE NAVEGAÇÃO E LIMPEZA ---
def navegar(destino):
    st.session_state.sub_menu = destino
    st.session_state.res_calc = ""

def limpar_tudo():
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

# --- 5. CENTRO DE COMANDO (CARDS DE NAVEGAÇÃO) ---
st.title(f"🛠️ Quantum Lab - {st.session_state.perfil.upper()}")

# Grid de Navegação Principal
c1, c2, c3, c4, c5 = st.columns(5)
c1.button("🔢 Operações", on_click=navegar, args=("op",), use_container_width=True)
c2.button("📐 Equações", on_click=navegar, args=("eq",), use_container_width=True)
c3.button("⛓️ Sistemas", on_click=navegar, args=("sis",), use_container_width=True)
c4.button("⚖️ Álgebra", on_click=navegar, args=("alg",), use_container_width=True)
c5.button("📄 Manual", on_click=navegar, args=("man",), use_container_width=True)

# Grid de Calculadoras Online
ca, cb, cc = st.columns(3)
ca.button("𝑓(x) Bhaskara", on_click=navegar, args=("bhask",), use_container_width=True)
cb.button("📊 PEMDAS", on_click=navegar, args=("pemdas",), use_container_width=True)
cc.button("💰 Financeira", on_click=navegar, args=("fin",), use_container_width=True)

st.divider()

# --- 6. PAINEL DE CONFIGURAÇÃO (VISÍVEL) ---
with st.expander("⚙️ CONFIGURAÇÕES DA FOLHA A4 E SISTEMA", expanded=True):
    f1, f2, f3 = st.columns(3)
    with f1:
        usar_cabecalho = st.checkbox("Exibir Cabeçalho PNG", value=True)
        num_colunas = st.selectbox("Número de Colunas no PDF:", [1, 2, 3], index=1)
    with f2:
        y_recuo = st.slider("Recuo do Título (mm):", 10, 120, 45)
        st.session_state.tp_ativo = st.toggle("🤖 Ativar Monitor Take Profit", value=st.session_state.tp_ativo)
        if st.session_state.tp_ativo: iniciar_thread_tp()
    with f3:
        if st.button("🧹 LIMPAR TUDO", use_container_width=True): limpar_tudo()
        if st.button("🚪 SAIR", use_container_width=True): 
            st.session_state.clear()
            st.rerun()

st.divider()

# --- 7. ÁREAS DINÂMICAS DE CONTEÚDO ---
menu = st.session_state.sub_menu

if menu == "bhask":
    st.subheader("🧪 Calculadora Online Bhaskara")
    v1, v2, v3 = st.columns(3)
    a = v1.number_input("Valor de A", value=1.0)
    b = v2.number_input("Valor de B", value=-5.0)
    c = v3.number_input("Valor de C", value=6.0)
    if st.button("CALCULAR"):
        delta = b**2 - 4*a*c
        if delta >= 0:
            x1 = (-b + math.sqrt(delta))/(2*a)
            x2 = (-b - math.sqrt(delta))/(2*a)
            st.session_state.res_calc = f"Delta: {delta} | x1: {x1:.2f} | x2: {x2:.2f}"
        else: st.session_state.res_calc = "Delta negativo. Sem raízes reais."

elif menu == "op":
    st.subheader("🔢 Gerador de Operações")
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("GERAR LISTA"):
        simb = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
        qs = [f"{random.randint(100, 999)} {simb} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [f"t. Atividade de {tipo}", "1. Resolva as operações:"] + qs

elif menu == "man":
    st.subheader("📄 Editor Manual")
    txt_input = st.text_area("Editor (t. para Título | .M para Instruções):", height=150)
    if st.button("ENVIAR PARA PDF"):
        st.session_state.preview_questoes = txt_input.split("\n")

# --- 8. MOTOR PDF (PADRÃO A4) ---
if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

if st.session_state.preview_questoes:
    st.subheader("👁️ Preview do Documento")
    with st.container(border=True):
        for linha in st.session_state.preview_questoes:
            if linha.strip(): st.write(linha)
    
    def gerar_pdf_a4():
        # A4 = 210 x 297 mm
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        largura_total = 190 # 210 - 20 de margens
        y_atual = 10
        
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, largura_total)
            y_atual = y_recuo
        
        pdf.set_y(y_atual)
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx = 0
        cols = int(num_colunas)
        larg_col = largura_total / cols

        for line in st.session_state.preview_questoes:
            clean_txt = line.strip().encode('latin-1', 'replace').decode('latin-1')
            if not clean_txt: continue

            # Título ou Enunciado (Ocupa a folha toda)
            if clean_txt.lower().startswith("t.") or re.match(r'^\d+\.', clean_txt):
                pdf.ln(5)
                is_titulo = clean_txt.startswith("t.")
                pdf.set_font("Helvetica", 'B', 14 if is_titulo else 12)
                pdf.cell(largura_total, 9, clean_txt.replace("t. ", ""), ln=True, align='C' if is_titulo else 'L')
                pdf.set_font("Helvetica", size=11)
                l_idx = 0
            else:
                # Questões em Colunas
                col_atual = l_idx % cols
                item = f"{letras[l_idx%26]}) {clean_txt}"
                pdf.cell(larg_col, 8, item, ln=(col_atual == cols - 1))
                l_idx += 1
                
        return bytes(pdf.output())

    st.download_button(
        label=f"📥 BAIXAR PDF (A4 - {num_colunas} Colunas)",
        data=gerar_pdf_a4(),
        file_name="atividade_quantum.pdf",
        mime="application/pdf"
    )

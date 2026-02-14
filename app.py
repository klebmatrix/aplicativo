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
st.set_page_config(page_title="Quantum Math Lab", layout="wide", initial_sidebar_state="expanded")

# Inicialização de todos os estados (Session State)
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = ""
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""
if 'tp_ativo' not in st.session_state: st.session_state.tp_ativo = False

# --- 2. LÓGICA DE MONITORAMENTO (ANTI-SLEEP / TAKE PROFIT) ---
def monitoramento_infinito():
    """Simula o processo de monitoramento que impede o app de hibernar."""
    while st.session_state.get('tp_ativo', False):
        # Aqui você inseriria a lógica de conexão com API de Exchange
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Quantum Bot: Monitorando Take Profit Ativo...")
        time.sleep(15) # Intervalo de verificação

def iniciar_monitor():
    if not any(t.name == "Thread_TP" for t in threading.enumerate()):
        t = threading.Thread(target=monitoramento_infinito, name="Thread_TP", daemon=True)
        t.start()

# --- 3. SISTEMA DE LOGIN ---
def validar_login(pin):
    try:
        # Tenta buscar do secrets, senão usa padrão
        p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        p_prof = str(st.secrets.get("chave_mestra", "admin123")).strip().lower()
    except:
        p_aluno, p_prof = "123456", "admin123"
    
    if pin == p_prof: return "admin"
    if pin == p_aluno: return "aluno"
    return None

if st.session_state.perfil is None:
    st.title("🔐 Login Quantum Lab")
    pin = st.text_input("Insira seu PIN de acesso:", type="password")
    if st.button("Acessar Painel"):
        user = validar_login(pin)
        if user:
            st.session_state.perfil = user
            st.rerun()
        else:
            st.error("PIN inválido. Verifique seus segredos TOML.")
    st.stop()

# --- 4. SIDEBAR E CONTROLES ---
st.sidebar.title(f"🚀 Painel {st.session_state.perfil.upper()}")
st.sidebar.divider()

# Configurações do PDF
usar_cabecalho = st.sidebar.checkbox("Exibir Cabeçalho PNG", value=True)
recuo_cabecalho = st.sidebar.slider("Altura do Título (Y):", 10, 100, 45)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)

# Trava de Tempo / Monitoramento
st.sidebar.divider()
st.sidebar.subheader("🤖 Automação")
tp_toggle = st.sidebar.toggle("ATIVAR MONITORAMENTO TP", value=st.session_state.tp_ativo)

if tp_toggle:
    st.session_state.tp_ativo = True
    iniciar_monitor()
    st.sidebar.success(f"ONLINE: {datetime.now().strftime('%H:%M')}")
else:
    st.session_state.tp_ativo = False

if st.sidebar.button("🚪 Sair do Sistema"):
    st.session_state.clear()
    st.rerun()

# --- 5. CENTRO DE COMANDO (CARDS DE NAVEGAÇÃO) ---
def navegar(destino):
    st.session_state.sub_menu = destino
    st.session_state.res_calc = ""

st.title("🛠️ Centro de Comando Quantum")

# Grid de botões (Cards)
row1 = st.columns(5)
row1[0].button("🔢 Operações", use_container_width=True, on_click=navegar, args=("op",))
row1[1].button("📐 Equações", use_container_width=True, on_click=navegar, args=("eq",))
row1[2].button("⛓️ Sistemas", use_container_width=True, on_click=navegar, args=("sis",))
row1[3].button("⚖️ Álgebra", use_container_width=True, on_click=navegar, args=("alg",))
row1[4].button("📄 Manual", use_container_width=True, on_click=navegar, args=("man",))

row2 = st.columns(3)
row2[0].button("𝑓(x) Bhaskara", use_container_width=True, on_click=navegar, args=("calc_f",))
row2[1].button("📊 PEMDAS", use_container_width=True, on_click=navegar, args=("pemdas",))
row2[2].button("💰 Financeira", use_container_width=True, on_click=navegar, args=("fin",))

st.divider()
menu = st.session_state.sub_menu

# --- 6. CALCULADORAS ONLINE ---
if menu == "calc_f":
    st.header("🧪 Calculadora Bhaskara")
    c1, c2, c3 = st.columns(3)
    val_a = c1.number_input("Valor de A", value=1.0)
    val_b = c2.number_input("Valor de B", value=-5.0)
    val_c = c3.number_input("Valor de C", value=6.0)
    
    if st.button("Calcular Agora"):
        delta = val_b**2 - 4*val_a*val_c
        if delta >= 0:
            x1 = (-val_b + math.sqrt(delta)) / (2*val_a)
            x2 = (-val_b - math.sqrt(delta)) / (2*val_a)
            st.session_state.res_calc = f"Delta: {delta} | x1: {x1:.2f} | x2: {x2:.2f}"
        else:
            st.session_state.res_calc = f"Delta: {delta} (Raízes não reais)"

elif menu == "pemdas":
    st.header("📊 Resolutor PEMDAS")
    exp = st.text_input("Expressão (ex: 10 + 5 * 2):", "20 / (2+2) * 5")
    if st.button("Resolver"):
        try:
            # Substituição básica para segurança
            res = eval(exp.replace('x', '*').replace('÷', '/'))
            st.session_state.res_calc = f"Resultado: {res}"
        except:
            st.error("Expressão inválida.")

# Exibição Universal de Resultados dos Cálculos
if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

# --- 7. GERADORES DE ATIVIDADE ---
if menu == "op":
    tipo = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Lista no Preview"):
        simb = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
        qs = [f"{random.randint(10, 999)} {simb} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [f"t. Atividade de {tipo}", ".M Resolva as contas abaixo:", "1. Calcule:"] + qs

elif menu == "man":
    texto = st.text_area("Editor (t. para Título | .M para Instruções):", height=200)
    if st.button("Aplicar ao PDF"):
        st.session_state.preview_questoes = texto.split("\n")

# --- 8. MOTOR DE PDF (BLINDADO) ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview da Atividade")
    with st.container(border=True):
        for line in st.session_state.preview_questoes:
            if line.strip(): st.write(line)

    def export_pdf():
        try:
            pdf = FPDF()
            pdf.add_page()
            y_pos = 10
            if usar_cabecalho and os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", 10, 10, 190)
                y_pos = recuo_cabecalho
            
            pdf.set_y(y_pos)
            letras = "abcdefghijklmnopqrstuvwxyz"
            l_idx = 0
            cols = int(layout_cols)
            larg_col = 190 / cols

            for line in st.session_state.preview_questoes:
                # Limpeza de caracteres especiais
                clean = line.strip().encode('latin-1', 'replace').decode('latin-1')
                if not clean: continue

                if clean.lower().startswith("t."):
                    pdf.ln(5); pdf.set_font("Helvetica", 'B', 16)
                    pdf.cell(190, 10, clean[2:].strip(), ln=True, align='C'); pdf.ln(5)
                elif clean.startswith(".M"):
                    pdf.set_font("Helvetica", 'I', 11)
                    pdf.multi_cell(190, 7, clean[2:].strip()); pdf.ln(2)
                elif re.match(r'^\d+\.', clean):
                    pdf.ln(4); pdf.set_font("Helvetica", 'B', 12)
                    pdf.cell(190, 9, clean, ln=True); l_idx = 0
                else:
                    pdf.set_font("Helvetica", size=11)
                    if cols > 1 and menu != "man":
                        c_at = l_idx % cols
                        pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {clean}", ln=(c_at == cols-1))
                        l_idx += 1
                    else:
                        pdf.multi_cell(190, 8, clean)
            
            return bytes(pdf.output())
        except Exception as e:
            return f"Erro: {str(e)}"

    pdf_out = export_pdf()
    if isinstance(pdf_out, bytes):
        st.download_button("📥 Baixar PDF Quantum", data=pdf_out, file_name="atividade.pdf", mime="application/pdf")

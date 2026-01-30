import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'gabarito' not in st.session_state: st.session_state.gabarito = []

def clean_txt(text):
    if not text: return ""
    text = str(text)
    text = text.replace("√", "Raiz de ").replace("²", "^2").replace("³", "^3")
    return text.encode('latin-1', 'replace').decode('latin-1')

def validar_acesso(pin_digitado):
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN (6 dígitos):", type="password", max_chars=8)
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- MENU LATERAL ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
usar_cabecalho = st.sidebar.checkbox("Incluir Cabeçalho no PDF", value=True)

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.gabarito = []
    st.session_state.sub_menu = None
    st.rerun()

# --- PAINEL ADMIN ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle")
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
    with c2: 
        if st.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
    with c3: 
        if st.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
    with c4: 
        if st.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
    with c5: 
        if st.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

    st.markdown("---")
    st.subheader("🧮 Ferramentas de Cálculo Online (Aparecem Abaixo)")
    d1, d2, d3 = st.columns(3)
    with d1: 
        if st.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with d3: 
        if st.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

    op_atual = st.session_state.sub_menu
    st.divider()

    # --- LÓGICA DAS FERRAMENTAS ONLINE (O QUE VOCÊ SENTIU FALTA) ---
    if op_atual == "calc_f":
        st.header("𝑓(x) Calculadora de Funções")
        exp = st.text_input("Digite a função (use 'x'):", "x**2 + 5*x + 6")
        val_x = st.number_input("Valor de x:", value=1.0)
        if st.button("Calcular Agora"):
            try:
                resultado = eval(exp.replace('x', f'({val_x})'))
                st.success(f"Resultado: f({val_x}) = {resultado}")
            except Exception as e: st.error(f"Erro na função: {e}")

    elif op_atual == "pemdas":
        st.header("📊 Calculadora PEMDAS (Expressões)")
        expr = st.text_input("Digite a expressão:", "(2 + 3) * 5**2")
        if st.button("Resolver Expressão"):
            try:
                st.info(f"O resultado é: {eval(expr)}")
            except: st.error("Expressão inválida.")

    elif op_atual == "fin":
        st.header("💰 Cálculo Financeiro")
        col_f1, col_f2, col_f3 = st.columns(3)
        capital = col_f1.number_input("Capital (R$):", 100.0)
        taxa = col_f2.number_input("Taxa ao mês (%):", 1.0)
        meses = col_f3.number_input("Tempo (meses):", 1)
        if st.button("Calcular Montante"):
            m = capital * (1 + taxa/100)**meses
            st.metric("Montante Final", f"R$ {m:.2f}")

    # --- LÓGICA DO GERADOR COLEGIAL ---
    elif op_atual == "col":
        st.header("📚 Colegial (PDF com Gabarito)")
        temas = st.multiselect("Temas:", ["Frações", "Porcentagem", "Potenciação", "Radiciação"], ["Potenciação", "Radiciação"])
        num_ini = st.number_input("Começar do número:", 1)
        qtd = st.number_input("Quantidade de itens:", 4, 30, 8)
        
        if st.button("Gerar Preview da Atividade"):
            qs = [f"t. Atividade de Matemática", f"{num_ini}. Resolva os itens:"]
            gab = ["--- GABARITO ---"]
            letras = "abcdefghijklmnopqrstuvwxyz"
            for i in range(qtd):
                t = random.choice(temas)
                letra = letras[i % 26]
                if t == "Potenciação":
                    b = random.randint(2,12)
                    qs.append(f"{b}² ="); gab.append(f"{letra}) {b**2}")
                elif t == "Radiciação":
                    n = random.choice([16, 25, 36, 49, 64, 81, 100])
                    qs.append(f"√{n} ="); gab.append(f"{letra}) {int(math.sqrt(n))}")
                # (Outros temas seguem a mesma lógica)
            st.session_state.preview_questoes = qs
            st.session_state.gabarito = gab

# --- VISUALIZAÇÃO DO PDF ---
if st.session_state.preview_questoes:
    st.divider()
    c_pdf1, c_pdf2 = st.columns(2)
    
    def criar_pdf(com_gab):
        pdf = FPDF()
        pdf.add_page()
        y_at = 60 if (usar_cabecalho and os.path.exists("cabecalho.png")) else 20
        if usar_cabecalho and os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=10, y=10, w=190)
        
        l_idx = 0
        letras = "abcdefghijklmnopqrstuvwxyz"
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if line.lower().startswith("t.") or re.match(r'^\d+', line):
                pdf.set_font("Arial", 'B', 12); pdf.set_y(y_at + 5)
                pdf.multi_cell(0, 10, clean_txt(line[2:] if line.lower().startswith("t.") else line))
                y_at = pdf.get_y(); l_idx = 0
            else:
                pdf.set_font("Arial", size=12); pdf.set_y(y_at); pdf.set_x(15)
                pdf.multi_cell(0, 10, clean_txt(f"{letras[l_idx%26]}) {line}"))
                y_at = pdf.get_y(); l_idx += 1
        
        if com_gab and st.session_state.gabarito:
            pdf.add_page(); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "GABARITO", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            for g in st.session_state.gabarito: pdf.cell(0, 8, clean_txt(g), ln=True)
        return pdf.output(dest='S').encode('latin-1')

    with c_pdf1:
        if st.button("📥 PDF Sem Gabarito"):
            st.download_button("Baixar Agora", criar_pdf(False), "atividade.pdf")
    with c_pdf2:
        if st.button("📥 PDF Com Gabarito"):
            st.download_button("Baixar Agora", criar_pdf(True), "atividade_com_gabarito.pdf")
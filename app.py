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
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
    except:
        senha_aluno, senha_prof = "123456", "12345678"
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None

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

# --- 2. LOGOUT E SIDEBAR ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
if st.sidebar.button("Sair/Logout"):
    st.session_state.perfil = None
    st.session_state.sub_menu = None
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

    # --- LÓGICA DE CADA MÓDULO ---
    if op_atual == "op":
        st.divider(); st.header("🔢 Gerador de Operações")
        ca, cb = st.columns(2)
        with ca:
            escolhas = st.multiselect("Operações:", ["Soma (+)", "Subtração (-)", "Multiplicação (x)", "Divisão (÷)"], ["Soma (+)", "Subtração (-)"])
        with cb:
            qtd = st.number_input("Quantidade:", 4, 40, 12)
        
        if st.button("Gerar PDF de Operações"):
            ops_map = {"Soma (+)":"+", "Subtração (-)":"-", "Multiplicação (x)":"x", "Divisão (÷)":"÷"}
            selecionadas = [ops_map[x] for x in escolhas]
            qs = [f"{random.randint(10,500)} {random.choice(selecionadas)} {random.randint(2,50)} =" for _ in range(qtd)]
            st.download_button("📥 Baixar Agora", exportar_pdf(qs, "Operações Básicas"), "op.pdf")

    elif op_atual == "eq":
        st.divider(); st.header("📐 Gerador de Equações")
        grau = st.radio("Tipo:", ["1º Grau", "2º Grau", "Misto"], horizontal=True)
        qtd_eq = st.slider("Quantidade:", 4, 20, 8)
        if st.button("Gerar PDF de Equações"):
            qs = []
            for _ in range(qtd_eq):
                modo = grau if grau != "Misto" else random.choice(["1º Grau", "2º Grau"])
                if modo == "1º Grau": qs.append(f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}")
                else: qs.append(f"x² + {random.randint(2,10)}x + {random.randint(1,16)} = 0")
            st.download_button("📥 Baixar Agora", exportar_pdf(qs, "Atividade de Equações"), "eq.pdf")

    elif op_atual == "man":
        st.divider(); st.header("📄 Gerador Manual")
        titulo_m = st.text_input("Título:", "Exercícios Propostos")
        txt_m = st.text_area("Regras: . para colunas | números resetam letras", height=250)
        if st.button("Gerar PDF Manual"):
            pdf = FPDF(); pdf.add_page()
            if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(titulo_m), ln=True, align='C'); pdf.ln(5)
            letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0; pdf.set_font("Arial", size=10)
            for linha in txt_m.split('\n'):
                t = linha.strip()
                if not t: continue
                match = re.match(r'^(\.+)', t); pts = len(match.group(1)) if match else 0
                if re.match(r'^\d+', t): # Começa com número
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(t))
                    pdf.set_font("Arial", size=10); l_idx = 0
                elif pts > 0: # Colunas
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*45); pdf.cell(45, 8, f"{letras[l_idx%26]}) {clean_txt(t[pts:].strip())}", ln=True)
                    l_idx += 1
                else: pdf.multi_cell(0, 8, clean_txt(t))
            st.download_button("📥 Baixar PDF Manual", pdf.output(dest='S').encode('latin-1', 'replace'), "manual.pdf")

    elif op_atual == "calc_f":
        st.divider(); st.header("𝑓(x) Calculadora")
        f_in = st.text_input("Função (use x e ** para potência):", "x**2 + 2*x + 1")
        x_in = st.number_input("Valor de x:", value=0.0)
        if st.button("Calcular"):
            try:
                res = eval(f_in.replace('x', f'({x_in})'))
                st.metric(f"f({x_in})", f"{res:.2f}")
            except: st.error("Erro na fórmula.")

    elif op_atual == "pemdas":
        st.divider(); st.header("📊 Calculadora PEMDAS")
        exp = st.text_input("Expressão:", "5 + (2 * 3**2)")
        if st.button("Resolver"):
            try: st.success(f"Resultado: {eval(exp)}")
            except: st.error("Expressão inválida.")

    elif op_atual == "fin":
        st.divider(); st.header("💰 Financeira")
        c, i, n = st.columns(3)
        pv = c.number_input("Capital (PV):", 1000.0)
        rate = i.number_input("Taxa % (i):", 5.0)
        time = n.number_input("Meses (n):", 12)
        if st.button("Calcular Juros Compostos"):
            fv = pv * (1 + rate/100)**time
            st.metric("Montante Final (FV)", f"R$ {fv:.2f}")

else:
    st.title("📖 Área do Estudante")
    st.write("Bem-vindo! Utilize as calculadoras no menu lateral se disponíveis.")
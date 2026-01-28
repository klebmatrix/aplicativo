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
        senha_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    except:
        senha_prof, senha_aluno = "12345678", "123456"
    if pin_digitado == senha_prof: return "admin"
    if pin_digitado == senha_aluno: return "aluno"
    return None

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso:
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 2. MENU LATERAL ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
if st.sidebar.button("Logout"):
    st.session_state.perfil = None
    st.session_state.sub_menu = None
    st.rerun()

# --- 3. FUNÇÃO MESTRA PDF ---
def exportar_atividade_pdf(questoes, titulo):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", x=12.5, y=8, w=185)
        pdf.set_y(46)
    else: pdf.set_y(15)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=clean_txt(titulo), ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=11)
    letras = "abcdefghijklmnopqrstuvwxyz"
    for i, q in enumerate(questoes):
        pdf.multi_cell(0, 10, txt=f"{letras[i%26]}) {clean_txt(q)}")
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. PAINEL PROFESSOR ---
if st.session_state.perfil == "admin":
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

    st.divider()
    op = st.session_state.sub_menu

    # --- GERADOR: OPERAÇÕES ---
    if op == "op":
        st.header("🔢 Configurar Operações Básicas")
        col_a, col_b = st.columns(2)
        with col_a:
            soma = st.checkbox("Soma (+)", True)
            sub = st.checkbox("Subtração (-)", True)
            mult = st.checkbox("Multiplicação (x)")
            div = st.checkbox("Divisão (÷)")
        with col_b:
            qtd = st.number_input("Quantidade de questões:", 1, 50, 10)
            nivel = st.select_slider("Dificuldade:", options=["Fácil", "Médio", "Difícil"])
        
        escolhidas = [o for o, v in zip(['+', '-', 'x', '÷'], [soma, sub, mult, div]) if v]
        
        if st.button("Gerar Atividade"):
            if not escolhidas: st.warning("Selecione pelo menos uma operação.")
            else:
                qs = []
                range_n = {"Fácil": (1, 50), "Médio": (50, 500), "Difícil": (500, 5000)}[nivel]
                for _ in range(qtd):
                    n1, n2 = random.randint(*range_n), random.randint(1, 50)
                    qs.append(f"{n1} {random.choice(escolhidas)} {n2} =")
                
                st.session_state.preview = qs
                st.success("Atividade Gerada!")

        if 'preview' in st.session_state and op == "op":
            for i, q in enumerate(st.session_state.preview): st.write(f"**{chr(97+i%26)})** {q}")
            st.download_button("📥 Baixar PDF", exportar_atividade_pdf(st.session_state.preview, "Operações Básicas"), "ops.pdf")

    # --- GERADOR: EQUAÇÕES ---
    elif op == "eq":
        st.header("📐 Configurar Equações")
        tipo_eq = st.multiselect("Tipos de Equação:", ["1º Grau (ax + b = c)", "2º Grau (x² + bx + c = 0)"], ["1º Grau (ax + b = c)"])
        qtd_eq = st.number_input("Quantidade:", 1, 30, 6)
        
        if st.button("Gerar Equações"):
            qs = []
            for _ in range(qtd_eq):
                t = random.choice(tipo_eq)
                if "1º" in t: qs.append(f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}")
                else: qs.append(f"x² + {random.randint(2,10)}x + {random.randint(1,20)} = 0")
            st.session_state.preview_eq = qs
        
        if 'preview_eq' in st.session_state:
            for i, q in enumerate(st.session_state.preview_eq): st.write(f"**{chr(97+i%26)})** {q}")
            st.download_button("📥 Baixar PDF", exportar_atividade_pdf(st.session_state.preview_eq, "Atividade de Equações"), "equacoes.pdf")

    # --- GERADOR: MANUAL (O MAIS IMPORTANTE) ---
    elif op == "man":
        st.header("📄 Gerador Manual Personalizado")
        titulo_m = st.text_input("Título da Atividade:", "Exercícios de Fixação")
        txt_m = st.text_area("Conteúdo (Use . para colunas | Números resetam letras):", height=300)
        
        if st.button("Gerar PDF Manual"):
            pdf = FPDF(); pdf.add_page()
            if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
            else: pdf.set_y(15)
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(titulo_m), ln=True, align='C'); pdf.ln(5)
            
            letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
            pdf.set_font("Arial", size=10)
            
            for linha in txt_m.split('\n'):
                t = linha.strip()
                if not t: continue
                match = re.match(r'^(\.+)', t); pts = len(match.group(1)) if match else 0
                
                if re.match(r'^\d+', t): # Inicia com número: Questão nova
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(t))
                    pdf.set_font("Arial", size=10); l_idx = 0 # Reseta letra para a)
                elif pts > 0: # É uma coluna
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*45)
                    pdf.cell(45, 8, f"{letras[l_idx%26]}) {clean_txt(t[pts:].strip())}", ln=True)
                    l_idx += 1
                else:
                    pdf.multi_cell(0, 8, clean_txt(t))
            
            st.download_button("📥 Baixar PDF Manual", pdf.output(dest='S').encode('latin-1', 'replace'), "manual.pdf")

# --- 5. PAINEL ALUNO ---
else:
    st.title("📖 Área do Estudante")
    st.info("Utilize as calculadoras online abaixo.")
    # Aqui entrariam os cards de cálculo para o aluno...
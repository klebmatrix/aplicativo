import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO INICIAL (Fixa) ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# Inicialização de variáveis para não dar erro de "KeyError" ou "Undefined"
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = "op" # Padrão inicial
if 'preview_data' not in st.session_state: st.session_state.preview_data = []

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        s_prof = str(st.secrets.get("chave_mestra", "12345678")).strip().lower()
        s_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        if pin == s_prof: st.session_state.perfil = "admin"
        elif pin == s_aluno: st.session_state.perfil = "aluno"
        else: st.error("PIN incorreto.")
        st.rerun()
    st.stop()

# --- 3. SIDEBAR FIXA ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

# --- 4. ÁREA DOS GERADORES (Apenas Professor) ---
if st.session_state.perfil == "admin":
    st.title("🛠️ Painel do Professor")
    
    # Menu de seleção por abas (mais estável que botões soltos)
    aba_gerador, aba_calculadora = st.tabs(["📝 GERADORES DE PDF", "🧮 CALCULADORAS ONLINE"])

    with aba_gerador:
        st.subheader("Escolha o tipo de atividade")
        tipo = st.selectbox("Módulo:", ["Operações Básicas", "Equações", "Colegial Completo", "Álgebra Linear", "Manual"], key="main_select")
        
        # Filtros específicos por tipo
        if tipo == "Operações Básicas":
            ops = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
            qtd = st.number_input("Questões:", 1, 50, 10)
            if st.button("🔍 Gerar Preview"):
                st.session_state.preview_data = [f"{random.randint(10,99)} {random.choice(ops)} {random.randint(2,20)} =" for _ in range(qtd)]

        elif tipo == "Colegial Completo":
            temas = st.multiselect("Tópicos:", ["Frações", "Potência", "Raiz", "Sistemas", "Matrizes"], ["Frações"])
            qtd = st.number_input("Questões:", 1, 40, 10)
            if st.button("🔍 Gerar Preview"):
                res = []
                for _ in range(qtd):
                    t = random.choice(temas)
                    if t == "Frações": res.append(f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/{random.randint(2,5)} =")
                    elif t == "Potência": res.append(f"{random.randint(2,10)}^{random.randint(2,3)} =")
                    elif t == "Raiz": res.append(f"√{random.randint(2,12)**2} =")
                    elif t == "Sistemas": res.append(f"Resolva: {{ x+y={random.randint(5,10)} | x-y={random.randint(1,4)} }}")
                    elif t == "Matrizes": res.append(f"Det da Matriz 2x2: {np.random.randint(1,9, (2,2)).tolist()}")
                st.session_state.preview_data = res

        elif tipo == "Manual":
            txt_m = st.text_area("Digite o conteúdo (. para colunas):", height=200)
            if st.button("🔍 Visualizar Manual"):
                st.session_state.preview_data = txt_m.split('\n')

        # --- ÁREA DE DOWNLOAD (Sempre Visível se houver dados) ---
        if st.session_state.preview_data:
            st.divider()
            st.write("### 👀 Prévia")
            for q in st.session_state.preview_data: st.write(q)
            
            # Lógica do PDF
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10)
            if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "Atividade Matematica", ln=True, align='C'); pdf.ln(5)
            for i, q in enumerate(st.session_state.preview_data):
                pdf.multi_cell(0, 10, f"{chr(97+(i%26))}) {clean_txt(q)}")
            
            st.download_button("📥 Baixar PDF Agora", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")

    with aba_calculadora:
        # CALCULADORAS FIXAS (Não somem)
        st.subheader("🧮 Calculadoras Online")
        calc_tipo = st.radio("Selecione a ferramenta:", ["PEMDAS", "f(x) Função", "Financeira"], horizontal=True)
        
        if calc_tipo == "PEMDAS":
            exp = st.text_input("Expressão:", "5 + (2 * 10)")
            if st.button("Resolver"): st.success(f"Resultado: {eval(exp)}")
        
        elif calc_tipo == "f(x) Função":
            f_in = st.text_input("f(x):", "x**2")
            x_v = st.number_input("Valor de x:", 2)
            if st.button("Calcular"): st.metric("f(x)", eval(f_in.replace('x', str(x_v))))
        
        elif calc_tipo == "Financeira":
            pv = st.number_input("Capital:", 1000.0)
            tax = st.number_input("Taxa %:", 5.0)
            if st.button("Calcular 1 mês"): st.write(f"Montante: {pv * (1 + tax/100)}")

else:
    st.title("📖 Área do Aluno")
    st.info("Utilize as calculadoras na aba de ferramentas.")
import streamlit as st
import random
import re
import os
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO INICIAL (Obrigatório ser o primeiro) ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicializa as variáveis para não dar erro de "não definido"
if 'preview_questoes' not in st.session_state:
    st.session_state.preview_questoes = []
if 'menu_aberto' not in st.session_state:
    st.session_state.menu_aberto = None

# --- 2. LOGIN (Simplificado para teste) ---
if 'logado' not in st.session_state:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        if pin == "123456" or pin == "chave_mestra": # Use seus secrets aqui depois
            st.session_state.logado = True
            st.rerun()
    st.stop()

# --- 3. INTERFACE PRINCIPAL ---
st.sidebar.title("🚀 Painel Quantum")
colunas_pdf = st.sidebar.selectbox("Colunas no PDF", [1, 2, 3], index=1)
if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.menu_aberto = None
    st.rerun()

st.title("🛠️ Centro de Comando")

# --- 4. AS DUAS LINHAS DE BOTÕES (Layout solicitado) ---
st.subheader("📝 Geradores de PDF (5)")
g1, g2, g3, g4, g5 = st.columns(5)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.menu_aberto = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.menu_aberto = "eq"
if g3.button("📚 Colegial", use_container_width=True): st.session_state.menu_aberto = "col"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.menu_aberto = "alg"
if g5.button("📄 Manual", use_container_width=True): st.session_state.menu_aberto = "man"

st.markdown("---")
st.subheader("🧮 Ferramentas de Cálculo (3)")
d1, d2, d3 = st.columns(3)
if d1.button("𝑓(x) Funções", use_container_width=True): st.session_state.menu_aberto = "calc_f"
if d2.button("📊 PEMDAS", use_container_width=True): st.session_state.menu_aberto = "pemdas"
if d3.button("💰 Financeira", use_container_width=True): st.session_state.menu_aberto = "fin"

st.divider()

# --- 5. LÓGICA DOS MENUS (AQUI É ONDE A MÁGICA ACONTECE) ---
menu = st.session_state.menu_aberto

if menu == "op":
    st.subheader("🔢 Gerador de Operações")
    n_ini = st.number_input("Iniciar no nº:", value=6)
    qtd = st.slider("Quantidade:", 5, 30, 10)
    if st.button("✨ Gerar Agora"):
        # Regras: .M1 na esquerda, t. no centro, questão começando no 6
        res = [".M1", "t. ATIVIDADE DE MATEMÁTICA", f"{n_ini}. Resolva as contas:"]
        for _ in range(qtd):
            res.append(f"{random.randint(10,99)} + {random.randint(10,99)} =")
        st.session_state.preview_questoes = res
        st.success("Gerado com sucesso! Veja o preview abaixo.")

elif menu == "man":
    st.subheader("📄 Inserção Manual")
    texto = st.text_area("Digite: .M1 (módulo), t. (título), 6. (questão), . (item)")
    if st.button("📝 Aplicar Texto"):
        st.session_state.preview_questoes = texto.split('\n')

elif menu == "calc_f":
    st.subheader("𝑓(x) Funções")
    st.info("Ferramenta online em desenvolvimento...")

# --- 6. PREVIEW E PDF (ESTA PARTE É FIXA) ---
if st.session_state.preview_questoes:
    st.divider()
    st.subheader("👁️ Preview do PDF")
    
    with st.container(border=True):
        for l in st.session_state.preview_questoes:
            st.text(l)

    # Função do PDF reconstruída para não dar erro de encoding
    def build_pdf(lista):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx = 0
        y_pos = 20
        larg_col = 190 / colunas_pdf

        for line in lista:
            line = line.strip()
            if not line: continue
            
            # .M1 -> Esquerda Negrito
            if re.match(r'^\.M(\d+)', line, re.IGNORECASE):
                pdf.set_font("Helvetica", 'B', 12)
                pdf.cell(190, 10, f"M{re.findall(r'\d+', line)[0]}", ln=True, align='L')
                l_idx = 0
            # t. -> Centro Negrito
            elif line.lower().startswith("t."):
                pdf.set_font("Helvetica", 'B', 14)
                pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
                l_idx = 0
            # 6. -> Esquerda Normal
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", '', 12)
                pdf.cell(190, 10, line, ln=True, align='L')
                l_idx = 0
            # Itens -> Colunas
            else:
                pdf.set_font("Helvetica", '', 12)
                col = l_idx % colunas_pdf
                txt_item = f"{letras[l_idx % 26]}) {line.lstrip('. ')}"
                pdf.cell(larg_col, 8, txt_item, align='L', ln=(col == colunas_pdf - 1))
                l_idx += 1
        
        return pdf.output(dest='S').encode('latin-1')

    # Download direto
    st.download_button("📥 Baixar PDF", data=build_pdf(st.session_state.preview_questoes), file_name="atividade.pdf")
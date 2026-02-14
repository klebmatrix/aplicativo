import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF
from io import BytesIO  # Importação necessária para lidar com memória

# --- 1. CONFIGURAÇÃO E PERSISTÊNCIA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicializa estados se não existirem
for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else None if key == 'perfil' else ""

# --- 2. LOGIN (Secrets Render) ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    return "admin" if pin == p_prof else "aluno" if pin == p_aluno else None

if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin_input)
        if res: 
            st.session_state.perfil = res
            st.rerun()
        else: 
            st.error("PIN Incorreto")
    st.stop()

# --- 3. SIDEBAR (CONFIGURAÇÕES E LOGOUT) ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Usar cabecalho.png", value=True)
recuo_cabecalho = st.sidebar.slider("Altura do Título:", 20, 80, 45)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)

st.sidebar.divider()
if st.sidebar.button("🧹 Limpar Atividade", use_container_width=True):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

if st.sidebar.button("🚪 Sair / Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- 4. CENTRO DE COMANDO ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5 = st.columns(5)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas", use_container_width=True): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara", use_container_width=True): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS GERADORES (Simplificado para o exemplo) ---
if menu == "op":
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Atividade"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        qs = [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", f"t. Atividade de {tipo}", "1. Calcule:"] + qs
# (Outras lógicas mantidas conforme seu original...)

# --- 7. MOTOR PDF (COM TÍTULO SEPARADO E SUPORTE A MANUAL) ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview da Atividade")
    with st.container(border=True):
        for line in st.session_state.preview_questoes: 
            st.write(line)

    def gerar_pdf_final():
        try:
            # latin-1 é mais seguro para FPDF padrão, mas fpdf2 lida bem com UTF-8
            pdf = FPDF()
            pdf.add_page()
            
            # 1. CABEÇALHO (IMAGEM)
            y_atual = 10
            if usar_cabecalho and os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", 10, 10, 190)
                y_atual = recuo_cabecalho # Define onde o título começa após a imagem
            
            pdf.set_y(y_atual)
            letras = "abcdefghijklmnopqrstuvwxyz"
            l_idx = 0
            larg_col = 190 / int(layout_cols)
            
            # 2. PROCESSAMENTO DAS LINHAS
            for line in st.session_state.preview_questoes:
                line = line.strip()
                if not line: continue
                
                # Identifica Título (t.)
                if line.lower().startswith("t."):
                    pdf.ln(5)
                    pdf.set_font("Helvetica", 'B', 16)
                    pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
                    pdf.ln(5)
                
                # Identifica Metadados ou Instruções (.M)
                elif line.startswith(".M"):
                    pdf.set_font("Helvetica", 'I', 11)
                    pdf.multi_cell(190, 8, line[2:].strip())
                    pdf.ln(2)
                
                # Identifica Questão Numerada (ex: 1. Calcule)
                elif re.match(r'^\d+\.', line):
                    pdf.ln(4)
                    pdf.set_font("Helvetica", 'B', 12)
                    pdf.cell(190, 10, line, ln=True)
                    l_idx = 0 # Reseta o contador de letras (a, b, c) para a nova questão
                
                # Itens das Questões (Colunas) ou Texto do Manual
                else:
                    pdf.set_font("Helvetica", size=12)
                    if int(layout_cols) > 1:
                        col = l_idx % int(layout_cols)
                        txt = f"{letras[l_idx%26]}) {line.lstrip('. ')}"
                        pdf.cell(larg_col, 8, txt, ln=(col == int(layout_cols)-1))
                        l_idx += 1
                    else:
                        # Se for 1 coluna, trata como texto corrido (Manual)
                        pdf.multi_cell(190, 8, line)
            
            # 3. CONVERSÃO SEGURA PARA BYTES
            resultado_pdf = pdf.output()
            if isinstance(resultado_pdf, (bytearray, bytes)):
                return bytes(resultado_pdf)
            return resultado_pdf.encode('latin-1')
            
        except Exception as e:
            st.error(f"Erro na geração do PDF: {e}")
            return None

    # Botão de Download
    pdf_bytes = gerar_pdf_final()
    if pdf_bytes:
        st.download_button(
            label="📥 Baixar PDF da Atividade",
            data=pdf_bytes,
            file_name="atividade_quantum.pdf",
            mime="application/pdf",
            key="download_pdf_final"
        )

import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF
from io import BytesIO

# --- 1. CONFIGURAÇÃO E PERSISTÊNCIA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização robusta do Session State
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = ""
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""

# --- 2. LOGIN ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "")).strip().lower()
    return "admin" if pin == p_prof else "aluno" if pin == p_aluno else None

if st.session_state.perfil is None:
    st.title("🔐 Login Quantum")
    pin_input = st.text_input("Digite seu PIN:", type="password")
    if st.button("Acessar Sistema"):
        res = validar_acesso(pin_input)
        if res:
            st.session_state.perfil = res
            st.rerun()
        else:
            st.error("PIN Incorreto")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 Painel {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Exibir Cabeçalho (PNG)", value=True)
recuo_cabecalho = st.sidebar.slider("Altura após cabeçalho:", 10, 100, 45)
layout_cols = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

if st.sidebar.button("🚪 Sair"):
    st.session_state.clear()
    st.rerun()

# --- 4. CENTRO DE COMANDO ---
st.title("🛠️ Centro de Comando Quantum")
cols = st.columns(5)
botoes = ["🔢 Operações", "📐 Equações", "⛓️ Sistemas", "⚖️ Álgebra", "📄 Manual"]
tags = ["op", "eq", "sis", "alg", "man"]

for col, nome, tag in zip(cols, botoes, tags):
    if col.button(nome, use_container_width=True):
        st.session_state.sub_menu = tag

cols_calc = st.columns(3)
if cols_calc[0].button("𝑓(x) Bhaskara", use_container_width=True): st.session_state.sub_menu = "calc_f"
if cols_calc[1].button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
if cols_calc[2].button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS GERADORES ---
if menu == "op":
    tipo = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Lista"):
        simb = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
        qs = [f"{random.randint(10, 999)} {simb} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [f"t. Atividade de {tipo}", ".M Resolva as operações com atenção:", "1. Calcule:"] + qs

elif menu == "man":
    txt = st.text_area("Editor Manual (Use 't.' para título e '.M' para instruções):", height=200)
    if st.button("Lançar no Preview"):
        st.session_state.preview_questoes = txt.split("\n")

# --- 7. MOTOR PDF (REVISADO E BLINDADO) ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview do Documento")
    with st.container(border=True):
        for line in st.session_state.preview_questoes:
            if line.strip(): st.write(line)

    def gerar_pdf_seguro():
        try:
            pdf = FPDF()
            pdf.add_page()
            
            y_start = 10
            if usar_cabecalho and os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", 10, 10, 190)
                y_start = recuo_cabecalho
            
            pdf.set_y(y_start)
            letras = "abcdefghijklmnopqrstuvwxyz"
            l_idx = 0
            cols_count = int(layout_cols)
            larg_col = 190 / cols_count

            for line in st.session_state.preview_questoes:
                # Limpeza de caracteres incompatíveis com Latin-1
                raw_line = line.strip().encode('latin-1', 'replace').decode('latin-1')
                if not raw_line: continue

                # TÍTULO (t.)
                if raw_line.lower().startswith("t."):
                    pdf.ln(5)
                    pdf.set_font("Helvetica", 'B', 16)
                    pdf.cell(190, 10, raw_line[2:].strip(), ln=True, align='C')
                    pdf.ln(5)
                
                # INSTRUÇÕES (.M)
                elif raw_line.startswith(".M"):
                    pdf.set_font("Helvetica", 'I', 11)
                    pdf.multi_cell(190, 7, raw_line[2:].strip())
                    pdf.ln(2)

                # QUESTÃO NUMERADA (1., 2...)
                elif re.match(r'^\d+\.', raw_line):
                    pdf.ln(4)
                    pdf.set_font("Helvetica", 'B', 12)
                    pdf.cell(190, 9, raw_line, ln=True)
                    l_idx = 0
                
                # CONTEÚDO / ITENS
                else:
                    pdf.set_font("Helvetica", size=11)
                    if cols_count > 1 and menu != "man":
                        col_atual = l_idx % cols_count
                        txt_item = f"{letras[l_idx%26]}) {raw_line.lstrip('. ')}"
                        pdf.cell(larg_col, 8, txt_item, ln=(col_atual == cols_count - 1))
                        l_idx += 1
                    else:
                        pdf.multi_cell(190, 7, raw_line)
            
            # Retorno em bytes puros para o Streamlit
            return bytes(pdf.output())
        except Exception as e:
            return f"Erro: {str(e)}"

    # Geração e Botão de Download
    pdf_final = gerar_pdf_seguro()
    
    if isinstance(pdf_final, bytes):
        st.download_button(
            label="📥 Baixar PDF Corrigido",
            data=pdf_final,
            file_name="atividade_quantum.pdf",
            mime="application/pdf",
            key="btn_pdf_v3"
        )
    else:
        st.error(pdf_final)


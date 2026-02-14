import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de estados do sistema
for key in ['perfil', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = None if key == 'perfil' else ([] if key == 'preview_questoes' else "")

# --- 2. SISTEMA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab - Acesso")
    with st.container(border=True):
        pin = st.text_input("Digite seu PIN de acesso:", type="password")
        if st.button("ENTRAR", use_container_width=True):
            # Validação simples (pode usar st.secrets dps)
            if pin == "123": 
                st.session_state.perfil = "admin"
                st.rerun()
            else:
                st.error("PIN incorreto. Tente novamente.")
    st.stop()

# --- 3. BARRA LATERAL (MENU E CONFIGS) ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")

menu = st.sidebar.selectbox(
    "SELECIONE A FERRAMENTA:",
    ["Início", "🔢 Operações", "📐 Equações", "𝑓(x) Bhaskara", "⛓️ Sistemas", "💰 Financeira", "📄 Manual"]
)

st.sidebar.divider()
st.sidebar.subheader("⚙️ Configurações do PDF")
usar_cabecalho = st.sidebar.checkbox("Usar cabeçalho.png", value=False)
layout_cols = st.sidebar.selectbox("Colunas:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 LIMPAR TUDO", use_container_width=True):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

if st.sidebar.button("🚪 SAIR", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- 4. LÓGICA DAS FERRAMENTAS ---
st.title(f"🛠️ {menu}")

if menu == "Início":
    st.info("Escolha uma ferramenta no menu lateral para começar a gerar suas atividades.")

elif menu == "🔢 Operações":
    op = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    qtd = st.slider("Quantidade:", 4, 40, 12)
    if st.button("GERAR LISTA"):
        sinal = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[op]
        qs = [f"{random.randint(10, 999)} {sinal} {random.randint(10, 99)} =" for _ in range(qtd)]
        st.session_state.preview_questoes = [f"t. Lista de {op}", "1. Resolva os cálculos abaixo:"] + qs

elif menu == "📐 Equações":
    if st.button("GERAR EQUAÇÕES 1º GRAU"):
        qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(10)]
        st.session_state.preview_questoes = ["t. Equações de 1º Grau", "1. Determine o valor de x:"] + qs

elif menu == "𝑓(x) Bhaskara":
    col1, col2, col3 = st.columns(3)
    a = col1.number_input("Valor de a", value=1.0)
    b = col2.number_input("Valor de b", value=-5.0)
    c = col3.number_input("Valor de c", value=6.0)
    if st.button("CALCULAR"):
        delta = b**2 - 4*a*c
        if delta >= 0:
            x1 = (-b + math.sqrt(delta)) / (2*a)
            x2 = (-b - math.sqrt(delta)) / (2*a)
            st.session_state.res_calc = f"Delta: {delta} | x1: {x1:.2f} | x2: {x2:.2f}"
        else:
            st.session_state.res_calc = "Delta negativo! Não existem raízes reais."

elif menu == "💰 Financeira":
    capital = st.number_input("Capital (R$):", value=1000.0)
    taxa = st.number_input("Taxa (% ao mês):", value=2.0)
    tempo = st.number_input("Tempo (meses):", value=12)
    if st.button("GERAR JUROS SIMPLES"):
        juros = capital * (taxa/100) * tempo
        st.session_state.res_calc = f"Juros: R$ {juros:.2f} | Total: R$ {capital + juros:.2f}"

elif menu == "📄 Manual":
    txt = st.text_area("Digite suas questões (uma por linha):", height=200)
    if st.button("IMPORTAR PARA PREVIEW"):
        st.session_state.preview_questoes = txt.split("\n")

# --- 5. RESULTADOS E EXPORTAÇÃO PDF ---

# Exibe resultado de cálculos rápidos (Bhaskara/Financeira)
if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

# Exibe Preview e Botão de Download se houver questões
if st.session_state.preview_questoes:
    st.divider()
    st.subheader("👁️ Preview da Folha")
    with st.container(border=True):
        for line in st.session_state.preview_questoes:
            if line.strip(): st.write(line)

    def gerar_pdf():
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("helvetica", size=12)
        
        y_pos = 20
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=10, w=190)
            y_pos = 50 
        
        pdf.set_y(y_pos)
        larg_col = 190 / layout_cols
        l_idx = 0
        letras = "abcdefghijklmnopqrstuvwxyz"

        for line in st.session_state.preview_questoes:
            # Limpeza de caracteres especiais para evitar erro no PDF
            clean = line.strip().encode('latin-1', 'replace').decode('latin-1')
            if not clean: continue
            
            if clean.startswith("t."):
                pdf.ln(5)
                pdf.set_font("helvetica", style='B', size=14)
                pdf.cell(190, 10, clean[2:].strip(), ln=True, align='C')
                pdf.set_font("helvetica", size=12)
                l_idx = 0
            else:
                col_at = l_idx % layout_cols
                txt_item = f"{letras[l_idx%26]}) {clean}"
                pdf.cell(larg_col, 8, txt_item, ln=(col_at == layout_cols - 1))
                l_idx += 1
        
        # O output() no fpdf2 retorna bytes pronto para o download_button
        return pdf.output()

    # Só gera o botão se o PDF for construído com sucesso
    try:
        pdf_data = gerar_pdf()
        st.download_button(
            label="📥 BAIXAR ATIVIDADE EM PDF",
            data=pdf_data,
            file_name="quantum_atividade.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")

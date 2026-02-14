import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de estados para não perder dados
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""

# --- 2. LOGIN (DEPENDENTE DE SECRETS) ---
def validar_acesso(pin):
    try:
        # Se não houver secrets, ele usa os padrões abaixo
        p_aluno = str(st.secrets.get("acesso_aluno", "123")).strip()
        p_prof = str(st.secrets.get("chave_mestra", "admin")).strip().lower()
        if pin == p_prof: return "admin"
        if pin == p_aluno: return "aluno"
    except: pass
    return None

if st.session_state.perfil is None:
    st.title("🔐 Login Quantum")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("ACESSAR"):
        res = validar_acesso(pin_input)
        if res:
            st.session_state.perfil = res
            st.rerun()
        else: st.error("PIN INCORRETO!")
    st.stop()

# --- 3. MENU LATERAL (A ESTRUTURA QUE NÃO FALHA) ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")

menu = st.sidebar.selectbox(
    "ESCOLHA A FERRAMENTA:",
    [
        "Início", 
        "🔢 Operações", 
        "📐 Equações", 
        "⛓️ Sistemas", 
        "𝑓(x) Bhaskara",
        "📄 Manual"
    ]
)

st.sidebar.divider()
usar_cabecalho = st.sidebar.checkbox("Usar cabeçalho.png", value=True)
layout_cols = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 LIMPAR TUDO", use_container_width=True):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

if st.sidebar.button("🚪 SAIR", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- 4. ÁREAS DE CONTEÚDO (O QUE APARECE NA TELA) ---
st.title(f"🛠️ {menu}")

# Bloco 1: Operações
if menu == "🔢 Operações":
    tipo = st.radio("Escolha a operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("GERAR LISTA"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        qs = [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [f"t. Lista de {tipo}", "1. Calcule os resultados abaixo:"] + qs

# Bloco 2: Equações
elif menu == "📐 Equações":
    grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("GERAR EQUAÇÕES"):
        if grau == "1º Grau":
            qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(10)]
        else:
            qs = [f"x² - {random.randint(5,10)}x + {random.randint(1,6)} = 0" for _ in range(5)]
        st.session_state.preview_questoes = [f"t. Equações de {grau}", "1. Encontre o valor de x:"] + qs

# Bloco 3: Bhaskara
elif menu == "𝑓(x) Bhaskara":
    st.write("Calculadora Online")
    c1, c2, c3 = st.columns(3)
    a = c1.number_input("a", value=1.0)
    b = c2.number_input("b", value=-5.0)
    c = c3.number_input("c", value=6.0)
    if st.button("CALCULAR AGORA"):
        delta = b**2 - 4*a*c
        if delta >= 0:
            x1 = (-b + math.sqrt(delta))/(2*a)
            x2 = (-b - math.sqrt(delta))/(2*a)
            st.session_state.res_calc = f"Delta: {delta} | x1: {x1:.2f} | x2: {x2:.2f}"
        else: st.session_state.res_calc = "Delta negativo!"

# Bloco 4: Manual
elif menu == "📄 Manual":
    txt = st.text_area("Digite as questões (uma por linha):", placeholder="Ex: 10 + 10 =\nt. Título")
    if st.button("ENVIAR PARA PDF"):
        st.session_state.preview_questoes = txt.split("\n")

# Se for "Início" e não tiver nada selecionado
else:
    st.info("Selecione uma opção na barra lateral para abrir as ferramentas.")

# --- 5. EXIBIÇÃO E PDF (SÓ APARECE SE TIVER CONTEÚDO) ---
if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

if st.session_state.preview_questoes:
    st.divider()
    st.subheader("👁️ Preview da Folha A4")
    with st.container(border=True):
        for line in st.session_state.preview_questoes:
            if line.strip(): st.write(line)

    def gerar_pdf_a4():
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)
        
        y_pos = 20
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            y_pos = 50 # Recuo padrão para o título não bater na imagem
        
        pdf.set_y(y_pos)
        larg_col = 190 / layout_cols
        l_idx = 0
        letras = "abcdefghijklmnopqrstuvwxyz"

        for line in st.session_state.preview_questoes:
            clean = line.strip().encode('latin-1', 'replace').decode('latin-1')
            if not clean: continue
            
            if clean.startswith("t."):
                pdf.ln(5); pdf.set_font("Helvetica", 'B', 14)
                pdf.cell(190, 10, clean[2:].strip(), ln=True, align='C')
                pdf.set_font("Helvetica", size=11); l_idx = 0
            elif re.match(r'^\d+\.', clean):
                pdf.ln(5); pdf.set_font("Helvetica", 'B', 12)
                pdf.cell(190, 8, clean, ln=True); pdf.set_font("Helvetica", size=11); l_idx = 0
            else:
                col_at = l_idx % layout_cols
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {clean}", ln=(col_at == layout_cols - 1))
                l_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 BAIXAR PDF A4", data=gerar_pdf_a4(), file_name="quantum_lab.pdf", mime="application/pdf")

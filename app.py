import streamlit as st
import random
import re
import os
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO (Sempre o primeiro) ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de todos os estados necessários
for key in ['perfil', 'sub_menu', 'preview_questoes']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else None

# --- 2. LOGIN (Secrets do Render) ---
def validar_acesso(pin_digitado):
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN de Acesso:", type="password", max_chars=8)
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 3. BARRA LATERAL (CONFIGS + LIMPAR + SAIR) ---
st.sidebar.title(f"🚀 {'Professor' if st.session_state.perfil == 'admin' else 'Estudante'}")

# Opções de PDF
usar_cabecalho = st.sidebar.checkbox("Incluir Cabeçalho", value=True)
incluir_gabarito = st.sidebar.checkbox("Gerar Gabarito", value=False)
layout_colunas = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

st.sidebar.markdown("---")

# BOTÃO LIMPAR (RESTAURADO)
if st.sidebar.button("🧹 Limpar Tudo", use_container_width=True):
    st.session_state.preview_questoes = []
    st.session_state.sub_menu = None
    st.rerun()

# BOTÃO SAIR (RESTAURADO)
if st.sidebar.button("🚪 Sair / Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- 4. PAINEL DE COMANDO (8 BOTÕES) ---
if st.session_state.perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
    # LINHA 1: 5 GERADORES
    st.subheader("📝 Geradores de PDF")
    g1, g2, g3, g4, g5 = st.columns(5)
    if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
    if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
    if g3.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
    if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
    if g5.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

    # LINHA 2: 3 CÁLCULOS
    st.markdown("---")
    st.subheader("🧮 Ferramentas de Cálculo")
    c1, c2, c3 = st.columns(3)
    if c1.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    if c2.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
    if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

    menu = st.session_state.sub_menu
    st.divider()

    # Lógicas de Geração
    if menu == "op":
        st.header("🔢 Operações")
        n_ini = st.number_input("Iniciar no nº:", value=6)
        if st.button("Gerar Agora"):
            st.session_state.preview_questoes = [".M1", "t. OPERAÇÕES", f"{n_ini}. Calcule:"] + \
                [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(12)]
            st.rerun()

    elif menu == "man":
        st.header("📄 Módulo Manual")
        txt = st.text_area("Ex: .M1, t. Titulo, 6. Pergunta, .Item")
        if st.button("Aplicar"):
            st.session_state.preview_questoes = txt.split('\n')
            st.rerun()
    
    # Adicione as outras lógicas aqui conforme necessário...

# --- 5. PREVIEW E PDF ENGINE ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    with st.container(border=True):
        for item in st.session_state.preview_questoes: st.text(item)

    def export_pdf():
        try:
            pdf = FPDF()
            pdf.add_page()
            y_pos = 10
            
            if usar_cabecalho and os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", 10, 10, 190)
                y_pos = 65
            
            pdf.set_y(y_pos)
            letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
            n_cols = int(layout_colunas)
            larg_col = 190 / n_cols
            
            for line in st.session_state.preview_questoes:
                line = line.strip()
                if not line: continue
                
                # .M1 -> Esquerda Negrito
                if line.startswith(".M"):
                    pdf.set_font("Helvetica", 'B', 12)
                    pdf.cell(190, 10, line[1:], ln=True, align='L')
                    l_idx = 0
                # t. -> Centro Negrito
                elif line.lower().startswith("t."):
                    pdf.set_font("Helvetica", 'B', 14)
                    pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
                    l_idx = 0
                # 6. -> Esquerda Normal
                elif re.match(r'^\d+\.', line):
                    pdf.set_font("Helvetica", size=12)
                    pdf.cell(190, 10, line, ln=True, align='L')
                    l_idx = 0
                # Itens -> Letras a), b), c)
                else:
                    pdf.set_font("Helvetica", size=12)
                    col = l_idx % n_cols
                    pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line.lstrip('. ')}", align='L', ln=(col == n_cols-1))
                    l_idx += 1
            
            if incluir_gabarito:
                pdf.add_page()
                pdf.set_font("Helvetica", 'B', 16)
                pdf.cell(190, 10, "GABARITO", ln=True, align='C')

            return pdf.output(dest='S').encode('latin-1')
        except: return b""

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")
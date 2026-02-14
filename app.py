import streamlit as st
import random
import re
import os
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E PERSISTÊNCIA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de estados
for key in ['perfil', 'sub_menu', 'preview_questoes']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else None if key == 'perfil' else ""

# --- 2. LOGIN (Proteção TOML inclusa) ---
def validar_acesso(pin):
    try:
        p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        p_prof = str(st.secrets.get("chave_mestra", "admin123")).strip().lower()
    except Exception:
        # Fallback caso o secrets.toml esteja mal formatado
        p_aluno, p_prof = "123456", "admin123"
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
            st.error("PIN Incorreto ou Erro no Formato dos Segredos.")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 Painel {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Exibir Cabeçalho (PNG)", value=True)
recuo_cabecalho = st.sidebar.slider("Altura após cabeçalho:", 10, 100, 45)
layout_cols = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.rerun()

if st.sidebar.button("🚪 Sair"):
    st.session_state.clear()
    st.rerun()

# --- 4. CENTRO DE COMANDO ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5 = st.columns(5)
btns = [("🔢 Operações", "op"), ("📐 Equações", "eq"), ("⛓️ Sistemas", "sis"), ("⚖️ Álgebra", "alg"), ("📄 Manual", "man")]
for i, (nome, tag) in enumerate(btns):
    if [g1, g2, g3, g4, g5][i].button(nome, use_container_width=True):
        st.session_state.sub_menu = tag

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS GERADORES ---
if menu == "op":
    tipo = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Lista"):
        simb = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
        qs = [f"{random.randint(10, 999)} {simb} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [f"t. Atividade de {tipo}", ".M Resolva com atenção:", "1. Calcule:"] + qs

elif menu == "man":
    txt = st.text_area("Editor (t. Título | .M Info):", height=200, placeholder="Ex: t. Minha Atividade\n.M Leia as regras\nQuestão 1")
    if st.button("Lançar no Preview"):
        st.session_state.preview_questoes = txt.split("\n")

# --- 6. MOTOR PDF (REVISADO) ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview do Documento")
    with st.container(border=True):
        for line in st.session_state.preview_questoes:
            if line.strip(): st.write(line)

    def gerar_pdf():
        try:
            pdf = FPDF()
            pdf.add_page()
            y = 10
            if usar_cabecalho and os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", 10, 10, 190)
                y = recuo_cabecalho
            
            pdf.set_y(y)
            letras = "abcdefghijklmnopqrstuvwxyz"
            l_idx = 0
            cols_count = int(layout_cols)
            larg_col = 190 / cols_count

            for line in st.session_state.preview_questoes:
                # Resolve problemas de encoding (caracteres especiais)
                clean_line = line.strip().encode('latin-1', 'replace').decode('latin-1')
                if not clean_line: continue

                if clean_line.lower().startswith("t."):
                    pdf.ln(5); pdf.set_font("Helvetica", 'B', 16)
                    pdf.cell(190, 10, clean_line[2:].strip(), ln=True, align='C'); pdf.ln(5)
                
                elif clean_line.startswith(".M"):
                    pdf.set_font("Helvetica", 'I', 11)
                    pdf.multi_cell(190, 7, clean_line[2:].strip()); pdf.ln(2)

                elif re.match(r'^\d+\.', clean_line):
                    pdf.ln(4); pdf.set_font("Helvetica", 'B', 12)
                    pdf.cell(190, 9, clean_line, ln=True); l_idx = 0
                
                else:
                    pdf.set_font("Helvetica", size=11)
                    if cols_count > 1 and menu != "man":
                        col_atual = l_idx % cols_count
                        pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {clean_line}", ln=(col_atual == cols_count - 1))
                        l_idx += 1
                    else:
                        pdf.multi_cell(190, 7, clean_line)
            
            return bytes(pdf.output())
        except Exception as e:
            return f"Erro: {str(e)}"

    pdf_data = gerar_pdf()
    if isinstance(pdf_data, bytes):
        st.download_button("📥 Baixar PDF", data=pdf_data, file_name="atividade.pdf", mime="application/pdf")
    else:
        st.error(pdf_data)

# --- 7. ESPAÇO PARA AUTOMAÇÃO (Take Profit) ---
st.divider()
st.subheader("🤖 Automação Quantum (Take Profit)")
tp_ativo = st.toggle("Ativar Monitoramento Infinito")
if tp_ativo:
    st.info("O sistema está pronto para monitorar preços em tempo real.")


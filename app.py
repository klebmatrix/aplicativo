import streamlit as st
import random
import os
from fpdf import FPDF

# =====================================================
# CONFIG INICIAL
# =====================================================

st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if "perfil" not in st.session_state:
    st.session_state.perfil = ""

if "questoes" not in st.session_state:
    st.session_state.questoes = []

if "gabarito" not in st.session_state:
    st.session_state.gabarito = []


# =====================================================
# LOGIN SIMPLES
# aluno = 123
# admin = admin
# =====================================================

def validar_login(pin):
    if pin == "123":
        return "aluno"
    if pin == "admin":
        return "admin"
    return None


if not st.session_state.perfil:

    st.title("🔐 Login Quantum")

    pin = st.text_input("PIN", type="password")

    if st.button("Entrar"):
        perfil = validar_login(pin)

        if perfil:
            st.session_state.perfil = perfil
            st.rerun()
        else:
            st.error("PIN incorreto")

    st.stop()


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title(f"👤 {st.session_state.perfil.upper()}")

if st.sidebar.button("🚪 Sair"):
    st.session_state.clear()
    st.rerun()

st.sidebar.divider()

usar_logo = st.sidebar.checkbox("Logo no PDF", True)
mostrar_campos = st.sidebar.checkbox("Nome / Turma / Data", True)
espaco_resposta = st.sidebar.checkbox("Espaço para resposta", True)
mostrar_gabarito = st.sidebar.checkbox("Gerar PDF Professor", True)
colunas = st.sidebar.selectbox("Colunas PDF", [1, 2, 3], 1)


# =====================================================
# FUNÇÕES
# =====================================================

def limpar_txt(txt):
    return txt.encode("latin-1", "ignore").decode("latin-1")


# -----------------------------------------------------
# GERADOR DE OPERAÇÕES + GABARITO
# -----------------------------------------------------

def gerar_operacoes():

    questoes = []
    respostas = []

    for _ in range(12):

        a = random.randint(100, 999)
        b = random.randint(100, 999)

        questoes.append(f"{a} + {b} =")
        respostas.append(a + b)

    return questoes, respostas


# -----------------------------------------------------
# EXPORTAR PDF
# -----------------------------------------------------

def export_pdf(questoes, respostas=None):

    pdf = FPDF("P", "mm", "A4")
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()

    margem = 15
    largura = 210 - (margem * 2)
    pdf.set_left_margin(margem)

    # LOGO
    if usar_logo and os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", margem, 10, largura)
        pdf.ln(40)

    # CAMPOS
    if mostrar_campos:
        pdf.set_font("Helvetica", size=12)
        pdf.cell(largura/2, 8, "Nome: __________________________")
        pdf.cell(largura/4, 8, "Turma: ____")
        pdf.cell(largura/4, 8, "Data: ____/____/____", ln=True)
        pdf.ln(8)

    letras = "abcdefghijklmnopqrstuvwxyz"
    largura_col = largura / colunas
    idx = 0

    for i, q in enumerate(questoes):

        texto = f"{letras[idx%26]}) {q}"

        if espaco_resposta and respostas is None:
            texto += " ________"

        if respostas:
            texto += f"   ({respostas[i]})"

        pdf.set_font("Helvetica", size=12)
        pdf.cell(largura_col, 8, limpar_txt(texto),
                 ln=(idx % colunas == colunas - 1))

        idx += 1

    return bytes(pdf.output())


# =====================================================
# INTERFACE
# =====================================================

st.title("🛠️ Quantum Math Lab")

if st.button("🔢 Gerar Operações de Soma"):

    q, g = gerar_operacoes()

    st.session_state.questoes = q
    st.session_state.gabarito = g


# =====================================================
# PREVIEW + DOWNLOAD
# =====================================================

if st.session_state.questoes:

    st.subheader("👁️ Preview")

    for q in st.session_state.questoes:
        st.write(q)

    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "📥 PDF Aluno",
            export_pdf(st.session_state.questoes),
            "atividade_aluno.pdf"
        )

    if mostrar_gabarito:
        with c2:
            st.download_button(
                "🧠 PDF Professor",
                export_pdf(
                    st.session_state.questoes,
                    st.session_state.gabarito
                ),
                "atividade_gabarito.pdf"
            )

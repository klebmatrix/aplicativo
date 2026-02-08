import streamlit as st
import random
import re
import os
import math
import ast
import operator as op
from fpdf import FPDF

# ======================================================
# CONFIG GERAL
# ======================================================

st.set_page_config(page_title="Quantum Math Lab", layout="wide")

defaults = {
    "perfil": "",
    "menu": "",
    "preview": []
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ======================================================
# CALCULADORA SEGURA (sem eval)
# ======================================================

OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

def safe_eval(expr):
    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return OPS[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return OPS[type(node.op)](_eval(node.operand))
        else:
            raise TypeError("Expressão inválida")
    return _eval(ast.parse(expr, mode="eval").body)


# ======================================================
# LOGIN
# ======================================================

def validar(pin):
    aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    prof = str(st.secrets.get("chave_mestra", "admin")).strip().lower()

    if pin == prof:
        return "admin"
    if pin == aluno:
        return "aluno"
    return None


if not st.session_state.perfil:
    st.title("🔐 Login Quantum")

    pin = st.text_input("PIN", type="password")

    if st.button("Entrar"):
        perfil = validar(pin)
        if perfil:
            st.session_state.perfil = perfil
            st.rerun()
        else:
            st.error("PIN incorreto")

    st.stop()


# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")

if st.sidebar.button("🚪 Sair", use_container_width=True):
    st.session_state.clear()
    st.rerun()

if st.sidebar.button("🧹 Limpar atividade", use_container_width=True):
    st.session_state.preview = []
    st.session_state.menu = ""
    st.rerun()

st.sidebar.divider()

usar_cabecalho = st.sidebar.checkbox("Cabeçalho escolar no PDF", True)
layout_cols = st.sidebar.selectbox("Colunas PDF", [1, 2, 3], 1)


# ======================================================
# GERADORES DE QUESTÕES
# ======================================================

def gerar_operacoes(tipo):
    if tipo == "Soma":
        return [f"{random.randint(100,999)} + {random.randint(100,999)} =" for _ in range(12)]

    if tipo == "Subtração":
        return [f"{random.randint(500,999)} - {random.randint(10,499)} =" for _ in range(12)]

    if tipo == "Multiplicação":
        return [f"{random.randint(10,99)} x {random.randint(2,9)} =" for _ in range(12)]

    return [f"{random.randint(10,50)*d} ÷ {d} =" for d in [random.randint(2,9) for _ in range(12)]]


def gerar_equacoes(grau):
    if grau == "1º Grau":
        return [f"{random.randint(2,10)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(8)]
    return [f"x² - {random.randint(2,12)}x + {random.randint(1,20)} = 0" for _ in range(5)]


def gerar_rad(tipo):
    if tipo == "Quadrada":
        return [f"√{random.randint(2,15)**2} =" for _ in range(10)]
    return [f"³√{random.randint(2,10)**3} =" for _ in range(10)]


# ======================================================
# PDF PROFISSIONAL A4
# ======================================================

def export_pdf(questoes, usar_cabecalho, cols):

    pdf = FPDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    margem = 15
    largura = 210 - (margem * 2)

    pdf.set_left_margin(margem)
    pdf.set_right_margin(margem)

    # ---------- Cabeçalho ----------
    pdf.set_font("Helvetica", size=11)

    if usar_cabecalho and os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", margem, 10, largura)
        pdf.ln(40)

    pdf.cell(largura/2, 8, "Nome: _________________________________")
    pdf.cell(largura/4, 8, "Turma: ______")
    pdf.cell(largura/4, 8, "Data: ____/____/______", ln=True)

    pdf.ln(10)

    letras = "abcdefghijklmnopqrstuvwxyz"
    largura_col = largura / cols
    idx = 0

    for line in questoes:

        line = line.strip()
        if not line:
            continue

        line = line.replace("√", "Raiz de ").replace("³√", "Raiz cubica de ")

        # quebra manual
        if line.startswith("---"):
            pdf.add_page()
            idx = 0
            continue

        elif line.startswith(".."):
            pdf.multi_cell(0, 8, line[2:])
            idx = 0

        elif line.startswith(".M"):
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 6, line[1:])
            idx = 0

        elif line.lower().startswith("t."):
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, line[2:], ln=True, align="C")
            idx = 0

        elif re.match(r'^\d+\.', line):
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, line, ln=True)
            idx = 0

        else:
            pdf.set_font("Helvetica", size=12)
            txt = f"{letras[idx%26]}) {line}"
            txt = txt.encode("latin-1", "ignore").decode("latin-1")

            pdf.cell(largura_col, 8, txt, ln=(idx % cols == cols-1))
            idx += 1

    return bytes(pdf.output())


# ======================================================
# INTERFACE PRINCIPAL
# ======================================================

st.title("🛠️ Centro de Comando Quantum")

c1, c2, c3, c4 = st.columns(4)

if c1.button("🔢 Operações"):
    st.session_state.menu = "op"

if c2.button("📐 Equações"):
    st.session_state.menu = "eq"

if c3.button("🎓 Radiciação"):
    st.session_state.menu = "rad"

if c4.button("✍️ Manual"):
    st.session_state.menu = "manual"


menu = st.session_state.menu


# ======================================================
# TELAS
# ======================================================

if menu == "op":
    tipo = st.radio("Operação", ["Soma", "Subtração", "Multiplicação", "Divisão"])
    if st.button("Gerar"):
        qs = gerar_operacoes(tipo)
        st.session_state.preview = [".M1", f"t. {tipo}", "1. Calcule:"] + qs


elif menu == "eq":
    grau = st.radio("Grau", ["1º Grau", "2º Grau"])
    if st.button("Gerar"):
        qs = gerar_equacoes(grau)
        st.session_state.preview = [".M1", f"t. Equações {grau}", "1. Resolva:"] + qs


elif menu == "rad":
    tipo = st.radio("Tipo", ["Quadrada", "Cúbica"])
    if st.button("Gerar"):
        qs = gerar_rad(tipo)
        st.session_state.preview = [".M1", f"t. Radiciação {tipo}", "1. Calcule:"] + qs


elif menu == "manual":
    txt = st.text_area("Digite uma linha por vez\nUse '..' para texto livre\nUse '---' para nova página")
    if st.button("Aplicar"):
        st.session_state.preview = txt.split("\n")


# ======================================================
# PREVIEW + DOWNLOAD
# ======================================================

if st.session_state.preview:
    st.divider()
    st.subheader("👁️ Preview")

    for l in st.session_state.preview:
        st.write(l)

    pdf = export_pdf(st.session_state.preview, usar_cabecalho, layout_cols)

    st.download_button(
        "📥 Baixar PDF A4",
        pdf,
        "atividade.pdf",
        "application/pdf"
    )

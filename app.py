import streamlit as st
import random
import re
import os
import ast
import operator as op
from fpdf import FPDF

# ======================================================
# CONFIG
# ======================================================

st.set_page_config(page_title="Quantum Math Lab", layout="wide")

DEFAULTS = {
    "perfil": "",
    "menu": "",
    "preview": []
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ======================================================
# UTIL
# ======================================================

def limpar_txt(t: str) -> str:
    """Remove unicode que quebra o FPDF."""
    return t.encode("latin-1", "ignore").decode("latin-1")


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
    aluno = str(st.secrets.get("acesso_aluno", "123456"))
    prof = str(st.secrets.get("chave_mestra", "admin"))
    if pin == prof:
        return "admin"
    if pin == aluno:
        return "aluno"
    return None


if not st.session_state.perfil:
    st.title("🔐 Login Quantum")
    pin = st.text_input("PIN", type="password")

    if st.button("Entrar"):
        p = validar(pin)
        if p:
            st.session_state.perfil = p
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

usar_logo = st.sidebar.checkbox("Logo no PDF", True)
mostrar_campos = st.sidebar.checkbox("Nome / Turma / Data", True)
layout_cols = st.sidebar.selectbox("Colunas PDF", [1, 2, 3], 1)


# ======================================================
# GERADORES
# ======================================================

def gerar_ops(tipo):
    if tipo == "Soma":
        return [f"{random.randint(100,999)} + {random.randint(100,999)} =" for _ in range(12)]
    if tipo == "Subtração":
        return [f"{random.randint(500,999)} - {random.randint(10,499)} =" for _ in range(12)]
    if tipo == "Multiplicação":
        return [f"{random.randint(10,99)} x {random.randint(2,9)} =" for _ in range(12)]
    return [f"{random.randint(10,50)*d} ÷ {d} =" for d in [random.randint(2,9) for _ in range(12)]]


def gerar_eq(grau):
    if grau == "1º Grau":
        return [f"{random.randint(2,10)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(8)]
    return [f"x² - {random.randint(2,12)}x + {random.randint(1,20)} = 0" for _ in range(5)]


def gerar_rad(tipo):
    if tipo == "Quadrada":
        return [f"√{random.randint(2,15)**2} =" for _ in range(10)]
    return [f"³√{random.randint(2,10)**3} =" for _ in range(10)]


# ======================================================
# PDF PROFISSIONAL
# ======================================================

def export_pdf(questoes, usar_logo, mostrar_campos, cols):

    pdf = FPDF("P", "mm", "A4")
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()

    margem = 15
    largura = 210 - (margem * 2)

    pdf.set_left_margin(margem)
    pdf.set_right_margin(margem)
    pdf.set_font("Helvetica", size=11)

    # ---------- LOGO ----------
    if usar_logo and os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", margem, 10, largura)
        pdf.ln(40)

    # ---------- CAMPOS OPCIONAIS ----------
    if mostrar_campos:
        pdf.cell(largura/2, 8, "Nome: __________________________")
        pdf.cell(largura/4, 8, "Turma: ____")
        pdf.cell(largura/4, 8, "Data: ____/____/____", ln=True)
        pdf.ln(8)

    letras = "abcdefghijklmnopqrstuvwxyz"
    col_w = largura / cols
    idx = 0

    for line in questoes:

        line = line.strip()
        if not line:
            continue

        line = (
            line.replace("√", "Raiz de ")
                .replace("³√", "Raiz cubica de ")
        )

        if line.startswith("---"):
            pdf.add_page()
            idx = 0
            continue

        elif line.startswith(".."):
            pdf.multi_cell(largura, 8, limpar_txt(line[2:]))
            idx = 0

        elif line.lower().startswith("t."):
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, limpar_txt(line[2:]), ln=True, align="C")
            idx = 0

        elif re.match(r'^\d+\.', line):
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, limpar_txt(line), ln=True)
            idx = 0

        else:
            pdf.set_font("Helvetica", size=12)
            txt = limpar_txt(f"{letras[idx%26]}) {line}")
            pdf.cell(col_w, 8, txt, ln=(idx % cols == cols-1))
            idx += 1

    return bytes(pdf.output())


# ======================================================
# INTERFACE
# ======================================================

st.title("🛠️ Centro de Comando Quantum")

c1, c2, c3, c4 = st.columns(4)

if c1.button("🔢 Operações"): st.session_state.menu = "op"
if c2.button("📐 Equações"): st.session_state.menu = "eq"
if c3.button("🎓 Radiciação"): st.session_state.menu = "rad"
if c4.button("✍️ Manual"): st.session_state.menu = "manual"


menu = st.session_state.menu


# ======================================================
# TELAS
# ======================================================

if menu == "op":
    t = st.radio("Operação", ["Soma","Subtração","Multiplicação","Divisão"])
    if st.button("Gerar"):
        st.session_state.preview = ["t. Operações", "1. Calcule:"] + gerar_ops(t)

elif menu == "eq":
    g = st.radio("Grau", ["1º Grau","2º Grau"])
    if st.button("Gerar"):
        st.session_state.preview = ["t. Equações", "1. Resolva:"] + gerar_eq(g)

elif menu == "rad":
    r = st.radio("Tipo", ["Quadrada","Cúbica"])
    if st.button("Gerar"):
        st.session_state.preview = ["t. Radiciação", "1. Calcule:"] + gerar_rad(r)

elif menu == "manual":
    txt = st.text_area("Use '..' texto livre | '---' nova página")
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

    pdf_bytes = export_pdf(
        st.session_state.preview,
        usar_logo,
        mostrar_campos,
        layout_cols
    )

    st.download_button(
        "📥 Baixar PDF A4",
        pdf_bytes,
        "atividade.pdf",
        "application/pdf"
    )

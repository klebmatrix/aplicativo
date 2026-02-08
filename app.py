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

for k, v in {
    "perfil": "",
    "menu": "",
    "preview": [],
    "gabarito": []
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ======================================================
# UTIL
# ======================================================

def limpar_txt(t):
    return t.encode("latin-1", "ignore").decode("latin-1")


# ======================================================
# RESOLVER EXPRESSÕES (gabarito automático)
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
            raise TypeError
    return _eval(ast.parse(expr, mode="eval").body)


def resolver(expr):
    try:
        expr = expr.replace("x","*").replace("÷","/").replace("=","")
        return round(safe_eval(expr), 2)
    except:
        return "?"


# ======================================================
# GERADORES COM GABARITO
# ======================================================

def gerar_ops(tipo):
    qs, ans = [], []
    for _ in range(12):
        if tipo == "Soma":
            a,b = random.randint(100,999), random.randint(100,999)
            qs.append(f"{a} + {b} =")
            ans.append(a+b)

        elif tipo == "Subtração":
            a,b = random.randint(500,999), random.randint(10,499)
            qs.append(f"{a} - {b} =")
            ans.append(a-b)

        elif tipo == "Multiplicação":
            a,b = random.randint(10,99), random.randint(2,9)
            qs.append(f"{a} x {b} =")
            ans.append(a*b)

        else:
            d = random.randint(2,9)
            a = random.randint(10,50)*d
            qs.append(f"{a} ÷ {d} =")
            ans.append(a//d)

    return qs, ans


# ======================================================
# LOGIN
# ======================================================

if not st.session_state.perfil:
    st.title("🔐 Login Quantum")
    pin = st.text_input("PIN", type="password")

    if st.button("Entrar"):
        if pin == st.secrets.get("chave_mestra","admin"):
            st.session_state.perfil="admin"
            st.rerun()
        elif pin == st.secrets.get("acesso_aluno","123456"):
            st.session_state.perfil="aluno"
            st.rerun()
        else:
            st.error("PIN incorreto")

    st.stop()


# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.title("⚙️ PDF")

usar_logo = st.sidebar.checkbox("Logo", True)
mostrar_campos = st.sidebar.checkbox("Nome/Turma/Data", True)
mostrar_gabarito = st.sidebar._

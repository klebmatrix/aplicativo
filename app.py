import streamlit as st
import random
import os
import math
from fpdf import FPDF
from io import BytesIO

1. CONFIGURAÇÃO
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""

2. LOGIN
if not st.session_state.autenticado:
st.title("🔐 Quantum Suite - Acesso")
chave = str(st.secrets.get("chave_mestra", "admin")).strip().lower()
pin = st.text_input("Chave Mestra:", type="password")
if st.button("DESBLOQUEAR"):
if pin.lower() == chave:
st.session_state.autenticado = True
st.rerun()
else: st.error("Chave Inválida.")
st.stop()

3. SIDEBAR (TAKE PROFIT ATIVO)
st.sidebar.title("🚀 QUANTUM SUITE")
menu = st.sidebar.selectbox("FERRAMENTA:", ["🔢 Operações", "📐 Equações", "🎓 Colegial (Rad/Pot/%)", "Bhaskara", "💰 Financeira (Take Profit)", "📄 Manual"])
st.sidebar.divider()
st.sidebar.success("✅ Take Profit: INFINITO ATIVO")
st.sidebar.divider()
usar_cabecalho = st.sidebar.checkbox("Usar cabeçalho.png", value=False)
layout_cols = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 LIMPAR TUDO"):
st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()

4. FUNÇÃO PDF (ESTILO: TÍTULO NEGRITO 14 CENTRALIZADO)
def gerar_pdf_bytes():
pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=10)
y_pos = 45 if usar_cabecalho else 15
if usar_cabecalho and os.path.exists("cabecalho.png"):
pdf.image("cabecalho.png", 10, 10, 190)
pdf.set_y(y_pos)
larg_col = 190 / layout_cols
l_idx = 0
letras = "abcdefghijklmnopqrstuvwxyz"
for line in st.session_state.preview_questoes:
clean = line.strip().replace('x2', 'x²').replace('v2', '√').replace('v3', '³√')
try: clean = clean.encode('latin-1', 'replace').decode('latin-1')
except: pass
if clean.startswith("t."):
pdf.ln(5)
pdf.set_font("Arial", 'B', 14)
pdf.cell(190, 10, clean[2:].strip(), ln=True, align='C')
l_idx = 0
elif clean.startswith("txt."):
pdf.ln(2)
pdf.set_font("Arial", size=10)
pdf.cell(190, 7, clean[4:].strip(), ln=True, align='L')
else:
pdf.set_font("Arial", size=10)
col_at = l_idx % layout_cols
txt_quest = f"{letras[l_idx % 26]}) {clean}"
pdf.cell(larg_col, 7, txt_quest, ln=(col_at == layout_cols - 1))
l_idx += 1
pdf_out = pdf.output(dest='S')
buffer = BytesIO()
buffer.write(pdf_out.encode('latin-1') if isinstance(pdf_out, str) else pdf_out)
buffer.seek(0)
return buffer

5. FERRAMENTAS (COLEGIAL INTEGRADO)
st.title(f"🛠️ {menu}")
if menu == "🎓 Colegial (Rad/Pot/%)":
sub = st.radio("Tema:", ["Potenciação", "Radiciação", "Porcentagem"], horizontal=True)
if st.button("GERAR"):
if sub == "Potenciação":
qs = [f"{random.randint(2,12)}x2 =" for _ in range(12)]
st.session_state.preview_questoes = ["t. Exercícios de Potenciação", "txt. 1. Calcule:"] + qs
elif sub == "Radiciação":
bs = [4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144]
qs = [f"v2({random.choice(bs)}) =" for _ in range(12)]
st.session_state.preview_questoes = ["t. Exercícios de Radiciação", "txt. 1. Calcule a raiz:"] + qs
else:
qs = [f"{random.randint(5,50)}% de {random.randint(100,1000)} =" for _ in range(12)]
st.session_state.preview_questoes = ["t. Exercícios de Porcentagem", "txt. 1. Calcule:"] + qs
elif menu == "🔢 Operações":
tipo = st.radio("Tipo:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
if st.button("GERAR"):
s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
st.session_state.preview_questoes = [f"t. Lista de {tipo}", "txt. Resolva:"] + [f"{random.randint(10,99)} {s} {random.randint(1,99)} =" for _ in range(12)]
elif menu == "💰 Financeira (Take Profit)":
v1 = st.number_input("Entrada:", value=100.0)
p = st.number_input("Alvo %:", value=10.0)
if st.button("CALCULAR"):
st.session_state.res_calc = f"Take Profit Ativo: R$ {v1*(1+p/100):.2f}"
elif menu == "📄 Manual":
txt = st.text_area("Comandos: t. (título) | txt. (instrução)", height=150)
if st.button("LANÇAR"): st.session_state.preview_questoes = txt.split("\n")

6. DOWNLOAD
if st.session_state.res_calc: st.info(st.session_state.res_calc)
if st.session_state.preview_questoes:
st.divider()
try:
buf = gerar_pdf_bytes()
st.download_button("📥 BAIXAR PDF", buf, "quantum.pdf", "application/pdf")
except Exception as e: st.error(f"Erro: {e}")

import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

for key in ['perfil', 'sub_menu', 'preview_questoes']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else None

# --- 2. FUNÇÃO DO CABEÇALHO ---
def preparar_cabecalho(escola, materia, prof):
    try:
        img = Image.new('RGB', (800, 200), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([5, 5, 795, 195], outline="black", width=2)
        try: font = ImageFont.truetype("Arial.ttf", 20)
        except: font = ImageFont.load_default()
        
        draw.text((30, 30), f"ESCOLA: {escola.upper()}", fill="black", font=font)
        draw.text((30, 80), f"DISCIPLINA: {materia.upper()}", fill="black", font=font)
        draw.text((450, 80), f"PROF: {prof.upper()}", fill="black", font=font)
        draw.text((30, 130), "ALUNO(A): ________________________________________________", fill="black", font=font)
        
        img.save("cabecalho_pronto.png")
        return "cabecalho_pronto.png"
    except: return None

# --- 3. LOGIN ---
def validar_acesso(pin):
    if pin == str(st.secrets.get("chave_mestra", "chave_mestra")).lower(): return "admin"
    if pin == str(st.secrets.get("acesso_aluno", "123456")): return "aluno"
    return None

if st.session_state.perfil is None:
    st.title("🔐 Login Quantum")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin_input)
        if res:
            st.session_state.perfil = res
            st.rerun()
        else: st.error("PIN Incorreto")
    st.stop()

# --- 4. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Cabeçalho no Topo", value=True)
txt_escola = st.sidebar.text_input("Escola:", "Republ")
txt_materia = st.sidebar.text_input("Matéria:", "Matemática")
txt_prof = st.sidebar.text_input("Professor:", "KLEBER")
layout_cols = st.sidebar.selectbox("Colunas:", [1, 2, 3], index=2)

if st.sidebar.button("🧹 Limpar Tudo", use_container_width=True):
    st.session_state.preview_questoes = []; st.session_state.sub_menu = None; st.rerun()

if st.sidebar.button("🚪 Sair", use_container_width=True):
    st.session_state.clear(); st.rerun()

# --- 5. PAINEL DE COMANDO (8 BOTÕES) ---
st.title("🛠️ Centro de Comando")
g1, g2, g3, g4, g5 = st.columns(5)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- LÓGICA DE GERAÇÃO REAL ---
if menu == "op":
    n = st.number_input("Início:", value=6)
    if st.button("Gerar"):
        ops = [f"{random.randint(10,99)} {random.choice(['+', '-', 'x'])} {random.randint(1,50)} =" for _ in range(15)]
        st.session_state.preview_questoes = [".M1", f"t. ATIVIDADE DE {txt_materia.upper()}", f"{n}. Resolva as operações:"] + ops
        st.rerun()

elif menu == "eq":
    n = st.number_input("Início:", value=6)
    if st.button("Gerar Equações"):
        eqs = [f"{random.randint(2,9)}x {'+' if random.random()>0.5 else '-'} {random.randint(1,20)} = {random.randint(21,60)}" for _ in range(10)]
        st.session_state.preview_questoes = [".M1", "t. EQUAÇÕES DE 1º GRAU", f"{n}. Determine o valor de x:"] + eqs
        st.rerun()

elif menu == "col":
    n = st.number_input("Início:", value=6)
    if st.button("Gerar Potenciação"):
        pots = [f"{random.randint(2,12)}^{random.randint(2,3)} =" for _ in range(10)]
        st.session_state.preview_questoes = [".M1", "t. POTENCIAÇÃO", f"{n}. Calcule as potências:"] + pots
        st.rerun()

elif menu == "alg":
    n = st.number_input("Início:", value=6)
    if st.button("Gerar Prod. Notáveis"):
        prods = [f"({random.randint(1,5)}x + {random.randint(1,5)})^2 =" for _ in range(6)]
        st.session_state.preview_questoes = [".M1", "t. PRODUTOS NOTÁVEIS", f"{n}. Desenvolva:"] + prods
        st.rerun()

elif menu == "man":
    txt = st.text_area("Texto Manual:")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n"); st.rerun()

elif menu == "calc_f":
    a = st.number_input("Valor de a:", value=1.0)
    b = st.number_input("Valor de b:", value=-3.0)
    c = st.number_input("Valor de c:", value=2.0)
    if st.button("Calcular Raízes"):
        delta = b**2 - 4*a*c
        if delta < 0: st.error("Não possui raízes reais.")
        else:
            x1 = (-b + math.sqrt(delta))/(2*a)
            x2 = (-b - math.sqrt(delta))/(2*a)
            st.success(f"Raízes: x1={x1}, x2={x2}")

elif menu == "pemdas":
    exp = st.text_input("Expressão:", "2 + 5 * 3 - (10 / 2)")
    if st.button("Resolver"): st.write(f"Resultado: {eval(exp)}")

elif menu == "fin":
    p = st.number_input("Capital (P):", value=1000.0)
    i = st.number_input("Taxa % (i):", value=2.0)
    t = st.number_input("Tempo meses (t):", value=12)
    if st.button("Juros Simples"): st.write(f"Juros: R$ {p * (i/100) * t:.2f}")

# --- 6. MOTOR PDF ---
if st.session_state.preview_questoes:
    st.divider()
    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        y = 5
        if usar_cabecalho:
            img = preparar_cabecalho(txt_escola, txt_materia, txt_prof)
            pdf.image(img, 10, 5, 190); y = 65
        pdf.set_y(y)
        letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
        n_cols = int(layout_cols)
        larg_col = 190 / n_cols
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            if line.startswith(".M"):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line[1:], ln=True)
            elif line.lower().startswith("t."):
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:].strip().upper(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                pdf.set_font("Helvetica", size=12)
                col = l_idx % n_cols
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line.lstrip('. ')}", ln=(col == n_cols-1))
                l_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")
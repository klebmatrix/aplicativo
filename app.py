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

# --- 2. FUNÇÃO PARA USAR SUA IMAGEM (cabecalho.png) ---
def preparar_cabecalho(escola, materia, prof):
    try:
        # Tenta abrir a sua imagem na pasta
        if os.path.exists("cabecalho.png"):
            img = Image.open("cabecalho.png").convert("RGB")
        else:
            # Caso a imagem suma, ele cria um fundo branco para não travar
            img = Image.new('RGB', (800, 200), color='white')
            
        draw = ImageDraw.Draw(img)
        try: 
            font = ImageFont.truetype("Arial.ttf", 20)
        except: 
            font = ImageFont.load_default()
        
        # ESCREVENDO POR CIMA DA SUA IMAGEM
        # Ajuste os números (85, 25) se o texto precisar subir ou descer na sua imagem
        draw.text((85, 25), escola.upper(), fill="black", font=font)
        draw.text((85, 55), materia.upper(), fill="black", font=font)
        draw.text((450, 55), prof.upper(), fill="black", font=font)
        
        img.save("cabecalho_pronto.png")
        return "cabecalho_pronto.png"
    except Exception as e:
        return "cabecalho.png" # Se der erro, usa a imagem original sem texto

# --- 3. LOGIN ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin == p_aluno: return "aluno"
    if pin == p_prof: return "admin"
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

# --- 4. BARRA LATERAL (OPÇÕES) ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Mostrar Cabeçalho", value=True)
txt_escola = st.sidebar.text_input("Escola:", "Republ")
txt_materia = st.sidebar.text_input("Matéria:", "Matemática")
txt_prof = st.sidebar.text_input("Professor:", "KLEBER")
layout_cols = st.sidebar.selectbox("Colunas:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 Limpar Tudo", use_container_width=True):
    st.session_state.preview_questoes = []; st.session_state.sub_menu = None; st.rerun()

if st.sidebar.button("🚪 Sair", use_container_width=True):
    st.session_state.clear(); st.rerun()

# --- 5. PAINEL DE COMANDO (TODOS OS 8 BOTÕES) ---
st.title("🛠️ Centro de Comando")
g1, g2, g3, g4, g5 = st.columns(5)
if g1.button("🔢 Operações"): st.session_state.sub_menu = "op"
if g2.button("📐 Equações"): st.session_state.sub_menu = "eq"
if g3.button("📚 Colegial"): st.session_state.sub_menu = "col"
if g4.button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"
if g5.button("📄 Manual"): st.session_state.sub_menu = "man"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Funções"): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS"): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira"): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# LÓGICAS FUNCIONAIS
if menu == "op":
    n = st.number_input("Início:", value=6)
    if st.button("Gerar"):
        st.session_state.preview_questoes = [".M1", f"t. {txt_materia.upper()}", f"{n}. Resolva:"] + \
            [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(12)]
        st.rerun()

elif menu == "eq":
    n = st.number_input("Início:", value=6)
    if st.button("Gerar Equações"):
        st.session_state.preview_questoes = [".M1", "t. EQUAÇÕES", f"{n}. Resolva x:"] + \
            [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,80)}" for _ in range(10)]
        st.rerun()

elif menu == "col":
    n = st.number_input("Início:", value=6)
    if st.button("Gerar Potência"):
        st.session_state.preview_questoes = [".M1", "t. POTENCIAÇÃO", f"{n}. Calcule:"] + \
            [f"{random.randint(2,15)}^2 =" for _ in range(10)]
        st.rerun()

elif menu == "alg":
    n = st.number_input("Início:", value=6)
    if st.button("Gerar Álgebra"):
        st.session_state.preview_questoes = [".M1", "t. ÁLGEBRA", f"{n}. Desenvolva:"] + \
            ["(x+5)^2 =", "(x-3)^2 =", "(2x+1)^2 ="]
        st.rerun()

elif menu == "man":
    txt = st.text_area("Entrada Manual:")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n"); st.rerun()

elif menu == "calc_f":
    st.write("Calculadora de Raízes (ax² + bx + c)")
    a = st.number_input("a", value=1.0)
    b = st.number_input("b", value=-5.0)
    c = st.number_input("c", value=6.0)
    if st.button("Calcular"):
        delta = b**2 - 4*a*c
        if delta >= 0:
            st.success(f"x1 = {(-b + math.sqrt(delta))/(2*a)} | x2 = {(-b - math.sqrt(delta))/(2*a)}")

elif menu == "pemdas":
    exp = st.text_input("Expressão:", "2 + 3 * 4")
    if st.button("Resolver"): st.write(f"Resultado: {eval(exp)}")

elif menu == "fin":
    st.write("Juros Simples")
    cap = st.number_input("Capital", value=1000.0)
    if st.button("Calcular 10%"): st.write(f"Total: {cap * 1.1}")

# --- 6. MOTOR PDF (CENTRALIZADO NO TOPO) ---
if st.session_state.preview_questoes:
    st.divider()
    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        y_pos = 5
        if usar_cabecalho:
            img_p = preparar_cabecalho(txt_escola, txt_materia, txt_prof)
            pdf.image(img_p, 10, 5, 190)
            y_pos = 65
        
        pdf.set_y(y_pos)
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
                pdf.set_font("Helvetica", size=12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                pdf.set_font("Helvetica", size=12)
                col = l_idx % n_cols
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line.lstrip('. ')}", ln=(col == n_cols-1))
                l_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")
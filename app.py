import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES TÉCNICAS ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# Inicialização de Memória (Impede que as coisas sumam ao clicar)
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'menu_ativo' not in st.session_state: st.session_state.menu_ativo = "🔢 Operações"
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- 2. SISTEMA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Acesso Restrito")
    pin = st.text_input("Digite seu PIN:", type="password")
    if st.button("Liberar Sistema"):
        # Busca no Render/Secrets, se não achar usa o padrão
        s_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
        s_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        
        if pin == s_prof: st.session_state.perfil = "admin"
        elif pin == s_aluno: st.session_state.perfil = "aluno"
        else: st.error("PIN Inválido.")
        st.rerun()
    st.stop()

# --- 3. MENU LATERAL FIXO ---
st.sidebar.title(f"👤 {st.session_state.perfil.upper()}")
st.session_state.menu_ativo = st.sidebar.radio("Selecione um Módulo:", 
    ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual", "🧮 Calculadoras"])

if st.sidebar.button("🔴 Sair do Sistema"):
    st.session_state.perfil = None
    st.rerun()

# --- 4. LÓGICA DOS MÓDULOS ---
menu = st.session_state.menu_ativo

# Título do Módulo
st.title(f"Módulo: {menu}")

if menu == "🔢 Operações":
    ops = st.multiselect("Escolha as operações:", ["+", "-", "x", "÷"], ["+", "-"])
    qtd = st.slider("Quantidade de questões:", 5, 50, 10)
    if st.button("🎲 Gerar Novas Questões"):
        st.session_state.preview_questoes = [f"{random.randint(10,500)} {random.choice(ops)} {random.randint(2,50)} =" for _ in range(qtd)]

elif menu == "📐 Equações":
    grau = st.radio("Grau da Equação:", ["1º Grau", "2º Grau", "Misto"])
    if st.button("🎲 Gerar Equações"):
        qs = []
        for _ in range(10):
            escolha = grau if grau != "Misto" else random.choice(["1º Grau", "2º Grau"])
            if escolha == "1º Grau": qs.append(f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}")
            else: qs.append(f"x² + {random.randint(2,10)}x + {random.randint(1,16)} = 0")
        st.session_state.preview_questoes = qs

elif menu == "📚 Colegial":
    temas = st.multiselect("Tópicos:", ["Frações", "Potência", "Raiz", "Sistemas 2x2", "Funções"], ["Frações"])
    if st.button("🎲 Gerar Atividade Colegial"):
        qs = []
        for _ in range(12):
            t = random.choice(temas)
            if t == "Frações": qs.append(f"{random.randint(1,9)}/{random.randint(2,5)} {random.choice(['+', '-', 'x', '÷'])} {random.randint(1,9)}/{random.randint(2,5)} =")
            elif t == "Potência": qs.append(f"{random.randint(2,12)}^{random.randint(2,3)} =")
            elif t == "Raiz": qs.append(f"√{random.randint(2,12)**2} =")
            elif t == "Sistemas 2x2": 
                x, y = random.randint(1,5), random.randint(1,5)
                qs.append(f"Sistema: {{ x+y={x+y} | x-y={x-y} }}")
            else: qs.append(f"Domínio de f(x) = {random.randint(1,9)} / (x - {random.randint(1,20)})")
        st.session_state.preview_questoes = qs

elif menu == "⚖️ Álgebra Linear":
    ordem = st.selectbox("Ordem da Matriz:", ["2x2", "3x3"])
    if st.button("🎲 Gerar Matrizes"):
        size = 2 if ordem == "2x2" else 3
        st.session_state.preview_questoes = [f"Calcule o determinante da matriz {ordem}:\n{np.random.randint(1,10, (size,size))}" for _ in range(3)]

elif menu == "📄 Manual":
    txt_m = st.text_area("Digite sua atividade (. para colunas):", height=300)
    if st.button("🔍 Visualizar Conteúdo"):
        st.session_state.preview_questoes = txt_m.split('\n')

elif menu == "🧮 Calculadoras":
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📊 PEMDAS")
        exp = st.text_input("Expressão:", "2 + 3 * 4")
        if st.button("Calcular Expressão"): st.success(f"Resultado: {eval(exp)}")
    with c2:
        st.subheader("𝑓(x) Função")
        f_in = st.text_input("f(x):", "x**2")
        x_in = st.number_input("x:", 2)
        if st.button("Calcular f(x)"): st.metric("Resultado", eval(f_in.replace('x', str(x_in))))

# --- 5. ÁREA DE VISUALIZAÇÃO E PDF (Sempre no fim da página) ---
if st.session_state.preview_questoes and menu != "🧮 Calculadoras":
    st.divider()
    st.subheader("👀 Prévia da Atividade")
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    
    with st.container(border=True):
        for q in st.session_state.preview_questoes:
            if not q.strip(): continue
            # Regra de negrito para números no manual
            if menu == "📄 Manual" and re.match(r'^\d+', q):
                st.markdown(f"### {q}"); l_idx = 0
            else:
                st.write(f"**{letras[l_idx%26]})** {q.replace('.', '')}")
                l_idx += 1

    # GERAÇÃO DO PDF
    if st.button("📥 Gerar PDF para Download"):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10); l_idx = 0
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(f"Atividade - {menu}"), ln=True, align='C'); pdf.ln(5)
        
        for q in st.session_state.preview_questoes:
            if not q.strip(): continue
            match = re.match(r'^(\.+)', q); pts = len(match.group(1)) if match else 0
            if re.match(r'^\d+', q):
                pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(q)); pdf.set_font("Arial", size=10); l_idx = 0
            elif pts > 0: # Colunas
                if pts > 1: pdf.set_y(pdf.get_y() - 8)
                pdf.set_x(10 + (pts-1)*45); pdf.cell(45, 8, f"{letras[l_idx%26]}) {clean_txt(q[pts:].strip())}", ln=True); l_idx += 1
            else:
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(q)}"); l_idx += 1
        
        st.download_button("✅ Baixar Agora", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")
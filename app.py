import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
    except:
        senha_aluno, senha_prof = "123456", "12345678"
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 2. MENU E LOGOUT ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
if st.sidebar.button("Sair/Logout"):
    st.session_state.perfil = None
    st.session_state.sub_menu = None
    st.rerun()

# --- 3. FUNÇÃO PDF ---
def exportar_pdf(questoes, titulo):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", x=12.5, y=8, w=185)
        pdf.set_y(46)
    else: pdf.set_y(15)
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, txt=clean_txt(titulo), ln=True, align='C'); pdf.ln(5)
    pdf.set_font("Arial", size=11); letras = "abcdefghijklmnopqrstuvwxyz"
    for i, q in enumerate(questoes):
        pdf.multi_cell(0, 10, txt=f"{letras[i%26]}) {clean_txt(q)}")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. PAINEL PRINCIPAL (ADMIN) ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle do Professor")
    
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações\nBásicas", use_container_width=True): st.session_state.sub_menu = "op"
    with c2: 
        if st.button("📐 Equações\n1º e 2º Grau", use_container_width=True): st.session_state.sub_menu = "eq"
    with c3: 
        if st.button("📚 Colegial\nFrações/Funções", use_container_width=True): st.session_state.sub_menu = "col"
    with c4: 
        if st.button("⚖️ Álgebra\nLinear", use_container_width=True): st.session_state.sub_menu = "alg"
    with c5: 
        if st.button("📄 Gerador\nManual", use_container_width=True): st.session_state.sub_menu = "man"

    st.markdown("---")
    st.subheader("🧮 Ferramentas de Cálculo Online")
    d1, d2, d3 = st.columns(3)
    with d1: 
        if st.button("𝑓(x) Cálculo\nde Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 Expressões\n(PEMDAS)", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with d3: 
        if st.button("💰 Calculadora\nFinanceira", use_container_width=True): st.session_state.sub_menu = "fin"

    op_atual = st.session_state.sub_menu
    st.divider()

    # --- MÓDULOS DE GERADORES ---
    if op_atual == "op":
        st.header("🔢 Operações")
        escolhas = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
        qtd = st.number_input("Qtd:", 4, 30, 10)
        if st.button("Gerar PDF"):
            qs = [f"{random.randint(10,500)} {random.choice(escolhas)} {random.randint(2,50)} =" for _ in range(qtd)]
            st.download_button("Baixar", exportar_pdf(qs, "Operações"), "op.pdf")

    elif op_atual == "eq":
        st.header("📐 Equações")
        grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        if st.button("Gerar PDF"):
            qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" if grau == "1º Grau" else f"x² + {random.randint(2,8)}x + {random.randint(1,12)} = 0" for _ in range(8)]
            st.download_button("Baixar", exportar_pdf(qs, "Equações"), "eq.pdf")

    elif op_atual == "col":
        st.header("📚 Colegial (Frações e Funções)")
        tipo_col = st.selectbox("Escolha o tema:", ["Soma de Frações", "Simplificação", "Domínio de Funções"])
        if st.button("Gerar PDF Colegial"):
            if "Frações" in tipo_col:
                qs = [f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/{random.randint(2,5)} =" for _ in range(6)]
            else:
                qs = [f"Determine o domínio de f(x) = {random.randint(1,10)}/(x - {random.randint(1,20)})" for _ in range(5)]
            st.download_button("Baixar", exportar_pdf(qs, tipo_col), "colegial.pdf")

    elif op_atual == "alg":
        st.header("⚖️ Álgebra Linear (Matrizes)")
        ordem = st.selectbox("Ordem da Matriz:", ["2x2", "3x3"])
        if st.button("Gerar Matrizes"):
            qs = [f"Calcule o Determinante da Matriz {ordem}: \n {np.random.randint(1,10, size=(2,2) if ordem=='2x2' else (3,3))}" for _ in range(3)]
            st.download_button("Baixar", exportar_pdf(qs, f"Matrizes {ordem}"), "algebra.pdf")

    if aba == "📄 Manual":
    # Exemplo de como usar o título com t.
    txt_input = st.text_area("Digite sua atividade:", height=250, 
                             value="t. AVALIAÇÃO DE MATEMÁTICA\n1. Calcule as raízes:\na) ,V36\nb) ,V49\n2. Resolva o sistema:\na) { 2x+y=20 | x-y=5")
    if st.button("🔍 Gerar Atividade"):
        st.session_state.preview_questoes = txt_input.split('\n')

# --- 6. VISUALIZAÇÃO (PREVIEW) ---
if st.session_state.preview_questoes:
    st.divider()
    
    # CABEÇALHO (Sempre aparece no topo se o arquivo existir)
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)
    else:
        st.warning("⚠️ Arquivo 'cabecalho.png' não encontrado no servidor.")

    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0

    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        # RECONHECIMENTO DE TÍTULO (t. ou TÍTULO:)
        if line.lower().startswith("t.") or line.lower().startswith("titulo:"):
            titulo_limpo = line.replace("t.", "").replace("titulo:", "").replace("TITULO:", "").strip()
            st.markdown(f"<h1 style='text-align: center; color: #007bff;'>{titulo_limpo}</h1>", unsafe_allow_html=True)
            st.divider()
        
        # Questões Numeradas
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0
            
        # Itens em Cards
        else:
            with st.container(border=True):
                col1, col2 = st.columns([0.1, 0.9])
                with col1:
                    st.write(f"**{letras[l_idx%26]})**")
                with col2:
                    if "{" in line or "|" in line:
                        cont = line.replace("{", "").strip()
                        if "|" in cont:
                            partes = cont.split("|")
                            st.latex(r" \begin{cases} " + partes[0].strip() + r" \\ " + partes[1].strip() + r" \end{cases} ")
                        else: st.write(line)
                    else:
                        f = tratar_math(line)
                        if "\\" in f or "{" in f: st.latex(f)
                        else: st.write(line.replace(',', ''))
            l_idx += 1

    # --- 7. PDF ---
    if st.button("📥 Baixar PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho no PDF
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=8, w=190)
            pdf.set_y(50)
        else:
            pdf.set_y(20)
            
        pdf.set_font("Arial", size=12)
        l_idx = 0
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            # Título no PDF
            if line.lower().startswith("t.") or line.lower().startswith("titulo:"):
                titulo_limpo = line.replace("t.", "").replace("titulo:", "").replace("TITULO:", "").strip()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, clean_txt(titulo_limpo), ln=True, align='C')
                pdf.ln(5)
                pdf.set_font("Arial", size=12)
            
            elif re.match(r'^\d+', line):
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 12)
                pdf.multi_cell(0, 8, clean_txt(line))
                pdf.set_font("Arial", size=12)
                l_idx = 0
            
            elif "{" in line and "|" in line:
                partes = line.replace("{", "").split("|")
                pdf.cell(10, 10, f"{letras[l_idx%26]})")
                cx, cy = pdf.get_x(), pdf.get_y()
                pdf.set_font("Courier", size=18); pdf.text(cx, cy + 7, "{"); pdf.set_font("Arial", size=12)
                pdf.text(cx + 5, cy + 4, clean_txt(partes[0].strip()))
                pdf.text(cx + 5, cy + 9, clean_txt(partes[1].strip()))
                pdf.ln(15)
                l_idx += 1
            else:
                item = re.sub(r'^[a-z][\)\.]\s*', '', line).replace(',', '')
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(item)}")
                l_idx += 1
                
        st.download_button("✅ Download Final", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")
    # --- MÓDULOS DE CÁLCULO ---
    elif op_atual == "calc_f":
        st.header("𝑓(x) Calculadora")
        f = st.text_input("f(x):", "x**2")
        x = st.number_input("x:", value=1.0)
        if st.button("Calcular"):
            st.metric("Resultado", eval(f.replace('x', f'({x})')))

    elif op_atual == "pemdas":
        st.header("📊 PEMDAS")
        exp = st.text_input("Expressão:", "2 + 3 * 4")
        if st.button("Resolver"): st.success(f"Resultado: {eval(exp)}")

    elif op_atual == "fin":
        st.header("💰 Financeira")
        pv = st.number_input("Capital:", 100.0)
        i = st.number_input("Taxa %:", 1.0)
        n = st.number_input("Meses:", 1.0)
        if st.button("Calcular"): st.metric("Montante", f"{pv * (1 + i/100)**n:.2f}")

else:
    st.title("📖 Estudante")
    st.info("Painel de consulta liberado.")
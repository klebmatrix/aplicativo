import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    """Substitui símbolos que travam o PDF por versões seguras"""
    rep = {
        "√": "V",
        "²": "^2",
        "³": "^3",
        "÷": "/",
        "x": "*",
        "≤": "<=",
        "≥": ">="
    }
    for original, novo in rep.items():
        text = text.replace(original, novo)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        s_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        if pin == s_prof: 
            st.session_state.perfil = "admin"
            st.rerun()
        else: st.error("PIN Inválido.")
    st.stop()

# --- 3. MENU LATERAL ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
aba = st.sidebar.radio("Módulos:", ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual", "🧮 Calculadoras"])

# --- 4. LÓGICA DE GERAÇÃO (COLEGIAL COM RAIZ) ---
if aba == "📚 Colegial":
    st.subheader("Colegial: Fração, Potência, Raiz e Porcentagem")
    temas = st.multiselect("Tópicos:", ["Frações", "Potenciação", "Radiciação (V)", "Porcentagem"], ["Radiciação (V)"])
    if st.button("🎲 Gerar"):
        qs = []
        for _ in range(10):
            t = random.choice(temas)
            if t == "Radiciação (V)":
                # Formato solicitado: 2V25=10
                n = random.randint(2, 5)
                base = random.randint(2, 12)**2
                qs.append(f"{n}V{base} =")
            elif t == "Frações":
                qs.append(f"{random.randint(1,9)}/2 + {random.randint(1,9)}/3 =")
            elif t == "Potenciação":
                qs.append(f"{random.randint(2,10)}^2 =")
            else:
                qs.append(f"{random.randint(5,50)}% de {random.randint(100,500)} =")
        st.session_state.preview_questoes = qs

elif aba == "⚖️ Álgebra Linear":
    sub = st.radio("Opção:", ["Sistemas", "Matrizes", "Funções"])
    if st.button("🎲 Gerar"):
        if sub == "Sistemas":
            x, y = random.randint(1,5), random.randint(1,5)
            st.session_state.preview_questoes = [f"[SIS] x + y = {x+y} | x - y = {x-y}"]
        elif sub == "Matrizes":
            m = np.random.randint(1, 10, (2,2))
            st.session_state.preview_questoes = ["Det de:\n" + "\n".join([" | ".join(map(str, l)) for l in m])]
        else:
            st.session_state.preview_questoes = ["f(x) = 2x + 10. Calcule f(5)"]

elif aba == "📄 Manual":
    txt = st.text_area("Manual (t. para título, [SIS] para sistema, V para raiz)", height=200)
    if st.button("🔍 Preview"): st.session_state.preview_questoes = txt.split('\n')

# --- 5. VISUALIZAÇÃO E PDF (BLINDADO CONTRA ERROS) ---
if st.session_state.preview_questoes:
    st.divider()
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    
    with st.container(border=True):
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            if "[SIS]" in line:
                partes = line.replace("[SIS]", "").split("|")
                st.write(f"**{letras[l_idx%26]})**")
                st.latex(r" \begin{cases} " + partes[0] + r" \\ " + partes[1] + r" \end{cases} ")
                l_idx += 1
            elif line.startswith("t."):
                st.subheader(line[2:].strip())
            elif re.match(r'^\d+', line):
                st.markdown(f"**{line}**")
                l_idx = 0
            else:
                # Mostra o símbolo de raiz bonitinho na tela, mas limpa no PDF
                st.write(f"**{letras[l_idx%26]})** {line.replace('V', '√').replace('.', '')}")
                l_idx += 1

    # BOTÃO DE PDF REVISADO
    if st.button("📥 Gerar PDF (Versão Segura)"):
        try:
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11); l_idx = 0
            if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
            
            for q in st.session_state.preview_questoes:
                line = q.strip()
                if not line: continue
                
                if "[SIS]" in line:
                    partes = line.replace("[SIS]", "").split("|")
                    pdf.set_font("Arial", 'B', 11); pdf.cell(10, 10, f"{letras[l_idx%26]})")
                    cx, cy = pdf.get_x(), pdf.get_y()
                    pdf.set_font("Courier", size=18); pdf.text(cx, cy + 7, "{"); pdf.set_font("Arial", size=11)
                    pdf.text(cx + 5, cy + 4, clean_txt(partes[0])); pdf.text(cx + 5, cy + 9, clean_txt(partes[1]))
                    pdf.ln(12); l_idx += 1
                elif line.startswith("t."):
                    pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(line[2:].strip()), ln=True, align='C'); pdf.set_font("Arial", size=11)
                elif re.match(r'^\d+', line):
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(line)); pdf.set_font("Arial", size=11); l_idx = 0
                else:
                    pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(line)}")
                    l_idx += 1
            
            st.download_button("✅ Baixar Agora", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}. Tente remover caracteres especiais.")
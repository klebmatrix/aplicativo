import streamlit as st
import random
import re
import os
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

for key in ['perfil', 'sub_menu', 'preview_questoes']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else None

# --- 2. FUNÇÃO PARA EDITAR O CABEÇALHO ---
def preparar_cabecalho(escola, materia, prof):
    try:
        # Abre a imagem base (deve estar na pasta do projeto)
        img = Image.open("cabecalho.png")
        draw = ImageDraw.Draw(img)
        
        # Tenta carregar uma fonte legível. Se não houver, usa a padrão.
        try:
            font = ImageFont.truetype("Arial.ttf", 18)
        except:
            font = ImageFont.load_default()
        
        # Escreve os dados em coordenadas aproximadas (ajuste se necessário)
        draw.text((85, 22), escola, fill="black", font=font)   # Campo Escola
        draw.text((85, 52), materia, fill="black", font=font)  # Campo Matéria
        draw.text((450, 52), prof, fill="black", font=font)   # Campo Professor
        
        img.save("cabecalho_pronto.png")
        return "cabecalho_pronto.png"
    except:
        return "cabecalho.png" # Se der erro, usa a original pura

# --- 3. LOGIN ---
def validar_acesso(pin_digitado):
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 4. SIDEBAR (CONFIGS, LIMPAR, SAIR) ---
st.sidebar.title(f"🚀 {'Professor' if st.session_state.perfil == 'admin' else 'Estudante'}")
usar_cabecalho = st.sidebar.checkbox("Incluir Cabeçalho", value=True)
layout_colunas = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Limpar Tudo", use_container_width=True):
    st.session_state.preview_questoes = []
    st.session_state.sub_menu = None
    st.rerun()

if st.sidebar.button("🚪 Sair / Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- 5. PAINEL ADMIN (8 BOTÕES) ---
if st.session_state.perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
    st.subheader("📝 Geradores de PDF")
    g1, g2, g3, g4, g5 = st.columns(5)
    if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
    if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
    if g3.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
    if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
    if g5.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

    st.subheader("🧮 Ferramentas de Cálculo")
    c1, c2, c3 = st.columns(3)
    if c1.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    if c2.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
    if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

    menu = st.session_state.sub_menu
    st.divider()

    if menu == "op":
        st.header("🔢 Operações")
        n_ini = st.number_input("Iniciar no nº:", value=6)
        if st.button("Gerar Agora"):
            st.session_state.preview_questoes = [".M1", "t. ATIVIDADE", f"{n_ini}. Calcule:"] + \
                [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(12)]
            st.rerun()

    elif menu == "man":
        st.header("📄 Módulo Manual")
        txt = st.text_area("Ex: .M1, t. Título, 6. Pergunta, .Item")
        if st.button("Aplicar"):
            st.session_state.preview_questoes = txt.split('\n')
            st.rerun()

# --- 6. PREVIEW E MOTOR PDF (CABEÇALHO NO TOPO) ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    for item in st.session_state.preview_questoes: st.text(item)

    def export_pdf():
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Posição inicial no topo da folha
            y_pos = 5 
            
            if usar_cabecalho:
                # Preenche com os dados: Escola, Matéria, Professor
                img_path = preparar_cabecalho("Republ", "Matemática", "PROF. KLEBER")
                
                # Insere a imagem centralizada (10mm margem esquerda em 210mm total)
                pdf.image(img_path, x=10, y=y_pos, w=190)
                y_pos = 60  # Ajuste do salto para o texto começar após o cabeçalho
            
            pdf.set_y(y_pos)
            letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
            n_cols = int(layout_colunas)
            larg_col = 190 / n_cols
            
            for line in st.session_state.preview_questoes:
                line = line.strip()
                if not line: continue
                
                # .M1 -> Módulo em Negrito
                if line.startswith(".M"):
                    pdf.set_font("Helvetica", 'B', 12)
                    pdf.cell(190, 10, line[1:], ln=True, align='L')
                    l_idx = 0
                # t. -> Título Centralizado
                elif line.lower().startswith("t."):
                    pdf.set_font("Helvetica", 'B', 14)
                    pdf.cell(190, 10, line[2:].strip().upper(), ln=True, align='C')
                    l_idx = 0
                # Se a linha começa com NÚMERO (ex: 6.)
                elif re.match(r'^\d+\.', line):
                    pdf.set_font("Helvetica", size=12)
                    pdf.cell(190, 10, line, ln=True, align='L')
                    l_idx = 0 # Reinicia para os próximos itens serem letras
                # Itens automáticos em letras (a, b, c...)
                else:
                    pdf.set_font("Helvetica", size=12)
                    col = l_idx % n_cols
                    texto_item = f"{letras[l_idx % 26]}) {line.lstrip('. ')}"
                    pdf.cell(larg_col, 8, texto_item, align='L', ln=(col == n_cols - 1))
                    l_idx += 1
            
            return pdf.output(dest='S').encode('latin-1')
        except:
            return b""

    st.download_button("📥 Baixar PDF Quantum", data=export_pdf(), file_name="atividade_republ.pdf")
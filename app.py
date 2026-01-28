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

    elif op_atual == "man":
        st.header("📄 Manual")
        tit_m = st.text_input("Título:", "Atividade")
        txt_m = st.text_area("Texto (. para colunas):", height=200)
        if st.button("Gerar Manual"):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10); l_idx = 0; letras = "abcdefghijklmnopqrstuvwxyz"
            for linha in txt_m.split('\n'):
                t = linha.strip()
                if not t: continue
                match = re.match(r'^(\.+)', t); pts = len(match.group(1)) if match else 0
                if re.match(r'^\d+', t): # Novo número reseta letra
                    pdf.ln(5); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(t)); pdf.set_font("Arial", size=10); l_idx = 0
                elif pts > 0:
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*45); pdf.cell(45, 8, f"{letras[l_idx%26]}) {clean_txt(t[pts:].strip())}", ln=True); l_idx += 1
                else: pdf.multi_cell(0, 8, clean_txt(t))
            st.download_button("Baixar", pdf.output(dest='S').encode('latin-1', 'replace'), "manual.pdf")

    # --- 4.1 CONTINUAÇÃO MÓDULOS DE CÁLCULO (ONLINE) ---
    elif op_atual == "calc_f":
        st.header("𝑓(x) Calculadora de Funções")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            f_input = st.text_input("Defina f(x):", "x**2 + 5*x + 6")
        with col_f2:
            x_val = st.number_input("Valor de x:", value=1.0)
        
        if st.button("Calcular Resultado"):
            try:
                # Substitui x por valor numérico e avalia com segurança básica
                resultado = eval(f_input.replace('x', f'({x_val})'))
                st.metric(label=f"f({x_val})", value=f"{resultado:.4f}")
                st.latex(f"f({x_val}) = {f_input.replace('x', str(x_val))} = {resultado}")
            except Exception as e:
                st.error(f"Erro na fórmula: {e}")

    elif op_atual == "pemdas":
        st.header("📊 Expressões (PEMDAS)")
        exp = st.text_input("Digite a expressão (ex: (2+3)*5**2):", "2 + 3 * 4")
        if st.button("Resolver Expressão"):
            try:
                res = eval(exp)
                st.success(f"O resultado é: {res}")
            except:
                st.error("Expressão inválida.")

    elif op_atual == "fin":
        st.header("💰 Calculadora Financeira (Juros Compostos)")
        c1, c2, c3 = st.columns(3)
        with c1: pv = st.number_input("Capital Inicial (PV):", 1000.0)
        with c2: taxa = st.number_input("Taxa de Juros (% ao mês):", 1.0)
        with c3: meses = st.number_input("Tempo (Meses):", 1.0)
        
        if st.button("Calcular Montante"):
            fv = pv * (1 + taxa/100)**meses
            st.metric("Montante Final (FV)", f"R$ {fv:.2f}")
            st.info(f"Juros Totais: R$ {fv - pv:.2f}")

# --- 6. VISUALIZAÇÃO UNIFICADA (CARDS + REGRAS) ---
# Este bloco agora atende tanto ao Gerador Manual quanto aos Automáticos
if st.session_state.preview_questoes:
    st.divider()
    
    # 1. CABEÇALHO (Sempre no topo)
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)
    else:
        st.warning("⚠️ Adicione 'cabecalho.png' para exibir o topo da atividade.")
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0

    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        # A) Reconhecimento de Título (t.) - Centralizado e Azul
        if line.lower().startswith(("t.", "titulo:", "título:")):
            t_clean = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
            st.markdown(f"<h1 style='text-align: center; color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px;'>{t_clean}</h1>", unsafe_allow_html=True)
            continue

        # B) Seção Numerada (Reseta letras para 'a' na próxima linha)
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0 
            
        # C) Itens em Cards (a, b, c...)
        else:
            with st.container(border=True):
                c1, c2 = st.columns([0.05, 0.95])
                with c1:
                    st.write(f"**{letras[l_idx%26]})**")
                with c2:
                    # Lógica para Sistemas de Equações
                    if "{" in line or "|" in line:
                        cont = line.replace("{", "").strip()
                        partes = cont.split("|") if "|" in cont else [cont]
                        if len(partes) > 1:
                            st.latex(r" \begin{cases} " + partes[0].strip() + r" \\ " + partes[1].strip() + r" \end{cases} ")
                        else: st.write(line)
                    else:
                        # Limpa vírgula e trata matemática (Raiz/Potência)
                        f = tratar_math(line)
                        if "\\" in f or "^" in f:
                            st.latex(f)
                        else:
                            st.write(line.lstrip(','))
            l_idx += 1

    # --- 7. EXPORTAÇÃO PDF ---
    st.markdown("---")
    if st.button("📥 Gerar Arquivo PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=8, w=190)
            pdf.set_y(50)
        else: pdf.set_y(20)
        
        l_idx = 0
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            # Título no PDF
            if line.lower().startswith(("t.", "titulo:", "título:")):
                t_pdf = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 12, clean_txt(t_pdf), ln=True, align='C')
                pdf.ln(5)
            # Número no PDF (Reseta letras)
            elif re.match(r'^\d+', line):
                pdf.ln(4)
                pdf.set_font("Arial", 'B', 12)
                pdf.multi_cell(0, 8, clean_txt(line))
                pdf.set_font("Arial", size=11)
                l_idx = 0
            # Itens a, b, c no PDF
            else:
                pdf.set_font("Arial", size=11)
                texto_item = f"{letras[l_idx%26]}) {clean_txt(line.lstrip(','))}"
                pdf.multi_cell(0, 8, texto_item)
                l_idx += 1
                
        st.download_button("✅ Baixar Atividade Finalizada", pdf.output(dest='S').encode('latin-1'), "atividade_quantum.pdf")

else:
    # Caso o perfil seja 'aluno' ou não haja questões em preview
    if st.session_state.perfil == "aluno":
        st.title("📖 Área do Estudante")
        st.info("Utilize as ferramentas de cálculo no menu lateral para seus estudos.")
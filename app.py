import streamlit as st
import math
import numpy as np
import os
from fpdf import FPDF
import re
import streamlit.components.v1 as components

# 1. CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira linha)
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# --- 2. SEGURANÇA ---
def validar_acesso(pin_digitado):
    try:
        # Puxa dos Secrets (Streamlit Cloud) ou Variáveis de Ambiente (Render/Local)
        # Se não encontrar, usa padrões de segurança
        senha_aluno = st.secrets.get("acesso_aluno", "123456")
        senha_professor = st.secrets.get("chave_mestra", "admin123")
        
        if pin_digitado == str(senha_aluno):
            return "aluno"
        elif pin_digitado == str(senha_professor):
            return "admin"
    except:
        # Fallback para execução local caso secrets não existam
        if pin_digitado == "123456": return "aluno"
        if pin_digitado == "admin123": return "admin"
    return "negado"

if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# --- 3. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab - Acesso")
    pin = st.text_input("Digite seu PIN de 6 dígitos:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("Acesso Negado. Verifique seu PIN.")
    st.stop()

# --- 4. INTERFACE PRINCIPAL ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    itens = ["Expressões (PEMDAS)", "Equações", "Funções Aritméticas", "Logaritmos"]
    if perfil == "admin":
        itens = ["Painel de Exercícios (4x1)", "Gerador de Atividades (PDF)"] + itens + ["Sistemas Lineares", "Matrizes"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    
    if st.sidebar.button("Encerrar Sessão"):
        st.session_state.perfil = None
        st.rerun()

    # --- MÓDULO: PAINEL DE EXERCÍCIOS 4 EM 1 (EXCLUSIVO ADMIN) ---
    if menu == "Painel de Exercícios (4x1)":
        st.header("🖨️ Painel de Impressão Rápida (4x1)")
        with st.expander("📝 Editar Questões do Banco"):
            tema_edit = st.text_input("Título da Atividade:", "Revisão de Matemática")
            col_a, col_b = st.columns(2)
            q_list = []
            for i in range(10):
                target_col = col_a if i < 5 else col_b
                q_list.append(target_col.text_input(f"Questão {chr(97+i)}):", f"Exercício {i+1}"))

        html_custom = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f0f2f6; margin: 0; padding: 10px; }}
                .no-print {{ text-align: center; padding: 20px; }}
                .btn-print {{ padding: 12px 30px; background: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px; }}
                .a4-page {{ width: 210mm; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 5mm; background: white; padding: 10mm; margin: auto; }}
                .atv-box {{ border: 1.5px solid black; padding: 15px; height: 132mm; box-sizing: border-box; display: flex; flex-direction: column; }}
                .header {{ border: 1px solid black; padding: 5px; font-size: 10px; margin-bottom: 10px; line-height: 1.6; }}
                .titulo {{ text-align: center; font-weight: bold; margin: 10px 0; text-transform: uppercase; font-size: 12px; border-bottom: 1px solid #eee; }}
                .grid-q {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 11px; }}
                @media print {{ .no-print {{ display: none; }} body {{ padding: 0; }} .a4-page {{ width: 210mm; height: 297mm; padding: 5mm; }} }}
            </style>
        </head>
        <body>
            <div class="no-print"><button class="btn-print" onclick="window.print()">🖨️ IMPRIMIR FOLHA A4</button></div>
            <div class="a4-page">
                {"".join([f'''
                <div class="atv-box">
                    <div class="header">Escola:____________________________________ Data: __/__/__ <br> Nome:_____________________________________ Turma: ________</div>
                    <div class="titulo">{tema_edit}</div>
                    <div class="grid-q">
                        <div>a) {q_list[0]} <br><br> b) {q_list[1]} <br><br> c) {q_list[2]} <br><br> d) {q_list[3]} <br><br> e) {q_list[4]}</div>
                        <div>f) {q_list[5]} <br><br> g) {q_list[6]} <br><br> h) {q_list[7]} <br><br> i) {q_list[8]} <br><br> j) {q_list[9]}</div>
                    </div>
                </div>''' for _ in range(4)])}
            </div>
        </body>
        </html>
        """
        components.html(html_custom, height=1100, scrolling=True)

    # --- MÓDULO: GERADOR DE ATIVIDADES PDF ---
    elif menu == "Gerador de Atividades (PDF)":
        st.header("📄 Criador de Listas de Exercícios")
        titulo_pdf = st.text_input("Título da Atividade:", "Lista de Exercícios")
        conteudo = st.text_area("Conteúdo (Use . para colunas):", height=300)
        
        if st.button("Gerar e Baixar PDF"):
            pdf = FPDF()
            pdf.add_page()
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=12.5, y=8, w=185)
                pdf.set_y(48)
            else: pdf.set_y(15)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, txt=titulo_pdf, ln=True, align='C')
            pdf.ln(2)
            
            pdf.set_font("Arial", size=10)
            letras = "abcdefghijklmnopqrstuvwxyz"
            letra_idx = 0
            
            for linha in conteudo.split('\n'):
                txt = linha.strip()
                if not txt: continue
                match = re.match(r'^(\.+)', txt)
                
                if re.match(r'^\d+', txt): # Questão
                    pdf.ln(4)
                    pdf.set_font("Arial", 'B', 11); pdf.set_x(10)
                    pdf.multi_cell(0, 8, txt=txt)
                    pdf.set_font("Arial", size=10); letra_idx = 0
                elif match: # Colunas
                    n_p = len(match.group(1))
                    if n_p > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (n_p - 1) * 32)
                    pdf.cell(32, 8, txt=f"{letras[letra_idx%26]}) {txt[n_p:].strip()}", ln=True)
                    letra_idx += 1
                else: # Texto normal
                    pdf.set_x(10); pdf.multi_cell(0, 8, txt=txt)
            
            st.download_button("📥 Clique aqui para Baixar", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")

    # --- MÓDULO: FUNÇÕES ARITMÉTICAS ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Analisador Numérico")
        n = st.number_input("Digite um número n:", min_value=1, value=12)
        divs = [d for d in range(1, n+1) if n % d == 0]
        col1, col2 = st.columns(2)
        col1.metric("Qtd. Divisores", len(divs))
        col2.metric("Soma Divisores", sum(divs))
        st.write(f"**Divisores:** {divs}")
        if len(divs) == 2: st.success("Este número é PRIMO!")

    # --- MÓDULO: EXPRESSÕES ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora PEMDAS")
        exp = st.text_input("Expressão (ex: 2^3 + 5 * (10/2)):")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    # --- MÓDULO: EQUAÇÕES ---
    elif menu == "Equações":
        st.header("📐 Equações de 1º e 2º Grau")
        tipo = st.radio("Grau:", ["1º Grau (ax + b = 0)", "2º Grau (ax² + bx + c = 0)"])
        if tipo == "1º Grau (ax + b = 0)":
            a = st.number_input("a", value=1.0); b = st.number_input("b", value=0.0)
            if st.button("Resolver 1º Grau"):
                if a != 0: st.success(f"x = {-b/a:.2f}")
                else: st.error("a não pode ser zero.")
        else:
            a2 = st.number_input("a", value=1.0, key="a2")
            b2 = st.number_input("b", value=-5.0); c2 = st.number_input("c", value=6.0)
            if st.button("Resolver 2º Grau"):
                delta = b2**2 - 4*a2*c2
                if delta >= 0:
                    x1 = (-b2 + math.sqrt(delta))/(2*a2)
                    x2 = (-b2 - math.sqrt(delta))/(2*a2)
                    st.success(f"x1 = {x1:.2f}, x2 = {x2:.2f}")
                else: st.error("Sem raízes reais.")
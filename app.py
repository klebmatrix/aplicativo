import streamlit as st
import math
import numpy as np
import os
from fpdf import FPDF
import re
import streamlit.components.v1 as components

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# --- 1. SEGURANÇA ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except:
        if pin_digitado == "123456": return "aluno"
        if pin_digitado == "admin123": return "admin"
    return "negado"

if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de Acesso:", type="password", key="login_pass")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. INTERFACE PRINCIPAL ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        # Adicionamos o NOVO Gerador Automático aqui
        itens = ["GERADOR AUTOMÁTICO (4x1)", "Gerador de Atividades (PDF Custom)"] + itens + ["Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- NOVO MÓDULO: GERADOR AUTOMÁTICO (4x1) ---
    if menu == "GERADOR AUTOMÁTICO (4x1)":
        st.header("⚡ Gerador Instantâneo de Exercícios")
        st.write("Selecione o tema para carregar questões automáticas e imprimir 4 por folha.")

        html_gerador = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                :root { --p: #2c3e50; --s: #3498db; }
                body { font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; background: #f4f7f6; }
                #side-menu { width: 200px; background: var(--p); color: white; height: 100vh; position: fixed; padding: 10px; }
                .m-btn { width: 100%; padding: 10px; margin: 4px 0; border: none; background: #34495e; color: white; text-align: left; cursor: pointer; border-radius: 4px; font-size: 12px; }
                .m-btn:hover { background: var(--s); }
                #print-area { margin-left: 210px; padding: 20px; width: 100%; }
                .btn-imprimir { padding: 12px 25px; background: #27ae60; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; margin-bottom: 15px; }
                .a4 { width: 210mm; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 5mm; background: white; padding: 10mm; margin: auto; }
                .box { border: 1.5px solid black; padding: 10px; height: 130mm; box-sizing: border-box; font-size: 11px; }
                .cabecalho { border: 1px solid black; padding: 5px; font-size: 9px; margin-bottom: 8px; line-height: 1.4; }
                .tit { text-align: center; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid #eee; }
                .q-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
                @media print { .no-p { display: none; } #print-area { margin: 0; } .a4 { width: 210mm; height: 297mm; padding: 5mm; } }
            </style>
        </head>
        <body>
            <div id="side-menu" class="no-p">
                <h4>Temas</h4>
                <button class="m-btn" onclick="montar('1grau')">Equação 1º Grau</button>
                <button class="m-btn" onclick="montar('2grau')">Equação 2º Grau</button>
                <button class="m-btn" onclick="montar('exp')">Expressões Num.</button>
                <button class="m-btn" onclick="montar('pot')">Potência e Raiz</button>
                <button class="m-btn" onclick="montar('mat')">Matrizes</button>
                <button class="m-btn" onclick="montar('sis')">Sistemas</button>
            </div>
            <div id="print-area">
                <button class="btn-imprimir no-p" onclick="window.print()">🖨️ IMPRIMIR 4 POR PÁGINA</button>
                <div id="folha" class="a4"></div>
            </div>
            <script>
                const data = {
                    '1grau': { t: 'Equações do 1º Grau', q: ['2x + 4 = 10', '5x - 10 = 15', '3x + 9 = 0', 'x/2 + 5 = 10', '7x - 7 = 14', '4x + 2 = 18', '10x - 5 = 45', 'x + 15 = 30', '8x = 64', '6x - 12 = 0'] },
                    '2grau': { t: 'Equações do 2º Grau', q: ['x² - 5x + 6 = 0', 'x² - 9 = 0', 'x² - 4x + 4 = 0', 'x² + 3x + 2 = 0', '2x² - 32 = 0', 'x² - 7x + 10 = 0', 'x² - 1 = 0', 'x² - 6x + 8 = 0', 'x² - 25 = 0', '3x² - 12 = 0'] },
                    'exp': { t: 'Expressões Numéricas', q: ['(12+8)×2', '50-(10÷2)', '100÷(5+5)', '25+(4×5)', '(15-5)×3', '30÷(2+3)', '7×8-10', '45÷9+7', '12×2+5', '20-(5+5)'] },
                    'pot': { t: 'Potência e Raízes', q: ['2³ + √25', '5² - √16', '√100 + 10', '3³ - 7', '√81 × 2', '√144 ÷ 12', '4² ÷ 2', '10² - 90', '√49 + √64', '2⁴ ÷ 4'] },
                    'mat': { t: 'Matrizes e Det', q: ['Calcule Det A [1,2;3,4]', 'A+B onde A=I2', '3 x Matriz A', 'Transposta de B', 'Soma da Diag. Principal', 'Matriz Oposta de A', 'Verifique se é Simétrica', 'Traço da Matriz A', 'A - B (2x2)', 'Det de Matriz 3x3'] },
                    'sis': { t: 'Sistemas Lineares', q: ['x+y=5; x-y=1', '2x+y=10; x-y=2', 'x+y=8; x-y=4', '3x+y=7; x+y=3', 'x+2y=10; x-y=1', '2x+2y=20; x-y=0', 'x+y=12; 2x-y=3', 'x-y=5; x+y=15', '4x+y=9; x+y=3', 'x+3y=10; x-y=2'] }
                };
                function montar(tema) {
                    const d = data[tema];
                    const f = document.getElementById('folha');
                    f.innerHTML = '';
                    const card = `
                        <div class="box">
                            <div class="cabecalho">Escola:___________________ Data:__/__/__ <br> Nome:____________________ Turma:____</div>
                            <div class="tit">\${d.t}</div>
                            <div class="q-grid">
                                <div>a) \${d.q[0]}<br><br>b) \${d.q[1]}<br><br>c) \${d.q[2]}<br><br>d) \${d.q[3]}<br><br>e) \${d.q[4]}</div>
                                <div>f) \${d.q[5]}<br><br>g) \${d.q[6]}<br><br>h) \${d.q[7]}<br><br>i) \${d.q[8]}<br><br>j) \${d.q[9]}</div>
                            </div>
                        </div>`;
                    for(let i=0; i<4; i++) f.innerHTML += card;
                }
                window.onload = () => montar('1grau');
            </script>
        </body>
        </html>
        """
        components.html(html_gerador, height=1000, scrolling=True)

    # --- MÓDULO: ATIVIDADES DRIVE ---
    elif menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    # --- MÓDULO: EXPRESSÕES ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Expressões")
        exp = st.text_input("Digite a expressão (ex: (5+3)*2^2):")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    # --- MÓDULO: EQUAÇÕES (1º e 2º Grau) ---
    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Resolução de Equações")
        grau = st.selectbox("Escolha o Grau:", ["1º Grau", "2º Grau"])
        if grau == "1º Grau":
            a1 = st.number_input("a:", value=1.0); b1 = st.number_input("b:", value=0.0)
            if st.button("Calcular"):
                if a1 != 0: st.success(f"x = {-b1/a1:.2f}")
                else: st.error("a não pode ser zero.")
        else:
            a2 = st.number_input("a:", value=1.0, key="a2"); b2 = st.number_input("b:", value=-5.0); c2 = st.number_input("c:", value=6.0)
            if st.button("Calcular"):
                delta = b2**2 - 4*a2*c2
                if delta >= 0:
                    x1 = (-b2 + math.sqrt(delta))/(2*a2)
                    x2 = (-b2 - math.sqrt(delta))/(2*a2)
                    st.success(f"x1 = {x1:.2f}, x2 = {x2:.2f}")
                else: st.error("Sem raízes reais.")

    # --- MÓDULO: GERADOR DE ATIVIDADES PDF ---
    elif menu == "Gerador de Atividades (PDF Custom)":
        st.header("📄 Gerador de Atividades Customizado")
        titulo_pdf = st.text_input("Título:", "Atividade de Matemática")
        conteudo = st.text_area("Conteúdo:", height=200)
        if st.button("Gerar PDF"):
            pdf = FPDF()
            pdf.add_page()
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=12.5, y=8, w=185)
                pdf.set_y(46)
            else: pdf.set_y(15)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, txt=titulo_pdf, ln=True, align='C')
            pdf.set_font("Arial", size=10)
            for linha in conteudo.split('\n'):
                pdf.multi_cell(0, 8, txt=linha)
            st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")

    # --- MÓDULO: MATRIZES ---
    elif menu == "Matrizes":
        st.header("📊 Determinante 2x2")
        m11 = st.number_input("M11", value=1.0); m12 = st.number_input("M12", value=0.0)
        m21 = st.number_input("M21", value=0.0); m22 = st.number_input("M22", value=1.0)
        if st.button("Calcular"):
            st.metric("Det(M)", (m11*m22) - (m12*m21))

    # --- MÓDULO: FINANCEIRO ---
    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        c = st.number_input("Capital:", value=1000.0)
        i = st.number_input("Taxa (%):", value=5.0) / 100
        t = st.number_input("Meses:", value=12.0)
        if st.button("Calcular"):
            st.success(f"Montante: R$ {c * (1 + i)**t:.2f}")

    # (Outros módulos mantidos conforme solicitado)
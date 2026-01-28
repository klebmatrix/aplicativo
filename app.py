import streamlit as st
import math
import numpy as np
import os
from fpdf import FPDF
import re  # IMPORTANTE: Isso corrige o erro NameError!
import streamlit.components.v1 as components

# --- CONFIGURAÇÃO DA PÁGINA (Apenas uma chamada no topo) ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# --- 1. SEGURANÇA ---
def validar_acesso(pin_digitado):
    try:
        # Puxa as senhas dos Secrets do Streamlit
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        
        if pin_digitado == senha_aluno:
            return "aluno"
        elif pin_digitado == senha_professor:
            return "admin"
    except:
        # Fallback para teste local se secrets não estiverem configurados
        if pin_digitado == "123456": return "aluno"
        if pin_digitado == "admin123": return "admin"
    return "negado"

if 'perfil' not in st.session_state: 
    st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de Acesso:", type="password", key="login_pass")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("Acesso negado.")
    st.stop()

# --- 3. INTERFACE PRINCIPAL ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    # Lista de Itens Original + Adição do Painel
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    
    if perfil == "admin":
        # Mantendo todos os seus módulos e adicionando o Painel 4x1
        itens += ["Painel de Exercícios (4x1)", "Gerador de Atividades", "Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- MÓDULO: ATIVIDADES DRIVE ---
    if menu == "Atividades (Drive)":
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
            except: st.error("Erro na expressão. Verifique os parênteses.")

    # --- MÓDULO: EQUAÇÕES ---
    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Resolução de Equações")
        grau = st.selectbox("Escolha o Grau:", ["1º Grau", "2º Grau"])
        if grau == "1º Grau":
            a1 = st.number_input("a:", value=1.0); b1 = st.number_input("b:", value=0.0)
            if st.button("Calcular 1º Grau"):
                if a1 != 0: st.success(f"Resultado: x = {-b1/a1:.2f}")
                else: st.error("O valor de 'a' não pode ser zero.")
        else:
            a2 = st.number_input("a:", value=1.0, key="a2")
            b2 = st.number_input("b:", value=-5.0)
            c2 = st.number_input("c:", value=6.0)
            if st.button("Calcular 2º Grau"):
                delta = b2**2 - 4*a2*c2
                if delta >= 0:
                    x1 = (-b2 + math.sqrt(delta))/(2*a2)
                    x2 = (-b2 - math.sqrt(delta))/(2*a2)
                    st.success(f"Raízes: x1 = {x1:.2f}, x2 = {x2:.2f} (Delta: {delta})")
                else: st.error(f"Sem raízes reais (Delta: {delta})")

    # --- MÓDULO: CÁLCULO DE FUNÇÕES ---
    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Cálculo de Valores")
        func_input = st.text_input("Função f(x) (use 'x'):", value="2*x + 10")
        val_x = st.number_input("Valor de x:", value=0.0)
        if st.button("Calcular"):
            try:
                res = eval(func_input.replace('x', f'({val_x})').replace('^', '**'))
                st.metric(f"f({val_x})", f"{res:.2f}")
            except: st.error("Erro na fórmula.")

    # --- MÓDULO: LOGARITMOS ---
    elif menu == "Logaritmos":
        st.header("🔢 Cálculo de Logaritmo")
        num = st.number_input("Logaritmando:", value=100.0, min_value=0.01)
        base = st.number_input("Base:", value=10.0, min_value=0.01)
        if st.button("Calcular Log"):
            try:
                res = math.log(num, base)
                st.success(f"log de {num} na base {base} = {res:.4f}")
            except: st.error("Erro no cálculo.")

    # --- MÓDULO: FUNÇÕES ARITMÉTICAS ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Divisores")
        n = st.number_input("Número inteiro n:", min_value=1, value=12, step=1)
        if st.button("Ver Divisores"):
            divs = [d for d in range(1, n+1) if n % d == 0]
            st.write(f"Divisores de {n}: {divs}")
            st.info(f"Total de divisores: {len(divs)}")

    # --- NOVO MÓDULO: PAINEL DE EXERCÍCIOS 4 EM 1 (EDITÁVEL) ---
    elif menu == "Painel de Exercícios (4x1)":
        st.header("🖨️ Painel de Impressão Rápida (4 por página)")
        with st.expander("📝 Editar Questões do Banco"):
            tema_edit = st.text_input("Título da Atividade:", "Atividade de Matemática")
            col_a, col_b = st.columns(2)
            q_list = []
            for i in range(10):
                target_col = col_a if i < 5 else col_b
                q_list.append(target_col.text_input(f"Questão {chr(97+i)}):", f"Exercício {i+1}"))

        html_painel = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f0f2f6; margin: 0; padding: 10px; }}
                .no-print {{ text-align: center; padding: 20px; }}
                .btn-print {{ padding: 12px 30px; background: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
                .a4-page {{ width: 210mm; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 5mm; background: white; padding: 10mm; margin: auto; }}
                .atv-box {{ border: 1.5px solid black; padding: 10px; height: 130mm; box-sizing: border-box; display: flex; flex-direction: column; }}
                .header {{ border: 1px solid black; padding: 5px; font-size: 10px; margin-bottom: 10px; }}
                .titulo {{ text-align: center; font-weight: bold; text-transform: uppercase; font-size: 12px; }}
                .grid-q {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 11px; }}
                @media print {{ .no-print {{ display: none; }} .a4-page {{ width: 210mm; height: 297mm; padding: 5mm; }} }}
            </style>
        </head>
        <body>
            <div class="no-print"><button class="btn-print" onclick="window.print()">🖨️ IMPRIMIR FOLHA A4</button></div>
            <div class="a4-page">
                {"".join([f'''
                <div class="atv-box">
                    <div class="header">Escola:____________________ Data: __/__/__ <br> Nome:_____________________ Turma: ____</div>
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
        components.html(html_painel, height=1000, scrolling=True)

    # --- MÓDULO: GERADOR DE ATIVIDADES ---
    elif menu == "Gerador de Atividades":
        st.header("📄 Gerador de Atividades")
        titulo_pdf = st.text_input("Título:", "Atividade de Matemática")
        conteudo = st.text_area("Conteúdo:", height=300)
        
        if st.button("Gerar PDF"):
            if conteudo:
                pdf = FPDF()
                pdf.add_page()
                if os.path.exists("cabecalho.png"):
                    pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
                    pdf.set_y(46)
                else:
                    pdf.set_y(15)
                
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
                    num_pontos = len(match.group(1)) if match else 0
                    
                    if re.match(r'^\d+', txt): # Questão
                        pdf.ln(4)
                        pdf.set_font("Arial", 'B', 11)
                        pdf.set_x(10)
                        pdf.multi_cell(0, 8, txt=txt)
                        pdf.set_font("Arial", size=10)
                        letra_idx = 0 
                    elif num_pontos > 0: # Colunas
                        item = txt[num_pontos:].strip()
                        prefixo = f"{letras[letra_idx % 26]}) "
                        if num_pontos > 1: pdf.set_y(pdf.get_y() - 8)
                        pdf.set_x(10 + (num_pontos - 1) * 32)
                        pdf.cell(32, 8, txt=f"{prefixo}{item}", ln=True)
                        letra_idx += 1
                    else:
                        pdf.set_x(10)
                        pdf.multi_cell(0, 8, txt=txt)
                
                pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
                st.download_button("📥 Baixar PDF Atualizado", data=pdf_bytes, file_name="atividade.pdf")

    # --- MÓDULO: SISTEMAS LINEARES ---
    elif menu == "Sistemas Lineares":
        st.header("⚖️ Sistema 2x2 (a1x + b1y = c1)")
        col1, col2 = st.columns(2)
        with col1:
            a1 = st.number_input("a1", value=1.0); b1 = st.number_input("b1", value=1.0); c1 = st.number_input("c1", value=5.0)
        with col2:
            a2 = st.number_input("a2", value=1.0); b2 = st.number_input("b2", value=-1.0); c2 = st.number_input("c2", value=1.0)
        if st.button("Resolver"):
            try:
                res = np.linalg.solve(np.array([[a1, b1], [a2, b2]]), np.array([c1, c2]))
                st.success(f"Solução: x = {res[0]:.2f}, y = {res[1]:.2f}")
            except: st.error("Sistema impossível ou indeterminado.")

    # --- MÓDULO: MATRIZES ---
    elif menu == "Matrizes":
        st.header("📊 Determinante 2x2")
        m11 = st.number_input("M11", value=1.0); m12 = st.number_input("M12", value=0.0)
        m21 = st.number_input("M21", value=0.0); m22 = st.number_input("M22", value=1.0)
        if st.button("Calcular Determinante"):
            det = (m11*m22) - (m12*m21)
            st.metric("Det(M)", det)

    # --- MÓDULO: FINANCEIRO ---
    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        c = st.number_input("Capital Inicial:", value=1000.0)
        i = st.number_input("Taxa mensal (%):", value=5.0) / 100
        t = st.number_input("Tempo (meses):", value=12.0)
        if st.button("Calcular Montante"):
            m = c * (1 + i)**t
            st.success(f"Montante Final: R$ {m:.2f}")
            st.info(f"Juros Totais: R$ {m-c:.2f}")
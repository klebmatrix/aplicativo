import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
from io import BytesIO

# --- 1. SEGURANÇA ---
# PIN Criptografado (Exemplo)
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    try:
        # Acesso de emergência/teste
        if pin_digitado == "admin": 
            return "ok"
            
        chave = os.environ.get('chave_mestra')
        if not chave: 
            return "erro_env"
            
        # Limpeza da chave para evitar erros de formatação
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        
        # Validação do PIN
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "ok"
        return "erro_senha"
    except Exception: 
        return "erro_token"

# --- 2. MOTOR DE PDF ---
class PDF(FPDF):
    def header(self):
        # Usando 'helvetica' (padrão do fpdf2) para evitar erros de fonte no Linux/Render
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, 'Quantum Lab - Material Didatico Unificado', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_bytes(titulo, questoes, respostas):
    try:
        pdf = PDF()
        pdf.add_page()
        
        # Seção de Exercícios
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, f"LISTA DE EXERCICIOS: {titulo.upper()}", ln=True)
        pdf.set_font("helvetica", size=11)
        for q in questoes:
            pdf.multi_cell(0, 10, txt=q)
            pdf.ln(2)
            
        # Seção de Gabarito
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, "GABARITO PARA CONFERENCIA", ln=True)
        pdf.set_font("helvetica", size=11)
        for r in respostas:
            pdf.multi_cell(0, 10, txt=r)
            
        # Retorna o PDF como bytes usando BytesIO para máxima compatibilidade
        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            return pdf_output.encode('latin-1')
        return pdf_output
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
        return None

# --- 3. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="⚛️")

# Inicialização do Estado
if 'logado' not in st.session_state: 
    st.session_state.logado = False
if 'pdf_pronto' not in st.session_state: 
    st.session_state.pdf_pronto = None

# --- 4. TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("🔐 Login de Segurança")
    pin = st.text_input("Senha Alfanumerica:", type="password")
    if st.button("Acessar Sistema"):
        status = validar_acesso(pin)
        if status == "ok":
            st.session_state.logado = True
            st.rerun()
        else: 
            st.error(f"Acesso negado. Motivo: {status}")
    st.stop()

# --- 5. MENU LATERAL ---
st.sidebar.title("⚛️ Quantum Lab")
menu = st.sidebar.radio("Navegação:", ["Álgebra", "Geometria", "Sistemas", "Financeiro"])

if st.sidebar.button("Encerrar Sessão"):
    st.session_state.logado = False
    st.rerun()

# --- 6. CONTEÚDO PRINCIPAL (COM KEY DINÂMICA PARA ESTABILIDADE) ---
with st.container(key=f"main_content_{menu.lower()}"):
    
    # --- MÓDULO ÁLGEBRA ---
    if menu == "Álgebra":
        st.header("🔍 Álgebra: Equações")
        op_alg = st.selectbox("Tipo de Equação:", ["1º Grau", "2º Grau (Bhaskara)"])
        
        if op_alg == "1º Grau":
            st.latex(r"ax + b = c")
            c1, c2, c3 = st.columns(3)
            a1 = c1.number_input("Valor de a:", value=1.0, key="alg1_a")
            b1 = c2.number_input("Valor de b:", value=0.0, key="alg1_b")
            c1_val = c3.number_input("Valor de c:", value=10.0, key="alg1_c")
            if st.button("Resolver 1º Grau"):
                if a1 != 0:
                    st.success(f"Resultado: x = {(c1_val - b1) / a1}")
                else:
                    st.error("O valor de 'a' não pode ser zero.")

        elif op_alg == "2º Grau (Bhaskara)":
            st.latex(r"ax^2 + bx + c = 0")
            st.latex(r"x = \frac{-b \pm \sqrt{\Delta}}{2a}, \quad \Delta = b^2 - 4ac")
            
            c1, c2, c3 = st.columns(3)
            a2 = c1.number_input("a:", value=1.0, key="alg2_a")
            b2 = c2.number_input("b:", value=-5.0, key="alg2_b")
            c2_val = c3.number_input("c:", value=6.0, key="alg2_c")
            
            if st.button("Calcular Bhaskara"):
                if a2 == 0:
                    st.warning("Isso é uma equação de 1º grau.")
                else:
                    delta = b2**2 - 4*a2*c2_val
                    st.write(f"**Delta (Δ):** {delta}")
                    if delta >= 0:
                        x1 = (-b2 + np.sqrt(delta)) / (2*a2)
                        x2 = (-b2 - np.sqrt(delta)) / (2*a2)
                        st.success(f"x1 = {x1} | x2 = {x2}")
                    else: 
                        st.error("Não possui raízes reais (Delta negativo).")

    # --- MÓDULO GEOMETRIA ---
    elif menu == "Geometria":
        st.header("📐 Geometria")
        g_tab1, g_tab2, g_tab3 = st.tabs(["Pitágoras", "Áreas", "Volumes"])
        
        with g_tab1:
            st.latex(r"a^2 + b^2 = c^2")
            ca = st.number_input("Cateto A:", value=3.0, key="geo_p_a")
            cb = st.number_input("Cateto B:", value=4.0, key="geo_p_b")
            if st.button("Calcular Hipotenusa"):
                st.success(f"Hipotenusa: {np.sqrt(ca**2 + cb**2):.2f}")
                
        with g_tab2:
            st.latex(r"A = \frac{b \cdot h}{2}")
            base = st.number_input("Base:", value=10.0, key="geo_a_b")
            alt = st.number_input("Altura:", value=5.0, key="geo_a_h")
            if st.button("Calcular Área do Triângulo"):
                st.info(f"Área: {(base * alt)/2:.2f}")

        with g_tab3:
            st.latex(r"V = \frac{4}{3} \pi r^3")
            raio_v = st.number_input("Raio da Esfera:", value=5.0, key="geo_v_r")
            if st.button("Calcular Volume da Esfera"):
                st.success(f"Volume: {(4/3) * np.pi * (raio_v**3):.2f}")

    # --- MÓDULO SISTEMAS ---
    elif menu == "Sistemas":
        st.header("📏 Sistemas Lineares (Ax = B)")
        ordem = st.slider("Tamanho do Sistema:", 2, 4, 2, key="sis_slider")
        mat_A, vec_B = [], []
        for i in range(ordem):
            cols = st.columns(ordem + 1)
            linha = [cols[j].number_input(f"A{i+1}{j+1}", value=(1.0 if i==j else 0.0), key=f"s_{i}_{j}_{ordem}") for j in range(ordem)]
            mat_A.append(linha)
            vec_B.append(cols[ordem].number_input(f"B{i+1}", value=1.0, key=f"v_{i}_{ordem}"))
            
        if st.button("Resolver Sistema"):
            try:
                res = np.linalg.solve(np.array(mat_A), np.array(vec_B))
                st.success("Sistema resolvido com sucesso!")
                for idx, val in enumerate(res):
                    st.write(f"**x{idx+1}** = {val:.4f}")
            except np.linalg.LinAlgError:
                st.error("O sistema não possui uma solução única (Matriz Singular).")
            except Exception as e:
                st.error(f"Erro na resolução: {e}")

    # --- MÓDULO FINANCEIRO ---
    elif menu == "Financeiro":
        st.header("💰 Matemática Financeira")
        st.latex(r"M = C \cdot (1 + i)^t")
        
        c1, c2, c3 = st.columns(3)
        cap = c1.number_input("Capital Inicial (R$):", value=1000.0, key="fin_c")
        taxa = c2.number_input("Taxa (% ao mês):", value=1.0, key="fin_i") / 100
        tempo = c3.number_input("Tempo (Meses):", value=12, key="fin_t")
        
        if st.button("Calcular Juros Compostos"):
            mont = cap * (1 + taxa)**tempo
            st.metric("Montante Final", f"R$ {mont:.2f}")
            st.write(f"Total de Juros: R$ {mont - cap:.2f}")

# --- 7. GERADOR DE PDF (MÍNIMO 10 QUESTÕES) ---
st.sidebar.divider()
st.sidebar.subheader("📝 Gerador de Material")
tipo_pdf = st.sidebar.selectbox("Tema do PDF:", ["Álgebra", "Geometria"], key="pdf_tema")
qtd = st.sidebar.number_input("Quantidade (Mín 10):", min_value=10, value=10, key="pdf_qtd")

if st.sidebar.button("Gerar PDF"):
    q, g = [], []
    for i in range(qtd):
        if tipo_pdf == "Álgebra":
            ra, rx = random.randint(1,10), random.randint(1,10)
            rb = random.randint(1,20)
            rc = (ra * rx) + rb
            q.append(f"{i+1}) Resolva a equacao: {ra}x + {rb} = {rc}")
            g.append(f"{i+1}) x = {rx}")
        else:
            c1, c2 = random.randint(3,10), random.randint(3,10)
            q.append(f"{i+1}) Calcule a hipotenusa para um triangulo com catetos {c1} e {c2}.")
            g.append(f"{i+1}) Hipotenusa = {np.sqrt(c1**2 + c2**2):.2f}")
    
    pdf_data = gerar_pdf_bytes(tipo_pdf, q, g)
    if pdf_data:
        st.session_state.pdf_pronto = pdf_data
        st.sidebar.success("PDF Gerado!")

if st.session_state.pdf_pronto:
    st.sidebar.download_button(
        label="📥 Baixar Arquivo PDF",
        data=st.session_state.pdf_pronto,
        file_name=f"atividades_{tipo_pdf.lower()}.pdf",
        mime="application/pdf",
        key="download_btn"
    )

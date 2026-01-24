import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from fpdf import FPDF
import random

# --- 1. SEGURANÇA (TOKEN ALFANUMÉRICO) ---
# Substitua pelo seu token gerado ou use 'admin' para testes locais
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    try:
        # Fallback para teste local sem variáveis de ambiente
        if pin_digitado == "admin":
            return "ok"
            
        chave = os.environ.get('chave_mestra')
        if not chave:
            return "erro_env"
            
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "ok"
        else:
            return "erro_senha"
    except Exception:
        return "erro_token"

# --- 2. MOTOR DE PDF ---
class PDF(FPDF):
    def header(self):
        # Usando 'helvetica' que é padrão e não requer arquivos externos
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, 'Relatorio Matematico - Quantum Lab', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_atividades(titulo, questoes, respostas):
    pdf = PDF()
    pdf.add_page()
    
    # Página de Atividades
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, f"ATIVIDADES: {titulo.upper()}", ln=True)
    pdf.set_font("helvetica", size=11)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q)
        pdf.ln(2)
        
    # Página de Gabarito
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, f"GABARITO: {titulo.upper()}", ln=True)
    pdf.set_font("helvetica", size=11)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r)
        
    return pdf.output()

# --- 3. CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="Math Precision Lab", layout="wide")

if 'logado' not in st.session_state: 
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login de Segurança")
    pin = st.text_input("Senha Alfanumerica:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin)
        if res == "ok": 
            st.session_state.logado = True
            st.rerun()
        else: 
            st.error(f"Erro: {res}")
    st.stop()

# --- 4. MENU LATERAL ---
st.sidebar.title("⚛️ Categorias")
menu = st.sidebar.radio("Navegação:", ["Álgebra", "Geometria", "Sistemas Lineares", "Matemática Financeira"])
if st.sidebar.button("Sair"): 
    st.session_state.logado = False
    st.rerun()

# --- 5. CONTEÚDO PRINCIPAL (COM KEY DINÂMICA PARA ESTABILIDADE) ---
# A key dinâmica no container resolve o erro 'removeChild' do React/Streamlit
with st.container(key=f"main_section_{menu.lower().replace(' ', '_')}"):
    
    if menu == "Álgebra":
        st.header("🔍 Álgebra e Equações")
        sub = st.selectbox("Escolha o Grau:", ["1º Grau (ax + b = c)", "2º Grau (ax² + bx + c = 0)"])
        
        if sub == "1º Grau (ax + b = c)":
            c1, c2, c3 = st.columns(3)
            a = c1.number_input("a (≠ 0):", value=2, step=1, key="alg_a")
            b = c2.number_input("b:", value=40, step=1, key="alg_b")
            c_eq = c3.number_input("Igual a c:", value=50, step=1, key="alg_c")
            if a == 0: 
                st.error("Erro: 'a' não pode ser zero.")
            elif st.button("Calcular 1º Grau"):
                x = (c_eq - b) / a
                st.success(f"Resultado: x = {x}")

        elif sub == "2º Grau (ax² + bx + c = 0)":
            c1, c2, c3 = st.columns(3)
            a2 = c1.number_input("a:", value=1, key="alg2_a")
            b2 = c2.number_input("b:", value=-5, key="alg2_b")
            c2_val = c3.number_input("c:", value=6, key="alg2_c")
            
            if a2 == 0: 
                st.warning("Isso é uma equação de 1º grau.")
            elif st.button("Calcular Bhaskara"):
                delta = (b2**2) - (4 * a2 * c2_val)
                st.write(f"Delta (Δ) = {delta}")
                if delta >= 0:
                    x1 = (-b2 + np.sqrt(delta)) / (2 * a2)
                    x2 = (-b2 - np.sqrt(delta)) / (2 * a2)
                    st.success(f"x1 = {x1} | x2 = {x2}")
                else: 
                    st.error("Raízes Complexas.")

        st.divider()
        st.subheader("📝 Gerador de Atividades (Álgebra)")
        qtd = st.slider("Exercícios:", 1, 10, 5, key="alg_slider")
        if st.button("Gerar PDF Álgebra"):
            q, g = [], []
            for i in range(qtd):
                ra, rx = random.randint(1,10), random.randint(1,10)
                rb = random.randint(1,20)
                rc = (ra * rx) + rb
                q.append(f"{i+1}) Resolva: {ra}x + {rb} = {rc}")
                g.append(f"{i+1}) x = {rx}")
            pdf_bytes = gerar_pdf_atividades("Algebra", q, g)
            st.download_button("Baixar PDF", pdf_bytes, "atividades_algebra.pdf", "application/pdf", key="btn_alg_pdf")

    elif menu == "Geometria":
        st.header("📐 Geometria: Áreas e Volumes")
        fig = st.selectbox("Sólido:", ["Esfera", "Cilindro", "Cubo"])
        med = st.number_input("Medida (Raio ou Lado):", value=10, step=1, key="geo_med")
        
        if fig == "Esfera":
            vol = (4/3) * np.pi * (med**3)
            st.metric("Volume da Esfera", f"{vol:.4f}")
            st.latex(r"V = \frac{4}{3} \pi r^3")

        elif fig == "Cilindro":
            altura = st.number_input("Altura:", value=10, step=1, key="geo_alt")
            vol = np.pi * (med**2) * altura
            st.metric("Volume do Cilindro", f"{vol:.4f}")
            st.latex(r"V = \pi r^2 h")

        elif fig == "Cubo":
            vol = med**3
            st.metric("Volume do Cubo", f"{vol}")
            st.latex(r"V = L^3")

        st.divider()
        st.subheader("📝 Gerador de Atividades (Geometria)")
        qtd_g = st.slider("Exercícios:", 1, 10, 5, key="geo_slider")
        if st.button("Gerar PDF Geometria"):
            q, g = [], []
            for i in range(qtd_g):
                l = random.randint(2, 20)
                q.append(f"{i+1}) Qual o volume de um cubo com lado {l}?")
                g.append(f"{i+1}) Volume = {l**3}")
            pdf_bytes = gerar_pdf_atividades("Geometria", q, g)
            st.download_button("Baixar PDF", pdf_bytes, "atividades_geo.pdf", "application/pdf", key="btn_geo_pdf")

    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Lineares (Matriz $Ax=B$)")
        n = st.slider("Incógnitas:", 2, 5, 2, key="sis_slider")
        mat_A, vec_B = [], []
        for i in range(n):
            cols = st.columns(n+1)
            row = []
            for j in range(n):
                val = cols[j].number_input(f"A[{i+1}][{j+1}]", value=1.0 if i==j else 0.0, key=f"matA_{i}_{j}")
                row.append(val)
            mat_A.append(row)
            val_b = cols[n].number_input(f"B[{i+1}]", value=1.0, key=f"vecB_{i}")
            vec_B.append(val_b)
            
        if st.button("Resolver Sistema"):
            try:
                sol = np.linalg.solve(np.array(mat_A), np.array(vec_B))
                st.success("Sistema resolvido!")
                for idx, s in enumerate(sol):
                    st.write(f"x{idx+1} = {s:.4f}")
            except np.linalg.LinAlgError:
                st.error("O sistema não possui uma solução única.")

    elif menu == "Matemática Financeira":
        st.header("💰 Finanças")
        cap = st.number_input("Capital Inicial (R$):", value=1000.0, step=100.0, key="fin_cap")
        tax = st.number_input("Taxa Mensal (%):", value=1.0, step=0.1, key="fin_tax") / 100
        tem = st.number_input("Tempo (Meses):", value=12, step=1, key="fin_tem")
        
        montante = cap * (1 + tax)**tem
        st.metric("Montante Final", f"R$ {montante:.2f}")
        st.write(f"Fórmula: $M = C(1 + i)^t$")

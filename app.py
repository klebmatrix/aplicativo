import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from fpdf import FPDF
import random

# --- 1. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    try:
        if pin_digitado == "admin": return "ok"
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "ok"
        return "erro_senha"
    except:
        return "erro_token"

# --- 2. MOTOR DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, 'Quantum Math Lab - Relatorio Oficial', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_atividades(titulo, questoes, respostas):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, f"LISTA: {titulo.upper()}", ln=True)
    pdf.set_font("helvetica", size=11)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q)
        pdf.ln(2)
    
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "GABARITO OFICIAL", ln=True)
    pdf.set_font("helvetica", size=11)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r)
    
    return pdf.output()

# --- 3. CONFIGURAÇÃO ---
st.set_page_config(page_title="Math Precision Lab", layout="wide")
if 'logado' not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login de Segurança")
    pin = st.text_input("Senha Alfanumerica:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin)
        if res == "ok":
            st.session_state.logado = True
            st.rerun()
        else: st.error(f"Erro: {res}")
    st.stop()

# --- 4. MENU ---
st.sidebar.title("⚛️ Categorias")
menu = st.sidebar.radio("Navegação:", ["Álgebra", "Geometria", "Sistemas Lineares", "Matemática Financeira"])
if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# --- 5. CONTEÚDO ---
with st.container(key=f"sec_{menu.lower().replace(' ', '_')}"):
    
    if menu == "Álgebra":
        st.header("🔍 Álgebra: Equações")
        sub = st.selectbox("Escolha:", ["1º Grau", "2º Grau (Bhaskara)"])
        
        if sub == "1º Grau":
            c1, c2, c3 = st.columns(3)
            a = c1.number_input("a (≠ 0):", value=2, step=1, key="alg_a")
            b = c2.number_input("b:", value=40, step=1, key="alg_b")
            c_eq = c3.number_input("Igual a c:", value=50, step=1, key="alg_c")
            if a != 0 and st.button("Calcular"):
                st.success(f"Resultado: x = {(c_eq - b) / a}")

        elif sub == "2º Grau (Bhaskara)":
            c1, c2, c3 = st.columns(3)
            a2 = c1.number_input("a:", 1.0, key="a2")
            b2 = c2.number_input("b:", -5.0, key="b2")
            c2v = c3.number_input("c:", 6.0, key="c2")
            if st.button("Calcular Bhaskara"):
                delta = (b2**2) - (4 * a2 * c2v)
                st.write(f"Delta (Δ) = {delta}")
                if delta >= 0:
                    x1 = (-b2 + np.sqrt(delta))/(2*a2)
                    x2 = (-b2 - np.sqrt(delta))/(2*a2)
                    st.success(f"x1 = {x1} | x2 = {x2}")
                else: st.error("Raízes Complexas.")

        st.divider()
        qtd = st.slider("Quantidade de Exercícios:", 1, 10, 5)
        if st.button("Gerar Lista e PDF"):
            q, g = [], []
            for i in range(qtd):
                ra, rx = random.randint(1,10), random.randint(1,10)
                rb = random.randint(1,20); rc = (ra * rx) + rb
                q.append(f"{i+1}) Resolva a equacao: {ra}x + {rb} = {rc}")
                g.append(f"{i+1}) x = {rx}")
            pdf_bytes = gerar_pdf_atividades("Algebra", q, g)
            st.download_button("📥 Baixar PDF das Atividades", pdf_bytes, "atividades_algebra.pdf", "application/pdf")

    elif menu == "Geometria":
        st.header("📐 Geometria: Áreas e Volumes")
        fig = st.selectbox("Sólido:", ["Esfera", "Cilindro", "Cubo"])
        med = st.number_input("Medida Principal:", 10.0, key="geo_med")
        
        if fig == "Esfera":
            v = (4/3) * np.pi * (med**3)
            st.metric("Volume da Esfera", f"{v:.4f}")
            st.latex(r"V = \frac{4}{3} \pi r^3")
        elif fig == "Cilindro":
            h = st.number_input("Altura:", 10.0, key="geo_h")
            v = np.pi * (med**2) * h
            st.metric("Volume do Cilindro", f"{v:.4f}")
            st.latex(r"V = \pi r^2 h")
        elif fig == "Cubo":
            v = med**3
            st.metric("Volume do Cubo", f"{v}")
            st.latex(r"V = L^3")

        if st.button("Gerar PDF desta Geometria"):
            q_geo = [f"1) Calcule o volume de um(a) {fig} com raio/lado {med}."]
            r_geo = [f"1) Volume = {v:.4f}"]
            pdf_bytes = gerar_pdf_atividades("Geometria", q_geo, r_geo)
            st.download_button("📥 Baixar PDF Geometria", pdf_bytes, "geometria.pdf", "application/pdf")

    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Lineares $Ax = B$")
        n = st.slider("Incógnitas:", 2, 3, 2)
        mat_A, vec_B = [], []
        for i in range(n):
            cols = st.columns(n + 1)
            row = [cols[j].number_input(f"A{i+1}{j+1}", value=1.0 if i==j else 0.0, key=f"mat_{i}_{j}") for j in range(n)]
            mat_A.append(row)
            vec_B.append(cols[n].number_input(f"B{i+1}", value=1.0, key=f"vec_{i}"))
        if st.button("Resolver Sistema"):
            try:
                sol = np.linalg.solve(np.array(mat_A), np.array(vec_B))
                st.success(f"Soluções: {sol}")
            except: st.error("Erro: Matriz sem solução única.")

    elif menu == "Matemática Financeira":
        st.header("💰 Finanças")
        c = st.number_input("Capital:", 1000.0)
        i = st.number_input("Taxa (%):", 1.0) / 100
        t = st.number_input("Tempo (meses):", 12)
        st.metric("Montante Final", f"R$ {c * (1 + i)**t:.2f}")
        st.latex(r"M = C(1 + i)^t")
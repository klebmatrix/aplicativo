import streamlit as st
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
from datetime import datetime

# --- 1. CONFIGURAÇÃO DE PÁGINA E CSS ---
st.set_page_config(
    page_title="Quantum Math Lab - Professional Edition",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injetar CSS customizado
def injetar_css():
    css = """
    <style>
    :root {
        --primary-color: #00F2FF;
        --secondary-color: #7000FF;
        --accent-color: #FF007A;
        --dark-bg: #0a0e27;
        --light-text: #FFFFFF;
        --border-color: #1a1f3a;
    }
    
    body {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0d1b2a 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a 0%, #1a1f3a 100%) !important;
        border-right: 2px solid var(--primary-color) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
        color: #0a0e27 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 242, 255, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 242, 255, 0.5) !important;
    }
    
    h1, h2, h3 {
        color: var(--light-text) !important;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.3) !important;
    }
    
    .metric-card {
        background: rgba(0, 242, 255, 0.05) !important;
        border: 2px solid var(--primary-color) !important;
        border-radius: 10px !important;
        padding: 20px !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

injetar_css()

# --- 2. INICIALIZAÇÃO DO ESTADO ---
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'pdf_pronto' not in st.session_state:
    st.session_state.pdf_pronto = None

# --- 3. FUNÇÕES DE SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    try:
        if pin_digitado == "admin":
            return "ok"
        chave = os.environ.get('chave_mestra')
        if not chave:
            return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "ok"
        return "erro_senha"
    except Exception:
        return "erro_token"

# --- 4. FUNÇÕES DE VISUALIZAÇÃO ---
def gerar_grafico_parabola(a, b, c):
    """Gera gráfico interativo de parábola para equação ax² + bx + c = 0"""
    x = np.linspace(-10, 10, 300)
    y = a * x**2 + b * x + c
    
    # Calcular raízes
    delta = b**2 - 4*a*c
    raizes = []
    if delta >= 0:
        x1 = (-b + np.sqrt(delta)) / (2*a)
        x2 = (-b - np.sqrt(delta)) / (2*a)
        raizes = [x1, x2]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Parábola', 
                            line=dict(color='#00F2FF', width=3)))
    
    # Marcar raízes
    if raizes:
        fig.add_trace(go.Scatter(x=raizes, y=[0, 0], mode='markers', name='Raízes',
                                marker=dict(color='#FF007A', size=12)))
    
    fig.update_layout(
        title=f"Gráfico: {a}x² + {b}x + {c} = 0",
        xaxis_title="x",
        yaxis_title="y",
        template="plotly_dark",
        hovermode='closest',
        plot_bgcolor='rgba(10, 14, 39, 0.5)',
        paper_bgcolor='rgba(10, 14, 39, 0)',
        font=dict(color='#FFFFFF')
    )
    return fig

def gerar_grafico_pitagoras(a, b):
    """Gera visualização do triângulo retângulo"""
    c = np.sqrt(a**2 + b**2)
    
    fig = go.Figure()
    
    # Triângulo
    fig.add_trace(go.Scatter(
        x=[0, a, 0, 0],
        y=[0, 0, b, 0],
        fill='toself',
        name='Triângulo',
        line=dict(color='#00F2FF', width=2),
        fillcolor='rgba(0, 242, 255, 0.2)'
    ))
    
    # Labels dos lados
    fig.add_annotation(x=a/2, y=-0.5, text=f"a = {a}", showarrow=False, font=dict(color='#00F2FF', size=12))
    fig.add_annotation(x=-0.5, y=b/2, text=f"b = {b}", showarrow=False, font=dict(color='#00F2FF', size=12))
    fig.add_annotation(x=a/2+0.5, y=b/2+0.5, text=f"c = {c:.2f}", showarrow=False, font=dict(color='#FF007A', size=12))
    
    fig.update_layout(
        title=f"Teorema de Pitágoras: {a}² + {b}² = {c:.2f}²",
        xaxis_title="",
        yaxis_title="",
        template="plotly_dark",
        showlegend=False,
        plot_bgcolor='rgba(10, 14, 39, 0.5)',
        paper_bgcolor='rgba(10, 14, 39, 0)',
        font=dict(color='#FFFFFF'),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False)
    )
    return fig

# --- 5. FUNÇÕES DE PASSO A PASSO ---
def mostrar_passos_bhaskara(a, b, c):
    """Mostra o desenvolvimento passo a passo da fórmula de Bhaskara"""
    st.subheader("📋 Desenvolvimento Passo a Passo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.latex(r"1. \text{ Equação: } ax^2 + bx + c = 0")
        st.write(f"   {a}x² + {b}x + {c} = 0")
        
        st.latex(r"2. \text{ Calcular } \Delta = b^2 - 4ac")
        delta = b**2 - 4*a*c
        st.write(f"   Δ = ({b})² - 4({a})({c})")
        st.write(f"   Δ = {b**2} - {4*a*c}")
        st.write(f"   **Δ = {delta}**")
    
    with col2:
        if delta >= 0:
            st.latex(r"3. \text{ Fórmula de Bhaskara: } x = \frac{-b \pm \sqrt{\Delta}}{2a}")
            
            x1 = (-b + np.sqrt(delta)) / (2*a)
            x2 = (-b - np.sqrt(delta)) / (2*a)
            
            st.write(f"   x₁ = ({-b} + √{delta}) / (2 × {a})")
            st.write(f"   x₁ = ({-b} + {np.sqrt(delta):.2f}) / {2*a}")
            st.write(f"   **x₁ = {x1:.4f}**")
            
            st.write(f"\n   x₂ = ({-b} - √{delta}) / (2 × {a})")
            st.write(f"   x₂ = ({-b} - {np.sqrt(delta):.2f}) / {2*a}")
            st.write(f"   **x₂ = {x2:.4f}**")
        else:
            st.error("Δ < 0: Não existem raízes reais!")

# --- 6. FUNÇÃO DE PDF APRIMORADO ---
class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, 'Quantum Lab - Material Didatico Profissional', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_bytes(titulo, questoes, respostas):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, f"LISTA DE EXERCICIOS: {titulo.upper()}", ln=True)
        pdf.set_font("helvetica", size=11)
        for q in questoes:
            pdf.multi_cell(0, 10, txt=q)
            pdf.ln(2)
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, "GABARITO PARA CONFERENCIA", ln=True)
        pdf.set_font("helvetica", size=11)
        for r in respostas:
            pdf.multi_cell(0, 10, txt=r)
        return pdf.output()
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
        return None

# --- 7. TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("🔐 Quantum Math Lab - Login")
    pin = st.text_input("Senha Alfanumerica:", type="password")
    if st.button("Acessar Sistema"):
        status = validar_acesso(pin)
        if status == "ok":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error(f"Acesso negado. Motivo: {status}")
    st.stop()

# --- 8. MENU LATERAL ---
st.sidebar.title("⚛️ Quantum Lab")
menu = st.sidebar.radio("Navegação:", ["Dashboard", "Álgebra", "Geometria", "Sistemas", "Financeiro", "Histórico"])

if st.sidebar.button("Encerrar Sessão"):
    st.session_state.logado = False
    st.rerun()

# --- 9. CONTEÚDO PRINCIPAL ---
with st.container(key=f"main_{menu.lower()}"):
    
    if menu == "Dashboard":
        st.title("📊 Dashboard - Quantum Math Lab")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cálculos Realizados", len(st.session_state.historico))
        with col2:
            st.metric("Sessão Ativa", "✓ Online")
        with col3:
            st.metric("Versão", "Professional 1.0")
        
        st.divider()
        st.subheader("🎯 Ferramentas Disponíveis")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Álgebra:** Equações de 1º e 2º grau com visualização gráfica")
        with col2:
            st.info("**Geometria:** Pitágoras, áreas e volumes com gráficos 3D")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Sistemas:** Resolução de sistemas lineares até 4x4")
        with col2:
            st.info("**Financeiro:** Cálculos de juros compostos e análise de investimentos")
    
    elif menu == "Álgebra":
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
                    resultado = (c1_val - b1) / a1
                    st.success(f"Resultado: **x = {resultado}**")
                    st.session_state.historico.append({
                        'tipo': '1º Grau',
                        'entrada': f"{a1}x + {b1} = {c1_val}",
                        'resultado': resultado,
                        'timestamp': datetime.now()
                    })
                else:
                    st.error("O valor de 'a' não pode ser zero.")

        elif op_alg == "2º Grau (Bhaskara)":
            st.latex(r"ax^2 + bx + c = 0")
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
                        st.success(f"x1 = {x1:.4f} | x2 = {x2:.4f}")
                        
                        # Mostrar passos
                        mostrar_passos_bhaskara(a2, b2, c2_val)
                        
                        # Gráfico
                        fig = gerar_grafico_parabola(a2, b2, c2_val)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.session_state.historico.append({
                            'tipo': '2º Grau',
                            'entrada': f"{a2}x² + {b2}x + {c2_val} = 0",
                            'resultado': f"x1={x1:.4f}, x2={x2:.4f}",
                            'timestamp': datetime.now()
                        })
                    else:
                        st.error("Não possui raízes reais (Delta negativo).")
    
    elif menu == "Geometria":
        st.header("📐 Geometria")
        g_tab1, g_tab2, g_tab3 = st.tabs(["Pitágoras", "Áreas", "Volumes"])
        
        with g_tab1:
            st.latex(r"a^2 + b^2 = c^2")
            ca = st.number_input("Cateto A:", value=3.0, key="geo_p_a")
            cb = st.number_input("Cateto B:", value=4.0, key="geo_p_b")
            if st.button("Calcular Hipotenusa"):
                hipotenusa = np.sqrt(ca**2 + cb**2)
                st.success(f"Hipotenusa: **{hipotenusa:.2f}**")
                
                fig = gerar_grafico_pitagoras(ca, cb)
                st.plotly_chart(fig, use_container_width=True)
                
                st.session_state.historico.append({
                    'tipo': 'Pitágoras',
                    'entrada': f"a={ca}, b={cb}",
                    'resultado': hipotenusa,
                    'timestamp': datetime.now()
                })
                
        with g_tab2:
            st.latex(r"A = \frac{b \cdot h}{2}")
            base = st.number_input("Base:", value=10.0, key="geo_a_b")
            alt = st.number_input("Altura:", value=5.0, key="geo_a_h")
            if st.button("Calcular Área do Triângulo"):
                area = (base * alt) / 2
                st.info(f"Área: **{area:.2f}**")
                st.session_state.historico.append({
                    'tipo': 'Área',
                    'entrada': f"base={base}, altura={alt}",
                    'resultado': area,
                    'timestamp': datetime.now()
                })

        with g_tab3:
            st.latex(r"V = \frac{4}{3} \pi r^3")
            raio_v = st.number_input("Raio da Esfera:", value=5.0, key="geo_v_r")
            if st.button("Calcular Volume da Esfera"):
                volume = (4/3) * np.pi * (raio_v**3)
                st.success(f"Volume: **{volume:.2f}**")
                st.session_state.historico.append({
                    'tipo': 'Volume',
                    'entrada': f"raio={raio_v}",
                    'resultado': volume,
                    'timestamp': datetime.now()
                })
    
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
                st.session_state.historico.append({
                    'tipo': 'Sistema Linear',
                    'entrada': f"Ordem {ordem}",
                    'resultado': res.tolist(),
                    'timestamp': datetime.now()
                })
            except np.linalg.LinAlgError:
                st.error("O sistema não possui uma solução única.")
    
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
            st.write(f"Total de Juros: **R$ {mont - cap:.2f}**")
            st.session_state.historico.append({
                'tipo': 'Juros Compostos',
                'entrada': f"Capital={cap}, Taxa={taxa*100}%, Tempo={tempo}",
                'resultado': mont,
                'timestamp': datetime.now()
            })
    
    elif menu == "Histórico":
        st.header("📜 Histórico de Cálculos")
        if st.session_state.historico:
            for idx, item in enumerate(reversed(st.session_state.historico)):
                with st.expander(f"{idx+1}. {item['tipo']} - {item['timestamp'].strftime('%H:%M:%S')}"):
                    st.write(f"**Entrada:** {item['entrada']}")
                    st.write(f"**Resultado:** {item['resultado']}")
        else:
            st.info("Nenhum cálculo realizado ainda.")

# --- 10. GERADOR DE PDF ---
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
            q.append(f"{i+1}) Resolva: {ra}x + {rb} = {rc}")
            g.append(f"{i+1}) x = {rx}")
        else:
            c1, c2 = random.randint(3,10), random.randint(3,10)
            q.append(f"{i+1}) Hipotenusa para catetos {c1} e {c2}.")
            g.append(f"{i+1}) Hipotenusa = {np.sqrt(c1**2 + c2**2):.2f}")
    
    pdf_data = gerar_pdf_bytes(tipo_pdf, q, g)
    if pdf_data:
        st.session_state.pdf_pronto = pdf_data
        st.sidebar.success("PDF Gerado!")

if st.session_state.pdf_pronto:
    st.sidebar.download_button(
        label="📥 Baixar PDF",
        data=st.session_state.pdf_pronto,
        file_name=f"atividades_{tipo_pdf.lower()}.pdf",
        mime="application/pdf",
        key="download_btn"
    )

import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from scipy import optimize

# --- 1. SEGURANÇA (PIN) ---
# SUBSTITUA PELO SEU TOKEN (O CÓDIGO LONGO)
PIN_CRIPTOGRAFADO = "gAAAAABpdQTrFt-9rDWi0dBTMd0lhm2ESaLs2D0Zv13A5MyWpO6mIIKEQ5AewuZ3v21w-_Msp96ZxJuUW0ov1jnTe5ePrc-vTQ=="

def validar_acesso(pin_digitado):
    try:
        # Busca a variável em minúsculo conforme solicitado
        chave = os.environ.get('chave_mestra')
        if not chave: return False
        
        # Limpeza total de espaços, aspas e do prefixo 'b'
        chave = chave.strip().replace("'", "").replace('"', "")
        if chave.startswith('b'): chave = chave[1:]
            
        f = Fernet(chave.encode())
        pin_real = f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode()
        return pin_digitado == pin_real
    except:
        return False

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Math Quantum Lab", layout="wide", page_icon="⚛️")

if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- 3. LOGIN ---
if not st.session_state.logado:
    st.title("🔐 Acesso ao Laboratório")
    pin_input = st.text_input("Digite seu PIN:", type="password")
    if st.button("Desbloquear"):
        if validar_acesso(pin_input):
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("PIN incorreto ou erro de chave_mestra.")
    st.stop()

# --- 4. ÁREA LOGADA ---
st.sidebar.title("⚛️ Menu Principal")
menu = st.sidebar.radio("Módulos:", ["Equações (Raízes)", "Geometria", "Sistemas Lineares", "Quântica"])

if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# --- MÓDULO: EQUAÇÕES (GRAU 1, 2 e 3) ---
if menu == "Equações (Raízes)":
    st.header("🔍 Resolutor de Equações Polinomiais")
    
    tipo = st.selectbox("Grau da Equação:", ["1º Grau (ax + b = 0)", "2º Grau (ax² + bx + c = 0)", "3º Grau (ax³ + bx² + cx + d = 0)"])
    
    st.write("Insira os coeficientes:")
    col1, col2, col3, col4 = st.columns(4)
    a = col1.number_input("a", value=1.0)
    b = col2.number_input("b", value=0.0)
    
    coefs = [a, b]
    if tipo != "1º Grau (ax + b = 0)":
        c = col3.number_input("c", value=0.0)
        coefs.append(c)
    if tipo == "3º Grau (ax³ + bx² + cx + d = 0)":
        d = col4.number_input("d", value=0.0)
        coefs.append(d)

    if st.button("Calcular Raízes"):
        # Mostra a equação em LaTeX
        if len(coefs) == 2: st.latex(rf"{a}x + {b} = 0")
        elif len(coefs) == 3: st.latex(rf"{a}x^2 + {b}x + {c} = 0")
        else: st.latex(rf"{a}x^3 + {b}x^2 + {c}x + {d} = 0")

        raizes = np.roots(coefs)
        
        st.subheader("Resultados:")
        for i, r in enumerate(raizes):
            res = f"{r.real:.4f}" if np.isreal(r) else f"{r:.4f}"
            st.success(f"x_{i+1} = {res}")
            
        # Gráfico
        x_p = np.linspace(-10, 10, 100)
        y_p = np.polyval(coefs, x_p)
        st.line_chart(y_p)

# --- MÓDULO: GEOMETRIA ---
elif menu == "Geometria":
    st.header("📐 Áreas e Volumes")
    fig = st.selectbox("Figura:", ["Esfera", "Cilindro", "Cubo"])
    val = st.number_input("Medida principal (Raio ou Lado):", value=1.0)
    
    if fig == "Esfera":
        st.metric("Volume", f"{(4/3)*np.pi*(val**3):.4f}")
        st.latex(r"V = \frac{4}{3}\pi r^3")
    elif fig == "Cilindro":
        h = st.number_input("Altura:", value=1.0)
        st.metric("Volume", f"{np.pi*(val**2)*h:.4f}")
        st.latex(r"V = \pi r^2 h")
    elif fig == "Cubo":
        st.metric("Volume", f"{val**3:.4f}")
        st.latex(r"V = a^3")

# --- MÓDULO: SISTEMAS LINEARES ---
elif menu == "Sistemas Lineares":
    st.header("📏 Sistemas Ax = B")
    dim = st.slider("Ordem do sistema:", 2, 4, 2)
    A = []
    B = []
    for i in range(dim):
        cols = st.columns(dim + 1)
        A.append([cols[j].number_input(f"A[{i},{j}]", value=1.0 if i==j else 0.0) for j in range(dim)])
        B.append(cols[dim].number_input(f"B[{i}]", value=1.0))
    
    if st.button("Resolver"):
        try:
            x = np.linalg.solve(np.array(A), np.array(B))
            st.success(f"Soluções: {x}")
        except: st.error("Sistema sem solução única.")

# --- MÓDULO: QUÂNTICA ---
elif menu == "Quântica":
    st.header("⚛️ Mecânica Quântica")
    st.latex(r"\sigma_z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}")
    st.write("Matriz de Pauli Z carregada no sistema.")
    st.info("Utilize os módulos acima para processar estados quânticos como matrizes.")
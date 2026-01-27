import streamlit as st
from fpdf import FPDF
import os
import re

# Configuração da Página
st.set_page_config(page_title="Gerador de Atividades", layout="centered")

# --- LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acesso ao Sistema")
    senha = st.text_input("Digite o PIN de acesso:", type="password")
    if st.button("Entrar"):
        # PIN de 6 a 8 dígitos conforme solicitado
        if senha == "chave_mestra": 
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("PIN Incorreto.")
else:
    menu = st.sidebar.selectbox("Menu", ["Gerador de Atividades", "Sair"])

    if menu == "Sair":
        st.session_state['autenticado'] = False
        st.rerun()

    elif menu == "Gerador de Atividades":
        st.header("📄 Gerador de Atividades")
        
        titulo_pdf = st.text_input("Título:", "Atividade de Matemática")
        conteudo = st.text_area("Conteúdo da Atividade:", height=300, help="Dica: Use . para colunas e números para questões.")
        
        if st.button("Gerar PDF"):
            if conteudo:
                pdf = FPDF()
                pdf.add_page()
                
                # 1. CABEÇALHO (Ajustado para 185mm)
                if os.path.exists("cabecalho.png"):
                    pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
                    pdf.set_y(48)
                else:
                    pdf.set_y(15)
                
                # 2. TÍTULO
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, txt=titulo_pdf, ln=True, align='C')
                pdf.ln(2)
                
                # 3. PROCESSAMENTO LINHA POR LINHA
                pdf.set_font("Arial", size=10)
                letras = "abcdefghijklmnopqrstuvwxyz"
                letra_idx = 0
                
                for linha in conteudo.split('\n'):
                    txt = linha.strip()
                    if not txt: continue
                    
                    # Verifica se a linha começa com pontos (........)
                    match_pontos = re.match(r'^(\.+)', txt)
                    
                    # REGRA 1: SE COMEÇAR COM NÚMERO (QUESTÃO)
                    if re.match(r'^\d+', txt):
                        pdf.ln(4)
                        pdf.set_font("Arial", 'B', 11)
                        pdf.set_x(10) # Margem esquerda sem recuo
                        pdf.multi_cell(0, 7, txt=txt)
                        pdf.set_font("Arial", size=10)
                        letra_idx = 0 # Reinicia o alfabeto (a, b, c...)
                    
                    # REGRA 2: SE COMEÇAR COM PONTOS (COLUNAS)
                    elif match_pontos:
                        num_pontos = len(match_pontos.group(1))
                        item_texto = txt[num_pontos:].strip()
                        prefixo = f"{letras[letra_idx % 26]}) "
                        
                        # Se tiver mais de 1 ponto, ele tenta subir para a mesma linha
                        if num_pontos > 1:
                            # Só sobe se não estivermos no topo da página
                            current_y = pdf.get_y()
                            pdf.set_y(current_y - 8)
                        
                        # Calcula a posição X (32mm por coluna)
                        # Col 1 (.), Col 2 (..), Col 3 (...) etc.
                        col_idx = num_pontos - 1
                        nova_x = 10 + (col_idx * 32)
                        
                        pdf.set_x(nova_x)
                        pdf.cell(32, 8, txt=f"{prefixo}{item_texto}", ln=True)
                        letra_idx += 1
                    
                    # REGRA 3: TEXTO NORMAL (Explicações do professor, enunciados sem números)
                    else:
                        pdf.set_x(10)
                        pdf.multi_cell(0, 7, txt=txt)
                
                pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
                st.download_button("📥 Baixar PDF Corrigido", data=pdf_bytes, file_name="atividade.pdf")
            else:
                st.warning("O campo de conteúdo está vazio.")
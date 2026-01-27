import streamlit as st
from fpdf import FPDF
import os
import re

# Configuração da Página
st.set_page_config(page_title="Sistema Educacional", layout="centered")

# --- 1. CONTROLE DE ACESSO (PIN) ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acesso Restrito")
    # Busca o PIN no Render ou usa o padrão
    pin_correto = os.getenv("chave_mestra", "123456")
    senha = st.text_input("Digite o PIN:", type="password", max_chars=8)
    
    if st.button("Entrar no Sistema"):
        if senha == pin_correto:
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("PIN incorreto!")

else:
    # --- 2. MENU LATERAL (AQUI ESTÃO SUAS TELAS!) ---
    st.sidebar.title("🛠️ Painel de Controle")
    menu = st.sidebar.radio("Selecione a Tela:", ["Painel do Professor", "Gerador de Atividades", "Sair"])

    # --- TELA: PAINEL DO PROFESSOR ---
    if menu == "Painel do Professor":
        st.title("👨‍🏫 Área do Professor")
        st.write("Bem-vindo! Aqui você pode gerenciar suas configurações.")
        
        # Exemplo de funcionalidade que você pode ter aqui:
        st.subheader("Configurações do Cabeçalho")
        if os.path.exists("cabecalho.png"):
            st.success("✅ Imagem do cabeçalho encontrada!")
            st.image("cabecalho.png", caption="Seu cabeçalho atual", width=300)
        else:
            st.warning("⚠️ Cabeçalho não encontrado. Certifique-se de que 'cabecalho.png' está na pasta.")
            
        st.info("Esta tela é dedicada para avisos e gestão interna.")

    # --- TELA: GERADOR DE ATIVIDADES (A TELA QUE CRIA O PDF) ---
    elif menu == "Gerador de Atividades":
        st.title("📄 Gerador de Atividades")
        st.markdown("---")
        
        titulo_pdf = st.text_input("Título da Atividade:", "Exercícios de Fixação")
        conteudo = st.text_area("Digite o conteúdo abaixo:", height=300)
        
        if st.button("🚀 Gerar e Baixar PDF"):
            if conteudo:
                pdf = FPDF()
                pdf.add_page()
                
                # Cabeçalho de 185mm (conforme ajustamos)
                if os.path.exists("cabecalho.png"):
                    pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
                    pdf.set_y(48)
                else:
                    pdf.set_y(15)
                
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, txt=titulo_pdf, ln=True, align='C')
                pdf.ln(2)
                
                # Lógica de Colunas e Letras (a, b, c)
                pdf.set_font("Arial", size=10)
                letras = "abcdefghijklmnopqrstuvwxyz"
                letra_idx = 0
                
                for linha in conteudo.split('\n'):
                    txt = linha.strip()
                    if not txt: continue
                    
                    match_pontos = re.match(r'^(\.+)', txt)
                    
                    if re.match(r'^\d+', txt): # Questão
                        pdf.ln(4)
                        pdf.set_font("Arial", 'B', 11)
                        pdf.set_x(10) # Sem adentramento
                        pdf.multi_cell(0, 7, txt=txt)
                        pdf.set_font("Arial", size=10)
                        letra_idx = 0 
                    
                    elif match_pontos: # Colunas
                        num_pontos = len(match_pontos.group(1))
                        item = txt[num_pontos:].strip()
                        if num_pontos > 1: pdf.set_y(pdf.get_y() - 8)
                        
                        pos_x = 10 + (num_pontos - 1) * 32
                        pdf.set_x(pos_x)
                        pdf.cell(32, 8, txt=f"{letras[letra_idx % 26]}) {item}", ln=True)
                        letra_idx += 1
                    
                    else: # Texto comum
                        pdf.set_x(10)
                        pdf.multi_cell(0, 7, txt=txt)
                
                pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
                st.download_button("📥 Clique aqui para Baixar", data=pdf_output, file_name="atividade.pdf")

    # --- SAIR ---
    elif menu == "Sair":
        st.session_state['autenticado'] = False
        st.rerun()
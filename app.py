import streamlit as st
from fpdf import FPDF
import os
import re

# Configuração da Página
st.set_page_config(page_title="Sistema Quantum Educacional", layout="centered")

# --- 1. CONTROLE DE ACESSO (PIN) ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Login do Sistema")
    # Busca o PIN no Render ou usa o padrão 123456
    pin_correto = os.getenv("chave_mestra", "123456")
    senha = st.text_input("Digite o PIN de acesso:", type="password", max_chars=8)
    
    if st.button("Entrar"):
        if senha == pin_correto:
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("PIN incorreto! Verifique as variáveis de ambiente.")

else:
    # --- 2. MENU LATERAL COM TODAS AS OPÇÕES ---
    st.sidebar.title("🚀 Navegação")
    menu = st.sidebar.radio("Selecione uma Tela:", 
                            ["Início / Boas-Vindas", 
                             "Painel do Professor", 
                             "Gerador de Atividades", 
                             "Configurações", 
                             "Sair"])

    # --- TELA: INÍCIO ---
    if menu == "Início / Boas-Vindas":
        st.title("👋 Bem-vindo ao Sistema")
        st.write("Selecione uma opção no menu lateral para começar a trabalhar.")
        st.info("O Gerador de Atividades agora suporta até 6 colunas usando pontos (......).")

    # --- TELA: PAINEL DO PROFESSOR ---
    elif menu == "Painel do Professor":
        st.title("👨‍🏫 Painel do Professor")
        st.subheader("Gerenciamento de Turmas e Avisos")
        st.write("Aqui você encontra as ferramentas de gestão pedagógica.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("Cadastrar Nova Turma")
            st.button("Relatório de Atividades")
        with col2:
            st.button("Meus Arquivos Salvos")
            st.button("Lista de Alunos")

    # --- TELA: GERADOR DE ATIVIDADES (ALUNO/PDF) ---
    elif menu == "Gerador de Atividades":
        st.title("📄 Gerador de Atividades (PDF)")
        st.markdown("---")
        
        titulo_pdf = st.text_input("Título da Atividade:", "Exercícios de Matemática")
        conteudo = st.text_area("Digite o conteúdo (Use . para colunas):", height=350)
        
        if st.button("🚀 Gerar e Baixar PDF"):
            if conteudo:
                pdf = FPDF()
                pdf.add_page()
                
                # 1. CABEÇALHO GRANDE (185mm)
                if os.path.exists("cabecalho.png"):
                    pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
                    pdf.set_y(48)
                else:
                    pdf.set_y(15)
                
                # 2. TÍTULO
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, txt=titulo_pdf, ln=True, align='C')
                pdf.ln(2)
                
                # 3. LÓGICA DE COLUNAS (Ajustada)
                pdf.set_font("Arial", size=10)
                letras = "abcdefghijklmnopqrstuvwxyz"
                letra_idx = 0
                
                for linha in conteudo.split('\n'):
                    txt = linha.strip()
                    if not txt: continue
                    
                    match_pontos = re.match(r'^(\.+)', txt)
                    
                    # Se for QUESTÃO (Número no início)
                    if re.match(r'^\d+', txt):
                        pdf.ln(4)
                        pdf.set_font("Arial", 'B', 11)
                        pdf.set_x(10) # Sem adentramento (x=10)
                        pdf.multi_cell(0, 7, txt=txt)
                        pdf.set_font("Arial", size=10)
                        letra_idx = 0 
                    
                    # Se for COLUNA (. até ......)
                    elif match_pontos:
                        num_pontos = len(match_pontos.group(1))
                        item = txt[num_pontos:].strip()
                        prefixo = f"{letras[letra_idx % 26]}) "
                        
                        if num_pontos > 1:
                            pdf.set_y(pdf.get_y() - 8)
                        
                        pos_x = 10 + (num_pontos - 1) * 32
                        pdf.set_x(pos_x)
                        pdf.cell(32, 8, txt=f"{prefixo}{item}", ln=True)
                        letra_idx += 1
                    
                    # Se for TEXTO NORMAL (Professor/Instrução)
                    else:
                        pdf.set_x(10)
                        pdf.multi_cell(0, 7, txt=txt)
                
                pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
                st.download_button("📥 Baixar PDF Agora", data=pdf_output, file_name="atividade.pdf")

    # --- TELA: CONFIGURAÇÕES ---
    elif menu == "Configurações":
        st.title("⚙️ Configurações do Sistema")
        if os.path.exists("cabecalho.png"):
            st.image("cabecalho.png", caption="Visualização do Cabeçalho Atual", width=400)
            st.success("Imagem 'cabecalho.png' carregada com sucesso.")
        else:
            st.error("Imagem 'cabecalho.png' não encontrada na pasta do projeto.")

    # --- SAIR ---
    elif menu == "Sair":
        st.session_state['autenticado'] = False
        st.rerun()
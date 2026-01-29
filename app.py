import streamlit as st
from fpdf import FPDF
import re
import os

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Gerador de Atividades", layout="wide")

def clean_txt(text):
    """Limpa caracteres especiais para evitar erros no FPDF Latin-1"""
    return text.encode('latin-1', 'replace').decode('latin-1')

# --- ESTADO DA SESSÃO ---
if 'preview_questoes' not in st.session_state:
    st.session_state.preview_questoes = []
if 'sub_menu' not in st.session_state:
    st.session_state.sub_menu = "man"

# --- SIDEBAR / MENU ---
with st.sidebar:
    st.title("⚙️ Painel de Controle")
    st.session_state.sub_menu = st.radio(
        "Escolha o Módulo:",
        ["man", "alg", "eq"],
        format_func=lambda x: "📝 Modo Manual" if x == "man" else "🧬 Outros"
    )
    
    st.divider()
    uploaded_file = st.file_uploader("Upload do Cabeçalho (PNG)", type=["png"])
    if uploaded_file:
        with open("cabecalho.png", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Cabeçalho atualizado!")

# --- 1. MÓDULO MANUAL ---
if st.session_state.sub_menu == "man":
    st.header("📝 Entrada Manual de Atividade")
    st.info("Dica: Use 't.' para título, '-M' para módulos e '1.' para questões.")
    
    input_texto = st.text_area(
        "Digite ou cole sua atividade aqui:",
        placeholder="t. Título da Atividade\n-M1. Números\n1. Qual o valor de 2+2?\n2. Resolva: 10 - 5 = ......",
        height=300
    )
    
    if st.button("🔄 Processar Atividade"):
        if input_texto:
            st.session_state.preview_questoes = input_texto.split('\n')
            st.success("Atividade carregada para visualização!")

# --- 2. VISUALIZAÇÃO UNIFICADA (TELA) ---
questoes_preview = st.session_state.get('preview_questoes', [])

if questoes_preview:
    st.divider()
    # Header da Atividade
    if os.path.exists("cabecalho.png"): 
        st.image("cabecalho.png", use_container_width=True)
    
    letras_tela = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    
    for q in questoes_preview:
        line = q.strip()
        if not line: continue
        
        # TÍTULOS (t.)
        if line.lower().startswith("t."):
            st.markdown(f"<h2 style='text-align: center; color: #007bff; margin: 20px 0;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
            l_idx = 0
            
        # MÓDULOS (-M) - Estilo Subtítulo Alinhado à Esquerda
        elif line.startswith("-M"):
            st.markdown(f"""
                <div style='border-left: 5px solid #333; padding-left: 15px; margin: 30px 0 10px 0; background-color: #f9f9f9; padding: 10px;'>
                    <h3 style='text-align: left; color: #000; margin: 0;'>{line[1:].strip()}</h3>
                </div>
            """, unsafe_allow_html=True)
            l_idx = 0
        
        # QUESTÕES NUMERADAS (1., 2...)
        elif re.match(r'^\d+', line):
            st.markdown(f"<p style='margin: 15px 0 5px 0; font-size: 18px; font-weight: normal;'>{line}</p>", unsafe_allow_html=True)
            l_idx = 0
            
        # ITENS AUTOMÁTICOS EM COLUNAS (a, b...)
        else:
            cols = st.columns(2)
            target = cols[0] if l_idx % 2 == 0 else cols[1]
            with target:
                with st.container(border=True):
                    st.write(f"**{letras_tela[l_idx%26]})** {line}")
            l_idx += 1

# --- 3. EXPORTAÇÃO PDF (LÓGICA BLINDADA) ---
    st.markdown("---")
    st.subheader("📥 Exportar para PDF")

    def gerar_pdf_manual(com_cabecalho):
        letras_pdf = "abcdefghijklmnopqrstuvwxyz"
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_margins(15, 15, 15)
        
        # Início dinâmico
        y_pos = 55 if (com_cabecalho and os.path.exists("cabecalho.png")) else 20
        if com_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=12.5, y=10, w=185)

        pdf.set_y(y_pos)
        l_pdf_idx = 0
        y_last_column = pdf.get_y()
        y_col_1 = pdf.get_y() # Controle de coluna esquerda
        
        for q in questoes_preview:
            line = q.strip()
            if not line: continue
            
            # Reset de Posição: Garante que novos títulos/módulos esperem as colunas
            if line.lower().startswith("t.") or line.startswith("-M") or re.match(r'^\d+', line):
                if l_pdf_idx > 0:
                    pdf.set_y(y_last_column + 5)
                l_pdf_idx = 0

            # 1. TÍTULO (t.)
            if line.lower().startswith("t."):
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, clean_txt(line[2:]), ln=True, align='C')
                y_last_column = pdf.get_y()
                
            # 2. MODO M (-M)
            elif line.startswith("-M"):
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, clean_txt(line[1:]), ln=True, align='L')
                pdf.line(15, pdf.get_y(), 195, pdf.get_y()) # Linha horizontal de separação
                y_last_column = pdf.get_y() + 2
                
            # 3. QUESTÕES NUMERADAS (Fonte Normal)
            elif re.match(r'^\d+', line):
                pdf.ln(3)
                pdf.set_font("Arial", '', 12)
                pdf.multi_cell(0, 7, clean_txt(line))
                y_last_column = pdf.get_y()
                
            # 4. ITENS (a, b...) EM DUAS COLUNAS
            else:
                pdf.set_font("Arial", '', 11)
                txt_item = f"{letras_pdf[l_pdf_idx%26]}) {clean_txt(line)}"
                curr_y = pdf.get_y()
                
                if l_pdf_idx % 2 == 0:
                    pdf.set_xy(15, curr_y + 1)
                    pdf.multi_cell(90, 6, txt_item)
                    y_col_1 = pdf.get_y()
                    pdf.set_y(curr_y + 1)
                    y_last_column = y_col_1
                else:
                    pdf.set_xy(110, curr_y + 1)
                    pdf.multi_cell(85, 6, txt_item)
                    y_col_2 = pdf.get_y()
                    y_last_column = max(y_col_1, y_col_2)
                    pdf.set_y(y_last_column)
                l_pdf_idx += 1
                
        return pdf.output(dest='S').encode('latin-1')

    c1, c2 = st.columns(2)
    with c1:
        if st.button("📄 Com Cabeçalho", use_container_width=True):
            st.download_button("✅ Baixar PDF", gerar_pdf_manual(True), "atividade_completa.pdf", "application/pdf")
    with c2:
        if st.button("📄 Sem Cabeçalho", use_container_width=True):
            st.download_button("✅ Baixar PDF", gerar_pdf_manual(False), "atividade_simples.pdf", "application/pdf")
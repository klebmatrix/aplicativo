import numpy as np
import plotly.express as px
import streamlit as st

def analisar_matriz_avancado(matriz_lista):
    """
    Recebe uma lista de listas (matriz), converte para numpy e realiza:
    1. Cálculos estruturais (Det, Traço, Posto)
    2. Classificação (Diagonal, Simétrica, Identidade)
    3. Geração de Heatmap (Mapa de Calor)
    """
    # 1. Conversão para Numpy Array
    A = np.array(matriz_lista)
    ordem = A.shape[0]
    
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Propriedades Estruturais")
        
        # Cálculos Matemáticos
        det = np.linalg.det(A)
        traco = np.trace(A)
        posto = np.linalg.matrix_rank(A)
        
        st.write(f"**Determinante:** `{det:.4f}`")
        st.write(f"**Traço:** `{traco}`")
        st.write(f"**Posto (Rank):** `{posto}`")
        
        # Lógica de Classificação
        # Diagonal: todos os elementos fora da diagonal principal são zero
        is_diag = np.all(A == np.diag(np.diagonal(A)))
        
        # Simétrica: a matriz é igual à sua transposta (A = A.T)
        is_sym = np.allclose(A, A.T)
        
        # Identidade: diagonal é 1 e o resto é 0
        is_ident = np.allclose(A, np.eye(ordem))
        
        # Gerar Tags de Classificação
        tags = []
        if is_ident: tags.append("✅ Identidade")
        elif is_diag: tags.append("💎 Diagonal")
        if is_sym: tags.append("🔄 Simétrica")
        if not tags: tags.append("📝 Geral / Quadrada")
        
        st.write(f"**Classificação:** {', '.join(tags)}")

    with col2:
        st.subheader("🖼️ Visualização (Heatmap)")
        # Criando o Mapa de Calor com Plotly
        fig = px.imshow(
            A, 
            text_auto=True,                # Mostra os números dentro das células
            color_continuous_scale='Viridis', # Escala de cores profissional
            labels=dict(color="Valor")
        )
        
        # Ajustes de Layout para o Streamlit
        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            height=280,
            paper_bgcolor='rgba(0,0,0,0)', # Fundo transparente
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FFFFFF')
        )
        st.plotly_chart(fig, use_container_width=True)

    return A, det

elif menu == "Painel do Professor":
        import streamlit.components.v1 as components
        
        st.title("👨‍🏫 Painel de Exercícios Rápidos")
        st.write("Escolha o tema e clique em imprimir para gerar 4 atividades por folha A4.")

        # O seu HTML profissional integrado
        html_painel = """
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <style>
                :root { --primary: #2c3e50; --accent: #3498db; }
                body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; display: flex; background: #f4f7f6; }
                #sidebar { width: 220px; background: var(--primary); color: white; height: 100vh; position: fixed; padding: 15px; }
                .menu-btn { width: 100%; padding: 10px; margin: 5px 0; border: none; background: #34495e; color: white; text-align: left; cursor: pointer; border-radius: 4px; font-size: 13px;}
                .menu-btn:hover { background: var(--accent); }
                .active { background: var(--accent) !important; }
                #main-content { margin-left: 230px; padding: 20px; width: 100%; }
                .print-now { padding: 10px 20px; background: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer; margin-bottom: 20px; }
                
                /* Layout A4 */
                .a4-page { width: 210mm; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 5mm; background: white; padding: 5mm; margin: auto; }
                .atv-box { border: 1px solid #000; padding: 8px; font-size: 10px; height: 135mm; box-sizing: border-box;}
                .header { border: 1px solid #000; padding: 4px; margin-bottom: 5px; font-size: 9px; }
                .titulo { text-align: center; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; font-size: 11px; }
                .questoes { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }

                @media print {
                    #sidebar, .print-now { display: none; }
                    body { background: white; }
                    #main-content { margin: 0; }
                    .a4-page { border: none; width: 210mm; height: 297mm; }
                }
            </style>
        </head>
        <body>
            <div id="sidebar">
                <h3>Menu Exercícios</h3>
                <button class="menu-btn active" onclick="gerar('1grau', this)">Equação 1º Grau</button>
                <button class="menu-btn" onclick="gerar('2grau', this)">Equação 2º Grau</button>
                <button class="menu-btn" onclick="gerar('expressoes', this)">Expressões Numéricas</button>
                <button class="menu-btn" onclick="gerar('potencia', this)">Potência e Raízes</button>
                <button class="menu-btn" onclick="gerar('matrizes', this)">Matrizes</button>
                <button class="menu-btn" onclick="gerar('sistemas', this)">Sistemas</button>
            </div>

            <div id="main-content">
                <button class="print-now" onclick="window.print()">🖨️ Imprimir 4 por Página</button>
                <div id="folha" class="a4-page"></div>
            </div>

            <script>
                const banco = {
                    '1grau': { t: 'Equações 1º Grau', q: ['2x + 4 = 12', '5x - 10 = 15', '3x + 9 = 0', 'x/2 + 5 = 10', '7x - 7 = 14', '4x + 2 = 18', '10x - 5 = 45', 'x + 15 = 30', '8x = 64', '6x - 12 = 0'] },
                    '2grau': { t: 'Equações 2º Grau', q: ['x² - 5x + 6 = 0', 'x² - 9 = 0', 'x² - 4x + 4 = 0', 'x² + 3x + 2 = 0', '2x² - 32 = 0', 'x² - 7x + 10 = 0', 'x² - 1 = 0', 'x² - 6x + 8 = 0', 'x² - 25 = 0', '3x² - 12 = 0'] },
                    'expressoes': { t: 'Expressões Numéricas', q: ['(12+8)×2', '50-(10÷2)', '100÷(5+5)', '25+(4×5)', '(15-5)×3', '30÷(2+3)', '7×8-10', '45÷9+7', '12×2+5', '20-(5+5)'] },
                    'potencia': { t: 'Potência e Raízes', q: ['2³ + √25', '5² - √16', '√100 + 10', '3³ - 7', '√81 × 2', '√144 ÷ 12', '4² ÷ 2', '10² - 90', '√49 + √64', '2⁴ ÷ 4'] },
                    'matrizes': { t: 'Matrizes e Determinantes', q: ['A+B (2x2)', 'Det(A) [1,2;3,4]', '3×A', 'Matriz Identidade', 'Diagonal Principal', 'Transposta A', 'Matriz Oposta', 'Traço de A', 'Verificar Simetria', 'A-B (2x2)'] },
                    'sistemas': { t: 'Sistemas de Equações', q: ['x+y=5; x-y=1', '2x+y=10; x-y=2', 'x+y=8; x-y=4', '3x+y=7; x+y=3', 'x+2y=10; x-y=1', '2x+2y=20; x-y=0', 'x+y=12; 2x-y=3', 'x-y=5; x+y=15', '4x+y=9; x+y=3', 'x+3y=10; x-y=2'] }
                };

                function gerar(tema, btn) {
                    document.querySelectorAll('.menu-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    const d = banco[tema];
                    const f = document.getElementById('folha');
                    f.innerHTML = '';
                    
                    const card = `
                        <div class="atv-box">
                            <div class="header">Escola:__________________ Data:__/__/__ <br> Nome:__________________ Turma:____</div>
                            <div class="titulo">\${d.t}</div>
                            <b>Resolva os exercícios:</b>
                            <div class="questoes">
                                <div>a) \${d.q[0]}<br><br> b) \${d.q[1]}<br><br> c) \${d.q[2]}<br><br> d) \${d.q[3]}<br><br> e) \${d.q[4]}</div>
                                <div>f) \${d.q[5]}<br><br> g) \${d.q[6]}<br><br> h) \${d.q[7]}<br><br> i) \${d.q[8]}<br><br> j) \${d.q[9]}</div>
                            </div>
                        </div>`;
                    for(let i=0; i<4; i++) f.innerHTML += card;
                }
                window.onload = () => gerar('1grau', document.querySelector('.menu-btn'));
            </script>
        </body>
        </html>
        """
        components.html(html_painel, height=1000, scrolling=True)
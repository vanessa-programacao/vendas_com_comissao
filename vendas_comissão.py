import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Calculadora de Comissão de Vendas")

st.write("""
Este app permite que você faça upload da sua planilha Excel de vendas,
calcule as comissões descontando o imposto que você informar,
visualize gráficos e baixe o arquivo com os resultados.
""")

# Campo para o usuário informar o percentual do imposto
imposto_percentual = st.number_input(
    "Informe o percentual do imposto sobre a comissão (%)",
    min_value=0.0, max_value=100.0, value=5.0, step=0.1)

uploaded_file = st.file_uploader("Faça upload da planilha Excel de vendas", type=['xlsx', 'xls'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # Validar colunas essenciais
        col_esperadas = ['Vendedor', 'Cliente', 'Produto', 'Quantidade', 'Preço Unitário', 'Total Venda', 'Comissão (%)']
        faltando = [c for c in col_esperadas if c not in df.columns]
        if faltando:
            st.error(f"Colunas faltando na planilha: {faltando}")
        else:
            # Calcular comissões com imposto dinâmico
            df['Comissão Bruta'] = df['Total Venda'] * df['Comissão (%)'] / 100
            df['Comissão Líquida'] = df['Comissão Bruta'] * (1 - imposto_percentual / 100)

            st.subheader("Tabela com Comissões Calculadas")
            st.dataframe(df)

            # Gráfico: vendas por vendedor
            vendas_por_vendedor = df.groupby('Vendedor')['Total Venda'].sum().sort_values(ascending=False)
            st.subheader("Vendas Totais por Vendedor")
            st.bar_chart(vendas_por_vendedor)

            # Gráfico: produtos mais vendidos por quantidade
            produtos_mais_vendidos = df.groupby('Produto')['Quantidade'].sum().sort_values(ascending=False)
            st.subheader("Produtos Mais Vendidos (Quantidade)")
            st.bar_chart(produtos_mais_vendidos)

            # Criar arquivo Excel para download
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Comissões')
            data = output.getvalue()

            st.download_button(
                label="Baixar arquivo com comissões calculadas",
                data=data,
                file_name='vendas_com_comissao.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Faça upload da planilha para começar.")

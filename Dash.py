import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
import tempfile
from fpdf import FPDF

# Função para gerar o PDF
def export_to_pdf(dataframe, filename="dados_agro.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Adicionar marca d'água
    pdf.set_font("Arial", "B", 40)
    pdf.set_text_color(200, 200, 200)  # Cor cinza claro para a marca d'água
    page_width = pdf.w - 2 * pdf.l_margin  # Largura da página menos as margens
    page_height = pdf.h - 2 * pdf.t_margin  # Altura da página menos as margens
    pdf.rotate(45, 60, 190)  # Rotaciona a marca d'água para diagonal
    watermark_text = "Projeto Agrícola - Unespar"
    txt_width = pdf.get_string_width(watermark_text)
    pdf.rotate(0)  # Restaura a rotação
    x = (page_width - txt_width) / 2 + pdf.l_margin  # Centralizar horizontalmente
    y = (page_height) / 2 + pdf.t_margin  # Centralizar verticalmente
    pdf.text(x, y, watermark_text)

    # Título do relatório
    pdf.set_font("Arial", size=14, style="B")
    pdf.set_text_color(0, 0, 0)  # Cor preta para o título
    pdf.cell(200, 10, txt="Relatório de Dados - Variações dos Agro Commodities e Dólar", ln=True, align='C')
    pdf.ln(10)  # Espaçamento entre título e tabela

    # Criar cabeçalho da tabela
    pdf.set_font("Arial", size=10, style="B")
    col_width = (page_width - 4) / len(dataframe.columns)  # Largura das células, considerando as margens
    for col in dataframe.columns:
        pdf.cell(col_width, 10, str(col), border=1, align='C')
        
    pdf.ln()

    # Adicionar os dados do DataFrame ao PDF
    pdf.set_font("Arial", size=10)
    for index, row in dataframe.iterrows():
        for value in row:
            pdf.cell(col_width, 10, str(value), border=1, align='C')
        pdf.ln()

    # Salvar PDF em um arquivo temporário
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)
    return temp_pdf.name

# Exemplo de uso no seu código Streamlit
st.title("Dashboard Interativo: O Agro aplicado")

# Carregar os dados
file_path = "https://github.com/jonhrib/Agro_2024/raw/refs/heads/main/data/ATUALIZA%C3%87%C3%95ES_Final.xlsx"  # Substitua pelo caminho correto
data = pd.read_excel(file_path, sheet_name="Página1")

# Renomear colunas (ajustar conforme necessário)
columns_mapping = {
    'DATA': 'Data',
    'SOJA': 'Soja',
    'MILHO': 'Milho',
    'TRIGO': 'Trigo',
    'COMPRA': 'Dólar Compra',
    'VENDA': 'Dólar Venda'
}
data = data.rename(columns=columns_mapping)

# Conversão e formatação das datas
data['Data'] = pd.to_datetime(data['Data'], errors='coerce')
data['Data BR'] = data['Data'].dt.strftime('%d/%m/%Y')  # Formato brasileiro

# Limpeza e conversão de dados
for col in ['Soja', 'Milho', 'Trigo', 'Dólar Compra', 'Dólar Venda']:
    data[col] = pd.to_numeric(data[col], errors='coerce')

# Filtro de datas
st.sidebar.header("Filtros")
start_date = st.sidebar.date_input("Data Inicial", data['Data'].min())
end_date = st.sidebar.date_input("Data Final", data['Data'].max())
filtered_data = data[(data['Data'] >= pd.Timestamp(start_date)) & (data['Data'] <= pd.Timestamp(end_date))]

# Filtro de commodities
st.sidebar.header("Filtros de Commodities")
selected_commodities = st.sidebar.multiselect(
    "Selecione as Commodities",
    options=["Soja", "Milho", "Trigo"],
    default=["Soja", "Milho", "Trigo"]  # Selecionando as commodities por padrão
)

# Filtro de valores de Dólar (Compra ou Venda)
st.sidebar.header("Filtros de Dólar")
selected_dollar = st.sidebar.selectbox(
    "Selecione o Tipo de Dólar",
    options=["Dólar Compra", "Dólar Venda"],
    index=0  # Dólar Compra selecionado por padrão
)

# Aplicar os filtros nos dados
filtered_data = data[
    (data['Data'] >= pd.Timestamp(start_date)) & 
    (data['Data'] <= pd.Timestamp(end_date))
]

# Aplicar o filtro de commodities
filtered_data = filtered_data[selected_commodities + [selected_dollar]]

# Verificar se a coluna 'Data BR' existe, caso contrário, criar a coluna
if 'Data BR' not in filtered_data.columns:
    filtered_data['Data BR'] = filtered_data['Data'].dt.strftime('%d/%m/%Y')  # Adicionar a formatação correta

# Agora, você pode substituir a coluna 'Data' pela 'Data BR' para exibição
filtered_data['Data'] = filtered_data['Data BR']
st.dataframe(filtered_data.drop(columns=['Data BR']))  # Exibe o dataframe sem a coluna 'Data BR'

# Seleção de visualização
st.sidebar.header("Visualizações")
visualization_type = st.sidebar.selectbox(
    "Selecione o tipo de visualização",
    ["Correlação", "Médias Mensais", "Média do Dólar", "Tendências", "Exportação de Dados"]
)

# Visualização: Correlação
if visualization_type == "Correlação":
    st.subheader("Mapa de Calor de Correlação")
    
    # Calcular a matriz de correlação
    correlation_matrix = filtered_data[['Soja', 'Milho', 'Trigo', 'Dólar Compra', 'Dólar Venda']].corr()

    # Criar o mapa de calor
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        correlation_matrix,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        vmin=-1,
        vmax=1,
        cbar=True,
        ax=ax
    )
    ax.set_title("Mapa de Calor: Correlações Diárias", fontsize=16)
    
    # Exibir o gráfico na aplicação
    st.pyplot(fig)

    # Salvar o gráfico como PDF
    pdf_path = "MapaDeCalor_CorrelaçõesDiárias.pdf"
    plt.savefig(pdf_path, format="pdf")
    st.download_button(
        label="Baixar Mapa de Calor em PDF",
        data=open(pdf_path, "rb"),
        file_name="MapaDeCalor_CorrelaçõesDiárias.pdf",
        mime="application/pdf"
    )

# Visualização: Médias Mensais em barras
if visualization_type == "Médias Mensais":
    st.subheader("Médias Mensais de Preços: Commodities e Dólar")
    
    # Adicionar coluna 'Ano-Mês' com períodos mensais
    filtered_data['Ano-Mês'] = filtered_data['Data'].dt.to_period('M')

    # Selecionar as colunas numéricas para cálculo de médias
    numeric_columns = ['Soja', 'Milho', 'Trigo', 'Dólar Compra', 'Dólar Venda']
    monthly_means = (
        filtered_data.groupby('Ano-Mês')[numeric_columns]
        .mean()
        .reset_index()
    )

    # Ajustar exibição de 'Ano-Mês' para formato string (exemplo: "2024-01" -> "Jan/2024")
    monthly_means['Ano-Mês'] = monthly_means['Ano-Mês'].dt.strftime('%b/%Y')

    # Criar gráfico de barras para as médias mensais
    fig, ax = plt.subplots(figsize=(14, 8))
    monthly_means.set_index('Ano-Mês')[numeric_columns].plot(kind='bar', ax=ax, colormap='viridis')

    # Título e ajustes no gráfico
    ax.set_title("Médias Mensais de Preços: Commodities e Dólar", fontsize=16)
    ax.set_xlabel("Ano/Mês", fontsize=12)
    ax.set_ylabel("Preço Médio (R$)", fontsize=12)
    ax.legend(title="Categorias", fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Exibir o gráfico na aplicação
    st.pyplot(fig)

    # Salvar o gráfico como PDF
    pdf_path = "MédiasMensais_De_Commodities_E_Dólar.pdf"
    plt.savefig(pdf_path, format="pdf")
    st.download_button(
        label="Baixar Gráfico de Médias Mensais em PDF",
        data=open(pdf_path, "rb"),
        file_name="MédiasMensais_De_Commodities_E_Dólar.pdf",
        mime="application/pdf"
    )

# Visualização: Tendência
if visualization_type == "Tendências":
    st.subheader("Tendência de Preços: Regressão Linear")
    
    # Exemplo com "Soja" e "Dólar Compra"
    x = np.array(filtered_data['Dólar Compra']).reshape(-1, 1)
    y = np.array(filtered_data['Soja'])

    # Criar modelo de regressão linear
    model = LinearRegression()
    model.fit(x, y)

    # Predições
    predicted = model.predict(x)

    # Plotando as tendências
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(filtered_data['Data'], y, label='Preço Soja', color='b')
    ax.plot(filtered_data['Data'], predicted, label='Tendência (Regressão)', color='r', linestyle='--')
    ax.set_title('Tendência de Preços de Soja e Dólar', fontsize=16)
    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel('Preço (R$)', fontsize=12)
    ax.legend()

    # Exibir o gráfico
    st.pyplot(fig)

    # Salvar gráfico como PDF
    pdf_path = "Tendencia_Soja.pdf"
    plt.savefig(pdf_path, format="pdf")
    st.download_button(
        label="Baixar Tendência Soja em PDF",
        data=open(pdf_path, "rb"),
        file_name="Tendencia_Soja.pdf",
        mime="application/pdf"
    )

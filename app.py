import streamlit as st
import pandas as pd
from pylinac import FieldAnalysis
import tempfile
import os
from io import BytesIO  # para gerar Excel em memória
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análise de Campo - Pylinac", layout="centered")

st.title("📊 Análise de Campo com Pylinac")
st.write("Faça upload de um arquivo DICOM de imagem de campo para análise.")

# Upload do arquivo DICOM
uploaded_file = st.file_uploader("Selecione um arquivo DICOM", type=["dcm"])

if uploaded_file is not None:
    # Salva temporariamente o arquivo DICOM
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dcm") as temp_file:
        temp_file.write(uploaded_file.read())
        dicom_path = temp_file.name

    # Análise com pylinac
    fa = FieldAnalysis(dicom_path)
    fa.analyze()
    data = fa.results_data()

    # Organiza os dados em dicionário
    resultados = {
        "Campo Horizontal (cm)": round(data.field_size_vertical_mm / 10, 2),
        "Campo Vertical (cm)": round(data.field_size_horizontal_mm / 10, 2),
        "CAX (média central)": round(data.central_roi_mean, 4),
        "Planura Vertical (%)": round(data.protocol_results['flatness_vertical'], 1),
        "Planura Horizontal (%)": round(data.protocol_results['flatness_horizontal'], 1),
        "Simetria Vertical (%)": round(data.protocol_results['symmetry_vertical'], 1),
        "Simetria Horizontal (%)": round(data.protocol_results['symmetry_horizontal'], 1),
        "CAX -> Borda Superior (cm)": round(data.cax_to_top_mm / 10, 2),
        "CAX -> Borda Inferior (cm)": round(data.cax_to_bottom_mm / 10, 2),
        "CAX -> Borda Esquerda (cm)": round(data.cax_to_left_mm / 10, 2),
        "CAX -> Borda Direita (cm)": round(data.cax_to_right_mm / 10, 2),
        "Penumbra Esquerda (mm)": round(data.left_penumbra_mm, 1),
        "Penumbra Direita (mm)": round(data.right_penumbra_mm, 1),
        "Penumbra Superior (mm)": round(data.top_penumbra_mm, 1),
        "Penumbra Inferior (mm)": round(data.bottom_penumbra_mm, 1)
    }

    st.success("✅ Análise concluída com sucesso!")
    st.subheader("📋 Resultados")


    # Transpor resultados para formato vertical
    df = pd.DataFrame(list(resultados.items()), columns=["Métrica", "Valor"])

    # Dividir a página em duas colunas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Resultados")
        st.dataframe(df, use_container_width=True)

        # Texto tabular para copiar e colar no Excel
        texto_tabela = df.to_csv(sep="\t", index=False)

        st.markdown("### 📋 Copiar e colar no Excel")
        st.text_area("Selecione e copie (CTRL+C ou CMD+C):", value=texto_tabela, height=300)

        # Gerar Excel em memória
        def gerar_excel_em_memoria(dataframe):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                dataframe.to_excel(writer, index=False, sheet_name="Resultados")
            output.seek(0)
            return output

        excel_bytes = gerar_excel_em_memoria(df)

        # Botão de download
        st.download_button(
            label="📥 Baixar resultados em Excel",
            data=excel_bytes,
            file_name="relatorio_field_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col2:
    st.subheader("🖼️ Imagem da Análise")
    fa.plot_analyzed_image()  # Gera a imagem
    fig = plt.gcf()  # Captura a figura atual
    st.pyplot(fig)


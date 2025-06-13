import streamlit as st
import pandas as pd
from pylinac import FieldAnalysis
import tempfile
import os
from io import BytesIO  # para gerar Excel em memória

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

    # Mostrar resultados em 3 colunas
    cols = st.columns(3)
    items = list(resultados.items())
    col_len = (len(items) + 2) // 3  # para dividir igualmente

    for i, col in enumerate(cols):
        for key, value in items[i * col_len: (i + 1) * col_len]:
            col.markdown(f"**{key}:** {value}")

    # Criar DataFrame para exportar
    df = pd.DataFrame([resultados])

    # Gerar Excel em memória
    def gerar_excel_em_memoria(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            dataframe.to_excel(writer, index=False, sheet_name="Resultados")
        output.seek(0)
        return output

    excel_bytes = gerar_excel_em_memoria(df)

    # Botão para download
    st.download_button(
        label="📥 Baixar resultados em Excel",
        data=excel_bytes,
        file_name="relatorio_field_analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Remover o arquivo DICOM temporário
    os.remove(dicom_path)

import streamlit as st
import pandas as pd
from pylinac import FieldAnalysis
import tempfile
import os

st.set_page_config(page_title="Análise de Campo - Pylinac", layout="centered")

st.title("📊 Análise de Campo com Pylinac")
st.write("Faça upload de um arquivo DICOM de imagem de campo para análise.")

# Upload do arquivo DICOM
uploaded_file = st.file_uploader("Selecione um arquivo DICOM", type=["dcm"])

if uploaded_file is not None:
    # Salva temporariamente o arquivo
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

    # Criar 3 colunas para mostrar os resultados
    cols = st.columns(3)
    items = list(resultados.items())
    total_items = len(items)
    col_len = (total_items + 2) // 3  # arredonda pra cima

    for i, col in enumerate(cols):
        start_idx = i * col_len
        end_idx = start_idx + col_len
        for key, value in items[start_idx:end_idx]:
            col.markdown(f"**{key}:** {value}")

    # Gerar DataFrame para o Excel
    df = pd.DataFrame([resultados])

    @st.cache_data
    def gerar_excel(df):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            df.to_excel(tmp.name, index=False)
            return tmp.name

    excel_path = gerar_excel(df)

    # Lê o arquivo em bytes, remove arquivo e disponibiliza para download
    with open(excel_path, "rb") as file:
        data = file.read()

    os.remove(dicom_path)
    os.remove(excel_path)

    st.download_button(
        label="📥 Baixar resultados em Excel",
        data=data,
        file_name="relatorio_field_analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

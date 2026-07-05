import os
import tempfile
import streamlit as st
from src.mp3_inspector import obtener_info_mp3
from src.utils import get_memory_usage

st.set_page_config(
    page_title="Trace Analyzer",
    page_icon="🎧",
    layout="centered",
)

st.title(
    "🎧 Trace Analyzer - :red[MP3] Technical Inspection",
    width="stretch",
    text_alignment="center",
    anchor="ppal",
    #help="help",
)
st.caption(
    "Upload an .mp3 file to extract, parse, and visualize its physical, technical, and ID3 tag metadata. "
    "This is a sandbox project to test audio processing performance on Streamlit Cloud."
)

_, col_c, _ = st.columns([2, 5, 2])

with col_c:
    archivo_subido = st.file_uploader(
    label="",
        type=["mp3"],
        accept_multiple_files=False,
        width="stretch",
    )

with col_c:
    boton_procesar = st.button(
        "Process File",
        type="primary",
        icon=":material/play_arrow:",
        icon_position="right",
        width="stretch",     
        key="process_file_button"
    )

if boton_procesar:
    if archivo_subido is None:
        st.warning(
            "Please select or drag and drop an .mp3 file before clicking Process File."
        )
        st.stop()

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(archivo_subido.getbuffer())
            temp_path = temp_file.name

        resultados = obtener_info_mp3(temp_path)

        if not resultados["exito"]:
            st.error(resultados["error"])
            st.stop()

        st.divider()

        col_res1, col_res2 = st.columns(2)

        with col_res1:
            st.subheader("Physical characteristics")
            st.table(resultados["fisicos"])

            st.subheader("ID3 Tags")

            if resultados["etiquetas"]:
                tags_limpios = {
                    str(k).capitalize(): v[0] if isinstance(v, list) and v else v
                    for k, v in resultados["etiquetas"].items()
                }
                st.table(tags_limpios)
            else:
                st.info("This file does not contain ID3 tags.")

        with col_res2:
            st.subheader("Technical Details")
            st.table(resultados["tecnicos"])

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

st.divider()

# Integración del monitor de memoria en la parte central
st.metric("System Memory Usage", f"{get_memory_usage():.2f} MB")


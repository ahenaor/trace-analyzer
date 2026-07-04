import os
import tempfile

import streamlit as st

from src.mp3_inspector import obtener_info_mp3


st.set_page_config(
    page_title="Audio Radiografía",
    page_icon="🎧",
    layout="centered",
)


st.title("Audio Radiografía")
st.caption(
    "Sube un archivo .mp3 para extraer su radiografía física, técnica y etiquetas ID3."
)


archivo_subido = st.file_uploader(
    "Selecciona un archivo MP3",
    type=["mp3"],
    accept_multiple_files=False,
)


st.write("")

col_izq, col_centro, col_der = st.columns([3, 2, 3])

with col_centro:
    boton_procesar = st.button(
        "Procesar archivo",
        use_container_width=True,
        type="primary",
    )


st.divider()


if boton_procesar:
    if archivo_subido is None:
        st.warning(
            "Por favor, selecciona o arrastra un archivo .mp3 antes de hacer clic en Procesar."
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

        st.success(f"Archivo analizado correctamente: **{archivo_subido.name}**")

        col_res1, col_res2 = st.columns(2)

        with col_res1:
            st.subheader("Características físicas")
            st.table(resultados["fisicos"])

            st.subheader("Metadatos ID3")

            if resultados["etiquetas"]:
                tags_limpios = {
                    str(k).capitalize(): v[0] if isinstance(v, list) and v else v
                    for k, v in resultados["etiquetas"].items()
                }
                st.table(tags_limpios)
            else:
                st.info("Este archivo no contiene etiquetas ID3.")

        with col_res2:
            st.subheader("Detalles técnicos")
            st.table(resultados["tecnicos"])

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
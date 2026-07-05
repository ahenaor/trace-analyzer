import os
import tempfile
import streamlit as st
from src.mp3_inspector import obtener_info_mp3
from src.m4a_inspector import obtener_info_m4a
from src.audio_converter import convertir_mp3_a_m4a
from src.utils import get_memory_usage

st.set_page_config(
    page_title="Trace Analyzer",
    page_icon="🎧",
    layout="centered",
)

st.title(
    "🎧 Trace Analyzer - :red[MP3]",
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
        if resultados["exito"]:
            st.subheader("Archivo original")

            # Fila 1: Características Físicas (2 columnas, mucho espacio)
            col_peso, col_duracion = st.columns(2)
            with col_peso:
                st.metric("Peso", resultados["fisicos"].get("Peso", "N/A"), border=True, width="stretch")
            with col_duracion:
                st.metric("Duración", resultados["fisicos"].get("Duración", "N/A"), border=True, width="stretch")

            # Fila 2: Características Técnicas (3 columnas)
            col_bit, col_sample, col_canales = st.columns(3)
            with col_bit:
                st.metric("Bitrate", resultados["tecnicos"].get("Bitrate", "N/A"), border=True, width="stretch")
            with col_sample:
                st.metric("Sample Rate", resultados["tecnicos"].get("Sample Rate", "N/A"), border=True, width="stretch")
            with col_canales:
                st.metric("Canales", resultados["tecnicos"].get("Canales", "N/A"), border=True, width="stretch")
            
            st.divider()

            archivo_convertido_path = temp_path.replace(".mp3", "_optimized.m4a")

            with st.spinner("Convirtiendo audio a M4A / AAC / mono / 16 kHz / 64k..."):
                conversion = convertir_mp3_a_m4a(
                    archivo_entrada=temp_path,
                    archivo_salida=archivo_convertido_path,
                    bitrate="64k",
                )
            
            if conversion["exito"]:
                resultados_convertido = obtener_info_m4a(archivo_convertido_path)

                if resultados_convertido["exito"]:
                    st.subheader("Archivo optimizado para transcripción")

                    col_peso_opt, col_duracion_opt = st.columns(2)

                    with col_peso_opt:
                        st.metric("Peso optimizado", resultados_convertido["fisicos"].get("Peso", "N/A"), border=True, width="stretch",)

                    with col_duracion_opt:
                        st.metric("Duración", resultados_convertido["fisicos"].get("Duración", "N/A"), border=True, width="stretch",)

                    col_bit_opt, col_sample_opt, col_canales_opt = st.columns(3)

                    with col_bit_opt:
                        st.metric(
                            "Bitrate",
                            resultados_convertido["tecnicos"].get("Bitrate", "N/A"),
                            border=True,
                            width="stretch",
                        )

                    with col_sample_opt:
                        st.metric(
                            "Sample Rate",
                            resultados_convertido["tecnicos"].get("Sample Rate", "N/A"),
                            border=True,
                            width="stretch",
                        )

                    with col_canales_opt:
                        st.metric(
                            "Canales",
                            resultados_convertido["tecnicos"].get("Canales", "N/A"),
                            border=True,
                            width="stretch",
                        )

                    with open(archivo_convertido_path, "rb") as file:
                        st.download_button(
                            label="Download optimized M4A",
                            data=file,
                            file_name="audio_optimized_for_transcription.m4a",
                            mime="audio/mp4",
                            type="primary",
                            icon=":material/download:",
                            width="stretch",
                        )

                else:
                    st.warning(
                        "El archivo fue convertido, pero no fue posible leer sus metadatos técnicos."
                    )
                    st.error(resultados_convertido["error"])

            else:
                st.error(conversion["error"])

                if conversion.get("detalle"):
                    with st.expander("Ver detalle técnico del error"):
                        st.code(conversion["detalle"])

        else:
            st.error(resultados["error"])


    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

st.divider()

_, col_cc, _ = st.columns([3, 3, 3])
with col_cc:
    # Integración del monitor de memoria en la parte central
    st.metric("System Memory Usage", f"{get_memory_usage():.2f} MB")


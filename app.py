import os
import tempfile
from pathlib import Path

import streamlit as st

from src.audio_converter import convertir_audio_a_m4a
from src.audio_inspector import SUPPORTED_EXTENSIONS, obtener_info_audio
from src.utils import get_memory_usage


BITRATE_SALIDA = "64k"
SAMPLE_RATE_SALIDA = 16000
CANALES_SALIDA = 1


st.set_page_config(
    page_title="Trace Analyzer",
    page_icon="🎧",
    layout="centered",
)


def mostrar_metricas_audio(resultados: dict, titulo: str) -> None:
    st.subheader(titulo)

    col_peso, col_duracion = st.columns(2)

    with col_peso:
        st.metric(
            "Peso",
            resultados["fisicos"].get("Peso", "N/A"),
            border=True,
            width="stretch",
        )

    with col_duracion:
        st.metric(
            "Duración",
            resultados["fisicos"].get("Duracion", "N/A"),
            border=True,
            width="stretch",
        )

    col_bit, col_sample, col_canales = st.columns(3)

    with col_bit:
        st.metric(
            "Bitrate",
            resultados["tecnicos"].get("Bitrate", "N/A"),
            border=True,
            width="stretch",
        )

    with col_sample:
        st.metric(
            "Sample Rate",
            resultados["tecnicos"].get("Sample Rate", "N/A"),
            border=True,
            width="stretch",
        )

    with col_canales:
        st.metric(
            "Canales",
            resultados["tecnicos"].get("Canales", "N/A"),
            border=True,
            width="stretch",
        )


def calcular_reduccion_peso(peso_original_mb: float | None, peso_convertido_mb: float | None) -> float | None:
    if not peso_original_mb or not peso_convertido_mb:
        return None
    if peso_original_mb <= 0:
        return None
    return (1 - (peso_convertido_mb / peso_original_mb)) * 100


st.title(
    "🎧 Trace Analyzer - :red[Audio]",
    width="stretch",
    text_alignment="center",
    anchor="ppal",
)

st.caption(
    "Upload an .mp3, .m4a or .wav file to inspect its main technical metadata, "
    "convert it to M4A/AAC mono 16 kHz, and download an optimized version for transcription."
)

_, col_c, _ = st.columns([2, 5, 2])

with col_c:
    archivo_subido = st.file_uploader(
        label="",
        type=["mp3", "m4a", "wav"],
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
        key="process_file_button",
    )

if boton_procesar:
    if archivo_subido is None:
        st.warning(
            "Please select or drag and drop an .mp3, .m4a or .wav file before clicking Process File."
        )
        st.stop()

    extension_entrada = Path(archivo_subido.name).suffix.lower()

    if extension_entrada not in SUPPORTED_EXTENSIONS:
        st.error("Unsupported file format. Please upload an .mp3, .m4a or .wav file.")
        st.stop()

    temp_path = None
    archivo_convertido_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension_entrada) as temp_file:
            temp_file.write(archivo_subido.getbuffer())
            temp_path = temp_file.name

        resultados_original = obtener_info_audio(temp_path)

        if not resultados_original["exito"]:
            st.error(resultados_original["error"])
            st.stop()

        mostrar_metricas_audio(resultados_original, "Archivo original")

        st.divider()

        st.info(
            f"Conversión objetivo: M4A / AAC / mono / 16 kHz / {BITRATE_SALIDA}.",
            icon="🎯",
        )

        fd, archivo_convertido_path = tempfile.mkstemp(suffix="_optimized.m4a")
        os.close(fd)

        with st.spinner(
            f"Convirtiendo audio a M4A / AAC / mono / 16 kHz / {BITRATE_SALIDA}..."
        ):
            conversion = convertir_audio_a_m4a(
                archivo_entrada=temp_path,
                archivo_salida=archivo_convertido_path,
                bitrate=BITRATE_SALIDA,
                sample_rate=SAMPLE_RATE_SALIDA,
                channels=CANALES_SALIDA,
            )

        if not conversion["exito"]:
            st.error(conversion["error"])

            if conversion.get("detalle"):
                with st.expander("Ver detalle técnico del error"):
                    st.code(conversion["detalle"])

            st.stop()

        resultados_convertido = obtener_info_audio(archivo_convertido_path)

        if not resultados_convertido["exito"]:
            st.warning(
                "El archivo fue convertido, pero no fue posible leer sus metadatos técnicos."
            )
            st.error(resultados_convertido["error"])
            st.stop()

        mostrar_metricas_audio(resultados_convertido, "Archivo optimizado para transcripción")

        reduccion = calcular_reduccion_peso(
            resultados_original.get("valores", {}).get("peso_mb"),
            resultados_convertido.get("valores", {}).get("peso_mb"),
        )

        if reduccion is not None:
            st.metric(
                "Reducción de peso",
                f"{reduccion:.1f}%",
                border=True,
                width="stretch",
            )

        with open(archivo_convertido_path, "rb") as file:
            archivo_convertido_bytes = file.read()

        nombre_base = Path(archivo_subido.name).stem
        nombre_descarga = f"{nombre_base}_optimized_for_transcription.m4a"

        st.download_button(
            label="Download optimized M4A",
            data=archivo_convertido_bytes,
            file_name=nombre_descarga,
            mime="audio/mp4",
            type="primary",
            icon=":material/download:",
            width="stretch",
        )

    finally:
        for path in [temp_path, archivo_convertido_path]:
            if path and os.path.exists(path):
                os.remove(path)

st.divider()

_, col_cc, _ = st.columns([3, 3, 3])
with col_cc:
    st.metric("System Memory Usage", f"{get_memory_usage():.2f} MB")

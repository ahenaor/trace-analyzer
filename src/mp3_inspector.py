import os
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError


MPEG_MODES = {
    0: "Estéreo",
    1: "Joint Stereo",
    2: "Dual Channel",
    3: "Mono",
}

MPEG_VERSIONS = {
    1: "MPEG-1",
    2: "MPEG-2",
    2.5: "MPEG-2.5",
}


def obtener_info_mp3(path: str) -> dict:
    """
    Analiza un archivo MP3 y devuelve sus metadatos físicos, técnicos e ID3.

    Parameters
    ----------
    path : str
        Ruta local del archivo MP3 a analizar.

    Returns
    -------
    dict
        Diccionario con estado de éxito, información física, técnica y etiquetas.
    """
    try:
        peso_mb = os.path.getsize(path) / (1024 * 1024)

        audio = MP3(path)
        info = audio.info

        try:
            tags = EasyID3(path)
        except ID3NoHeaderError:
            tags = {}

        minutos, segundos = divmod(int(info.length), 60)

        bitrate_kbps = info.bitrate // 1000 if info.bitrate else "No disponible"
        sample_rate_khz = info.sample_rate / 1000 if info.sample_rate else "No disponible"

        return {
            "exito": True,
            "fisicos": {
                "Peso": f"{peso_mb:.2f} MB",
                "Duración": f"{minutos}m {segundos:02d}s",
            },
            "tecnicos": {
                "Canales": f"{'Estéreo' if info.channels == 2 else 'Mono'} ({info.channels})",
                "Sample Rate": f"{sample_rate_khz} kHz",
                "Bitrate": f"{bitrate_kbps} kbps",
                "Modo MPEG": MPEG_MODES.get(info.mode, str(info.mode)),
                "Versión MPEG": MPEG_VERSIONS.get(info.version, str(info.version)),
                "VBR": "Sí" if getattr(info, "bitrate_mode", None) == 1 else "No",
            },
            "etiquetas": tags,
        }

    except HeaderNotFoundError:
        return {
            "exito": False,
            "error": "El archivo no tiene un encabezado MP3 válido.",
        }

    except Exception as e:
        return {
            "exito": False,
            "error": f"Error inesperado al procesar el archivo: {e}",
        }
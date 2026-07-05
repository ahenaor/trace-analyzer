import os
from mutagen.mp4 import MP4, MP4StreamInfoError


def obtener_info_m4a(path: str) -> dict:
    """
    Analiza un archivo M4A/AAC y devuelve metadatos físicos y técnicos básicos.

    Parameters
    ----------
    path : str
        Ruta local del archivo M4A a analizar.

    Returns
    -------
    dict
        Diccionario con estado de éxito, información física y técnica.
    """
    try:
        peso_mb = os.path.getsize(path) / (1024 * 1024)

        audio = MP4(path)
        info = audio.info

        minutos, segundos = divmod(int(info.length), 60)

        bitrate_kbps = (
            info.bitrate // 1000
            if getattr(info, "bitrate", None)
            else "No disponible"
        )

        sample_rate_khz = (
            info.sample_rate / 1000
            if getattr(info, "sample_rate", None)
            else "No disponible"
        )

        channels = getattr(info, "channels", "No disponible")

        return {
            "exito": True,
            "fisicos": {
                "Peso": f"{peso_mb:.2f} MB",
                "Duración": f"{minutos}m {segundos:02d}s",
            },
            "tecnicos": {
                "Canales": f"{'Mono' if channels == 1 else 'Estéreo' if channels == 2 else channels} ({channels})",
                "Sample Rate": f"{sample_rate_khz} kHz",
                "Bitrate": f"{bitrate_kbps} kbps",
                "Formato": "M4A / AAC",
            },
        }

    except MP4StreamInfoError:
        return {
            "exito": False,
            "error": "El archivo no tiene información válida de audio M4A/AAC.",
        }

    except Exception as e:
        return {
            "exito": False,
            "error": f"Error inesperado al procesar el archivo M4A: {e}",
        }
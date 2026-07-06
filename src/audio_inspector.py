import os
from pathlib import Path
from typing import Any

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
from mutagen.mp3 import MP3, HeaderNotFoundError, BitrateMode
from mutagen.mp4 import MP4, MP4StreamInfoError
from mutagen.wave import WAVE


SUPPORTED_EXTENSIONS = {".mp3", ".m4a", ".wav"}

MPEG_MODES = {
    0: "Estereo",
    1: "Joint Stereo",
    2: "Dual Channel",
    3: "Mono",
}

MPEG_VERSIONS = {
    1: "MPEG-1",
    2: "MPEG-2",
    2.5: "MPEG-2.5",
}

BITRATE_MODES = {
    BitrateMode.UNKNOWN: "Desconocido",
    BitrateMode.CBR: "CBR",
    BitrateMode.VBR: "VBR",
    BitrateMode.ABR: "ABR",
}


def _format_duration(seconds_float: float | int | None) -> str:
    if seconds_float is None:
        return "No disponible"

    total_seconds = int(seconds_float)
    minutos, segundos = divmod(total_seconds, 60)
    horas, minutos = divmod(minutos, 60)

    if horas > 0:
        return f"{horas}h {minutos:02d}m {segundos:02d}s"

    return f"{minutos}m {segundos:02d}s"


def _format_channels(channels: Any) -> str:
    if channels == 1:
        return "Mono (1)"
    if channels == 2:
        return "Estereo (2)"
    if channels in (None, "No disponible"):
        return "No disponible"
    return f"{channels} canales"


def _format_bitrate(bitrate: Any) -> str:
    if not bitrate:
        return "No disponible"
    return f"{int(bitrate) // 1000} kbps"


def _format_sample_rate(sample_rate: Any) -> str:
    if not sample_rate:
        return "No disponible"
    return f"{sample_rate / 1000:g} kHz"


def _base_response(path: str, info: Any, formato: str) -> dict:
    peso_mb = os.path.getsize(path) / (1024 * 1024)
    length = getattr(info, "length", None)
    bitrate = getattr(info, "bitrate", None)
    sample_rate = getattr(info, "sample_rate", None)
    channels = getattr(info, "channels", None)

    return {
        "exito": True,
        "formato": formato,
        "fisicos": {
            "Peso": f"{peso_mb:.2f} MB",
            "Duracion": _format_duration(length),
        },
        "tecnicos": {
            "Formato": formato,
            "Canales": _format_channels(channels),
            "Sample Rate": _format_sample_rate(sample_rate),
            "Bitrate": _format_bitrate(bitrate),
        },
        "valores": {
            "peso_mb": peso_mb,
            "duracion_segundos": float(length) if length is not None else None,
            "bitrate_bps": int(bitrate) if bitrate else None,
            "bitrate_kbps": int(bitrate) // 1000 if bitrate else None,
            "sample_rate_hz": int(sample_rate) if sample_rate else None,
            "channels": int(channels) if isinstance(channels, int) else None,
        },
        "etiquetas": {},
    }


def obtener_info_mp3(path: str) -> dict:
    try:
        audio = MP3(path)
        info = audio.info
        respuesta = _base_response(path, info, "MP3")

        bitrate_mode = getattr(info, "bitrate_mode", BitrateMode.UNKNOWN)
        bitrate_mode_label = BITRATE_MODES.get(bitrate_mode, str(bitrate_mode))

        respuesta["tecnicos"].update(
            {
                "Modo de Bitrate": bitrate_mode_label,
                "Es VBR": "Si" if bitrate_mode == BitrateMode.VBR else "No",
                "Modo MPEG": MPEG_MODES.get(getattr(info, "mode", None), str(getattr(info, "mode", "No disponible"))),
                "Version MPEG": MPEG_VERSIONS.get(getattr(info, "version", None), str(getattr(info, "version", "No disponible"))),
            }
        )
        respuesta["valores"]["bitrate_mode"] = bitrate_mode_label

        try:
            tags = EasyID3(path)
            respuesta["etiquetas"] = {k: list(v) for k, v in tags.items()}
        except ID3NoHeaderError:
            respuesta["etiquetas"] = {}

        return respuesta

    except HeaderNotFoundError:
        return {
            "exito": False,
            "error": "El archivo no tiene un encabezado MP3 valido.",
        }

    except Exception as e:
        return {
            "exito": False,
            "error": f"Error inesperado al procesar el archivo MP3: {e}",
        }


def obtener_info_m4a(path: str) -> dict:
    try:
        audio = MP4(path)
        respuesta = _base_response(path, audio.info, "M4A / AAC")

        if audio.tags:
            respuesta["etiquetas"] = {
                str(k): [str(item) for item in v] if isinstance(v, list) else str(v)
                for k, v in audio.tags.items()
            }

        return respuesta

    except MP4StreamInfoError:
        return {
            "exito": False,
            "error": "El archivo no tiene informacion valida de audio M4A/AAC.",
        }

    except Exception as e:
        return {
            "exito": False,
            "error": f"Error inesperado al procesar el archivo M4A: {e}",
        }


def obtener_info_wav(path: str) -> dict:
    try:
        audio = WAVE(path)
        respuesta = _base_response(path, audio.info, "WAV")

        # En WAV PCM no siempre existe bitrate en metadatos. Si no aparece,
        # lo estimamos con sample_rate * bits_per_sample * channels.
        if respuesta["valores"]["bitrate_bps"] is None:
            sample_rate = respuesta["valores"].get("sample_rate_hz")
            channels = respuesta["valores"].get("channels")
            bits_per_sample = getattr(audio.info, "bits_per_sample", None)

            if sample_rate and channels and bits_per_sample:
                estimated_bitrate = sample_rate * channels * bits_per_sample
                respuesta["valores"]["bitrate_bps"] = estimated_bitrate
                respuesta["valores"]["bitrate_kbps"] = estimated_bitrate // 1000
                respuesta["tecnicos"]["Bitrate"] = f"{estimated_bitrate // 1000} kbps"

            if bits_per_sample:
                respuesta["tecnicos"]["Bits por muestra"] = f"{bits_per_sample} bits"
                respuesta["valores"]["bits_per_sample"] = int(bits_per_sample)

        return respuesta

    except Exception as e:
        return {
            "exito": False,
            "error": f"Error inesperado al procesar el archivo WAV: {e}",
        }


def obtener_info_audio(path: str) -> dict:
    extension = Path(path).suffix.lower()

    if extension == ".mp3":
        return obtener_info_mp3(path)

    if extension == ".m4a":
        return obtener_info_m4a(path)

    if extension == ".wav":
        return obtener_info_wav(path)

    return {
        "exito": False,
        "error": (
            f"Formato no soportado: {extension}. "
            "Formatos soportados: .mp3, .m4a, .wav."
        ),
    }

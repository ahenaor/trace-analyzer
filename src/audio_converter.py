import os
import subprocess
from pathlib import Path


def convertir_mp3_a_m4a(
    archivo_entrada: str,
    archivo_salida: str,
    bitrate: str = "32k",
    sample_rate: int = 16000,
    channels: int = 1,
) -> dict:
    """
    Convierte un archivo .mp3 a .m4a optimizado para transcripción.

    Especificaciones por defecto:
    - Contenedor: .m4a
    - Codec: AAC
    - Canales: mono
    - Sample rate: 16 kHz
    - Bitrate: 32 kbps

    Parameters
    ----------
    archivo_entrada : str
        Ruta local del archivo MP3 de entrada.

    archivo_salida : str
        Ruta local donde se guardará el archivo M4A optimizado.

    bitrate : str, optional
        Bitrate de salida. Por defecto "32k".

    sample_rate : int, optional
        Frecuencia de muestreo de salida. Por defecto 16000.

    channels : int, optional
        Número de canales de salida. Por defecto 1.

    Returns
    -------
    dict
        Diccionario con estado de éxito, ruta de salida y mensaje de error si aplica.
    """
    try:
        if not os.path.exists(archivo_entrada):
            return {
                "exito": False,
                "error": f"El archivo de entrada no existe: {archivo_entrada}",
            }

        if not archivo_salida.lower().endswith(".m4a"):
            return {
                "exito": False,
                "error": "El archivo de salida debe tener extensión .m4a.",
            }

        Path(archivo_salida).parent.mkdir(parents=True, exist_ok=True)

        comando = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            archivo_entrada,
            "-vn",
            "-c:a",
            "aac",
            "-ac",
            str(channels),
            "-ar",
            str(sample_rate),
            "-b:a",
            bitrate,
            archivo_salida,
        ]

        resultado = subprocess.run(
            comando,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        return {
            "exito": True,
            "archivo_salida": archivo_salida,
            "bitrate": bitrate,
            "sample_rate": sample_rate,
            "channels": channels,
            "stdout": resultado.stdout,
            "stderr": resultado.stderr,
        }

    except FileNotFoundError:
        return {
            "exito": False,
            "error": (
                "No se encontró FFmpeg en el sistema. "
                "Verifica que esté instalado y disponible en el PATH."
            ),
        }

    except subprocess.CalledProcessError as e:
        return {
            "exito": False,
            "error": "FFmpeg falló durante la conversión.",
            "detalle": e.stderr,
        }

    except Exception as e:
        return {
            "exito": False,
            "error": f"Error inesperado durante la conversión: {e}",
        }
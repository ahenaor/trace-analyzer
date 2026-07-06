import os
import subprocess
from pathlib import Path


def convertir_audio_a_m4a(
    archivo_entrada: str,
    archivo_salida: str,
    bitrate: str = "64k",
    sample_rate: int = 16000,
    channels: int = 1,
) -> dict:
    """
    Convierte un archivo de audio soportado a .m4a optimizado para transcripcion.

    Especificaciones por defecto:
    - Contenedor: .m4a
    - Codec: AAC
    - Canales: mono
    - Sample rate: 16 kHz
    - Bitrate: 64 kbps

    Parameters
    ----------
    archivo_entrada : str
        Ruta local del archivo de entrada.

    archivo_salida : str
        Ruta local donde se guardara el archivo M4A optimizado.

    bitrate : str, optional
        Bitrate de salida. Por defecto "64k".

    sample_rate : int, optional
        Frecuencia de muestreo de salida. Por defecto 16000.

    channels : int, optional
        Numero de canales de salida. Por defecto 1.

    Returns
    -------
    dict
        Diccionario con estado de exito, ruta de salida y mensaje de error si aplica.
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
                "error": "El archivo de salida debe tener extension .m4a.",
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
            "-map",
            "0:a:0",
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
                "No se encontro FFmpeg en el sistema. "
                "Verifica que este instalado y disponible en el PATH."
            ),
        }

    except subprocess.CalledProcessError as e:
        return {
            "exito": False,
            "error": "FFmpeg fallo durante la conversion.",
            "detalle": e.stderr,
        }

    except Exception as e:
        return {
            "exito": False,
            "error": f"Error inesperado durante la conversion: {e}",
        }
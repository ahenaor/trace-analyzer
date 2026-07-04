# trace-analyzer
Inspect, optimize and transcribe audio files.

## Funcionalidades actuales

- Carga de un único archivo `.mp3`.
- Cálculo del peso del archivo.
- Cálculo de duración.
- Extracción de sample rate.
- Extracción de bitrate.
- Identificación de canales.
- Identificación de modo MPEG.
- Identificación de versión MPEG.
- Detección básica de VBR.
- Lectura de etiquetas ID3 cuando están disponibles.

## Roadmap

La visión del proyecto es evolucionar desde una radiografía básica de MP3 hacia una herramienta completa de preparación y transcripción de audio.

### Fase 1: Radiografía técnica de MP3

- Análisis de metadatos físicos y técnicos.
- Visualización simple en Streamlit.
- Despliegue público del MVP.

### Fase 2: Optimización y conversión

- Conversión de audios a formatos más livianos.
- Normalización de sample rate.
- Conversión a mono.
- Preparación de archivos para transcripción automática.

### Fase 3: Transcripción con IA

- Integración con Whisper de OpenAI.
- Generación de transcripciones.
- Exportación a `.txt`, `.json` o `.docx`.
- Posible uso de prompts de contexto para reducir errores en términos técnicos o nombres propios.

## Instalación local

```bash
git clone https://github.com/ahenaor/trace-analyzer.git
cd trace-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
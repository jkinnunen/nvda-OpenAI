# AI Hub

Si buscas una experiencia de escritorio dedicada con flujos adicionales, consulta [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) (app independiente y complemento NVDA minimo). AI Hub sigue siendo una opcion completa dentro de NVDA.

**AI Hub** es un complemento para NVDA que conecta el lector de pantalla con varias API de modelos de lenguaje (LLM). Permite redactar, resumir, traducir, describir imagenes, hacer preguntas por voz, transcribir audio y usar herramientas opcionales (TTS, OCR, etc.) sin salir de NVDA.

El **nombre del paquete** en NVDA sigue siendo `openai` (por compatibilidad). El **nombre visible** en menus y configuracion es **AI Hub**.

## Funciones principales

- Chat en una ventana principal con historial, prompt del sistema y seleccion de modelo/cuenta.
- Adjuntos de imagenes y documentos desde archivo, y URL remotas segun compatibilidad del proveedor.
- Pegado inteligente en el prompt (`Ctrl+V`) para rutas, archivos o URL unica.
- Historial de conversaciones (guardar, renombrar, borrar, reabrir).
- Comando de pregunta por voz (sin gesto por defecto; se asigna en Gestos de entrada -> AI Hub).
- Descripcion global: captura (`NVDA+E`) y region del objeto navegador (`NVDA+O`).
- Submenu de herramientas por proveedor (TTS, OCR, speech-to-text, Lyria, Ollama).

## Proveedores compatibles

Configura uno o varios proveedores en **Preferencias -> Configuracion -> AI Hub**.

| Proveedor | Rol |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT y relacionados; herramientas oficiales de transcripcion y TTS |
| [DeepSeek](https://www.deepseek.com/) | API DeepSeek compatible con OpenAI |
| Custom OpenAI | Cualquier endpoint HTTP compatible con OpenAI |
| Ollama | Modelos locales via endpoint compatible |
| [Mistral AI](https://mistral.ai/) | Mistral/Pixtral; herramientas Voxtral TTS, OCR y speech-to-text |
| [OpenRouter](https://openrouter.ai/) | Acceso unificado a muchos modelos |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; herramienta Lyria 3 Pro |

Tambien se pueden leer claves desde variables de entorno (`OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, etc.).

## Instalacion

1. Abre la [pagina de versiones](https://github.com/aaclause/nvda-OpenAI/releases).
2. Descarga el ultimo `.nvda-addon`.
3. Instala desde **Herramientas -> Gestionar complementos** en NVDA.

## Construccion y librerias

La compilacion con `scons` completa automaticamente las librerias en:

`addon/globalPlugins/AIHub/libs/`

Si faltan, `scons` descarga versiones fijas y extrae lo necesario:

- `markdown2` `2.5.4` -> `libs/markdown2.py`
- `Pillow` `12.1.1`:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

La carpeta `libs` esta ignorada por git.

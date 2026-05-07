Si buscas una experiencia de escritorio dedicada con flujos de trabajo adicionales, consulta [BasiliskLLM](https://github.com/SigmaNight/basiliskLLM/) (aplicación independiente más un complemento mínimo para NVDA). AI Hub sigue siendo una opción completa dentro de NVDA.

# AI Hub

**AI Hub** es un complemento para NVDA que conecta tu lector de pantalla con varias API de modelos de lenguaje de gran escala (LLM). Úsalo para redactar, resumir, ayudar con traducciones, visión (imágenes y capturas de pantalla), consultas por voz, transcripción y cuadros de herramientas opcionales (TTS, OCR y más), sin salir de NVDA.

El **nombre del paquete** en NVDA sigue siendo `openai` (por compatibilidad con instalaciones existentes). El **nombre visible** que ves en menús y configuración es **AI Hub**.

## Funciones de un vistazo

- **Chat** en un cuadro principal dedicado, con historial, prompt del sistema y selección de modelo/cuenta.
- **Imágenes y documentos** como adjuntos desde archivos; **URL** a archivos remotos con comprobaciones de tipo alineadas con el **proveedor seleccionado**.
- **Pegado inteligente** en el campo de prompt: pega archivos desde el portapapeles, rutas desde texto o una sola URL (también disponible en el menú contextual del prompt). `Ctrl+V` usa la misma lógica cuando el prompt tiene el foco.
- **Guardado de conversación e historial** con renombrado, eliminación y reapertura.
- **Hacer una pregunta** desde cualquier lugar (sin tecla predeterminada): asigna un gesto en **Gestos de entrada -> AI Hub** para grabar, enviar y escuchar o leer la respuesta.
- **Descripción global**: captura de pantalla (`NVDA+E`) o región del objeto navegador (`NVDA+O`) enviada a una sesión de chat.
- Submenú de **Herramientas** (en NVDA -> AI Hub): utilidades específicas de cada proveedor, como TTS, OCR, voz a texto, audio Lyria y gestión de modelos de Ollama.
- Las opciones de **razonamiento / búsqueda web** solo aparecen cuando el **modelo actual** las admite (varía según el proveedor).

Este complemento **no** incluye su propio comprobador de actualizaciones. Las **actualizaciones** se gestionan mediante la **Tienda oficial de complementos de NVDA** cuando instalas desde allí. Si instalas manualmente desde la [página de versiones](https://github.com/aaclause/nvda-OpenAI/releases), instala del mismo modo las compilaciones `.nvda-addon` más recientes.

## Proveedores compatibles

Configura **uno o más proveedores** en NVDA, en **Preferencias -> Configuración -> AI Hub**. Cada proveedor puede tener **varias cuentas con nombre** (claves API, organización opcional o URL base, cuando corresponda).

| Proveedor | Función |
|----------|------|
| [OpenAI](https://platform.openai.com/) | GPT y modelos relacionados; cuadros de herramientas oficiales de transcripción y TTS |
| [DeepSeek](https://www.deepseek.com/) | API de DeepSeek (compatible con OpenAI) |
| **OpenAI personalizado** | Cualquier API HTTP compatible con OpenAI (URL base personalizada + clave) |
| **Ollama** | Modelos locales mediante endpoint compatible con OpenAI; herramienta de gestión de modelos |
| [Mistral AI](https://mistral.ai/) | Mistral / Pixtral; herramientas de TTS Voxtral, OCR y voz a texto |
| [OpenRouter](https://openrouter.ai/) | Muchos modelos de terceros con una sola clave |
| [Anthropic](https://www.anthropic.com/) | Claude |
| [xAI](https://x.ai/) | Grok |
| [Google](https://ai.google.dev/) | Gemini; herramienta Lyria 3 Pro |

El complemento puede tomar claves API de **variables de entorno** cuando están definidas (por ejemplo, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY`, entre otras). La interfaz de configuración sigue siendo el lugar principal para gestionar cuentas.

### Motores de voz a texto (transcripción)

Para la **transcripción de micrófono / archivo** dentro del flujo principal (no la herramienta de transcripción separada de OpenAI), puedes elegir entre **whisper_cpp** (local), **openai** (API de Whisper) y **mistral**, en la sección **Audio** de la configuración de AI Hub.

## Instalación

1. Abre la [página de versiones del complemento](https://github.com/aaclause/nvda-OpenAI/releases).
2. Descarga el paquete `.nvda-addon` más reciente.

## Configuración inicial

1. Abre **NVDA -> Preferencias -> Configuración**.
2. Selecciona la categoría **AI Hub**.
3. En **API Accounts**, elige **Add account...**.
4. En el diálogo de cuenta, selecciona un proveedor, escribe un nombre de cuenta y completa los campos obligatorios (clave API para la mayoría de proveedores; URL base para **Custom OpenAI** y **Ollama**, y en Ollama se usa por defecto http://127.0.0.1:11434/v1 si está vacía).
5. Guarda y, opcionalmente, añade más cuentas, edita las existentes o elimina las que no uses de la lista.
6. Opcionalmente, ajusta **Audio**, **Comentarios del chat**, **Avanzado** / temperatura y **Guardado automático de conversación** (activado por defecto).

Hasta que al menos una cuenta de proveedor esté lista, al abrir el cuadro principal se te pedirá que añadas claves en la configuración de AI Hub.

## Actualizar desde versiones antiguas de "Open AI"

Si usaste una versión anterior de este complemento:

- La **configuración** se migra de la sección heredada **`OpenAI`** a **`AIHub`**. No deberías perder preferencias.
- Los **archivos de datos** (conversaciones, almacén de claves, adjuntos) se migran desde la carpeta **`openai`** dentro de tu directorio de configuración de usuario de NVDA hacia **`aihub`**.

No necesitas mover archivos manualmente, salvo que uses una configuración personalizada.

## Menú de NVDA: AI Hub

En el menú de NVDA encontrarás **AI Hub** (con la versión instalada en la etiqueta). Las opciones incluyen:

- **Documentación** — abre la guía de usuario en tu navegador (`doc\en\readme.html`).
- **Cuadro principal...** — abre la ventana de chat (`NVDA+G` de forma predeterminada).
- **Historial de conversaciones...** — gestiona chats guardados.
- **Herramientas** — submenú que agrupa utilidades de **OpenAI**, **Mistral**, **Google** y **Ollama** (ver abajo).
- **GitHub repository** / **BasiliskLLM** - enlaces rápidos.

## Cuadro principal

Ábrelo con **`NVDA+G`** o con **Cuadro principal...** en el menú de AI Hub.

### Qué puedes hacer

- Chatear con el modelo seleccionado; revisar **Mensajes** con navegación de teclado y menús contextuales (por ejemplo, **j** / **k** para moverte entre mensajes cuando el foco está en el área de mensajes; consulta las indicaciones en pantalla para el campo activo).
- Adjuntar **imágenes o documentos locales** y añadir **URL de archivos** cuando el proveedor lo admita. Los tipos no compatibles con el proveedor actual pueden generar una advertencia antes de enviar.
- **Pegar (archivo o texto)** desde el menú contextual del prompt, o **`Ctrl+V`** en el prompt: el complemento puede adjuntar archivos, insertar rutas de texto o tratar una sola URL como adjunto cuando corresponda.
- Grabar fragmentos de **audio**, adjuntar archivos de audio y usar **TTS** para el texto del prompt donde el modelo lo permita.
- **`Escape`** cierra el cuadro principal (cuando no hay ningún cuadro modal bloqueante abierto).
- **`Ctrl+R`** alterna la grabación de micrófono (cuando corresponda).
- **`F2`** renombra la conversación guardada actual (después de que exista en almacenamiento).
- **`Ctrl+N`** abre una instancia **nueva** del cuadro principal (sesión).

### Opciones que dependen del modelo

Algunos controles solo aparecen o se aplican en ciertos modelos:

- **Razonamiento** ("thinking") para modelos que lo exponen; el razonamiento en streaming se mantiene separado de la respuesta visible cuando la API proporciona esa distinción.
- **Esfuerzo de razonamiento** y controles relacionados donde el proveedor admite niveles.
- **Búsqueda web** solo para modelos que anuncian compatibilidad con búsqueda web.

La disponibilidad exacta cambia a medida que los proveedores actualizan sus API; la interfaz refleja el **modelo actualmente seleccionado**.

### Prompt del sistema

El prompt del sistema orienta el comportamiento del modelo. Se proporciona uno predeterminado adaptado a asistencia de accesibilidad; puedes editarlo, restablecerlo desde el menú contextual y, opcionalmente, conservar el último prompt usado (configurable en la configuración). El prompt del sistema consume tokens igual que cualquier otra entrada.

## Historial de conversaciones

Usa **Historial de conversaciones...** desde el menú de AI Hub, o asigna un gesto en **Gestos de entrada -> AI Hub**.

Puedes listar, abrir, renombrar, eliminar y crear conversaciones. Desde el cuadro principal, **F2** y **Ctrl+N** ayudan a gestionar la sesión actual.

### Guardado automático

Si **Guardado automático de conversación** está activado en la configuración (predeterminado), el complemento guarda (o actualiza) la conversación almacenada **después de cada respuesta completa del asistente**, y puede conservar el estado al cerrar el cuadro si hay algo que guardar. También puedes guardar desde el menú contextual del campo **Mensajes**. Si el guardado automático está desactivado, usa el guardado manual cuando quieras conservarla.

## Hacer una pregunta (voz)

Este comando **no tiene tecla predeterminada**. Asígnale una en **Gestos de entrada -> AI Hub**.

- Primera pulsación: iniciar grabación.
- Segunda pulsación durante la grabación: detener y enviar.
- Si la respuesta se reproduce como audio, vuelve a pulsar para detener la reproducción.

**Modos:**

- **Audio directo** — si el modelo seleccionado admite entrada de audio, tu grabación puede enviarse como audio sin necesidad de un paso de transcripción aparte.
- **Transcribir y luego chatear** — en caso contrario, el motor de transcripción configurado procesa la grabación y después el texto se envía al modelo de chat.

Si el cuadro principal está enfocado, se usa su **modelo actual**; en caso contrario, el complemento elige un modelo adecuado entre los proveedores configurados.

## Submenú Herramientas

La entrada **Herramientas** en el menú de AI Hub abre cuadros agrupados por proveedor (cada uno puede requerir la cuenta API correspondiente):

| Área del menú | Herramienta |
|-----------|------|
| Mistral | **Voxtral TTS...**, **OCR...**, **Voz a texto...** |
| Google | **Lyria 3 Pro...** |
| OpenAI | **TTS...**, **Transcripción / Traducción...** |
| Ollama | **Gestor de modelos...** |

Si no hay una cuenta configurada para el proveedor de una herramienta, el complemento te indicará que añadas una en la configuración de AI Hub.

## Comandos globales

Todos los gestos predeterminados pueden cambiarse en **NVDA -> Preferencias -> Gestos de entrada -> AI Hub**.

| Gesto | Acción |
|---------|--------|
| `NVDA+G` | Mostrar el cuadro principal de AI Hub |
| `NVDA+E` | Capturar pantalla y describir (añade imagen a una sesión) |
| `NVDA+O` | Describir la región actual del objeto navegador |
| *(sin gesto predeterminado)* | Historial de conversaciones. Asígnalo en Gestos de entrada -> AI Hub. |
| *(sin gesto predeterminado)* | Hacer una pregunta (grabar / enviar / detener audio). Asígnalo en Gestos de entrada -> AI Hub. |
| *(sin gesto predeterminado)* | Alternar grabación de micrófono y transcripción. Asígnalo en Gestos de entrada -> AI Hub. |

## Dónde se guardan los datos

Los archivos de trabajo, el índice de conversaciones guardadas, el archivo `accounts.json` unificado y los adjuntos se guardan en tu directorio de **configuración de usuario** de NVDA, en la carpeta **`aihub`** (después de la migración desde `openai`). Los archivos temporales usan una subcarpeta `tmp` y se limpian cuando corresponde (por ejemplo, al finalizar el complemento o al cerrar el cuadro de diálogo).

## Dependencias requeridas (obtenidas automáticamente durante la compilación)

Las compilaciones usan `scons` para poblar las librerías de ejecución en:

`addon/globalPlugins/AIHub/libs/`

Cuando falta una librería requerida, `scons` descarga ruedas fijadas y extrae solo lo necesario en esa carpeta. Las dependencias fijadas actuales son:

- **[markdown-it-py](https://pypi.org/project/markdown-it-py/)** `3.0.0` + **[mdurl](https://pypi.org/project/mdurl/)** `0.1.2` — extraído en `libs/` para el renderizado Markdown del chat.
- **[Pillow](https://pypi.org/project/Pillow/)** `12.1.1`, para:
  - Python `3.11` `win32` -> `libs/lib_py3.11_win32/`
  - Python `3.13` `win_amd64` -> `libs/lib_py3.13/`

El directorio `libs` está intencionalmente ignorado por git; quienes colaboran no necesitan confirmar artefactos incorporados.

## Solución de problemas (breve)

- **"No hay cuenta configurada"** — añade una clave API para el proveedor que seleccionaste en los ajustes de **AI Hub**.
- **El proveedor rechaza un adjunto** — comprueba el tipo y tamaño del archivo; prueba otro modelo o proveedor que admita el medio que necesitas.

Para incidencias y contribuciones, usa el enlace al **repositorio de GitHub** desde el menú de AI Hub.

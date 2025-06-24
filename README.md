# PPT to TXT Converter

Convierte presentaciones de PowerPoint (`.ppt`/`.pptx`) en resúmenes de texto y PDF utilizando modelos de lenguaje avanzados (Ollama/Gemma o Gemini) y una API web basada en FastAPI.

---

## Características

- **Carga de archivos PPT/PPTX** vía API REST.
- **Conversión automática a PDF** usando LibreOffice.
- **Extracción de imágenes de cada diapositiva**.
- **Resumen automático de cada diapositiva** usando IA (Ollama/Gemma o Gemini).
- **Generación de un resumen global** de toda la presentación.
- **Exportación del resumen global a PDF**.
- **Contenedores listos para producción** con Docker y Docker Compose.

---

## Requisitos

- Docker y Docker Compose instalados.
- Clave de API de Gemini (opcional, solo si usas el endpoint `/convert-ppt-gemini/`).

---

## Instalación y uso rápido

1. **Clona este repositorio:**

   ```sh
   git clone https://github.com/tu_usuario/ppt-to-txt.git
   cd ppt-to-txt
   ```

2. **Configura tus variables de entorno:**

   Crea un archivo `.env` en la raíz del proyecto y agrega tu clave de Gemini si la tienes:

   ```
   GEMINI_API_KEY=tu_clave_de_gemini
   ```

3. **Construye y levanta los servicios:**

   ```sh
   docker compose build
   docker compose up
   ```

4. **Accede a la API:**

   - FastAPI corre en [http://localhost:8000](http://localhost:8000)
   - Documentación interactiva en [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Endpoints principales

### `/convert-ppt-ollama/`

Convierte y resume usando Ollama/Gemma (modelo local).

**Ejemplo con `curl`:**

```sh
curl -X 'POST' \
  'http://localhost:8000/convert-ppt-ollama/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@archivo.pptx;type=application/vnd.openxmlformats-officedocument.presentationml.presentation'
```

### `/convert-ppt-gemini/`

Convierte y resume usando Gemini (requiere clave de API).

**Ejemplo con `curl`:**

```sh
curl -X 'POST' \
  'http://localhost:8000/convert-ppt-gemini/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@archivo.pptx;type=application/vnd.openxmlformats-officedocument.presentationml.presentation'
```

---

## Estructura del proyecto

- `main.py`: API FastAPI principal.
- `ppt_to_image.py`: Conversión de PPT a PDF y de PDF a imágenes.
- `slide_summary.py`: Resumen de diapositivas y presentaciones usando Ollama/Gemma.
- `gemini_summary.py`: Resumen usando Gemini.
- `Dockerfile` y `compose.yml`: Infraestructura de contenedores.

---

## Notas

- Los archivos convertidos y resúmenes se guardan en la carpeta `output/`.
- El modelo de Ollama se descarga automáticamente al iniciar el contenedor.
- Puedes personalizar los prompts y modelos en los archivos `slide_summary.py` y `gemini_summary.py`.

---

## Integrantes

- Luna Esteban
- Lucich Francisco
- Moretti Francisco
- Zubik Tomas

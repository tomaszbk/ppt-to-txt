# PPT to TXT Converter

Convierte presentaciones de PowerPoint (`.ppt`/`.pptx`) en resúmenes de texto y PDF utilizando modelos de lenguaje avanzados (Ollama/Gemma o Gemini) y una API web basada en FastAPI.

---

1. **Construye y levanta los servicios:**

   ```sh
   docker compose build
   docker compose up
   ```

2. **Accede a la API:**

   - FastAPI corre en [http://localhost:8000](http://localhost:8000)
   - Documentación interactiva y pruebas en [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Endpoint principal

Debes seleccionar que modelo utilizar y subir el archivo ppt\pptx que quieras resumir.

---

## Estructura del proyecto

- `main.py`: API FastAPI principal.
- `ppt_to_image.py`: Conversión de PPT a PDF y de PDF a imágenes.
- `slide_summary.py`: Resumen de diapositivas y presentaciones usando Ollama/Gemma.
- `agents.py`: Definición de agentes para el resumen de diapositivas y presentaciones.
- `Dockerfile` y `compose.yml`: Infraestructura de contenedores.

---

## Notas

- Los archivos convertidos y resúmenes se guardan en la carpeta `output/`.
- El modelo de Ollama se descarga automáticamente al iniciar el contenedor.
- Puedes personalizar los prompts y modelos en el archivo `agents.py`

---

## Integrantes

- Luna Esteban
- Lucich Francisco
- Moretti Francisco
- Zubik Tomas

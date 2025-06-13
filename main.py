import asyncio
import io
import os
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pathlib import Path

import uvicorn

from ppt_to_image import convert_pdf_to_images, convert_ppt_to_pdf
from slide_summary import analyze_slide

app = FastAPI(title="PPT to Text Converter")


@app.post("/convert-ppt/")
async def convert_ppt(file: UploadFile = File(...)):
    """
    FastAPI endpoint to convert PowerPoint files to text summaries.
    """
    if not file.filename.endswith((".ppt", ".pptx")):
        raise HTTPException(
            status_code=400, detail="Only PPT and PPTX files are supported"
        )

    try:
        # 1. Guardar el archivo subido temporalmente
        with NamedTemporaryFile(delete=False, suffix=".pptx") as tmp:
            tmp.write(await file.read())
            ppt_path = Path(tmp.name)

        # 2. Convertir a PDF
        pdf_path = convert_ppt_to_pdf(ppt_path)
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="No se pudo convertir a PDF")

        # 3. Convertir PDF a imágenes
        images = convert_pdf_to_images(pdf_path)
        if not images:
            raise HTTPException(status_code=500, detail="No se pudo convertir PDF a imágenes")

        # 4. Resumir cada slide usando el modelo
        summaries = []
        for idx, image in enumerate(images, 1):
            # Convertir la imagen a bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="PNG")
            img_bytes = img_bytes.getvalue()
            summary = await analyze_slide(img_bytes)
            summaries.append({"slide": idx, "summary": summary})

        # 5. Limpiar archivos temporales
        os.remove(ppt_path)
        os.remove(pdf_path)

        return JSONResponse(
            content={
                "filename": file.filename,
                "total_slides": len(summaries),
                "summaries": summaries,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/")
async def root():
    return {"message": "PPT to Text Converter API"}


def summarize_slides(image_paths, output_dir):
    """
    Summarize each slide image using the LLM and save the summaries to a text file.
    """
    summaries = []
    for i, image_path in enumerate(image_paths, 1):
        try:
            print(f"Summarizing slide {i}...")
            summary = asyncio.run(analyze_slide(image_path))
            summaries.append(f"Slide {i}:\n{summary}\n")
        except Exception as e:
            print(f"Error summarizing slide {i}: {e}")
            summaries.append(f"Slide {i}:\n[Error al resumir]\n")

    summary_path = os.path.join(output_dir, "slides_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.writelines(summaries)
    print(f"Resumen guardado en {summary_path}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

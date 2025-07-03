import io
import os
import asyncio
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response

from agents import (
    slide_agent_gemini,
    slide_agent_ollama,
    text_summary_agent_gemini,
    text_summary_agent_ollama,
)
from ppt_to_image import convert_pdf_to_images, convert_ppt_to_pdf
from slide_summary import analyze_slide, summarize_presentation

app = FastAPI(title="PPT to Text Converter")


class AIProvider(str, Enum):
    GEMINI = "Gemini"
    OLLAMA = "Ollama"


@app.post("/convert-ppt/")
async def convert_ppt(AI_model: AIProvider, file: UploadFile = File(...)):
    match AI_model:
        case AIProvider.OLLAMA:
            slide_agent = slide_agent_ollama
            text_summary_agent = text_summary_agent_ollama
        case AIProvider.GEMINI:
            slide_agent = slide_agent_gemini
            text_summary_agent = text_summary_agent_gemini

    filename = file.filename
    if not isinstance(filename, str) or not filename.endswith((".ppt", ".pptx")):
        raise HTTPException(
            status_code=400, detail="Only PPT and PPTX files are supported"
        )

    try:
        with NamedTemporaryFile(delete=False, suffix=".pptx") as tmp:
            tmp.write(await file.read())
            ppt_path = Path(tmp.name)

        pdf_path = convert_ppt_to_pdf(ppt_path)
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="No se pudo convertir a PDF")

        images = convert_pdf_to_images(pdf_path)
        if not images:
            raise HTTPException(
                status_code=500, detail="No se pudo convertir PDF a imágenes"
            )
        os.remove(ppt_path)
        os.remove(pdf_path)

        summaries = await get_summaries(images, slide_agent, AI_model)

        name_without_ext = filename.rsplit(".", 1)[0]
        pdf_filename = f"presentation_summary_{name_without_ext}.pdf"

        # Delay antes del resumen final si es Gemini
        if AI_model == AIProvider.GEMINI:
            print("Esperando antes del resumen final (Gemini rate limit)...")
            await asyncio.sleep(5)

        final_summary, pdf_bytes = await summarize_presentation(
            text_summary_agent,
            [s["summary"] for s in summaries],
            presentation_name=filename,
        )

        logs = {
            "filename": filename,
            "total_slides": len(summaries),
            "summaries": summaries,
            "final_summary": final_summary,
        }
        print(logs)

        # Return the PDF file directly
        if pdf_bytes:
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={pdf_filename}"},
            )
        else:
            raise HTTPException(status_code=500, detail="PDF generation failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


async def get_summaries(images, slide_agent, ai_model: AIProvider):
    summaries = []
    for idx, image in enumerate(images, 1):
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()

        # Delay para Gemini (excepto en la primera slide)
        if ai_model == AIProvider.GEMINI and idx > 1:
            # 60 segundos / 15 requests = 4 segundos por request (con margen de seguridad)
            delay_seconds = 5
            print(
                f"Esperando {delay_seconds} segundos antes de procesar slide {idx} (Gemini rate limit)..."
            )
            await asyncio.sleep(delay_seconds)

        summary = await analyze_slide(img_bytes, slide_agent)
        summaries.append({"slide": idx, "summary": summary})
        print(f"Slide {idx} completada")

    return summaries


@app.get("/")
async def root():
    return {"message": "PPT to Text Converter API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

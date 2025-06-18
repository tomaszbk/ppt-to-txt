import asyncio
import io
import os
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pathlib import Path

from ppt_to_image import convert_pdf_to_images, convert_ppt_to_pdf
from slide_summary import analyze_slide, summarize_presentation 
from gemini_summary import analyze_slide_gemini, summarize_presentation_gemini

app = FastAPI(title="PPT to Text Converter")

@app.post("/convert-ppt-ollama/")
async def convert_ppt_ollama(file: UploadFile = File(...)):
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
            raise HTTPException(status_code=500, detail="No se pudo convertir PDF a imágenes")

        summaries = []
        for idx, image in enumerate(images, 1):
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="PNG")
            img_bytes = img_bytes.getvalue()
            summary = await analyze_slide(img_bytes)
            summaries.append({"slide": idx, "summary": summary})

        all_summaries_text = "\n".join([f"Slide {s['slide']}: {s['summary']}" for s in summaries])
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)

        name_without_ext = filename.rsplit(".", 1)[0]
        pdf_filename = f"presentation_summary_{name_without_ext}.pdf"
        output_pdf = os.path.join(output_dir, pdf_filename)

        final_summary = await summarize_presentation(
            all_summaries_text,
            output_path=output_pdf,
            presentation_name=filename
        )

        os.remove(ppt_path)
        os.remove(pdf_path)

        return JSONResponse(
            content={
                "filename": filename,
                "total_slides": len(summaries),
                "summaries": summaries,
                "final_summary": final_summary,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/convert-ppt-gemini/")
async def convert_ppt_gemini(file: UploadFile = File(...)):
    filename = file.filename
    if not isinstance(filename, str) or not filename.endswith((".ppt", ".pptx")):
        raise HTTPException(status_code=400, detail="Only PPT and PPTX files are supported")

    try:
        with NamedTemporaryFile(delete=False, suffix=".pptx") as tmp:
            tmp.write(await file.read())
            ppt_path = Path(tmp.name)

        pdf_path = convert_ppt_to_pdf(ppt_path)
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="No se pudo convertir a PDF")

        images = convert_pdf_to_images(pdf_path)
        if not images:
            raise HTTPException(status_code=500, detail="No se pudo convertir PDF a imágenes")

        summaries = []
        for idx, image in enumerate(images, 1):
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="PNG")
            img_bytes = img_bytes.getvalue()

            summary = await analyze_slide_gemini(img_bytes)
            summaries.append({"slide": idx, "summary": summary})

            if idx != len(images):
                await asyncio.sleep(4)

        all_summaries_text = [f"Slide {s['slide']}: {s['summary']}" for s in summaries]
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)

        name_without_ext = filename.rsplit(".", 1)[0]
        pdf_filename = f"presentation_summary_{name_without_ext}.pdf"
        output_pdf = os.path.join(output_dir, pdf_filename)

        final_summary = await summarize_presentation_gemini(
            all_summaries_text,
            output_path=output_pdf,
            presentation_name=filename
        )

        os.remove(ppt_path)
        os.remove(pdf_path)

        return JSONResponse(
            content={
                "filename": filename,
                "total_slides": len(summaries),
                "summaries": summaries,
                "final_summary": final_summary,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")



@app.get("/")
async def root():
    return {"message": "PPT to Text Converter API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

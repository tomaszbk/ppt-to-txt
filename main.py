import asyncio
import os
from tempfile import NamedTemporaryFile

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL.Image import Image

from ppt_to_image import convert_pdf_to_images, convert_ppt_to_pdf
from slide_summary import analyze_slide, summarize_presentation

app = FastAPI(title="PPT to Text Converter")


@app.post("/convert-ppt/")
async def convert_ppt_endpoint(file: UploadFile = File(...)):
    """
    FastAPI endpoint to convert PowerPoint files to text summaries.
    """
    if not file.filename.endswith((".ppt", ".pptx")):
        raise HTTPException(
            status_code=400, detail="Only PPT and PPTX files are supported"
        )

    try:
        # Convert to images
        temp = NamedTemporaryFile(delete=False)
        contents = await file.read()
        with temp as f:
            f.write(contents)

        pdf = convert_ppt_to_pdf(temp.name)

        images: list[Image] = convert_pdf_to_images(pdf)

        if not images:
            raise HTTPException(
                status_code=500, detail="Failed to convert presentation to images"
            )

        # Generate summaries
        summaries = []
        for i, image in enumerate(images, 1):
            try:
                summary = await analyze_slide(image)
                summaries.append({"slide": i, "summary": summary})
            except Exception as e:
                summaries.append({"slide": i, "summary": f"Error: {str(e)}"})

        # Generate entire summary of file
        presentation_summary = summarize_presentation(summaries)

        return JSONResponse(
            content={
                "filename": file.filename,
                "total_slides": len(summaries),
                "summaries": summaries,
                "presentation_summary": presentation_summary,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    finally:
        os.remove(temp.name)


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

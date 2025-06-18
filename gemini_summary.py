import base64
import os
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm

GOOGLE_API_KEY = os.getenv("GCP_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

async def analyze_slide_gemini(image_bytes: bytes) -> str:
    """
    Envía una imagen a Gemini para analizar y resumir el contenido de una slide.
    """
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_content = {
        "inline_data": {
            "mime_type": "image/png",
            "data": image_base64,
        }
    }

    prompt = {
        "role": "user",
        "parts": [
            {
                "text": (
                    "You are an expert in analyzing presentation slides for educational purposes.\n"
                    "Summarize only the visible content of this slide clearly and concisely.\n"
                    "- No assumptions.\n"
                    "- No hallucinations.\n"
                    "- Just summarize what is visually present on the slide."
                )
            },
            image_content,
        ]
    }

    response = model.generate_content([prompt])
    return response.text.strip()


async def summarize_presentation_gemini(slide_summaries: list[str], output_path=None, presentation_name=None) -> str:
    """
    Recibe una lista de resúmenes individuales y genera un resumen global de la presentación.
    """
    joined_summary = "\n".join(slide_summaries)
    prompt = (
        "You are an academic summarization expert specializing in educational content.\n"
        "Given the following slide summaries, write a comprehensive and well-structured summary "
        "suitable for university students:\n\n"
        f"{joined_summary}"
    )

    response = model.generate_content(prompt)
    summary_text = response.text.strip()

    if output_path and output_path.endswith(".pdf"):
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = []

        # Título con nombre de la presentación
        if presentation_name:
            title = f"Resumen de la Presentación: {presentation_name}"
        else:
            title = "Resumen de la Presentación"
        story.append(Paragraph(title, styles["Title"]))
        story.append(Spacer(1, 0.5 * cm))

        # Párrafos del resumen
        for paragraph in summary_text.split("\n\n"):
            story.append(Paragraph(paragraph.strip(), styles["Normal"]))
            story.append(Spacer(1, 0.5 * cm))

        doc.build(story)
        print(f"Resumen global guardado en PDF: {output_path}")

    elif output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary_text)
        print(f"Resumen global guardado como texto en: {output_path}")

    return summary_text

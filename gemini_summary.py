import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

GOOGLE_API_KEY = os.getenv("GCP_API_KEY")


model = GeminiModel("gemini-1.5-flash", provider=GoogleGLAProvider(api_key=GOOGLE_API_KEY))
gemini_agent = Agent(model=model)

async def analyze_slide_gemini(image_bytes: bytes) -> str:
    """
    Envía una imagen a Gemini para analizar y resumir el contenido de una slide usando pydantic_ai.
    """
    prompt = (
        "Eres un experto en analizar diapositivas de presentaciones educativas.\n"
        "Resume únicamente la información explícita y visible de esta diapositiva de forma clara y concisa, en español.\n"
        "- No hagas suposiciones.\n"
        "- No inventes información.\n"
        "- Solo resume lo que está presente visualmente en la diapositiva."
    )
    image_content = BinaryContent(data=image_bytes, media_type="image/png")
    result = await gemini_agent.run([prompt, image_content])
    return result.output.strip()

async def summarize_presentation_gemini(slide_summaries: list[str], output_path=None, presentation_name=None) -> str:
    """
    Recibe una lista de resúmenes individuales y genera un resumen global de la presentación usando pydantic_ai.
    """
    joined_summary = "\n".join(slide_summaries)
    prompt = (
        "Eres un experto académico en resúmenes de contenido educativo.\n"
        "Dado el siguiente listado de resúmenes de diapositivas, escribe un resumen global completo y bien estructurado, en español, adecuado para estudiantes universitarios:\n\n"
        f"{joined_summary}"
    )
    result = await gemini_agent.run(prompt)
    summary_text = result.output.strip()

    if output_path and output_path.endswith(".pdf"):
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = []

        title = f"Resumen de la Presentación: {presentation_name}" if presentation_name else "Resumen de la Presentación"
        story.append(Paragraph(title, styles["Title"]))
        story.append(Spacer(1, 0.5 * cm))

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

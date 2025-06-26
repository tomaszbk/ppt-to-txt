import io

from pydantic_ai import Agent, BinaryContent
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


async def analyze_slide(image, slide_agent: Agent) -> str:
    """Use AI to analyze and summarize a single slide"""
    print("Analyzing slide...")
    result = await slide_agent.run(
        [
            BinaryContent(data=image, media_type="image/png"),
        ]
    )
    print("result: ", result.output)
    return result.output.strip()


async def summarize_presentation(
    text_summary_agent: Agent,
    slide_summaries: list[str],
    presentation_name=None,
) -> tuple[str, bytes | None]:
    """Genera un resumen de la presentación y lo guarda en un PDF visualmente agradable

    Returns:
        tuple: (summary_text, pdf_bytes or None)
    """
    result = await text_summary_agent.run(slide_summaries)
    summary_text = result.output.strip()
    print("Presentation Summary: ", summary_text)

    pdf_bytes = None

    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
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
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return summary_text, pdf_bytes

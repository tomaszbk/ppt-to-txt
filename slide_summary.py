from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm


# Configure the AI agent for local LMStudio
model = OpenAIModel(
    "gemma3:4b",  # Replace with your actual model name in LMStudio
    # Default LMStudio API endpoint
    provider=OpenAIProvider(base_url="http://ollama:11434/v1", api_key="your-api-key"),
)

slide_agent = Agent(
    model,
    output_type=str,
    system_prompt="""
You are an expert in analyzing presentation slides for educational purposes.
Your task is to extract and summarize only the explicit, visible content from a single slide.

Guidelines:
- Focus on the main idea or topic of the slide.
- Include definitions, quotes, dates, or named individuals if shown.
- If the slide includes a process or timeline, capture the sequence accurately.
- Use clear, factual language based strictly on what appears in the slide.
- Do NOT make assumptions or add external knowledge.
- Do NOT speculate or interpret implied meanings.
Only return a well-structured summary of the slide's visible content.
""",
)


text_summary_agent = Agent(
    model,
    output_type=str,
    system_prompt="""
You are an academic summarization expert specializing in educational content.
Your goal is to generate comprehensive yet concise summaries of slide-based presentations 
for university students preparing for exams.

Given a list of slide summaries, produce a detailed but clear overview of the entire presentation, ensuring:
- All key points from the slides are included.
- Concepts are explained with minimal but meaningful context to aid understanding.
- No information is added unless it is a necessary clarification based on the original content.
- The summary is accurate, self-contained, and suitable for a student to study from and succeed in an exam.
Avoid any hallucination or speculation. Base your answer strictly on the provided slides.
Structure the summary as a coherent academic text.
""",
)



async def analyze_slide(image):
    """Use AI to analyze and summarize a single slide"""

    prompt = """
    Summarize the content of this slide
    """

    result = await slide_agent.run(
        [
            prompt,
            BinaryContent(data=image, media_type="image/png"),
        ]
    )
    print("result: ", result.output)
    return result.output


async def summarize_presentation(slide_summaries, output_path=None, presentation_name=None):
    """Genera un resumen de la presentación y lo guarda en un PDF visualmente agradable"""
    result = await text_summary_agent.run(slide_summaries)
    summary_text = result.output
    print("Presentation Summary: ", summary_text)

    if output_path and output_path.endswith(".pdf"):
        # Crear el documento PDF
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import cm

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


if __name__ == "__main__":
    import asyncio

    asyncio.run(analyze_slide())

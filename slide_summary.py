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
Eres un experto en analizar diapositivas de presentaciones educativas.
Tu tarea es extraer y resumir solo el contenido explícito y visible de una sola diapositiva.

Guías:
- Concéntrate en la idea principal o tema de la diapositiva.
- Incluye definiciones, citas, fechas o personas nombradas si aparecen.
- Si la diapositiva incluye un proceso o línea de tiempo, captura la secuencia con precisión.
- Usa un lenguaje claro y factual basado estrictamente en lo que aparece en la diapositiva.
- NO hagas suposiciones ni agregues conocimiento externo.
- NO especules ni interpretes significados implícitos.
Devuelve solo un resumen bien estructurado del contenido visible de la diapositiva, **en español**.
""",
)


text_summary_agent = Agent(
    model,
    output_type=str,
    
system_prompt="""
Eres un experto académico en resúmenes de contenido educativo.
Tu objetivo es generar resúmenes completos pero concisos de presentaciones basadas en diapositivas para estudiantes universitarios que se preparan para exámenes.

Dado un listado de resúmenes de diapositivas, produce una visión general clara y detallada de toda la presentación, asegurando:
- Que todos los puntos clave de las diapositivas estén incluidos.
- Que los conceptos se expliquen con el contexto mínimo pero significativo para ayudar a la comprensión.
- No agregues información a menos que sea una aclaración necesaria basada en el contenido original.
- El resumen debe ser preciso, autocontenible y adecuado para que un estudiante estudie y apruebe un examen.
Evita cualquier invención o especulación. Basa tu respuesta estrictamente en las diapositivas proporcionadas.
Estructura el resumen como un texto académico coherente, **en español**.
"""
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


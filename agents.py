import os

from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.providers.openai import OpenAIProvider

GOOGLE_API_KEY = os.getenv("GCP_API_KEY", "NONE")
ollama_model = OpenAIModel(
    "gemma3:4b",
    provider=OpenAIProvider(base_url="http://ollama:11434/v1", api_key="your-api-key"),
)
gemini_model = GeminiModel(
    "gemini-1.5-flash", provider=GoogleGLAProvider(api_key=GOOGLE_API_KEY)
)


slide_agent_system_prompt = """
Eres un experto en analizar diapositivas de presentaciones educativas.
Tu tarea es extraer y resumir solo el contenido explícito y visible de una sola diapositiva.

Guías:
- Concéntrate en la idea principal o tema de la diapositiva.
- Incluye definiciones, citas, fechas o personas nombradas si aparecen.
- Si la diapositiva incluye un proceso o línea de tiempo, captura la secuencia con precisión.
- Usa un lenguaje claro y factual basado estrictamente en lo que aparece en la diapositiva.
- Ignora secciones decorativas o protocolarias como saludos, despedidas, agradecimientos o invitaciones a preguntas.
- NO hagas suposiciones ni agregues conocimiento externo.
- NO especules ni interpretes significados implícitos.
Devuelve solo un resumen bien estructurado del contenido visible de la diapositiva, **en español**.
"""

slide_agent_ollama = Agent(
    ollama_model,
    output_type=str,
    system_prompt=slide_agent_system_prompt,
)

slide_agent_gemini = Agent(
    gemini_model,
    output_type=str,
    system_prompt=slide_agent_system_prompt,
)


text_summary_agent_system_prompt = """
Eres un experto académico en resúmenes de contenido educativo.
Tu objetivo es generar resúmenes completos pero concisos de presentaciones basadas en diapositivas para estudiantes universitarios que se preparan para exámenes.

Dado un listado de resúmenes de diapositivas, produce una visión general clara y detallada de toda la presentación, asegurando:
- Que todos los puntos clave de las diapositivas estén incluidos.
- Que los conceptos se expliquen con el contexto mínimo pero significativo para ayudar a la comprensión.
- Ignora contenidos no académicos como saludos, despedidas, agradecimientos, invitaciones a preguntas o cualquier sección protocolar sin valor conceptual.
- No agregues información a menos que sea una aclaración necesaria basada en el contenido original.
- El resumen debe ser preciso, autocontenible y adecuado para que un estudiante estudie y apruebe un examen.
Evita cualquier invención o especulación. Basa tu respuesta estrictamente en las diapositivas proporcionadas.
Estructura el resumen como un texto académico coherente, **en español**.
"""

text_summary_agent_ollama = Agent(
    ollama_model,
    output_type=str,
    system_prompt=text_summary_agent_system_prompt,
)

text_summary_agent_gemini = Agent(
    gemini_model,
    output_type=str,
    system_prompt=text_summary_agent_system_prompt,
)

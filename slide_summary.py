from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Configure the AI agent for local LMStudio
model = OpenAIModel(
    "gemma:4b",  # Cambia aquí por el nombre del modelo en Ollama
    provider=OpenAIProvider(
        base_url="http://ollama:11434/v1",
        api_key="ollama"
    ),
)

slide_agent = Agent(
    model,
    output_type=str,
    system_prompt="""
    You are an expert at analyzing presentation slides and extracting key information.
    Summarize the content of this slide. Only describe the visible content. Don't make
    assumptions. Only reply with the summary of the slide content.
    """,
)


async def analyze_slide(image_path):
    """Use AI to analyze and summarize a single slide"""

    prompt = """
    Summarize the content of this slide
    """

    with open(image_path, "rb") as f:
        image_data = f.read()

    result = await slide_agent.run(
        [
            prompt,
            BinaryContent(data=image_data, media_type="image/png"),
        ]
    )
    print("result: ", result.output)
    return result.output


if __name__ == "__main__":
    import asyncio

    asyncio.run(analyze_slide())

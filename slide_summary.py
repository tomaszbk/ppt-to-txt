from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Configure the AI agent for local LMStudio
model = OpenAIModel(
    "gemma3:4b",  # Replace with your actual model name in LMStudio
    # Default LMStudio API endpoint
    provider=OpenAIProvider(
        base_url="http://ollama:11434/v1", api_key="your-api-key"
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


async def analyze_slide(image):
    """Use AI to analyze and summarize a single slide"""

    prompt = """
    Summarize the content of this slide
    """

    with open(image, "rb") as f:
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

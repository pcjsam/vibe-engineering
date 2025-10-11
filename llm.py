import os

from dotenv import load_dotenv
from fireworks import LLM


def get_llm_response():
    load_dotenv()
    api_key = os.getenv("FIREWORKS_API_KEY")

    llm = LLM(model="deepseek-v3p1-terminus", deployment_type="auto", api_key=api_key)

    response = llm.chat.completions.create(
        messages=[{"role": "user", "content": "Hello, how are you?"}]
    )

    return response.choices[0].message.content

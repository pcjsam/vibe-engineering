import os

from dotenv import load_dotenv
from fireworks import LLM

from schema import SpecifySchema


def get_specify_schema(prompt: str):
    load_dotenv()
    api_key = os.getenv("FIREWORKS_API_KEY")

    llm = LLM(model="deepseek-v3p1-terminus", deployment_type="auto", api_key=api_key)

    response = llm.chat.completions.create(
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "SpecifySchema",
                "schema": SpecifySchema.model_json_schema(),
            },
        },
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content

import os

from dotenv import load_dotenv
from google import genai


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

ENV_PATH = os.path.join(BASE_DIR, ".env")


load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)


def get_gemini_client():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY was not found. "
            f"Make sure the project .env exists at: {ENV_PATH}"
        )

    return genai.Client(
        api_key=api_key
    )


def ask_gemini(system_prompt, user_prompt):

    client = get_gemini_client()

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=user_prompt,
        system_instruction=system_prompt
    )

    return interaction.output_text
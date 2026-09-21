import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "Missing OPENAI_API_KEY. Create a .env file in the same folder as main.py with: OPENAI_API_KEY=your_key_here"
    )

client = OpenAI(api_key=api_key)


def load_agent_profile(file_path: str | Path) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Profile file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def chat_with_jimini(user_message: str, profile_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": profile_text},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    profile_path = Path(__file__).resolve().parent / "agent_profile.txt"
    profile_text = load_agent_profile(profile_path)

    print("Jimini is ready. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        reply = chat_with_jimini(user_input, profile_text)
        print(f"\nJimini: {reply}\n")

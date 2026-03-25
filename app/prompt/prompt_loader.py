from pathlib import Path

from langchain_core.prompts import PromptTemplate

prompt_path = Path(__file__).resolve().parents[2] / "prompts"


def load_prompt(name: str):
    file = prompt_path / f"{name}.prompt"
    if not file.exists():
        raise FileNotFoundError(f"[Prompt] 不存在: {file}")
    return file.read_text(encoding="utf-8")


if __name__ == "__main__":
    template = load_prompt("extend_keywords_for_column_recall")
    prompt = PromptTemplate(template=template, input_variables=["query"])
    print(prompt)

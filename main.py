import os
from project.agent import ReActAgent
from project.llm.providers import LLMFactory
from project.prompts.registry import get_prompt_registry


def build_agent() -> ReActAgent:
    provider = os.getenv("LLM_PROVIDER", "local")

    if provider == "local":
        llm = LLMFactory.create(
            "local",
            model=os.getenv("LOCAL_MODEL", "llama3"),
            base_url=os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate"),
        )
    elif provider == "openai":
        llm = LLMFactory.create("openai", api_key=os.environ["OPENAI_API_KEY"], model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    elif provider == "google":
        llm = LLMFactory.create("google", api_key=os.environ["GOOGLE_API_KEY"], model=os.getenv("GOOGLE_MODEL", "gemini-1.5-flash"))
    elif provider == "anthropic":
        llm = LLMFactory.create("anthropic", api_key=os.environ["ANTHROPIC_API_KEY"], model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"))
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER={provider}")

    return ReActAgent(llm=llm, prompt_registry=get_prompt_registry("project/prompts"), max_iterations=6)


if __name__ == "__main__":
    agent = build_agent()
    print("ReAct CSV Agent started. Type 'exit' to stop.")

    while True:
        question = input("\nUser: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        print("\nAssistant:", agent.run(question))

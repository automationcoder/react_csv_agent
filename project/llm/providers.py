from abc import ABC, abstractmethod
from typing import Dict, List

import requests


class LLMProvider(ABC):
    @abstractmethod
    def invoke(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError


class LocalOllamaProvider(LLMProvider):
    def __init__(
        self,
        model: str = "llama3.1:8b",
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def invoke(self, messages: List[Dict[str, str]]) -> str:
        prompt = "\n\n".join(
            "{}: {}".format(m["role"].upper(), m["content"])
            for m in messages
        )

        url = self.base_url

        if not url.endswith("/api/generate"):
            url = url + "/api/generate"

        print("\n========== OLLAMA REQUEST ==========")
        print("URL:", url)
        print("MODEL:", self.model)
        print("====================================\n")

        response = requests.post(
            url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=self.timeout,
        )

        if response.status_code != 200:
            return (
                "Final Answer: Local Ollama returned HTTP "
                + str(response.status_code)
                + ". Raw response: "
                + response.text
            )

        data = response.json()
        return data.get("response", str(data))


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def invoke(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content or ""


class GoogleProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def invoke(self, messages: List[Dict[str, str]]) -> str:
        prompt = "\n\n".join(
            "{}: {}".format(m["role"].upper(), m["content"])
            for m in messages
        )
        response = self.model.generate_content(prompt)
        return response.text


class AnthropicProvider(LLMProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-latest",
    ):
        import anthropic

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def invoke(self, messages: List[Dict[str, str]]) -> str:
        system = ""
        converted = []

        for msg in messages:
            if msg["role"] == "system":
                system += msg["content"] + "\n"
            else:
                converted.append(
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                    }
                )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system,
            messages=converted,
        )

        return response.content[0].text


class LLMFactory:
    @staticmethod
    def create(provider: str, **kwargs) -> LLMProvider:
        if provider == "local":
            return LocalOllamaProvider(**kwargs)

        if provider == "openai":
            return OpenAIProvider(**kwargs)

        if provider == "google":
            return GoogleProvider(**kwargs)

        if provider == "anthropic":
            return AnthropicProvider(**kwargs)

        raise ValueError("Unknown provider: {}".format(provider))
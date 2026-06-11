from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any
import yaml
from jinja2 import Template, StrictUndefined


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    version: str
    prompt: str
    description: str = ""
    variables: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class PromptRegistry:
    def __init__(self, folder: str = "project/prompts"):
        self.folder = Path(folder)
        self._templates: dict[str, PromptTemplate] = {}
        self.reload()

    def reload(self) -> None:
        templates: dict[str, PromptTemplate] = {}
        for path in self.folder.glob("*.yaml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            template = PromptTemplate(
                name=data["name"],
                version=str(data["version"]),
                description=data.get("description", ""),
                prompt=data["prompt"],
                variables=data.get("variables", []),
                metadata=data.get("metadata", {}),
            )
            templates[template.name] = template
        self._templates = templates

    def get(self, name: str) -> PromptTemplate:
        if name not in self._templates:
            raise KeyError(f"Prompt template '{name}' not found. Available: {self.list_templates()}")
        return self._templates[name]

    def list_templates(self) -> list[str]:
        return sorted(self._templates.keys())

    def render(self, name: str, **variables: Any) -> str:
        template = self.get(name)
        missing = [var for var in template.variables if var not in variables]
        if missing:
            raise ValueError(f"Missing variables for prompt '{name}': {missing}")
        return Template(template.prompt, undefined=StrictUndefined).render(**variables)


@lru_cache(maxsize=1)
def get_prompt_registry(folder: str = "project/prompts") -> PromptRegistry:
    return PromptRegistry(folder=folder)

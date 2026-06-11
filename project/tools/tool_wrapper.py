from dataclasses import dataclass
from typing import Any, Callable, Type
from pydantic import BaseModel, ValidationError


@dataclass(frozen=True)
class ToolWrapper:
    name: str
    function: Callable[[BaseModel], str]
    params_model: Type[BaseModel]
    description: str

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.params_model.model_json_schema(),
        }

    def call(self, args: dict[str, Any]) -> str:
        try:
            params = self.params_model(**args)
            return self.function(params)
        except ValidationError as exc:
            return f"Eroare validare parametri pentru tool '{self.name}': {exc}"
        except Exception as exc:
            return f"Eroare la execuția tool-ului '{self.name}': {exc}"

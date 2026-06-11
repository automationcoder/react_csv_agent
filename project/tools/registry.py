import inspect
import json
from typing import Callable, Dict, List, Optional
from pydantic import BaseModel
from project.tools.tool_wrapper import ToolWrapper

TOOL_REGISTRY: Dict[str, ToolWrapper] = {}


def register_tool(func: Callable) -> Callable:
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    if len(params) != 1:
        raise TypeError(f"Tool '{func.__name__}' must have exactly one parameter: params: BaseModel")

    annotation = params[0].annotation
    if annotation is inspect._empty or not issubclass(annotation, BaseModel):
        raise TypeError(f"Tool '{func.__name__}' parameter must be a Pydantic BaseModel subclass.")

    docstring = inspect.getdoc(func)
    if not docstring or len(docstring.strip()) < 15:
        raise ValueError(f"Tool '{func.__name__}' must have a descriptive docstring for the LLM.")

    wrapper = ToolWrapper(
        name=func.__name__,
        function=func,
        params_model=annotation,
        description=docstring.strip(),
    )

    if wrapper.name in TOOL_REGISTRY:
        raise ValueError(f"Tool '{wrapper.name}' is already registered.")

    TOOL_REGISTRY[wrapper.name] = wrapper
    return func


def get_tool(name: str) -> Optional[ToolWrapper]:
    return TOOL_REGISTRY.get(name)


def list_tools() -> list[str]:
    return list(TOOL_REGISTRY.keys())


def tools_catalog() -> str:
    return json.dumps([tool.schema() for tool in TOOL_REGISTRY.values()], indent=2, ensure_ascii=False)

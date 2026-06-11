import json
import project.tools.rag_tools  # noqa: F401
import re
from typing import Any, Dict, List, Optional

from project.llm.providers import LLMProvider
from project.prompts.registry import PromptRegistry
from project.tools.registry import TOOL_REGISTRY, tools_catalog

# Importing this module registers tools through decorators.
import project.tools.basic_tools  # noqa: F401


class ReActAgent:
    def __init__(
        self,
        llm: LLMProvider,
        prompt_registry: PromptRegistry,
        max_iterations: int = 6,
    ):
        self.llm = llm
        self.prompt_registry = prompt_registry
        self.max_iterations = max_iterations
        self.history: List[str] = []

    def run(self, user_input: str) -> str:
        scratchpad = ""

        for iteration in range(self.max_iterations):
            system_prompt = self.prompt_registry.render(
                "react_system",
                tools_catalog=tools_catalog(),
                conversation_history="\n".join(self.history[-10:]),
                user_input=user_input,
                scratchpad=scratchpad,
            )

            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                }
            ]

            response = self.llm.invoke(messages)

            print("\n========== RAW LLM RESPONSE ==========")
            print(response)
            print("======================================\n")

            final = self._extract_final_answer(response)

            if final is not None:
                self.history.append("User: " + user_input)
                self.history.append("Assistant: " + final)
                return final

            tool_calls = self._parse_tool_calls(response)

            if not tool_calls:
                scratchpad += (
                    "\nInvalid model output. Expected Action/Actions/Final Answer."
                    "\nModel output was:\n"
                    + response
                    + "\n"
                )
                continue

            observations = []

            for call in tool_calls:
                observation = self.execute_tool(call)
                observations.append(observation)

            scratchpad += (
                "\nLLM Output:\n"
                + response
                + "\n\nObservations:\n"
                + json.dumps(observations, indent=2, ensure_ascii=False)
                + "\n\nIMPORTANT: You already have the tool observation above. "
                + "Do not call the same tool again if the observation answers the user. "
                + "Now answer using exactly this format:\n"
                + "Final Answer: <clear answer for the user>\n"
            )

        return "Nu am putut finaliza răspunsul: limita de iterații a fost atinsă."

    def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, str]:
        name = tool_call.get("name")
        args = tool_call.get("args", {})

        print("\n========== TOOL CALL ==========")
        print("Tool:", name)
        print("Args:", json.dumps(args, indent=2, ensure_ascii=False))
        print("===============================\n")

        if name not in TOOL_REGISTRY:
            return {
                "tool": str(name),
                "content": "Eroare: tool-ul '" + str(name) + "' nu există.",
            }

        try:
            result = TOOL_REGISTRY[name].call(args)
            return {
                "tool": str(name),
                "content": str(result),
            }
        except Exception as exc:
            return {
                "tool": str(name),
                "content": "Eroare la executarea tool-ului: " + str(exc),
            }

    def _extract_final_answer(self, text: str) -> Optional[str]:
        patterns = [
            r"Final Answer:\s*(.*)",
            r"\*\*Final Answer\*\*\s*:?\s*(.*)",
            r"FINAL ANSWER:\s*(.*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.DOTALL)

            if match:
                final = match.group(1).strip()

                if final:
                    return final

                before_marker = text[: match.start()].strip()
                if before_marker:
                    return before_marker

        return None

    def _parse_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        multiple = re.search(
            r"Actions:\s*(\[.*\])",
            text,
            flags=re.DOTALL,
        )

        if multiple:
            try:
                data = json.loads(multiple.group(1))
                result = []

                for item in data:
                    result.append(
                        {
                            "name": item["name"],
                            "args": item.get("args", {}),
                        }
                    )

                return result
            except Exception:
                return []

        action_match = re.search(
            r"Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)",
            text,
        )

        if not action_match:
            return []

        action_name = action_match.group(1).strip()

        action_input_match = re.search(
            r"Action Input:\s*",
            text,
            flags=re.DOTALL,
        )

        if not action_input_match:
            return [
                {
                    "name": action_name,
                    "args": {},
                }
            ]

        json_start_index = action_input_match.end()
        json_text = text[json_start_index:].strip()

        args = self._extract_first_json_object(json_text)

        if args is None:
            args = {}

        return [
            {
                "name": action_name,
                "args": args,
            }
        ]

    def _extract_first_json_object(self, text: str) -> Optional[Dict[str, Any]]:
        start = text.find("{")

        if start == -1:
            return None

        brace_count = 0
        in_string = False
        escape = False

        for index in range(start, len(text)):
            char = text[index]

            if escape:
                escape = False
                continue

            if char == "\\":
                escape = True
                continue

            if char == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            if char == "{":
                brace_count += 1

            elif char == "}":
                brace_count -= 1

                if brace_count == 0:
                    candidate = text[start : index + 1]

                    try:
                        return json.loads(candidate)
                    except Exception:
                        return None

        return None
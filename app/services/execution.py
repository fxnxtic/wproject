import asyncio

import epicbox as eb
from openrouter.components import ToolDefinitionJSONTypedDict

from app.types.execution import ExecutionResult, RuntimeConfig

DEFAULT_RUNTIMES = [
    RuntimeConfig(
        name="execute_python",
        desc="Run .py file into python 3.12 environment",
        image="python:3.12-alpine",
        command="python3 main.py",
        network=True,
        files_fn=lambda content: [{"name": "main.py", "content": content.encode()}],
        limits={"cputime": 1, "memory": 64},
    )
]


class ExecutionService:
    def __init__(self, configs: list[RuntimeConfig] = DEFAULT_RUNTIMES) -> None:
        self._configs: list[RuntimeConfig] = configs

        self._configure(self._configs)

    @staticmethod
    def _make_profile(config: RuntimeConfig) -> eb.Profile:
        return eb.Profile(
            name=config.name,
            docker_image=config.image,
            command=config.command,
            network_disabled=config.network,
        )

    def _configure(self, configs: list[RuntimeConfig]) -> None:
        eb.configure([self._make_profile(cfg) for cfg in configs])

    @staticmethod
    async def execute(config: RuntimeConfig, content: str) -> ExecutionResult:
        result = await asyncio.to_thread(
            eb.run,
            config.name,
            command=config.command,
            files=config.files_fn(content),
            limits=config.limits,
        )
        return ExecutionResult(
            exit_code=result["exit_code"],
            stdout=result["stdout"].decode(),
            stderr=result["stderr"].decode(),
            duration=result["duration"],
            timeout=result["timeout"],
            oom_killed=result["oom_killed"],
        )

    @staticmethod
    def resolve(config: RuntimeConfig) -> ToolDefinitionJSONTypedDict:
        return {
            "type": "function",
            "function": {
                "name": config.name,
                "description": config.desc,
                "parameters": {
                    "type": "object",
                    "properties": {"content": {"type": "string"}},
                    "required": ["content"],
                },
            },
        }

    async def use_tool(self, name: str, **kwargs) -> str:
        cfg = next(cfg for cfg in self._configs if cfg.name == name)

        result = await self.execute(cfg, **kwargs)
        return result.model_dump_json()

    def resolve_all(self) -> list[ToolDefinitionJSONTypedDict]:
        return [self.resolve(cfg) for cfg in self._configs]

    @property
    def configs(self) -> list[RuntimeConfig]:
        return self._configs

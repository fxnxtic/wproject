from openrouter._hooks import Callable
from pydantic import BaseModel


class RuntimeConfig(BaseModel):
    name: str
    desc: str
    image: str
    command: str
    network: bool
    files_fn: Callable[[str], list[dict]]
    limits: dict[str, str | int | float]


class ExecutionResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    timeout: bool
    oom_killed: bool

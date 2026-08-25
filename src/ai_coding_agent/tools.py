from pathlib import Path

from langchain_core.tools import tool


WORKSPACE = Path("workspace")


@tool
def write_file(filename: str, content: str) -> str:
    """Create or overwrite a file inside the coding workspace."""

    WORKSPACE.mkdir(exist_ok=True)

    file_path = WORKSPACE / filename

    file_path.write_text(
        content,
        encoding="utf-8"
    )

    return f"File '{filename}' created successfully."


@tool
def read_file(filename: str) -> str:
    """Read a file from the coding workspace."""

    file_path = WORKSPACE / filename

    if not file_path.exists():
        return f"File '{filename}' does not exist."

    return file_path.read_text(
        encoding="utf-8"
    )


@tool
def list_files() -> str:
    """List all files inside the coding workspace."""

    WORKSPACE.mkdir(exist_ok=True)

    files = [
        str(file.relative_to(WORKSPACE))
        for file in WORKSPACE.rglob("*")
        if file.is_file()
    ]

    if not files:
        return "The workspace is empty."

    return "\n".join(files)
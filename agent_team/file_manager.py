
from pathlib import Path
import re

# Root directory: MultiAgentTeam/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# All AI-generated applications must be saved here
OUTPUT_DIR = PROJECT_ROOT / "generated_projects"

# create_project_folder() — creates a new application directory.
def create_project_folder(project_name: str) -> Path:
    """Create a separate folder for a generated application."""

    if not re.fullmatch(r"[a-zA-Z0-9_-]+", project_name):
        raise ValueError("Invalid project name.")

    project_path = OUTPUT_DIR / project_name

    # Prevent overwriting an existing project folder
    if project_path.exists():
        raise FileExistsError(
            f"Project already exists: {project_path}"
        )

    project_path.mkdir(parents=True, exist_ok=False)

    return project_path

# write_project_files() — writes generated code and documentation into it.

def write_project_files(project_name: str, files: dict) -> Path:
    """
    Save generated source files and documentation.
    Never executes generated code.
    """

    if not isinstance(files, dict) or not files:
        raise ValueError("Files must be a non-empty dictionary.")

    project_path = create_project_folder(project_name)

    try:
        for relative_path, content in files.items():

            if not isinstance(relative_path, str) or not relative_path.strip():
                raise ValueError("File path must be a non-empty string.")

            if not isinstance(content, str):
                raise TypeError("File content must be a string.")

            relative_path = Path(relative_path)

            if (
                relative_path.is_absolute()
                or relative_path.drive
                or ".." in relative_path.parts
                or not relative_path.parts
            ):
                raise ValueError(f"Unsafe file path: {relative_path}")

            file_path = project_path / relative_path

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

        return project_path

    except Exception:
        import shutil
        shutil.rmtree(project_path)
        raise

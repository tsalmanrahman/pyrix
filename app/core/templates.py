from pathlib import Path
from fastapi.templating import Jinja2Templates

# Cross-platform absolute path resolution: works on Windows, macOS, and Linux
# regardless of current working directory.
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

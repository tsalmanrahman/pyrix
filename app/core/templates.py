from pathlib import Path
from fastapi.templating import Jinja2Templates

# Cross-platform absolute path resolution: works on Windows, macOS, and Linux
# regardless of current working directory.
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def format_money(value, symbol: str = None, decimals: int = 2) -> str:
    """Formats numeric amounts with currency symbol and thousands commas."""
    try:
        if value is None or value == "":
            val = 0.0
        else:
            val = float(value)
        formatted = f"{val:,.{decimals}f}"
        if symbol:
            return f"{symbol} {formatted}" if len(symbol) > 1 else f"{symbol}{formatted}"
        return formatted
    except Exception:
        return str(value or "")

templates.env.filters["money"] = format_money


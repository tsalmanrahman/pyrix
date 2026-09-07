from pathlib import Path
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

# Cross-platform absolute path resolution: works on Windows, macOS, and Linux
# regardless of current working directory.
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@pass_context
def format_money(context, value, symbol: str = None, decimals: int = None) -> str:
    """Formats numeric amounts with dynamic company currency symbol and thousands commas."""
    # Handle direct python calls where context is not passed as first argument
    if not hasattr(context, "get") and not hasattr(context, "resolve"):
        decimals = symbol
        symbol = value
        value = context
        context = {}

    active_comp = context.get("active_company") if hasattr(context, "get") else None

    if symbol is None:
        if active_comp and isinstance(active_comp, dict):
            symbol = active_comp.get("currency_symbol") or active_comp.get("currency")
        elif hasattr(active_comp, "currency_symbol"):
            symbol = getattr(active_comp, "currency_symbol")
        else:
            symbol = "৳"

    if isinstance(symbol, dict):
        symbol = symbol.get("currency_symbol") or symbol.get("currency") or "৳"

    if decimals is None:
        if active_comp and isinstance(active_comp, dict):
            decimals = active_comp.get("decimal_places", 2)
        else:
            decimals = 2
    else:
        try:
            decimals = int(decimals)
        except Exception:
            decimals = 2

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

@pass_context
def get_currency_symbol(context, custom_company=None) -> str:
    """Returns active company currency symbol (e.g. '৳', '$', '€')."""
    comp = custom_company or (context.get("active_company") if hasattr(context, "get") else None)
    if isinstance(comp, dict):
        return comp.get("currency_symbol") or comp.get("currency") or "৳"
    return "৳"

@pass_context
def get_currency_code(context, custom_company=None) -> str:
    """Returns active company currency code (e.g. 'BDT', 'USD', 'EUR')."""
    comp = custom_company or (context.get("active_company") if hasattr(context, "get") else None)
    if isinstance(comp, dict):
        return comp.get("currency") or comp.get("currency_code") or "BDT"
    return "BDT"

templates.env.filters["money"] = format_money
templates.env.globals["currency_symbol"] = get_currency_symbol
templates.env.globals["currency_code"] = get_currency_code



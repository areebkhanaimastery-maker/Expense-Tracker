"""
Proxy module for backward compatibility.
Re-exports display routines from app.cli.formatting and app.cli.menus.
"""

from app.cli.formatting import display_expenses
from app.cli.menus import display_menu

__all__ = ["display_menu", "display_expenses"]

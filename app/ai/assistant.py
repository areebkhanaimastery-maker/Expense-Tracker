"""
Expense AI Assistant.

This module will provide a conversational AI interface
for the Expense Tracker. It will interpret natural-language
queries and invoke the appropriate service methods.

Implementation planned for Phase 4.
"""


class ExpenseAssistant:
    """AI assistant for expense management."""

    def __init__(self, service):
        self.service = service

    def process(self, user_input: str) -> str:
        """
        Process a natural-language user input
        and return an appropriate response.
        """
        raise NotImplementedError(
            "AI Assistant will be implemented in Phase 4."
        )

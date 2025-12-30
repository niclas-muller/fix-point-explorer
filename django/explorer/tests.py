from django.test import TestCase
from django.core.exceptions import ValidationError

from .models import Function


class FunctionModelTests(TestCase):
    def test_nonparsable_function_string_raises_syntax_error(self) -> None:
        nonparsable_examples = [
            "sin(x",
            "sin(x+u))",
            "((_o",
        ]
        for example in nonparsable_examples:
            self.assertRaises(ValidationError, Function.create, example)

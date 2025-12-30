from django.db import models
from django.core.exceptions import ValidationError

from sympy.parsing.sympy_parser import parse_expr
from tokenize import TokenError


class Function(models.Model):
    function_string = models.CharField(unique=True)

    @classmethod
    def create(cls, function_string: str) -> "Function":
        # Clean the string (all lowercase, no blanks allowed):
        function_string = function_string.lower().replace(" ", "")

        # Test for uniqueness:
        if function_string in cls.objects.values_list("function_string", flat=True):
            raise ValidationError(f"Function {function_string} already defined.")

        # Raise if string cannot be parsed into sympy expression:
        try:
            expr = parse_expr(function_string)
        except (SyntaxError, TokenError):
            raise ValidationError(
                f"Function {function_string} cannot be parsed.", code="invalid"
            )

        # Raise if parsed expression has more than one unknown:
        if len(expr.free_symbols) != 1:
            raise ValidationError(
                f"Function {function_string} has more than one variable."
            )

        return cls(function_string=function_string)

    def __str__(self) -> str:
        return self.function_string


class Limit(models.Model):
    function = models.ForeignKey(Function, on_delete=models.CASCADE)
    x_index = models.PositiveBigIntegerField()
    y_index = models.PositiveBigIntegerField()
    limit = models.DecimalField(max_digits=20, decimal_places=20)

    def x_value(self) -> float:
        "Translate the x_index into an x_value."
        # values between 0 and 9223372036854775807 = 2**63 - 1
        return self.x_index / 2.0**63

    def __str__(self) -> str:
        return f"{self.function} @ ({self.x_index},{self.y_index})"

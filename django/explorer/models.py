from typing import Callable
import re

from django.db import models
from django.core.exceptions import ValidationError

from sympy.core import Expr
from sympy.parsing.sympy_parser import parse_expr
from tokenize import TokenError
from sympy.abc import x, y, z
from sympy import lambdify, latex

ALLOWED_FUNCTION_ARGS = [x, y, z]
PREFERRED_FUNCTION_ARG = z
CONSTANT_SYMBOL_PATTERN = re.compile(r"^c\d+$")


class Function(models.Model):
    function_string = models.CharField(unique=True)

    @classmethod
    def create(cls, function_string: str) -> "Function":
        # Clean the string (all lowercase, no blanks allowed)
        function_string = function_string.lower().replace(" ", "")

        # Raise if string cannot be parsed into sympy expression
        try:
            expr = parse_expr(function_string)
        except (SyntaxError, TokenError):
            raise ValidationError(
                f"Function {function_string} cannot be parsed.", code="invalid"
            )

        # Make sure that expr is of type Expression
        # (handles subtle bugs such as Ellipsis not being converted to sympy
        if not isinstance(expr, Expr):
            raise ValidationError(
                f"Function {function_string} cannot be parsed.", code="invalid"
            )

        # Check that free_symbols are only sourced from allowed values
        # free_symbols *must* contain exactly one of [x,y,z] and can contain {c_i}
        symbols = expr.free_symbols
        functional_symbols = [
            symbol for symbol in symbols if symbol in ALLOWED_FUNCTION_ARGS
        ]
        other_symbols = symbols - set(functional_symbols)
        if len(functional_symbols) != 1:
            raise ValidationError(
                f"Arguments {functional_symbols} do not match requirements (use exactly one of x, y or z)."
            )

        for symbol in other_symbols:
            match = CONSTANT_SYMBOL_PATTERN.match(str(symbol))
            if not match:
                raise ValidationError(
                    f"Parameter {symbol} does not match requirements (use c1, c2, ...)."
                )

        # Rename functional symbol to z
        expr = expr.subs(functional_symbols[0], z)
        function_string = str(expr)

        # Test for uniqueness:
        if function_string in cls.objects.values_list("function_string", flat=True):
            raise ValidationError(f"Function {function_string} already defined.")

        return cls(function_string=function_string)

    @property
    def as_expr(self) -> Expr:
        return parse_expr(self.function_string)

    @property
    def parameter_names(self) -> set[str]:
        return set(
            [
                str(symbol)
                for symbol in self.as_expr.free_symbols
                if CONSTANT_SYMBOL_PATTERN.match(str(symbol))
            ]
        )

    def as_lambda(
        self, parameters: dict[str, complex]
    ) -> None | Callable[[complex], complex]:
        if set(parameters.keys()) != self.parameter_names:
            raise ValidationError("Did not provide values for all parameters.")
        lambda_expr: Callable[[complex], complex] = lambdify(
            z, self.as_expr.subs(parameters)
        )
        return lambda_expr

    @property
    def function_string_latex(self) -> str:
        return f"$${latex(self.as_expr)}$$"

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

from django.db import models


class Function(models.Model):
    "Mapping from function definition string (sympifyable) to function ID."

    function_string = models.CharField()

    def __str__(self) -> str:
        return self.function_string


class Limit(models.Model):
    "Per function, save the limiting values at all seen grid points."

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

from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db import IntegrityError
from django.db.models.query import QuerySet

from .models import Function

from sympy.parsing.sympy_parser import parse_expr
from tokenize import TokenError

from typing import Union


def is_valid_function_string(function_string: str) -> bool:
    try:
        expr = parse_expr(function_string)
    except (SyntaxError, TokenError):
        return False
    if expr is not None:
        return len(expr.free_symbols) == 1
    return False


def index(request: HttpRequest) -> HttpResponse:
    function_list = Function.objects.all()
    context: dict[str, Union[str, QuerySet[Function, Function]]] = {
        "function_list": function_list
    }
    if "function_string" in request.POST:
        if is_valid_function_string(
            function_string := request.POST["function_string"].replace(" ", "")
        ):
            function = Function(function_string=function_string)
            try:
                function.save()
            except IntegrityError:
                context.update(
                    {"message": f"Function {function_string} is already in db."}
                )
                return render(request, "explorer/index.html", context)
            return HttpResponseRedirect(
                reverse("explorer:index"),
            )
        context.update({"message": f"Invalid function {function_string}."})
    return render(request, "explorer/index.html", context)


def function(request: HttpRequest, function_id: int) -> HttpResponse:
    function = get_object_or_404(Function, id=function_id)
    context = {"function": function}
    return render(request, "explorer/function.html", context)

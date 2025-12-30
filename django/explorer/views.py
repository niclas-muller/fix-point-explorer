from typing import Union

from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet

from django_stubs_ext import StrOrPromise

from .models import Function


def index(request: HttpRequest) -> HttpResponse:
    function_list = Function.objects.all()
    context: dict[str, Union[StrOrPromise, QuerySet[Function, Function]]] = {
        "function_list": function_list
    }

    if "function_string" in request.POST:
        function_string = request.POST["function_string"]
        try:
            function = Function.create(function_string)
        except ValidationError as e:
            context.update({"message": e.message})
            return render(request, "explorer/index.html", context)

        function.save()
        return HttpResponseRedirect(reverse("explorer:index"))

    return render(request, "explorer/index.html", context)


def detail(request: HttpRequest, function_id: int) -> HttpResponse:
    function = get_object_or_404(Function, id=function_id)
    context = {"function": function}
    return render(request, "explorer/detail.html", context)
